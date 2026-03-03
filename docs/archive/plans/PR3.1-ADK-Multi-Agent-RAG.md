# PR3.1: Google ADK Multi-Agent RAG Integration

**Status:** ✅ Completed  
**Based on:** PR3 (Model Provider & Session Logic)  
**Date:** January 1, 2026  
**Completed:** January 1, 2026

---

## 1. Feature/Epic Summary

### Objective

Upgrade DovvyBuddy from single-provider LLM architecture to Google Agent Development Kit (ADK) based multi-agent RAG system, enabling specialized agents to coordinate on complex queries with tool use capabilities.

### User Impact

- **Improved response quality**: Specialized agents (Certification, Trip Planning) provide more accurate, contextual answers
- **Better safety handling**: Dedicated safety agent ensures appropriate disclaimers for medical/legal topics
- **Enhanced retrieval**: Retrieval agent actively fetches relevant context from knowledge base during conversation
- **Maintained experience**: API contract unchanged; users experience improvements transparently
- **Future capabilities**: Multi-agent foundation enables advanced features (booking, community, multilingual)

### Dependencies

- **Requires:** PR1 (Database Schema) — sessions table for state persistence
- **Requires:** PR3 (Model Provider & Session Logic) — baseline architecture to refactor
- **Integrates with:** PR2 (RAG Pipeline) — vector search wired to retrieval agent (conditional)
- **Enables:** PR4 (Lead Capture) — agent metadata provides richer lead signals
- **Enables:** PR5 (Chat Interface) — API contract preserved, transparent integration

### Assumptions

- **Assumption:** Google ADK SDK is compatible with Next.js serverless runtime (Vercel)
- **Assumption:** Multi-agent coordination overhead stays within 10s timeout
- **Assumption:** GCP Vertex AI costs acceptable for production use (~2-3 agent calls per query)
- **Assumption:** ADK provides sufficient tool execution reliability for production
- **Assumption:** PR2 RAG retrieval can be mocked if not ready; full integration deferred

---

## 2. Complexity & Fit

### Classification: `Single-PR` (with 6 implementation steps)

### Rationale

- **Behavior-preserving refactor**: API contract unchanged, user experience improved but not fundamentally different
- **Incremental approach**: 6 steps allow rollback at any point; old code preserved until Step 5
- **Self-contained scope**: ADK integration, agent definitions, orchestration upgrade contained within backend
- **No UI changes**: Frontend unaware of multi-agent architecture
- **Testable incrementally**: Each step has clear checkpoints and rollback strategy

While this refactor is substantial (replacing core LLM abstraction), the incremental approach and API preservation make it manageable as a single PR with multiple commits/phases.

---

## 3. Full-Stack Impact

### Frontend

**No changes planned.**  
API contract (`POST /api/chat`) unchanged. Frontend integration in PR5 remains unaffected.

### Backend

**Significant changes:**

- **New modules:**
  - `src/lib/agent/` — ADK agent abstraction layer
    - `types.ts` — Agent, Tool interfaces
    - `base-agent.ts` — ADK wrapper
    - `config.ts` — ADK initialization (genkit)
    - `retrieval-agent.ts` — Vector search specialist
    - `certification-agent.ts` — Certification query specialist
    - `trip-agent.ts` — Trip planning specialist
    - `safety-agent.ts` — Response validation
    - `agent-registry.ts` — Central agent lookup
    - `tools/` — Tool implementations
      - `vector-search-tool.ts`
      - `session-lookup-tool.ts`
      - `safety-check-tool.ts`

- **Modified modules:**
  - `src/lib/orchestration/chat-orchestrator.ts` — Multi-agent coordination
  - `src/lib/orchestration/types.ts` — Agent-specific types
  - `src/app/api/chat/route.ts` — ADK error mapping, telemetry

- **Deleted modules:**
  - `src/lib/model-provider/groq-provider.ts`
  - `src/lib/model-provider/gemini-provider.ts`
  - `src/lib/model-provider/factory.ts`
  - `src/lib/model-provider/base-provider.ts`
  - (Entire `src/lib/model-provider/` removed in Step 5)

- **New API endpoints:** None (existing `/api/chat` enhanced)

- **Authentication/Authorization:** No changes (guest sessions)

- **Validation:** Preserved from PR3

- **Error Handling:**
  - ADK-specific error mapping (tool failures, agent timeouts)
  - Graceful degradation (agent failure → fallback response)

