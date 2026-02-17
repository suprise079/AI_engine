import logger from '../../config/logger';
import { testScriptGenerator } from '../../services';

export class TestScriptService {
  /**
   * Generate an automation script from a test case.
   */
  generateScript(data: any): { script: string; language: string; framework: string } {
    logger.info('Received script generation request');

    const testCase = data.testCase;
    const framework = data.framework || 'selenium';
    const testData = data.testData || {};

    const script = testScriptGenerator.generateScript(testCase, testData, framework);
    logger.info(`Generated ${framework} script`);

    const language = framework === 'selenium' ? 'java' : 'javascript';

    return {
      script,
      language,
      framework,
    };
  }
}

