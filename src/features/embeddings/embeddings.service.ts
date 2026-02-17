import logger from '../../config/logger';
import { embeddingService } from '../../services/embedding-service';

export class EmbeddingsService {
  /**
   * Generate embedding for a single text.
   */
  async generate(text: string): Promise<{ embedding: number[]; dimension: number }> {
    logger.info(`Generating embedding for text (length: ${text.length})`);

    const embedding = await embeddingService.embed(text);

    return {
      embedding,
      dimension: embedding.length,
    };
  }

  /**
   * Generate embeddings for multiple texts.
   */
  async generateBatch(texts: string[]): Promise<{ embeddings: number[][]; count: number; dimension: number }> {
    logger.info(`Generating batch embeddings for ${texts.length} texts`);

    const embeddings = await embeddingService.embedBatch(texts);

    return {
      embeddings,
      count: embeddings.length,
      dimension: embeddings.length > 0 ? embeddings[0].length : 0,
    };
  }
}

