import logger from '../../config/logger';
import { Action } from '../../types';
import { componentRecognizer } from '../../services';
import { validateTimestamp } from '../../utils/timestamp-validator';

export class PagesService {
  /**
   * Detect pages and components from an action sequence.
   */
  detectPages(data: any): { sessionId: any; pages: any[] } {
    logger.info(`Received page detection request for session ${data.sessionId}`);

    // Validate and fix timestamps
    const fixedActions = data.actions.map((action: Action) => validateTimestamp(action));

    // Use ComponentRecognizer to identify pages and components
    const pages = componentRecognizer.identifyPagesAndComponents(fixedActions);
    logger.info(`Identified ${pages.length} pages with components`);

    return {
      sessionId: data.sessionId,
      pages,
    };
  }
}

