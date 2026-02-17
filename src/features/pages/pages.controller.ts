import { Request, Response } from 'express';
import logger from '../../config/logger';
import { PagesService } from './pages.service';

const pagesService = new PagesService();

/**
 * Detect pages endpoint handler (feature-based).
 */
export const detectPages = (req: Request, res: Response) => {
  try {
    const result = pagesService.detectPages(req.body);
    return res.json(result);
  } catch (error: any) {
    logger.error(`Error detecting pages: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while detecting pages',
    });
  }
};