### Data

**No schema changes.**

- **Tables used:**
  - `sessions` — Read/write unchanged
  - `content_embeddings` — Read via PR2 retrieval (if available)

- **Data operations:**
  - Tool: `vector-search-tool` queries embeddings table via PR2's `retrieveContext`
  - Tool: `session-lookup-tool` reads session history
  - No new writes

### Infra / Config

**New environment variables:**

```bash
# Google ADK Configuration
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
ADK_MODEL=gemini-2.0-flash
ENABLE_ADK=true  # Feature flag for gradual rollout

# Agent-specific config
# NOTE: Always use gemini-2.0-flash for all Gemini LLM calls (not pro versions)
ADK_RETRIEVAL_MODEL=gemini-2.0-flash
ADK_SPECIALIST_MODEL=gemini-2.0-flash
ADK_SAFETY_MODEL=gemini-2.0-flash

# Tool configuration
ENABLE_RAG=false  # Gate for PR2 integration
VECTOR_SEARCH_TIMEOUT_MS=2000
AGENT_TIMEOUT_MS=5000
```

**Removed environment variables:**

- `LLM_PROVIDER` (replaced by ADK)
- `GROQ_API_KEY` (replaced by GCP credentials)
- `GROQ_MODEL` (replaced by ADK_MODEL)

**CI/CD:**

- Add GCP service account credentials to Vercel environment variables
- Existing `pnpm typecheck && pnpm lint && pnpm test && pnpm build` covers new code

**Dependencies to add:**

- `@google-cloud/genkit`
- `@google-cloud/genkit-ai-googleai`
- `@genkit-ai/ai` (core)
- `@genkit-ai/googleai` (Vertex AI integration)

---

## 4. PR Roadmap (6-Step Plan)

### Step 1: ADK Foundation Setup

**Goal**  
Install Google ADK SDK, configure GCP authentication, create base agent abstraction.

**Scope**

**In scope:**

- Install ADK SDK packages
- Configure GCP project and service account
- Create `src/lib/agent/` module with base types
- Initialize ADK in `config.ts`
- Update `.env.example`

**Out of scope:**

- Agent implementations (Step 2)
- Orchestration changes (Step 4)
- Removing old providers (Step 5)

**Backend Changes**

1. **Dependencies** (`package.json`):

   ```json
   "@google-cloud/genkit": "^0.5.0",
   "@google-cloud/genkit-ai-googleai": "^0.5.0"
   ```

2. **New files:**
   - `src/lib/agent/types.ts`:

     ```typescript
     export interface Agent {
       name: string
       description: string
       tools?: Tool[]
       generate(input: AgentInput): Promise<AgentOutput>
     }

     export interface Tool {
       name: string
       description: string
       parameters: Record<string, any>
       execute(params: any): Promise<any>
     }

     export interface AgentInput {
       messages: Array<{ role: string; content: string }>
       context?: string
       sessionId?: string
     }

     export interface AgentOutput {
       content: string
       toolCalls?: Array<{ tool: string; params: any; result: any }>
       metadata?: { tokensUsed?: number; model?: string }
     }
     ```

   - `src/lib/agent/base-agent.ts`:

     ```typescript
     import { Agent, AgentInput, AgentOutput } from './types'

     export abstract class BaseAgent implements Agent {
       constructor(
         public name: string,
         public description: string,
         public tools: Tool[] = []
       ) {}

       abstract generate(input: AgentInput): Promise<AgentOutput>
     }
     ```

   - `src/lib/agent/config.ts`:

     ```typescript
     import { genkit } from '@google-cloud/genkit'
     import { googleAI } from '@genkit-ai/googleai'

     let genkitInstance: any = null

     export function getGenkit() {
       if (!genkitInstance) {
         if (!process.env.GOOGLE_CLOUD_PROJECT) {
           console.warn('GOOGLE_CLOUD_PROJECT not set; ADK disabled')
           return null
         }

         genkitInstance = genkit({
           plugins: [googleAI()],
           model: process.env.ADK_MODEL || 'gemini-2.0-flash',
         })
       }
       return genkitInstance
     }
     ```

   - `src/lib/agent/index.ts`:
     ```typescript
     export * from './types'
     export * from './base-agent'
     export * from './config'
     ```

3. **Configuration:**
   - Update `.env.example` with new vars (see Infra section)

**Frontend Changes:** None

