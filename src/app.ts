/**
 * Main Express application for AI Engine
 */

import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import { config } from './config/config';
import logger from './config/logger';
import { SuggestionGenerator } from './services/suggestion-generator';
import { ComponentRecognizer } from './services/component-recognizer';
import { TestCaseGenerator } from './services/test-case-generator';
import { TestScriptGenerator } from './services/test-script-generator';
import { OllamaService } from './services/ollama-service';
import { Action, FeedbackData } from './types';

const app = express();

// Middleware
app.use(cors({
  origin: config.CORS_ORIGINS,
  credentials: config.CORS_CREDENTIALS,
  methods: config.CORS_METHODS,
  allowedHeaders: config.CORS_HEADERS
}));

app.use(express.json({ limit: `${config.MAX_CONTENT_LENGTH}b` }));

// Request logging middleware
app.use((req: Request, _res: Response, next: NextFunction) => {
  logger.debug(`Request: ${req.method} ${req.path}`);
  if (req.is('application/json')) {
    logger.debug(`Request body size: ${JSON.stringify(req.body).length} bytes`);
  }
  next();
});

// Response logging middleware
app.use((req: Request, res: Response, next: NextFunction) => {
  const originalSend = res.send;
  res.send = function(body: any) {
    logger.debug(`Response: ${res.statusCode} for ${req.method} ${req.path}`);
    return originalSend.call(this, body);
  };
  next();
});

// Initialize services
const patternRecognizer = null; // Removed as per requirements
const suggestionGenerator = new SuggestionGenerator();
const componentRecognizer = new ComponentRecognizer();
const testCaseGenerator = new TestCaseGenerator();
const testScriptGenerator = new TestScriptGenerator();
const ollamaService = new OllamaService();

// Helper function to validate timestamps
function validateTimestamp(action: Action): Action {
  if (!action.actionTime) {
    action.actionTime = new Date().toISOString();
    return action;
  }

  const timestamp = action.actionTime;

  // Handle array-format timestamps like [2025, 3, 30, 18, 32, 55, 567000000]
  if (Array.isArray(timestamp) && timestamp.length >= 6) {
    try {
      const [year, month, day, hour, minute, second] = timestamp;
      const microsecond = timestamp.length > 6 ? Math.floor(timestamp[6] / 1000) : 0;
      const dt = new Date(year, month - 1, day, hour, minute, second, microsecond);
      action.actionTime = dt.toISOString();
      return action;
    } catch (e) {
      logger.warn(`Could not parse timestamp: ${timestamp}. Using current time.`);
      action.actionTime = new Date().toISOString();
      return action;
    }
  }

  // Check if it's a complete ISO format timestamp
  if (typeof timestamp === 'string') {
    if (timestamp.includes('T') && timestamp.length >= 19) {
      return action;
    }
    // If it's just a year or incomplete timestamp, replace it
    if (/^\d{4}$/.test(timestamp)) {
      logger.warn(`Fixing incomplete timestamp: ${timestamp}`);
      action.actionTime = new Date().toISOString();
      return action;
    }
  }

  // Try to parse the timestamp
  try {
    const parsed = new Date(timestamp as string);
    if (!isNaN(parsed.getTime())) {
      action.actionTime = parsed.toISOString();
      return action;
    }
  } catch (e) {
    // Ignore
  }

  logger.warn(`Could not parse timestamp: ${timestamp}. Using current time.`);
  action.actionTime = new Date().toISOString();
  return action;
}

// Error handlers
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  logger.error(`Unhandled exception: ${err.message}`, { error: err });
  res.status(500).json({
    error: 'Internal Server Error',
    message: 'An unexpected error occurred. Please try again later.'
  });
});

// Routes

