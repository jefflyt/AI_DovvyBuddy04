#!/usr/bin/env tsx
/**
 * RAG Performance Benchmark Script
 * 
 * Measures and compares:
 * - Retrieval latency (vector search performance)
 * - End-to-end response time (with vs without RAG)
 * - Similarity score distribution
 * - Response quality metrics
 * 
 * Usage:
 *   tsx scripts/benchmark-rag.ts
 */

import { config } from 'dotenv';
import pino from 'pino';
import { retrieveRelevantChunks } from '../src/lib/rag/retrieval';
import { orchestrateChat } from '../src/lib/orchestration/chat-orchestrator';

// Load environment variables
config({ path: '.env.local' });

const logger = pino({ name: 'rag-benchmark' });

interface BenchmarkResult {
  query: string;
  category: string;
  ragEnabled: boolean;
  retrieval?: {
    durationMs: number;
    chunksFound: number;
    avgSimilarity: number;
    minSimilarity: number;
    maxSimilarity: number;
  };
  orchestration: {
    durationMs: number;
    tokensUsed?: number;
    contextChunks: number;
    responseLength: number;
  };
}

// Test queries covering different categories
const TEST_QUERIES = [
  // Certification queries
  { query: 'What is PADI Open Water certification?', category: 'certification' },
  { query: 'What are the prerequisites for SSI Open Water?', category: 'certification' },
  { query: 'How long does it take to get certified?', category: 'certification' },
  
  // Dive site queries
  { query: 'Where should I dive in Tioman?', category: 'dive-site' },
  { query: 'What marine life can I see at Tiger Reef?', category: 'dive-site' },
  { query: 'What is the depth at Batu Malang?', category: 'dive-site' },
  
  // Trip planning queries
  { query: 'Best dive sites for beginners in Malaysia?', category: 'trip-planning' },
  { query: 'When is the best time to dive in Tioman?', category: 'trip-planning' },
  
  // Safety queries
  { query: 'What should I do if I run out of air?', category: 'safety' },
  { query: 'How do I equalize my ears underwater?', category: 'safety' },
];

/**
 * Benchmark retrieval performance
 */
async function benchmarkRetrieval(query: string): Promise<BenchmarkResult['retrieval']> {
  const startTime = Date.now();
  
  const results = await retrieveRelevantChunks(query, {
    topK: 5,
    minSimilarity: 0.7,
  });
  
  const durationMs = Date.now() - startTime;
  
  if (results.length === 0) {
    return {
      durationMs,
      chunksFound: 0,
      avgSimilarity: 0,
      minSimilarity: 0,
      maxSimilarity: 0,
    };
  }
  
  const similarities = results.map(r => r.similarity);
  const avgSimilarity = similarities.reduce((sum, s) => sum + s, 0) / similarities.length;
  const minSimilarity = Math.min(...similarities);
  const maxSimilarity = Math.max(...similarities);
  
  return {
    durationMs,
    chunksFound: results.length,
    avgSimilarity,
    minSimilarity,
    maxSimilarity,
  };
}

/**
 * Benchmark end-to-end orchestration
 */
async function benchmarkOrchestration(
  query: string,
  ragEnabled: boolean
): Promise<BenchmarkResult['orchestration']> {
  // Temporarily set ENABLE_RAG
  const originalValue = process.env.ENABLE_RAG;
  process.env.ENABLE_RAG = ragEnabled ? 'true' : 'false';
  
  const startTime = Date.now();
  
  try {
    const response = await orchestrateChat({ message: query });
    const durationMs = Date.now() - startTime;
    
    return {
      durationMs,
      tokensUsed: response.metadata?.tokensUsed,
      contextChunks: response.metadata?.contextChunks || 0,
      responseLength: response.response.length,
    };
  } finally {
    // Restore original value
    process.env.ENABLE_RAG = originalValue;
  }
}

/**
 * Run benchmark for a single query
 */
async function benchmarkQuery(
  query: string,
  category: string
): Promise<{ withRAG: BenchmarkResult; withoutRAG: BenchmarkResult }> {
  logger.info({ query, category, msg: 'Benchmarking query' });
  
  // Benchmark with RAG enabled
  const retrievalStats = await benchmarkRetrieval(query);
  const orchestrationWithRAG = await benchmarkOrchestration(query, true);
  
  const withRAG: BenchmarkResult = {
    query,
    category,
    ragEnabled: true,
    retrieval: retrievalStats,
    orchestration: orchestrationWithRAG,
  };
  
  // Benchmark with RAG disabled
  const orchestrationWithoutRAG = await benchmarkOrchestration(query, false);
  
  const withoutRAG: BenchmarkResult = {
    query,
    category,
    ragEnabled: false,
    orchestration: orchestrationWithoutRAG,
  };
  
  return { withRAG, withoutRAG };
}

/**
 * Calculate statistics from benchmark results
 */