**Data Changes:** None

**Verification:**

- `pnpm install` succeeds
- `pnpm typecheck` passes
- `pnpm build` succeeds
- Dev server starts (logs warning if GCP creds missing)
- Existing `/api/chat` still works (uses PR3 providers)

**Rollback:** Delete `src/lib/agent/`, restore `package.json`

---

### Step 2: Define Specialized Agents

**Goal**  
Create domain-specific agents (Retrieval, Certification, Trip, Safety) with tool registrations.

**Scope**

**In scope:**

- Retrieval agent (vector search)
- Certification agent (cert queries)
- Trip agent (destination queries)
- Safety agent (response validation)
- Tool definitions (stubs)
- Agent registry

**Out of scope:**

- Real tool implementations (Step 3)
- Orchestration integration (Step 4)

**Backend Changes**

1.  **Tool stubs** (`src/lib/agent/tools/`):
    - `vector-search-tool.ts`:

      ```typescript
      import { Tool } from '../types'

      export const vectorSearchTool: Tool = {
        name: 'search_knowledge_base',
        description:
          'Search the diving knowledge base for relevant information',
        parameters: {
          query: { type: 'string', description: 'Search query' },
          top_k: {
            type: 'number',
            description: 'Number of results',
            default: 5,
          },
        },
        async execute(params: { query: string; top_k?: number }) {
          // Mock implementation for Step 2
          console.log('Mock vector search:', params)
          return { chunks: [] }
        },
      }
      ```

    - `session-lookup-tool.ts`:

      ```typescript
      export const sessionLookupTool: Tool = {
        name: 'get_conversation_history',
        description: 'Retrieve recent conversation history',
        parameters: {
          sessionId: { type: 'string' },
          last_n: { type: 'number', default: 10 },
        },
        async execute(params: { sessionId: string; last_n?: number }) {
          console.log('Mock session lookup:', params)
          return { history: [] }
        },
      }
      ```

    - `safety-check-tool.ts`:
      ```typescript
      export const safetyCheckTool: Tool = {
        name: 'validate_safety',
        description: 'Check response for required safety disclaimers',
        parameters: {
          response: { type: 'string' },
          query: { type: 'string' },
        },
        async execute(params: { response: string; query: string }) {
          console.log('Mock safety check:', params)
          return { safe: true, warnings: [] }
        },
      }
      ```

2.  **Agent implementations:**
    - `src/lib/agent/retrieval-agent.ts`:

      ```typescript
      import { BaseAgent } from './base-agent'
      import { vectorSearchTool } from './tools/vector-search-tool'
      import { getGenkit } from './config'

      export class RetrievalAgent extends BaseAgent {
        constructor() {
          super('retrieval', 'Retrieval specialist for knowledge base search', [
            vectorSearchTool,
          ])
        }

        async generate(input: AgentInput): Promise<AgentOutput> {
          const genkit = getGenkit()
          if (!genkit) throw new Error('ADK not initialized')

          // ADK agent call with tool
          const prompt = `Find relevant information for: ${input.messages[input.messages.length - 1].content}`
          const result = await genkit.generate({
            model: process.env.ADK_RETRIEVAL_MODEL || 'gemini-1.5-flash',
            prompt,
            tools: this.tools,
          })

          return {
            content: result.text,
            toolCalls: result.toolCalls,
            metadata: { tokensUsed: result.usage?.totalTokens },
          }
        }
      }
      ```

    - `src/lib/agent/certification-agent.ts`:

      ````typescript
      import { BaseAgent } from './base-agent';
      import { vectorSearchTool, sessionLookupTool } from './tools';

           export class CertificationAgent extends BaseAgent {
             constructor() {
               super(
                 'certification',
                 'Specialist in diving certification queries',
                 [vectorSearchTool, sessionLookupTool]
               );
             }

             async generate(input: AgentInput): Promise<AgentOutput> {
               const genkit = getGenkit();
               if (!genkit) throw new Error('ADK not initialized');

               const systemPrompt = `You are a diving certification expert.

      Focus on PADI/SSI equivalency, prerequisites, course duration, and safety requirements.
      Include disclaimers for medical/depth topics. Use tools to retrieve context.`;

               const result = await genkit.generate({
                 model: process.env.ADK_SPECIALIST_MODEL || 'gemini-2.0-flash',
                 prompt: systemPrompt + '\n\n' + input.messages.map(m => `${m.role}: ${m.content}`).join('\n'),
                 tools: this.tools,
               });

               return {
                 content: result.text,
                 toolCalls: result.toolCalls,
                 metadata: { tokensUsed: result.usage?.totalTokens },
               };
             }
           }
           ```

      ````

    - `src/lib/agent/trip-agent.ts`:

      ````typescript
      export class TripAgent extends BaseAgent {
      constructor() {
      super(
      'trip',
      'Specialist in dive trip planning and destinations',
      [vectorSearchTool, sessionLookupTool]
      );
      }

             async generate(input: AgentInput): Promise<AgentOutput> {
               const systemPrompt = `You are a dive trip planning expert.

      Recommend sites based on certification level, experience, and preferences.
      Include safety considerations (currents, depth, conditions).`;

               // Similar to CertificationAgent implementation
               // ...
             }
           }
           ```

      ````

    - `src/lib/agent/safety-agent.ts`:

      ```typescript
      export class SafetyAgent extends BaseAgent {
        constructor() {
          super(
            'safety',
            'Validates responses for safety disclaimers',
            [safetyCheckTool]
          );
        }

        async generate(input: AgentInput): Promise<AgentOutput> {
          // Lightweight validation agent
          const systemPrompt = `Check if the response includes appropriate disclaimers for:
      ```

- Medical topics: "Consult dive medical professional"
- Depth limits: State certification max depth
- Legal topics: "Not legal advice"`;
  // ...
  }
  }

  ```

  ```

