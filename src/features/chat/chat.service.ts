import logger from '../../config/logger';
import { config } from '../../config/config';
import { llmRouter } from '../../services';
import { composePrompt } from '../../services/prompt-composer';

interface ChatRequestBody {
  prompt?: string;
  message?: string;
  content?: string;
  requestId?: string;
  sessionId?: string;
  tenantId?: string;
  projectId?: string;
  appId?: string;
  env?: string;
  pageUrl?: string;
  actions?: any[];
}

export class ChatService {
  /**
   * Handle non-streaming chat, including legacy and RAG-aware paths.
   * This encapsulates the core business logic used by the controller.
   */
  async handleChat(body: ChatRequestBody): Promise<{ response: string }> {
    const {
      prompt,
      message,
      content,
      sessionId,
      tenantId,
      projectId,
      appId,
      env,
      pageUrl,
      actions,
    } = body;

    const userText = message ?? content ?? prompt; // message (RAG), content (backend DTO), or prompt (legacy)

    // Legacy path: plain prompt, no RAG
    if (!tenantId || (!message && !content && prompt)) {
      const legacyPrompt = userText;
      logger.info(`Received legacy chat request with prompt (no RAG): ${legacyPrompt}`);

      const { text, provider, fallbackTriggered, durationMs } = await llmRouter.generateText(
        legacyPrompt ?? '',
        { requestId: body.requestId }
      );
      logger.info(`Chat response generated (${text.length} chars)`);
      logger.debug(`Chat response: ${text}`);

      const result: { response: string; meta?: { provider: string; fallbackTriggered: boolean; durationMs: number } } = {
        response: text.trim(),
      };
      if (config.DEBUG_LLM) {
        result.meta = { provider, fallbackTriggered: fallbackTriggered ?? false, durationMs };
      }
      return result;
    }

    // RAG-aware session chat path
    const userMessage: string = userText ?? '';
    logger.info(`Received session chat request for session ${sessionId} with RAG enabled`);

    // Build a minimal ActionSequence-like structure for live context (if actions provided)
    const actionSequence = {
      sessionId: sessionId ?? 'chat',
      actions: Array.isArray(actions) ? actions : [],
      tenantId,
      projectId,
      appId,
      env,
      pageUrl,
    };

    const composition = await composePrompt({
      sessionId: actionSequence.sessionId,
      tenantId: Number(tenantId) ?? 0,
      projectId: projectId != null ? Number(projectId) : undefined,
      appId: appId != null ? Number(appId) : undefined,
      env,
      pageUrl,
      intent: 'SUGGEST_NEXT_TESTS', // Use suggestions intent for retrieval heuristics
      actionSequence: actionSequence as unknown as import('../../types').ActionSequence,
      maxTokens: 1500,
    });

    const finalPrompt = `${composition.prompt}\n\n=== USER QUESTION ===\n${userMessage}`;

    logger.info(
      `Composed session chat prompt: ${composition.totalTokens} tokens, ${composition.chunksUsed} chunks`
    );

    const { text, provider, fallbackTriggered, durationMs } = await llmRouter.generateText(
      finalPrompt,
      { requestId: body.requestId }
    );

    logger.info(`Session chat response generated (${text.length} chars)`);

    const result: { response: string; meta?: { provider: string; fallbackTriggered: boolean; durationMs: number } } = {
      response: text.trim(),
    };
    if (config.DEBUG_LLM) {
      result.meta = { provider, fallbackTriggered: fallbackTriggered ?? false, durationMs };
    }
    return result;
  }

  /**
   * Whether streaming chat is enabled.
   */
  isStreamingEnabled(): boolean {
    return config.ENABLE_STREAMING_CHAT;
  }
}

