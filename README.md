# Hydra AI Engine

A Node.js/Express TypeScript microservice that provides AI-powered capabilities for test analysis and test generation using DeepSeek via Ollama. This service integrates with the Hydra Backend to provide intelligent test suggestions and automation.

## Features

- **Action Analysis**: Analyzes test action sequences and generates intelligent suggestions using DeepSeek AI
- **Component Detection**: Detects pages and components from action sequences
- **Test Case Generation**: Generates test cases from detected pages and actions
- **Test Script Generation**: Creates executable test scripts in various frameworks (Selenium, Cypress, Playwright)
- **Feedback Processing**: Processes user feedback to improve AI models
- **Chat API**: Direct API endpoint for testing Ollama/DeepSeek integration

## Requirements

- Node.js 18+ 
- npm 9+
- Ollama installed and running with `deepseek-coder` model

### Installing Ollama and DeepSeek Model

1. Install Ollama from https://ollama.ai
2. Pull the deepseek-coder model:
   ```bash
   ollama pull deepseek-coder
   ```
3. Verify installation:
   ```bash
   ollama run deepseek-coder "Hello, test"
   ```

## Installation

1. Clone the repository or navigate to the ai_engine directory:
```bash
cd ai_engine
```

2. Install dependencies:
```bash
npm install
```

3. Build the TypeScript code:
```bash
npm run build
```

## Configuration

The application uses environment-based configuration. You can configure the service using environment variables or by creating a `.env` file.

### Environment Variables

- `NODE_ENV`: Environment mode (development, production, qa) - Default: `development`
- `PORT`: Server port - Default: `3006`
- `HOST`: Server host - Default: `0.0.0.0`
- `DEBUG`: Enable debug mode - Default: `false`
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR) - Default: `INFO`
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins
- `CORS_CREDENTIALS`: Enable CORS credentials - Default: `true`
- `MAX_CONTENT_LENGTH`: Maximum request size in bytes - Default: `16777216` (16MB)
- `REQUEST_TIMEOUT`: Request timeout in seconds - Default: `200` (200 seconds)
- `OLLAMA_URL`: Ollama HTTP API URL - Default: `http://localhost:11434`
- `OLLAMA_MODEL`: Ollama model name - Default: `deepseek-coder`
- `OLLAMA_TIMEOUT`: Ollama query timeout in milliseconds - Default: `60000` (60 seconds)

### Example .env file

```env
NODE_ENV=development
PORT=3006
HOST=0.0.0.0
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_CREDENTIALS=true
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-coder
OLLAMA_TIMEOUT=60000
```

## Running the Application

### Development Mode

```bash
npm run dev
```

This uses `ts-node-dev` for hot-reloading during development.

### Production Mode

```bash
npm run build
npm start
```

Or using the production script:
```bash
npm run prod
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t hydra-ai-engine:latest .
```

### Run Docker Container

```bash
docker run -d -p 3006:3006 --name hydra-ai-engine \
  -e NODE_ENV=production \
  -e PORT=3006 \
  -e LOG_LEVEL=INFO \
  -e OLLAMA_URL=http://host.docker.internal:11434 \
  -e OLLAMA_MODEL=deepseek-coder \
  hydra-ai-engine:latest
```

**Note**: The Docker container connects to Ollama via HTTP API. Ollama should be running separately (either on the host machine or in another container). Set the `OLLAMA_URL` environment variable to point to your Ollama instance (e.g., `http://ollama:11434` for a container named "ollama", or `http://host.docker.internal:11434` to access Ollama on the host).

## API Endpoints

### Health Check
- **GET** `/health`
  - Returns the health status of the service
  - Response: `{"status": "healthy", "version": "1.0.0", ...}`

### Action Analysis
- **POST** `/analyze`
  - Analyzes a sequence of test actions and generates suggestions using DeepSeek AI
  - Request body: `{"sessionId": 123, "actions": [...]}`
  - Response: `{"sessionId": 123, "suggestions": [...]}`

### Feedback Processing
- **POST** `/feedback`
  - Processes feedback on suggestions
  - Request body: `{"suggestionId": 123, "status": "IMPLEMENTED", "feedback": "..."}`
  - Response: `{"status": "success"}`

### Page Detection
- **POST** `/detect-pages`
  - Detects pages and components from action sequences
  - Request body: `{"sessionId": 123, "actions": [...]}`
  - Response: `{"sessionId": 123, "pages": [...]}`