3. **Agent registry** (`src/lib/agent/agent-registry.ts`):

   ```typescript
   import { RetrievalAgent } from './retrieval-agent'
   import { CertificationAgent } from './certification-agent'
   import { TripAgent } from './trip-agent'
   import { SafetyAgent } from './safety-agent'

   const agents = {
     retrieval: new RetrievalAgent(),
     certification: new CertificationAgent(),
     trip: new TripAgent(),
     safety: new SafetyAgent(),
   }

   export function getAgent(name: string) {
     return agents[name]
   }

   export { agents }
   ```

**Frontend Changes:** None

**Data Changes:** None

**Verification:**

- All agents instantiate without errors
- Mock tool calls logged correctly
- `pnpm typecheck && pnpm build` succeeds
- Unit tests: instantiate each agent, call `.generate()` with mock input

**Rollback:** Delete agent files, keep `src/lib/agent/config.ts`

---

### Step 3: Implement Tool Integration

**Goal**  
Wire real implementations for vector search, session lookup, and safety validation tools.

**Scope**

**In scope:**

- Connect vector-search-tool to PR2 (if ready) or keep mock
- Implement session-lookup-tool using session service
- Implement safety-check-tool with rule-based validation

**Out of scope:**

- Orchestration changes (Step 4)
- Agent instruction tuning (iterative post-launch)

**Backend Changes**

1. **Vector search tool** (`src/lib/agent/tools/vector-search-tool.ts`):

   ```typescript
   import { retrieveContext } from '../../../lib/rag/retrieval'

   export const vectorSearchTool: Tool = {
     // ... (same interface)
     async execute(params: { query: string; top_k?: number }) {
       try {
         if (process.env.ENABLE_RAG !== 'true') {
           console.log('RAG disabled, returning empty chunks')
           return { chunks: [] }
         }

         const chunks = await retrieveContext(params.query, params.top_k || 5)
         return {
           chunks: chunks.map((c) => ({
             text: c.content,
             metadata: { source: c.metadata?.source, similarity: c.similarity },
           })),
         }
       } catch (error) {
         console.error('Vector search failed:', error)
         return { chunks: [], error: 'Search unavailable' }
       }
     },
   }
   ```

2. **Session lookup tool** (`src/lib/agent/tools/session-lookup-tool.ts`):

   ```typescript
   import { getSession } from '../../../lib/session/session-service'

   export const sessionLookupTool: Tool = {
     // ... (same interface)
     async execute(params: { sessionId: string; last_n?: number }) {
       try {
         const session = await getSession(params.sessionId)
         if (!session) {
           return { history: [] }
         }

         const lastN = params.last_n || 10
         const history = session.conversationHistory.slice(-lastN)

         return {
           history: history.map((m) => ({
             role: m.role,
             content: m.content,
             timestamp: m.timestamp,
           })),
         }
       } catch (error) {
         console.error('Session lookup failed:', error)
         return { history: [], error: 'Session unavailable' }
       }
     },
   }
   ```

