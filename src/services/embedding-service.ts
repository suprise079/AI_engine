/**
* Embedding Service - Generates vector embeddings for text using local models
* Uses @xenova/transformers for local inference (no API calls needed)
*/

import { pipeline, type FeatureExtractionPipeline } from '@xenova/transformers';
import logger from '../config/logger';
import { config } from '../config/config';

export class EmbeddingService {
    private static instance: EmbeddingService;
    private modelName: string;
    private pipelinePromise: Promise<FeatureExtractionPipeline> | null = null;
    private pipeline: FeatureExtractionPipeline | null = null;

    private constructor() {
        // Default model: all-MiniLM-L6-v2 (384 dimensions, fast, good quality)
        this.modelName = config.HYDRA_EMBEDDING_MODEL
    }

    public static getInstance(): EmbeddingService {
        if (!EmbeddingService.instance) {
            EmbeddingService.instance = new EmbeddingService();
        }
        return EmbeddingService.instance;
    }

    /**
     * Initialize the embedding pipeline (lazy loading)
     */
    private async initializePipeline(): Promise<FeatureExtractionPipeline> {
        if (this.pipeline) {
            return this.pipeline;
        }

        if (!this.pipelinePromise) {
            logger.info(`Loading embedding model: ${this.modelName}`);
            this.pipelinePromise = pipeline('feature-extraction', this.modelName, {
                quantized: true, // Use quantized model for faster loading
            });
        }

        this.pipeline = await this.pipelinePromise;
        logger.info(`Embedding model loaded successfully`);
        return this.pipeline;
    }

    /**
     * Generate embedding for a single text
     * @param text The text to embed
     * @returns Promise resolving to embedding vector (float array)
     */
    public async embed(text: string): Promise<number[]> {
        if (!text || text.trim().length === 0) {
            throw new Error('Text cannot be empty');
        }

        try {
            const extractor = await this.initializePipeline();
            const result = await extractor(text, { pooling: 'mean', normalize: true });
            
            // Convert tensor to array
            const embedding = Array.from(result.data);
            logger.debug(`Generated embedding of dimension ${embedding.length} for text (length: ${text.length})`);
            
            return embedding as number[];
        } catch (error: any) {
            logger.error(`Error generating embedding: ${error.message}`, { error });
            throw new Error(`Failed to generate embedding: ${error.message}`);
        }
    }

    /**
     * Generate embeddings for multiple texts (batch processing)
     * @param texts Array of texts to embed
     * @returns Promise resolving to array of embedding vectors
     */
    public async embedBatch(texts: string[]): Promise<number[][]> {
        if (!texts || texts.length === 0) {
            return [];
        }

        try {
            const extractor = await this.initializePipeline();
            const results = await Promise.all(
                texts.map(text => extractor(text, { pooling: 'mean', normalize: true }))
            );

            const embeddings = results.map((result: any) => Array.from(result.data) as number[]);
            logger.debug(`Generated ${embeddings.length} embeddings`);
            
            return embeddings;
        } catch (error: any) {
            logger.error(`Error generating batch embeddings: ${error.message}`, { error });
            throw new Error(`Failed to generate batch embeddings: ${error.message}`);
        }
    }

    /**
     * Get embedding dimension for the current model
     */
    public async getEmbeddingDimension(): Promise<number> {
        const testEmbedding = await this.embed('test');
        return testEmbedding.length;
    }

    /**
     * Convert embedding array to PGvector string format: "[0.1,0.2,...]"
     */
    public static toPGvectorString(embedding: number[]): string {
        return '[' + embedding.join(',') + ']';
    }

    /**
     * Convert PGvector string format to array
     */
    public static fromPGvectorString(pgvectorString: string): number[] {
        // Remove brackets and split by comma
        const cleaned = pgvectorString.replace(/[\[\]]/g, '');
        return cleaned.split(',').map(s => parseFloat(s.trim()));
    }
}

// Export singleton instance
export const embeddingService = EmbeddingService.getInstance();