// Health check
app.get('/health', (_req: Request, res: Response) => {
  try {
    const componentsStatus = {
      pattern_recognizer: patternRecognizer !== null,
      suggestion_generator: suggestionGenerator !== null,
      component_recognizer: componentRecognizer !== null,
      test_case_generator: testCaseGenerator !== null,
      test_script_generator: testScriptGenerator !== null
    };

    const allHealthy = Object.values(componentsStatus).every(v => v !== null);

    res.status(allHealthy ? 200 : 503).json({
      status: allHealthy ? 'healthy' : 'degraded',
      version: config.APP_VERSION,
      components: componentsStatus,
      timestamp: new Date().toISOString()
    });
  } catch (error: any) {
    logger.error(`Health check failed: ${error.message}`, { error });
    res.status(503).json({
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Analyze actions
app.post('/analyze', async (req: Request, res: Response) => {
  try {
    const data = req.body;
    logger.info(`Received analysis request for session ${data.sessionId} with ${data.actions?.length || 0} actions`);

    if (!data || !data.actions || !Array.isArray(data.actions) || data.actions.length === 0) {
      return res.status(400).json({ error: 'Invalid request. Actions data is required.' });
    }

    // Validate and fix timestamps
    const fixedActions = data.actions.map((action: Action) => validateTimestamp(action));

    // Generate suggestions using DeepSeek
    const suggestions = await suggestionGenerator.generateSuggestions({
      sessionId: data.sessionId,
      actions: fixedActions
    });

    logger.info(`Generated ${suggestions.length} suggestions`);

    return res.json({
      sessionId: data.sessionId,
      suggestions: suggestions.map(s => s.toDict())
    });
  } catch (error: any) {
    logger.error(`Error analyzing actions: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while analyzing actions'
    });
  }
});

// Process feedback
app.post('/feedback', (req: Request, res: Response) => {
  try {
    const data: FeedbackData = req.body;
    logger.info(`Received feedback for suggestion ${data.suggestionId}`);

    suggestionGenerator.processFeedback(
      data.suggestionId,
      data.status,
      data.feedback
    );

    return res.json({ status: 'success' });
  } catch (error: any) {
    logger.error(`Error processing feedback: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while processing feedback'
    });
  }
});

// Detect pages
app.post('/detect-pages', (req: Request, res: Response) => {
  try {
    const data = req.body;
    logger.info(`Received page detection request for session ${data.sessionId}`);

    if (!data || !data.actions || !Array.isArray(data.actions) || data.actions.length === 0) {
      return res.status(400).json({ error: 'Invalid request. Actions data is required.' });
    }

    // Validate and fix timestamps
    const fixedActions = data.actions.map((action: Action) => validateTimestamp(action));

    // Use ComponentRecognizer to identify pages and components
    const pages = componentRecognizer.identifyPagesAndComponents(fixedActions);
    logger.info(`Identified ${pages.length} pages with components`);

    return res.json({
      sessionId: data.sessionId,
      pages: pages
    });
  } catch (error: any) {
    logger.error(`Error detecting pages: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while detecting pages'
    });
  }
});

// Generate test cases
app.post('/generate-test-cases', (req: Request, res: Response) => {
  try {
    const data = req.body;
    logger.info(`Received test case generation request for session ${data.sessionId}`);

    if (!data || !data.pages) {
      return res.status(400).json({ error: 'Invalid request. Pages data is required.' });
    }

    const actions = data.actions || [];
    const pages = data.pages || [];
    const testCases = testCaseGenerator.generateTestCases(pages, actions);

    logger.info(`Generated ${testCases.length} test cases`);

    return res.json({
      sessionId: data.sessionId,
      testCases: testCases
    });
  } catch (error: any) {
    logger.error(`Error generating test cases: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while generating test cases'
    });
  }
});

// Generate script
app.post('/generate-script', (req: Request, res: Response) => {
  try {
    const data = req.body;
    logger.info('Received script generation request');

    if (!data || !data.testCase) {
      return res.status(400).json({ error: 'Invalid request. Test case data is required.' });
    }

    const testCase = data.testCase;
    const framework = data.framework || 'selenium';
    const testData = data.testData || {};

    const script = testScriptGenerator.generateScript(testCase, testData, framework);
    logger.info(`Generated ${framework} script`);

    const language = framework === 'selenium' ? 'java' : 'javascript';

    return res.json({
      script: script,
      language: language,
      framework: framework
    });
  } catch (error: any) {
    logger.error(`Error generating script: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while generating script'
    });
  }
});

// Chat API endpoint for testing Ollama/DeepSeek integration
app.post('/chat', async (req: Request, res: Response) => {
  try {
    const { prompt } = req.body;

    if (!prompt || typeof prompt !== 'string') {
      return res.status(400).json({ 
        error: 'Invalid request. Prompt is required and must be a string.' 
      });
    }

    logger.info(`Received chat request with prompt length: ${prompt.length}`);

    // Query DeepSeek via Ollama
    const response = await ollamaService.query(prompt);

    logger.info(`Chat response generated (${response.length} chars)`);

    return res.json({ 
      response: response.trim() 
    });
  } catch (error: any) {
    logger.error(`Error in chat endpoint: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: error.message || 'An error occurred while processing the chat request'
    });
  }
});

// Alternative API path for chat (backwards compatibility)
app.post('/api/chat', async (req: Request, res: Response) => {
  try {
    const { prompt } = req.body;

    if (!prompt || typeof prompt !== 'string') {
      return res.status(400).json({ 
        error: 'Invalid request. Prompt is required and must be a string.' 
      });
    }

    logger.info(`Received chat request (via /api/chat) with prompt length: ${prompt.length}`);

    // Query DeepSeek via Ollama
    const response = await ollamaService.query(prompt);

    logger.info(`Chat response generated (${response.length} chars)`);

    return res.json({ 
      response: response.trim() 
    });
  } catch (error: any) {
    logger.error(`Error in chat endpoint: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: error.message || 'An error occurred while processing the chat request'
    });
  }
});

// Start server
const PORT = config.PORT;
const HOST = config.HOST;

app.listen(PORT, HOST, () => {
  logger.info(`Starting ${config.APP_NAME} v${config.APP_VERSION}`);
  logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
  logger.info(`Debug mode: ${config.DEBUG}`);
  logger.info(`Log level: ${config.LOG_LEVEL}`);
  logger.info(`Server starting on ${HOST}:${PORT}`);
});

export default app;