3. **Safety check tool** (`src/lib/agent/tools/safety-check-tool.ts`):

   ```typescript
   export const safetyCheckTool: Tool = {
     // ... (same interface)
     async execute(params: { response: string; query: string }) {
       const warnings: string[] = []
       const response = params.response.toLowerCase()
       const query = params.query.toLowerCase()

       // Medical terms check
       const medicalTerms = [
         'medical',
         'doctor',
         'prescription',
         'diagnosis',
         'health condition',
       ]
       if (
         medicalTerms.some(
           (term) => response.includes(term) || query.includes(term)
         )
       ) {
         if (
           !response.includes('consult') &&
           !response.includes('medical professional')
         ) {
           warnings.push('Add medical disclaimer')
         }
       }

       // Depth limits check
       const depthMention = /(\d+)\s*(m|meter|metre|ft|feet)/i.exec(response)
       if (depthMention) {
         const depth = parseInt(depthMention[1])
         if (
           depth > 18 &&
           !response.includes('certification') &&
           !response.includes('advanced')
         ) {
           warnings.push('Mention certification requirements for depth')
         }
       }

       // Legal terms check
       const legalTerms = ['lawsuit', 'liability', 'insurance', 'legal']
       if (
         legalTerms.some(
           (term) => response.includes(term) || query.includes(term)
         )
       ) {
         if (!response.includes('not legal advice')) {
           warnings.push('Add legal disclaimer')
         }
       }

       return {
         safe: warnings.length === 0,
         warnings,
         suggestions: warnings.map((w) => {
           if (w.includes('medical'))
             return 'Consult a dive medical professional (DAN) for health-related concerns.'
           if (w.includes('legal'))
             return 'This is not legal advice. Consult appropriate professionals.'
           if (w.includes('certification'))
             return 'Ensure dive plan matches certification level and experience.'
           return ''
         }),
       }
     },
   }
   ```

**Frontend Changes:** None

**Data Changes:** None

**Verification:**

- Unit tests for each tool with real implementations
- Integration test: create session, call session-lookup-tool, verify history
- Integration test: call vector-search-tool (if PR2 ready), verify chunks
- Integration test: call safety-check-tool with unsafe response, verify warnings
- Manual: Set `.env.local`, call tools directly, inspect results

**Rollback:** Restore mock implementations

---

### Step 4: Multi-Agent Orchestration

**Goal**  
Upgrade `chat-orchestrator.ts` to coordinate multiple agents using ADK patterns.

**Scope**

**In scope:**

- Replace linear orchestration with multi-agent graph
- Implement query routing (certification vs trip vs general)
- Coordinate: routing → retrieval → specialist → safety
- Preserve API contract

**Out of scope:**

- API route changes (Step 5)
- Removing old providers (Step 5)

**Backend Changes**

1. **Orchestration types** (`src/lib/orchestration/types.ts`):

   ```typescript
   // Add agent-specific types
   export interface AgentGraphResult {
     response: string
     agentsUsed: string[]
     toolCalls: Array<{ agent: string; tool: string; duration: number }>
     metadata: {
       totalDuration: number
       tokensUsed: number
       queryType: string
     }
   }
   ```