### Test Case Generation
- **POST** `/generate-test-cases`
  - Generates test cases from pages and actions
  - Request body: `{"sessionId": 123, "actions": [...], "pages": [...]}`
  - Response: `{"sessionId": 123, "testCases": [...]}`

### Test Script Generation
- **POST** `/generate-script`
  - Generates executable test scripts
  - Request body: `{"testCase": {...}, "framework": "selenium", "testData": {...}}`
  - Response: `{"script": "...", "language": "java", "framework": "selenium"}`

### Chat API (Testing)
- **POST** `/chat`
  - Direct endpoint for testing Ollama/DeepSeek integration
  - Request body: `{"prompt": "Your question or prompt here"}`
  - Response: `{"response": "AI generated response"}`
  - Example:
    ```bash
    curl -X POST http://localhost:3006/chat \
      -H "Content-Type: application/json" \
      -d '{"prompt": "Write a hello world program in Python"}'
    ```
  - Also available at `/api/chat` for backwards compatibility

## Backend Integration

The AI Engine integrates with the Hydra Backend through the `AiEngineService`. The backend configuration should include:

```properties
# Backend application.properties
ai-engine.url=http://localhost:3006
ai-engine.timeout=30000
```

### Backend Configuration Files

Add the following to your backend properties files:
- `application-dev.properties`
- `application-qa.properties`
- `application-prod.properties`

```properties
ai-engine.url=http://localhost:3006
ai-engine.timeout=30000
```

For production, update the URL to match your deployment:
```properties
ai-engine.url=http://ai-engine-service:3006
ai-engine.timeout=30000
```

## Project Structure

```
ai_engine/
├── src/
│   ├── app.ts                      # Main Express application
│   ├── config/
│   │   ├── config.ts               # Configuration management
│   │   └── logger.ts               # Winston logger setup
│   ├── models/
│   │   └── index.ts                # Data models
│   ├── services/
│   │   ├── ollama-service.ts       # Ollama/DeepSeek integration
│   │   ├── suggestion-generator.ts # AI-powered suggestion generation
│   │   ├── component-recognizer.ts # Component detection
│   │   ├── test-case-generator.ts  # Test case generation
│   │   └── test-script-generator.ts # Test script generation
│   └── types/
│       └── index.ts                # TypeScript type definitions
├── dist/                           # Compiled JavaScript (generated)
├── package.json                     # Node.js dependencies
├── tsconfig.json                    # TypeScript configuration
├── Dockerfile                       # Docker configuration
├── .dockerignore                    # Docker ignore file
├── .gitignore                       # Git ignore file
└── README.md                        # This file
```

## Logging

The application uses Winston for logging with configurable levels:
- `DEBUG`: Detailed information for debugging
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages

Logs are formatted with timestamps and include request/response information.

## Error Handling

The application includes comprehensive error handling:
- **400 Bad Request**: Invalid request format or validation errors
- **404 Not Found**: Endpoint not found
- **405 Method Not Allowed**: HTTP method not allowed
- **413 Request Entity Too Large**: Request payload too large
- **500 Internal Server Error**: Unexpected server errors

All errors return JSON responses with error details (without exposing internal details in production).

## Development

### Running Tests

```bash
# Add test files and run
npm test
```

### Code Style

Follow TypeScript/ESLint style guide. Run linting:

```bash
npm run lint
```

Format code:

```bash
npm run format
```

## AI Model Integration

The service uses DeepSeek Coder via Ollama for intelligent analysis. The AI analyzes action sequences and identifies:

- Security vulnerabilities
- Performance issues
- Accessibility problems
- Usability concerns
- Edge cases
- Validation gaps
- Error handling issues
- Data integrity concerns

## Troubleshooting

### Ollama Not Found
If you get errors about Ollama not being found:
1. Ensure Ollama is installed and in your PATH
2. Verify with: `ollama --version`
3. Check that the model is pulled: `ollama list`

### Model Not Available
If DeepSeek model is not available:
```bash
ollama pull deepseek-coder
```

### Port Already in Use
Change the port using environment variable:
```bash
PORT=3007 npm start
```

## License

Copyright (c) QOT Systems. All rights reserved.

## Support

For issues and questions, please contact the Hydra development team.
