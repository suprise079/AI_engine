import { patternRecognizer, suggestionGenerator, componentRecognizer, testCaseGenerator, testScriptGenerator } from '../../services';
import { config } from '../../config/config';

export class HealthService {
  getHealthStatus() {
    const componentsStatus = {
      pattern_recognizer: patternRecognizer !== null, // Intentionally null - removed as per requirements
      suggestion_generator: suggestionGenerator !== null,
      component_recognizer: componentRecognizer !== null,
      test_case_generator: testCaseGenerator !== null,
      test_script_generator: testScriptGenerator !== null,
    };

    // Exclude pattern_recognizer from health check since it's intentionally removed
    const activeComponents = {
      suggestion_generator: componentsStatus.suggestion_generator,
      component_recognizer: componentsStatus.component_recognizer,
      test_case_generator: componentsStatus.test_case_generator,
      test_script_generator: componentsStatus.test_script_generator,
    };
    const allHealthy = Object.values(activeComponents).every((v) => v !== null);

    return {
      httpStatus: allHealthy ? 200 : 503,
      body: {
        status: allHealthy ? 'healthy' : 'degraded',
        version: config.APP_VERSION,
        components: componentsStatus,
        timestamp: new Date().toISOString(),
      },
    };
  }
}