2. **Orchestrator** (`src/lib/orchestration/chat-orchestrator.ts`):

   ```typescript
   import { getAgent } from '../agent/agent-registry'
   import { getSession, createSession, updateSessionHistory } from '../session'

   // Query routing logic
   function detectQueryType(
     message: string,
     history: any[]
   ): 'certification' | 'trip' | 'general' {
     const m = message.toLowerCase()

     // Certification keywords
     if (
       m.match(
         /certif|padi|ssi|open water|advanced|rescue|divemaster|course|training/
       )
     ) {
       return 'certification'
     }

     // Trip keywords
     if (
       m.match(
         /trip|destination|where to dive|dive site|travel|vacation|recommend|visit/
       )
     ) {
       return 'trip'
     }

     // Check history for context
     const recentMessages = history
       .slice(-4)
       .map((h) => h.content.toLowerCase())
       .join(' ')
     if (
       recentMessages.includes('certif') ||
       recentMessages.includes('course')
     ) {
       return 'certification'
     }
     if (
       recentMessages.includes('trip') ||
       recentMessages.includes('destination')
     ) {
       return 'trip'
     }

     return 'general'
   }

   export async function orchestrateChat(
     req: ChatRequest
   ): Promise<ChatResponse> {
     const startTime = Date.now()
     const agentsUsed: string[] = []
     const toolCalls: any[] = []

     // Validation (from PR3)
     if (!req?.message || req.message.length > MAX_MESSAGE_LENGTH) {
       throw new Error('Invalid message')
     }

     // Session management (from PR3)
     let sessionId = req.sessionId
     let session = sessionId ? await getSession(sessionId) : null
     if (!session) {
       session = await createSession()
       sessionId = session.id
     }

     // Build message context
     const messages = [
       ...session.conversationHistory.map((m) => ({
         role: m.role,
         content: m.content,
       })),
       { role: 'user', content: req.message },
     ]

     // Step 1: Query routing
     const queryType = detectQueryType(req.message, session.conversationHistory)
     console.log('Query routed to:', queryType)

     // Step 2: Retrieval (parallel with routing)
     const retrievalAgent = getAgent('retrieval')
     let context = ''
     try {
       const retrievalResult = await Promise.race([
         retrievalAgent.generate({ messages, sessionId }),
         new Promise((_, reject) =>
           setTimeout(() => reject(new Error('Retrieval timeout')), 2000)
         ),
       ])

       if (retrievalResult && retrievalResult.toolCalls) {
         const searchResults = retrievalResult.toolCalls.find(
           (tc) => tc.tool === 'search_knowledge_base'
         )
         if (searchResults?.result?.chunks) {
           context = searchResults.result.chunks.map((c) => c.text).join('\n\n')
         }
       }
       agentsUsed.push('retrieval')
     } catch (error) {
       console.warn('Retrieval failed, proceeding without context:', error)
     }

     // Step 3: Specialist response
     const specialistName =
       queryType === 'certification'
         ? 'certification'
         : queryType === 'trip'
           ? 'trip'
           : 'certification' // default to cert
     const specialist = getAgent(specialistName)

     let response: string
     try {
       const specialistResult = await Promise.race([
         specialist.generate({ messages, context, sessionId }),
         new Promise((_, reject) =>
           setTimeout(() => reject(new Error('Specialist timeout')), 5000)
         ),
       ])

       response = specialistResult.content
       agentsUsed.push(specialistName)

       if (specialistResult.toolCalls) {
         toolCalls.push(
           ...specialistResult.toolCalls.map((tc) => ({
             agent: specialistName,
             tool: tc.tool,
             duration: 0, // TODO: track
           }))
         )
       }
     } catch (error) {
       console.error('Specialist failed:', error)
       // Fallback: simple response
       response =
         "I'm having trouble processing that request. Please try rephrasing or ask something simpler."
     }

     // Step 4: Safety validation
     const safetyAgent = getAgent('safety')
     try {
       const safetyResult = await safetyAgent.generate({
         messages: [
           { role: 'user', content: req.message },
           { role: 'assistant', content: response },
         ],
       })

       if (safetyResult.toolCalls) {
         const safetyCheck = safetyResult.toolCalls.find(
           (tc) => tc.tool === 'validate_safety'
         )
         if (safetyCheck?.result?.warnings?.length > 0) {
           // Append disclaimers
           const suggestions = safetyCheck.result.suggestions || []
           if (suggestions.length > 0) {
             response += '\n\n' + suggestions.join(' ')
           }
         }
       }
       agentsUsed.push('safety')
     } catch (error) {
       console.warn('Safety validation failed:', error)
     }

     // Update session history
     await updateSessionHistory(sessionId, {
       userMessage: req.message,
       assistantMessage: response,
     })

     const totalDuration = Date.now() - startTime

     return {
       sessionId,
       response,
       metadata: {
         agentsUsed,
         toolCalls,
         queryType,
         totalDuration,
         contextChunks: context ? context.split('\n\n').length : 0,
       },
     }
   }
   ```

**Frontend Changes:** None

**Data Changes:** None

**Verification:**

- Unit tests: Query routing with sample messages
- Integration tests: Full orchestration flow with mocked agents
- Manual tests:
  - Send "What is Open Water certification?" → verify cert agent used
  - Send "Where should I dive in Tioman?" → verify trip agent used
  - Send query with medical terms → verify safety disclaimers appended
- Performance: Verify total duration <10s

**Rollback:** Restore PR3 orchestrator (rename current to `.adk.ts`, restore `.legacy.ts`)

