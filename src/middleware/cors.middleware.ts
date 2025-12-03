/**
 * CORS middleware configuration
 */

import cors from 'cors';
import { config } from '../config/config';

export const corsMiddleware = cors({
  origin: config.CORS_ORIGINS,
  credentials: config.CORS_CREDENTIALS,
  methods: config.CORS_METHODS,
  allowedHeaders: config.CORS_HEADERS
});