function calculateStats(results: BenchmarkResult[]) {
  const retrievalTimes = results
    .filter(r => r.retrieval)
    .map(r => r.retrieval!.durationMs);
  
  const orchestrationTimes = results.map(r => r.orchestration.durationMs);
  
  const similarities = results
    .filter(r => r.retrieval)
    .map(r => r.retrieval!.avgSimilarity);
  
  const chunksFound = results
    .filter(r => r.retrieval)
    .map(r => r.retrieval!.chunksFound);
  
  return {
    retrieval: {
      count: retrievalTimes.length,
      avgMs: avg(retrievalTimes),
      p50Ms: percentile(retrievalTimes, 50),
      p95Ms: percentile(retrievalTimes, 95),
      p99Ms: percentile(retrievalTimes, 99),
    },
    orchestration: {
      count: orchestrationTimes.length,
      avgMs: avg(orchestrationTimes),
      p50Ms: percentile(orchestrationTimes, 50),
      p95Ms: percentile(orchestrationTimes, 95),
      p99Ms: percentile(orchestrationTimes, 99),
    },
    similarity: {
      avg: avg(similarities),
      min: Math.min(...similarities),
      max: Math.max(...similarities),
    },
    chunks: {
      avg: avg(chunksFound),
      min: Math.min(...chunksFound),
      max: Math.max(...chunksFound),
    },
  };
}

function avg(numbers: number[]): number {
  if (numbers.length === 0) return 0;
  return numbers.reduce((sum, n) => sum + n, 0) / numbers.length;
}

function percentile(numbers: number[], p: number): number {
  if (numbers.length === 0) return 0;
  const sorted = [...numbers].sort((a, b) => a - b);
  const index = Math.ceil((p / 100) * sorted.length) - 1;
  return sorted[index];
}

/**
 * Format benchmark results for display
 */
