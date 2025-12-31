/**
 * POST /api/chat
 * Main chat endpoint for user-bot conversations
 */

import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import pino from 'pino';
import { orchestrateChat } from '@/lib/orchestration';

const logger = pino({ name: 'api-chat' });

// Request validation schema
const chatRequestSchema = z.object({
  sessionId: z.string().uuid().optional(),
  message: z.string().min(1).max(2000),
});

/**
 * POST /api/chat
 * Accept user message and return assistant response
 *
 * Request body:
 * {
 *   sessionId?: string,  // Optional UUID, creates new session if not provided
 *   message: string      // User message (1-2000 chars)
 * }
 *
 * Response:
 * {
 *   sessionId: string,
 *   response: string,
 *   metadata?: {
 *     tokensUsed?: number,
 *     contextChunks?: number,
 *     model?: string,
 *     promptMode?: string
 *   }
 * }
 *
 * Error responses:
 * - 400: Invalid request (validation error)
 * - 500: Server error (database, general)
 * - 503: Service unavailable (LLM API error)
 */
export async function POST(request: NextRequest) {
  const requestId = crypto.randomUUID();

  try {
    // Parse request body
    const body = await request.json();

    logger.info({
      requestId,
      sessionId: body.sessionId,
      msg: 'Received chat request',
    });

    // Validate request
    const validationResult = chatRequestSchema.safeParse(body);

    if (!validationResult.success) {
      logger.warn({
        requestId,
        errors: validationResult.error.errors,
        msg: 'Request validation failed',
      });

      return NextResponse.json(
        {
          error: 'Invalid request',
          code: 'VALIDATION_ERROR',
          details: validationResult.error.errors.map((e) => ({
            field: e.path.join('.'),
            message: e.message,
          })),
        },
        { status: 400 }
      );
    }

    const { sessionId, message } = validationResult.data;

    // Orchestrate chat
    const startTime = Date.now();
    const response = await orchestrateChat({
      sessionId,
      message,
    });
    const duration = Date.now() - startTime;

    logger.info({
      requestId,
      sessionId: response.sessionId,
      durationMs: duration,
      tokensUsed: response.metadata?.tokensUsed,
      msg: 'Chat request successful',
    });

    return NextResponse.json(response, { status: 200 });
  } catch (error) {
    logger.error({
      requestId,
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined,
      msg: 'Chat request failed',
    });

    // Determine error type and return appropriate response
    if (error instanceof Error) {
      const errorMessage = error.message.toLowerCase();

      // Validation errors (from orchestrator)
      if (
        errorMessage.includes('message') &&
        (errorMessage.includes('empty') || errorMessage.includes('length'))
      ) {
        return NextResponse.json(
          {
            error: error.message,
            code: 'VALIDATION_ERROR',
          },
          { status: 400 }
        );
      }

      // LLM API errors
      if (errorMessage.includes('api error') || errorMessage.includes('api key')) {
        return NextResponse.json(
          {
            error: 'AI service temporarily unavailable. Please try again in a moment.',
            code: 'LLM_SERVICE_UNAVAILABLE',
            details: process.env.NODE_ENV === 'development' ? error.message : undefined,
          },
          { status: 503 }
        );
      }

      // Database errors
      if (errorMessage.includes('database') || errorMessage.includes('session')) {
        return NextResponse.json(
          {
            error: 'Unable to process request. Please try again.',
            code: 'DATABASE_ERROR',
            details: process.env.NODE_ENV === 'development' ? error.message : undefined,
          },
          { status: 500 }
        );
      }
    }

    // Generic server error
    return NextResponse.json(
      {
        error: 'An unexpected error occurred. Please try again.',
        code: 'INTERNAL_SERVER_ERROR',
        details: process.env.NODE_ENV === 'development' && error instanceof Error
          ? error.message
          : undefined,
      },
      { status: 500 }
    );
  }
}

/**
 * OPTIONS handler for CORS preflight
 */
export async function OPTIONS() {
  return NextResponse.json(
    {},
    {
      status: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    }
  );
}
