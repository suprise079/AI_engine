# Hydra AI Engine

A Flask-based Python microservice that provides AI-powered capabilities for test analysis, pattern recognition, and test generation. This service integrates with the Hydra Backend to provide intelligent test suggestions and automation.

## Features

- **Action Analysis**: Analyzes test action sequences and generates intelligent suggestions
- **Pattern Recognition**: Identifies patterns in test actions for optimization
- **Component Detection**: Detects pages and components from action sequences
- **Test Case Generation**: Generates test cases from detected pages and actions
- **Test Script Generation**: Creates executable test scripts in various frameworks (Selenium, etc.)
- **Feedback Processing**: Processes user feedback to improve AI models

## Requirements

- Python 3.8+
- pip

## Installation

1. Clone the repository or navigate to the ai_engine directory:
```bash
cd ai_engine
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The application uses environment-based configuration. You can configure the service using environment variables or by creating a `.env` file (see `.env.example` for reference).

### Environment Variables

- `FLASK_ENV`: Environment mode (development, production, qa) - Default: `development`
- `PORT`: Server port - Default: `5000`
- `HOST`: Server host - Default: `0.0.0.0`
- `DEBUG`: Enable debug mode - Default: `False`
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR) - Default: `INFO`
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins
- `CORS_CREDENTIALS`: Enable CORS credentials - Default: `True`
- `MAX_CONTENT_LENGTH`: Maximum request size in bytes - Default: `16777216` (16MB)
- `REQUEST_TIMEOUT`: Request timeout in seconds - Default: `300` (5 minutes)

### Example .env file

```env
FLASK_ENV=development
PORT=5000
HOST=0.0.0.0
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_CREDENTIALS=True
```

## Running the Application

### Development Mode

```bash
python app.py
```

Or using Flask directly:
```bash
flask run
```

### Production Mode

Using Gunicorn (recommended for production):
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t hydra-ai-engine:latest .
```

### Run Docker Container

```bash
docker run -d -p 5000:5000 --name hydra-ai-engine \
  -e FLASK_ENV=production \
  -e PORT=5000 \
  -e LOG_LEVEL=INFO \
  hydra-ai-engine:latest
```

## API Endpoints

### Health Check
- **GET** `/health`
  - Returns the health status of the service
  - Response: `{"status": "healthy", "version": "1.0.0", ...}`

### Action Analysis
- **POST** `/analyze`
  - Analyzes a sequence of test actions and generates suggestions
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

## Backend Integration

The AI Engine integrates with the Hydra Backend through the `AiEngineService`. The backend configuration should include:

```properties
# Backend application.properties
ai-engine.url=http://localhost:5000
ai-engine.timeout=30000
```

### Backend Configuration Files

Add the following to your backend properties files:
- `application-dev.properties`
- `application-qa.properties`
- `application-prod.properties`

```properties
ai-engine.url=http://localhost:5000
ai-engine.timeout=30000
```

For production, update the URL to match your deployment:
```properties
ai-engine.url=http://ai-engine-service:5000
ai-engine.timeout=30000
```

## Project Structure

```
ai_engine/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── models.py                   # Data models
├── pattern_recognizer.py       # Pattern recognition logic
├── suggestion_generator.py     # Suggestion generation
├── component_recognizer.py      # Component detection
├── test_case_generator.py      # Test case generation
├── test_script_generator.py    # Test script generation
├── test_data_generator.py      # Test data generation
├── requirements.txt             # Python dependencies
├── Dockerfile                  # Docker configuration
├── .dockerignore               # Docker ignore file
├── .gitignore                  # Git ignore file
├── README.md                   # This file
└── __init__.py                 # Package initialization
```

## Logging

The application uses Python's standard logging module with configurable levels:
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
pytest
```

### Code Style

Follow PEP 8 Python style guide.

## License

Copyright (c) QOT Systems. All rights reserved.

## Support

For issues and questions, please contact the Hydra development team.