function formatResults(
  withRAG: BenchmarkResult[],
  withoutRAG: BenchmarkResult[]
) {
  const ragStats = calculateStats(withRAG);
  const noRagStats = calculateStats(withoutRAG);
  
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║           RAG PERFORMANCE BENCHMARK RESULTS                ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');
  
  console.log('📊 RETRIEVAL PERFORMANCE (Vector Search Only)');
  console.log('─────────────────────────────────────────────────────────────');
  console.log(`  Queries tested: ${ragStats.retrieval.count}`);
  console.log(`  Average time:   ${ragStats.retrieval.avgMs.toFixed(1)}ms`);
  console.log(`  P50 (median):   ${ragStats.retrieval.p50Ms.toFixed(1)}ms`);
  console.log(`  P95:            ${ragStats.retrieval.p95Ms.toFixed(1)}ms`);
  console.log(`  P99:            ${ragStats.retrieval.p99Ms.toFixed(1)}ms`);
  console.log('');
  
  console.log('🎯 SIMILARITY SCORES');
  console.log('─────────────────────────────────────────────────────────────');
  console.log(`  Average:        ${ragStats.similarity.avg.toFixed(3)}`);
  console.log(`  Min:            ${ragStats.similarity.min.toFixed(3)}`);
  console.log(`  Max:            ${ragStats.similarity.max.toFixed(3)}`);
  console.log('');
  
  console.log('📦 CHUNKS RETRIEVED');
  console.log('─────────────────────────────────────────────────────────────');
  console.log(`  Average:        ${ragStats.chunks.avg.toFixed(1)}`);
  console.log(`  Min:            ${ragStats.chunks.min}`);
  console.log(`  Max:            ${ragStats.chunks.max}`);
  console.log('');
  
  console.log('⚡ END-TO-END RESPONSE TIME (WITH RAG)');
  console.log('─────────────────────────────────────────────────────────────');
  console.log(`  Queries tested: ${ragStats.orchestration.count}`);
  console.log(`  Average time:   ${ragStats.orchestration.avgMs.toFixed(0)}ms`);
  console.log(`  P50 (median):   ${ragStats.orchestration.p50Ms.toFixed(0)}ms`);
  console.log(`  P95:            ${ragStats.orchestration.p95Ms.toFixed(0)}ms`);
  console.log(`  P99:            ${ragStats.orchestration.p99Ms.toFixed(0)}ms`);
  console.log('');
  
  console.log('⚡ END-TO-END RESPONSE TIME (WITHOUT RAG)');
  console.log('─────────────────────────────────────────────────────────────');
  console.log(`  Queries tested: ${noRagStats.orchestration.count}`);
  console.log(`  Average time:   ${noRagStats.orchestration.avgMs.toFixed(0)}ms`);
  console.log(`  P50 (median):   ${noRagStats.orchestration.p50Ms.toFixed(0)}ms`);
  console.log(`  P95:            ${noRagStats.orchestration.p95Ms.toFixed(0)}ms`);
  console.log(`  P99:            ${noRagStats.orchestration.p99Ms.toFixed(0)}ms`);
  console.log('');
  
  console.log('📈 COMPARISON (WITH RAG vs WITHOUT RAG)');
  console.log('─────────────────────────────────────────────────────────────');
  const overhead = ragStats.orchestration.avgMs - noRagStats.orchestration.avgMs;
  const overheadPct = ((overhead / noRagStats.orchestration.avgMs) * 100).toFixed(1);
  console.log(`  RAG overhead:   ${overhead.toFixed(0)}ms (+${overheadPct}%)`);
  console.log(`  Retrieval %:    ${((ragStats.retrieval.avgMs / ragStats.orchestration.avgMs) * 100).toFixed(1)}% of total`);
  console.log('');
  
  console.log('📋 PER-CATEGORY BREAKDOWN');
  console.log('─────────────────────────────────────────────────────────────');
  
  const categories = [...new Set(withRAG.map(r => r.category))];
  for (const category of categories) {
    const categoryResults = withRAG.filter(r => r.category === category);
    const avgRetrieval = avg(categoryResults.map(r => r.retrieval!.durationMs));
    const avgOrchestration = avg(categoryResults.map(r => r.orchestration.durationMs));
    const avgChunks = avg(categoryResults.map(r => r.retrieval!.chunksFound));
    const avgSim = avg(categoryResults.map(r => r.retrieval!.avgSimilarity));
    
    console.log(`  ${category}:`);
    console.log(`    Queries: ${categoryResults.length}`);
    console.log(`    Retrieval: ${avgRetrieval.toFixed(1)}ms`);
    console.log(`    Total: ${avgOrchestration.toFixed(0)}ms`);
    console.log(`    Chunks: ${avgChunks.toFixed(1)}`);
    console.log(`    Similarity: ${avgSim.toFixed(3)}`);
    console.log('');
  }
  
  console.log('✅ PERFORMANCE TARGETS');
  console.log('─────────────────────────────────────────────────────────────');
  const p95Target = 3000; // 3 seconds
  const p95Actual = ragStats.orchestration.p95Ms;
  const p95Status = p95Actual < p95Target ? '✅ PASS' : '❌ FAIL';
  console.log(`  P95 < 3s:       ${p95Status} (${p95Actual.toFixed(0)}ms / ${p95Target}ms)`);
  
  const retrievalTarget = 200; // 200ms
  const retrievalActual = ragStats.retrieval.p95Ms;
  const retrievalStatus = retrievalActual < retrievalTarget ? '✅ PASS' : '⚠️  WARN';
  console.log(`  Retrieval < 200ms: ${retrievalStatus} (${retrievalActual.toFixed(0)}ms / ${retrievalTarget}ms)`);
  
  const similarityTarget = 0.7;
  const similarityActual = ragStats.similarity.avg;
  const similarityStatus = similarityActual >= similarityTarget ? '✅ PASS' : '⚠️  WARN';
  console.log(`  Avg similarity > 0.7: ${similarityStatus} (${similarityActual.toFixed(3)} / ${similarityTarget})`);
  console.log('');
}

/**
 * Main benchmark execution
 */
async function main() {
  console.log('🚀 Starting RAG Performance Benchmark...\n');
  
  // Verify environment setup
  if (!process.env.DATABASE_URL) {
    throw new Error('DATABASE_URL not set');
  }
  
  if (!process.env.GROQ_API_KEY && !process.env.GEMINI_API_KEY) {
    throw new Error('No LLM API key configured');
  }
  
  const withRAG: BenchmarkResult[] = [];
  const withoutRAG: BenchmarkResult[] = [];
  
  // Run benchmarks
  for (const { query, category } of TEST_QUERIES) {
    try {
      const results = await benchmarkQuery(query, category);
      withRAG.push(results.withRAG);
      withoutRAG.push(results.withoutRAG);
      
      // Add delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (error) {
      logger.error({
        query,
        error: error instanceof Error ? error.message : 'Unknown error',
        msg: 'Benchmark failed',
      });
    }
  }
  
  // Display results
  formatResults(withRAG, withoutRAG);
  
  // Save detailed results to file
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputPath = `benchmark-results-${timestamp}.json`;
  
  // Use Node.js fs.writeFileSync instead of Bun.write for cross-runtime compatibility
  const fs = await import('fs');
  fs.writeFileSync(
    outputPath,
    JSON.stringify({ withRAG, withoutRAG, timestamp: new Date().toISOString() }, null, 2)
  );
  
  console.log(`📄 Detailed results saved to: ${outputPath}\n`);
  
  logger.info({ msg: 'Benchmark complete' });
}

// Run benchmark
main().catch((error) => {
  logger.error({
    error: error instanceof Error ? error.message : 'Unknown error',
    stack: error instanceof Error ? error.stack : undefined,
    msg: 'Benchmark failed',
  });
  process.exit(1);
});
