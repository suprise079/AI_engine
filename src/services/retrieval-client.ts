/**
 * Retrieval Client - Calls Spring Boot backend to retrieve relevant context chunks
 */

import logger from '../config/logger';
import { config } from '../config/config';

export interface ContextQueryRequest {
  tenantId: number;
  projectId?: number;
  appId?: number;
  env?: string;
  sessionId?: number;
  pageUrl?: string;
  queryText: string;
  intent: 'SUGGEST_NEXT_TESTS' | 'CREATE_CANDIDATE_TEST_CASES' | 'BUG_TRIAGE' | 'GENERATE_AUTOMATION_SKELETON';
  topK?: number;
  minScore?: number;
}

export interface ContextChunk {
  chunkId: number;
  documentId: number;
  chunkType: string;
  chunkText: string;
  score: number;
  sourceRef: string;
  metadata: Record<string, any>;
  tokenCount: number;
}

export interface ContextQueryResponse {
  chunks: ContextChunk[];
  retrievalLatencyMs: number;
  cacheHit: boolean;
  totalChunksFound: number;
}

export class RetrievalClient {
  private backendUrl: string;

  constructor() {
    this.backendUrl = config.BACKEND_URL;
  }

  /**
   * Query context store for relevant chunks
   */
  async query(request: ContextQueryRequest): Promise<ContextQueryResponse> {
    try {
      const url = `${this.backendUrl}/api/context/query`;
      
      logger.debug(`Querying context store: intent=${request.intent}, topK=${request.topK || 10}`);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tenantId: request.tenantId,
          projectId: request.projectId,
          appId: request.appId,
          env: request.env,
          sessionId: request.sessionId,
          pageUrl: request.pageUrl,
          queryText: request.queryText,
          intent: request.intent,
          topK: request.topK || 10,
          minScore: request.minScore || 0.5,
        }),
      });

      if (!response.ok) {
        throw new Error(`Context store query failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json() as ContextQueryResponse;
      logger.debug(`Retrieved ${data.chunks.length} chunks (cache hit: ${data.cacheHit})`);
      
      return data;
    } catch (error: any) {
      logger.error(`Error querying context store: ${error.message}`, { error });
      // Return empty response on error (graceful degradation)
      return {
        chunks: [],
        retrievalLatencyMs: 0,
        cacheHit: false,
        totalChunksFound: 0,
      };
    }
  }
}

export const retrievalClient = new RetrievalClient();
