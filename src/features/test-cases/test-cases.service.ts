import logger from '../../config/logger';
import { testCaseGenerator } from '../../services';

export class TestCasesService {
  /**
   * Generate test cases from pages and (optionally) actions.
   */
  generateTestCases(data: any): { sessionId: any; testCases: any[] } {
    logger.info(`Received test case generation request for session ${data.sessionId}`);

    const actions = data.actions || [];
    const pages = data.pages || [];
    const testCases = testCaseGenerator.generateTestCases(pages, actions);

    logger.info(`Generated ${testCases.length} test cases`);

    return {
      sessionId: data.sessionId,
      testCases,
    };
  }
}