---

### Step 5: API Contract Preservation & Cleanup

**Goal**  
Ensure `/api/chat` behavior unchanged, remove deprecated model-provider code, add telemetry.

**Scope**

**In scope:**

- Verify API contract unchanged
- Update error mapping for ADK errors
- Remove `src/lib/model-provider/` module
- Add ADK telemetry
- Update `.env.example`

**Out of scope:**

- Further agent tuning (iterative)

**Backend Changes**

1. **API route** (`src/app/api/chat/route.ts`):

   ```typescript
   // Update error handling
   import { orchestrateChat } from '../../../lib/orchestration/chat-orchestrator'

   export async function POST(request: Request) {
     try {
       const json = await request.json()
       const parsed = bodySchema.parse(json)

       const result = await orchestrateChat(parsed)

       // Log ADK telemetry
       console.log('ADK telemetry:', {
         agentsUsed: result.metadata?.agentsUsed,
         duration: result.metadata?.totalDuration,
         queryType: result.metadata?.queryType,
       })

       return NextResponse.json(result, { status: 200 })
     } catch (err: any) {
       // ADK-specific error mapping
       if (err?.message?.includes('ADK not initialized')) {
         return NextResponse.json(
           { error: 'Service unavailable', code: 'ADK_UNAVAILABLE' },
           { status: 503 }
         )
       }

       if (err?.message?.includes('timeout')) {
         return NextResponse.json(
           { error: 'Request timeout', code: 'TIMEOUT' },
           { status: 503 }
         )
       }

       // Existing error handling from PR3
       if (err?.code === 'VALIDATION' || err?.name === 'ZodError') {
         return NextResponse.json(
           { error: 'Invalid input', code: 'INVALID_INPUT' },
           { status: 400 }
         )
       }

       console.error('Chat error:', err)
       return NextResponse.json(
         { error: 'Internal server error', code: 'INTERNAL_ERROR' },
         { status: 500 }
       )
     }
   }
   ```

2. **Delete old provider code:**

   ```bash
   rm -rf src/lib/model-provider/
   ```

3. **Update .env.example:**
   - Remove: `LLM_PROVIDER`, `GROQ_API_KEY`, `GROQ_MODEL`
   - Add: ADK variables (from Step 1)

4. **Optional: ADK tracing** (`src/lib/agent/config.ts`):
   ```typescript
   // Enable Cloud Trace if configured
   if (process.env.GOOGLE_CLOUD_TRACE_ENABLED === 'true') {
     genkitInstance = genkit({
       plugins: [
         googleAI(),
         cloudTrace(), // Optional plugin
       ],
       telemetry: {
         instrumentation: 'googleCloudTrace',
       },
     })
   }
   ```

**Frontend Changes:** None

**Data Changes:** None

**Verification:**

- All PR3 curl tests pass with identical response format
- Error scenarios return correct status codes
- `pnpm typecheck && pnpm build` succeeds
- No imports of deleted model-provider code
- Telemetry logs appear correctly
- Compare responses before/after (quality spot check)

**Rollback:** Full git revert to PR3 baseline

---

### Step 6: RAG Integration (Conditional)

**Goal**  
If PR2 complete, wire real vector search to retrieval agent. Otherwise, document mock usage.

**Scope**

**In scope:**

- Connect vector-search-tool to PR2's `retrieveContext`
- Test with real vector DB
- Tune retrieval parameters

**Out of scope:**

- PR2 implementation (assumed ready or deferred)

**Backend Changes**

1. **Enable RAG** (`.env.local`):

   ```bash
   ENABLE_RAG=true
   ```

2. **Verify integration** (`src/lib/agent/tools/vector-search-tool.ts`):
   - Already implemented in Step 3
   - Confirm `retrieveContext` from PR2 works
   - If PR2 incomplete: keep `ENABLE_RAG=false`, add TODO comment

3. **Tune retrieval:**
   - Experiment with `top_k` (default 5, try 3-10)
   - Add similarity threshold if PR2 supports
   - Log retrieval quality metrics

**Frontend Changes:** None

**Data Changes:** None (uses PR2 schema)

**Verification:**

- Query "Open Water certification" → verify relevant chunks retrieved
- Query "Tioman dive sites" → verify destination content retrieved
- Compare response quality with/without RAG
- Check retrieval latency (<2s)

**Rollback:** Set `ENABLE_RAG=false`

