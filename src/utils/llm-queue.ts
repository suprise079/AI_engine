import logger from '../config/logger';
import { config } from '../config/config';

type Job<T> = {
  fn: () => Promise<T>;
  resolve: (value: T | PromiseLike<T>) => void;
  reject: (reason?: any) => void;
  enqueuedAt: number;
};

const CONCURRENCY_LIMIT = config.LLM_CONCURRENCY_LIMIT;
const QUEUE_TIMEOUT_MS = config.LLM_QUEUE_TIMEOUT_MS;

class LlmQueue {
  private activeCount = 0;
  private readonly queue: Job<unknown>[] = [];

  async enqueue<T>(fn: () => Promise<T>): Promise<T> {
    const enqueuedAt = Date.now();

    return new Promise<T>((resolve, reject) => {
      const job: Job<T> = {
        fn,
        resolve,
        reject,
        enqueuedAt
      };

      this.queue.push(job as Job<unknown>);
      logger.info(
        `LLM queue: job enqueued. queueLength=${this.queue.length}, active=${this.activeCount}, limit=${CONCURRENCY_LIMIT}`
      );
      this.processQueue();
    });
  }

  private processQueue() {
    if (this.activeCount >= CONCURRENCY_LIMIT) {
      return;
    }

    const now = Date.now();
    const next = this.queue.shift();
    if (!next) {
      return;
    }

    const waitTime = now - next.enqueuedAt;
    if (waitTime > QUEUE_TIMEOUT_MS) {
      logger.warn(
        `LLM queue: dropping job due to queue timeout. waitTime=${waitTime}ms, timeout=${QUEUE_TIMEOUT_MS}ms`
      );
      next.reject(
        Object.assign(new Error('LLM queue timeout exceeded'), {
          statusCode: 503
        })
      );
      // Try next job
      this.processQueue();
      return;
    }

    this.activeCount += 1;
    logger.info(
      `LLM queue: starting job. active=${this.activeCount}, remainingQueue=${this.queue.length}, waitTime=${waitTime}ms`
    );

    const jobStart = Date.now();
    next
      .fn()
      .then((result) => {
        const duration = Date.now() - jobStart;
        logger.info(`LLM queue: job completed in ${duration}ms`);
        next.resolve(result);
      })
      .catch((err) => {
        const duration = Date.now() - jobStart;
        logger.error(`LLM queue: job failed after ${duration}ms: ${err?.message || err}`);
        next.reject(err);
      })
      .finally(() => {
        this.activeCount -= 1;
        this.processQueue();
      });
  }
}

export const llmQueue = new LlmQueue();