---

## 5. Cross-Cutting Concerns

### Error Handling

- **ADK errors**: Map to HTTP status codes (503 for unavailable, 400 for validation)
- **Tool failures**: Log warning, return error to agent, agent decides handling
- **Agent timeouts**: 5s for specialist, 2s for retrieval, 1s for safety
- **Graceful degradation**: Always return response (degraded better than failed)

### Logging

- **Structured logging** (pino from PR3):

  ```typescript
  logger.info({
    agent: 'certification',
    duration: 1234,
    toolCalls: ['search_knowledge_base'],
    tokensUsed: 450,
  })
  ```

- **Privacy**: Log message length/type, not full content
- **ADK tracing**: Optional Cloud Trace integration for debugging

### Auth & Security

- **No auth changes**: Guest sessions (PR1/PR3)
- **GCP credentials**: Service account JSON protected (env var, not in repo)
- **Tool access**: Tools only access user's session data and public knowledge base

### Performance

- **Latency budget**: <10s total (Next.js timeout)
  - Retrieval: <2s
  - Specialist: <5s
  - Safety: <1s
- **Parallel execution**: Retrieval + routing in parallel
- **Model selection**: Flash for cheap tasks, Pro for reasoning
- **Monitoring**: Track P50/P95/P99 for each agent

---

## 6. Risks, Trade-offs, and Rollback

### Major Risks

1. **ADK SDK stability** (beta software)
   - Mitigation: Pin version, monitor releases, maintain abstraction

2. **GCP cost increase** (more LLM calls)
   - Mitigation: Use Flash models, cache, monitor usage, budget alerts

3. **Latency increase** (multi-agent overhead)
   - Mitigation: Parallel execution, timeouts, optimize prompts

4. **Complex debugging** (multi-agent coordination)
   - Mitigation: Structured logging, Cloud Trace, replay failed requests

5. **PR2 RAG dependency**
   - Mitigation: Feature flag `ENABLE_RAG`, graceful fallback to mock

### Trade-offs

1. **Complexity vs Specialization**: Accept orchestration complexity for better responses
2. **Provider Lock-in**: ADK ties to Google ecosystem for better integration
3. **Incremental vs Big Bang**: 6 steps with rollback points for lower risk
4. **Tool Granularity**: Start with 3 core tools, defer advanced tools

### Rollback Strategy

- **Steps 1-4**: Old provider code functional, use `ENABLE_ADK=false` flag
- **Step 5+**: Full git revert to PR3, restore from history
- **Database**: No schema changes, full rollback safe
- **API**: Contract preserved, rollback transparent to frontend

### Open Questions

1. **ADK serverless compatibility**: Test on Vercel early
2. **Agent memory**: Beyond session history? (Future enhancement)
3. **SEA-LION integration**: How to add language routing? (V2)
4. **Lead capture signals**: Can agent metadata improve PR4?
5. **Evaluation metrics**: How to measure multi-agent quality?

---

## 7. Success Criteria

PR3.1 is successful when:

- [x] All 6 steps complete with passing tests
- [x] `/api/chat` contract unchanged (PR3 tests pass)
- [x] Multi-agent coordination works (retrieval → specialist → safety)
- [x] Response quality maintained or improved vs PR3 baseline
- [x] Latency <10s P95
- [x] No regressions in error handling
- [x] GCP integration functional (service account, Vertex AI)
- [x] Documentation updated (env vars, architecture)
- [x] Code review self-checklist complete

**Note:** `src/lib/model-provider/` intentionally retained (not deleted per original Step 5) to provide fallback capability during Python migration (PR3.2). This enables safer rollback strategy and gradual transition.

---

## 8. Next Steps (Post-PR3.1)

After PR3.1 merges:

1. **Monitor & tune**:
   - Track agent performance metrics
   - Iterate on agent instructions based on response quality
   - Optimize latency hotspots

2. **PR4: Lead Capture**:
   - Leverage agent metadata (detected query type, cert level mentions)
   - Use conversation context for lead enrichment

3. **PR5: Chat Interface**:
   - API contract unchanged, transparent integration
   - Display agent activity (optional UX enhancement)

4. **Post-launch enhancements**:
   - Add more agents (FAQ, booking, community)
   - Implement conversation summarization for long sessions
   - Add agent evaluation framework
   - SEA-LION integration for multilingual (V2)

---

**End of PR3.1 Plan**
