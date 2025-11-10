from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import datetime
from pattern_recognizer import PatternRecognizer
from suggestion_generator import SuggestionGenerator
from component_recognizer import ComponentRecognizer
from test_case_generator import TestCaseGenerator
from test_script_generator import TestScriptGenerator
from models import ActionSequence, TestSuggestion
from config import get_config, Config

# Initialize logger
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Load configuration
config_class = get_config()
app.config.from_object(config_class)
config_class.init_app(app)

# Configure CORS
cors = CORS(
    app,
    origins=config_class.CORS_ORIGINS,
    supports_credentials=config_class.CORS_CREDENTIALS,
    methods=config_class.CORS_METHODS,
    allow_headers=config_class.CORS_HEADERS
)

# Initialize AI components
pattern_recognizer = PatternRecognizer()
suggestion_generator = SuggestionGenerator()
component_recognizer = ComponentRecognizer()
test_case_generator = TestCaseGenerator()
test_script_generator = TestScriptGenerator()

# Request logging middleware
@app.before_request
def log_request_info():
    """Log incoming request information."""
    logger.debug(f"Request: {request.method} {request.path}")
    if request.is_json:
        logger.debug(f"Request body size: {len(str(request.json))} bytes")


@app.after_request
def log_response_info(response):
    """Log outgoing response information."""
    logger.debug(f"Response: {response.status_code} for {request.method} {request.path}")
    return response


# Global error handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    logger.warning(f"Bad request: {str(error)}")
    return jsonify({
        "error": "Bad Request",
        "message": str(error) if str(error) else "Invalid request format"
    }), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    logger.warning(f"Not found: {request.path}")
    return jsonify({
        "error": "Not Found",
        "message": f"The requested endpoint '{request.path}' was not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed errors."""
    logger.warning(f"Method not allowed: {request.method} {request.path}")
    return jsonify({
        "error": "Method Not Allowed",
        "message": f"Method '{request.method}' is not allowed for this endpoint"
    }), 405


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle 413 Request Entity Too Large errors."""
    logger.warning(f"Request too large: {request.path}")
    return jsonify({
        "error": "Request Entity Too Large",
        "message": "The request payload exceeds the maximum allowed size"
    }), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error."""
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500

def validate_timestamp(action):
    """Validate and fix timestamps in action objects"""
    if 'actionTime' not in action or not action['actionTime']:
        action['actionTime'] = datetime.datetime.now().isoformat()
        return action
        
    timestamp = action['actionTime']
    
    # Handle array-format timestamps like [2025, 3, 30, 18, 32, 55, 567000000]
    if isinstance(timestamp, list) and len(timestamp) >= 6:
        try:
            # Extract year, month, day, hour, minute, second
            year, month, day = timestamp[0], timestamp[1], timestamp[2]
            hour, minute, second = timestamp[3], timestamp[4], timestamp[5]
            
            # Add milliseconds if available
            microsecond = timestamp[6] // 1000 if len(timestamp) > 6 else 0
            
            # Create datetime and convert to ISO format string
            dt = datetime.datetime(year, month, day, hour, minute, second, microsecond)
            action['actionTime'] = dt.isoformat()
            return action
        except (ValueError, IndexError) as e:
            logger.warning(f"Could not parse timestamp: {timestamp}. Using current time.")
            action['actionTime'] = datetime.datetime.now().isoformat()
            return action
    
    # Check if it's a complete ISO format timestamp with 'T'
    if isinstance(timestamp, str):
        if 'T' in timestamp and len(timestamp) >= 19:
            return action
        # If it's just a year or incomplete timestamp, replace it
        elif timestamp.isdigit() and len(timestamp) == 4:
            logger.warning(f"Fixing incomplete timestamp: {timestamp}")
            action['actionTime'] = datetime.datetime.now().isoformat()
            return action
    
    # If we get here, try to parse and convert the timestamp
    try:
        # Try to parse various formats
        if isinstance(timestamp, str):
            # Try common formats
            for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S.%f", 
                       "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                try:
                    dt = datetime.datetime.strptime(timestamp, fmt)
                    action['actionTime'] = dt.isoformat()
                    return action
                except ValueError:
                    continue
                    
        # If all parsing attempts fail, use current time
        logger.warning(f"Could not parse timestamp: {timestamp}. Using current time.")
        action['actionTime'] = datetime.datetime.now().isoformat()
        return action
    except Exception as e:
        logger.warning(f"Error processing timestamp {timestamp}: {str(e)}. Using current time.")
        action['actionTime'] = datetime.datetime.now().isoformat()
        return action


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    Returns the health status of the AI Engine service.
    
    Returns:
        JSON response with status information
    """
    try:
        # Check if AI components are initialized
        components_status = {
            "pattern_recognizer": pattern_recognizer is not None,
            "suggestion_generator": suggestion_generator is not None,
            "component_recognizer": component_recognizer is not None,
            "test_case_generator": test_case_generator is not None,
            "test_script_generator": test_script_generator is not None
        }
        
        all_healthy = all(components_status.values())
        
        return jsonify({
            "status": "healthy" if all_healthy else "degraded",
            "version": Config.APP_VERSION,
            "components": components_status,
            "timestamp": datetime.datetime.now().isoformat()
        }), 200 if all_healthy else 503
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }), 503

@app.route('/analyze', methods=['POST'])
def analyze_actions():
    """
    Analyze a sequence of test actions and generate suggestions.
    Expected JSON: {
        "sessionId": 123,
        "actions": [
            {
                "id": 1,
                "actionType": "NAVIGATE",
                "url": "https://example.com",
                "pageTitle": "Example Page",
                "sequenceNumber": 1,
                "actionTime": "2023-04-13T14:53:12"
            },
            ...
        ]
    }
    """
    try:
        data = request.json
        logger.info(f"Received analysis request for session {data.get('sessionId')}")
        
        # Validate request
        if not data or 'actions' not in data or not data['actions']:
            return jsonify({"error": "Invalid request. Actions data is required."}), 400
        
        # Validate and fix timestamps in all actions
        fixed_actions = [validate_timestamp(action) for action in data.get('actions', [])]
        
        # Convert to model objects
        action_sequence = ActionSequence(
            session_id=data.get('sessionId'),
            actions=fixed_actions
        )
        
        # Analyze patterns in the action sequence
        patterns = pattern_recognizer.find_patterns(action_sequence)
        logger.info(f"Found {len(patterns)} patterns")
        
        # Generate suggestions based on the patterns
        suggestions = suggestion_generator.generate_suggestions(action_sequence, patterns)
        logger.info(f"Generated {len(suggestions)} suggestions")
        
        return jsonify({
            "sessionId": data.get('sessionId'),
            "suggestions": [s.to_dict() for s in suggestions]
        }), 200
        
    except ValueError as e:
        logger.warning(f"Validation error in analyze_actions: {str(e)}")
        return jsonify({
            "error": "Validation Error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error analyzing actions: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal Server Error",
            "message": "An error occurred while analyzing actions"
        }), 500


@app.route('/feedback', methods=['POST'])
def process_feedback():
    """
    Process feedback on suggestions to improve the AI models.
    Expected JSON: {
        "suggestionId": 123,
        "status": "IMPLEMENTED", # or SKIPPED, DEFERRED
        "feedback": "This was helpful because..."
    }
    """
    try:
        data = request.json
        logger.info(f"Received feedback for suggestion {data.get('suggestionId')}")
        
        # Update models based on feedback (simplified for Phase 1)
        suggestion_generator.process_feedback(
            suggestion_id=data.get('suggestionId'),
            status=data.get('status'),
            feedback=data.get('feedback')
        )
        
        return jsonify({"status": "success"}), 200
        
    except ValueError as e:
        logger.warning(f"Validation error in process_feedback: {str(e)}")
        return jsonify({
            "error": "Validation Error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal Server Error",
            "message": "An error occurred while processing feedback"
        }), 500

@app.route('/detect-pages', methods=['POST'])
def detect_pages():
    """
    Detects pages and components from a sequence of actions.
    Expected JSON: {
        "sessionId": 123,
        "actions": [
            {
                "id": 1,
                "actionType": "NAVIGATE",
                "url": "https://example.com/login",
                "pageTitle": "Login Page",
                "sequenceNumber": 1,
                "actionTime": "2023-04-13T14:53:12"
            },
            ...
        ]
    }
    """
    try:
        data = request.json
        logger.info(f"Received page detection request for session {data.get('sessionId')}")
        
        # Validate request
        if not data or 'actions' not in data or not data['actions']:
            return jsonify({"error": "Invalid request. Actions data is required."}), 400
        
        # Validate and fix timestamps in all actions
        fixed_actions = [validate_timestamp(action) for action in data.get('actions', [])]
        
        # Use the ComponentRecognizer to identify pages and components
        pages = component_recognizer.identify_pages_and_components(fixed_actions)
        logger.info(f"Identified {len(pages)} pages with components")
        
        return jsonify({
            "sessionId": data.get('sessionId'),
            "pages": pages
        }), 200
        
    except ValueError as e:
        logger.warning(f"Validation error in detect_pages: {str(e)}")
        return jsonify({
            "error": "Validation Error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error detecting pages: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal Server Error",
            "message": "An error occurred while detecting pages"
        }), 500

@app.route('/generate-test-cases', methods=['POST'])
def generate_test_cases():
    """
    Generates test cases from a sequence of actions and pages.
    Expected JSON: {
        "sessionId": 123,
        "actions": [...],
        "pages": [...]
    }
    """
    try:
        data = request.json
        logger.info(f"Received test case generation request for session {data.get('sessionId')}")
        
        # Validate request
        if not data or 'pages' not in data:
            return jsonify({"error": "Invalid request. Pages data is required."}), 400
        
        # Use the TestCaseGenerator to generate test cases
        actions = data.get('actions', [])
        pages = data.get('pages', [])
        
        test_cases = test_case_generator.generate_test_cases(pages, actions)
        logger.info(f"Generated {len(test_cases)} test cases")
        
        return jsonify({
            "sessionId": data.get('sessionId'),
            "testCases": test_cases
        }), 200
        
    except ValueError as e:
        logger.warning(f"Validation error in generate_test_cases: {str(e)}")
        return jsonify({
            "error": "Validation Error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error generating test cases: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal Server Error",
            "message": "An error occurred while generating test cases"
        }), 500

@app.route('/generate-script', methods=['POST'])
def generate_script():
    """
    Generates a test script from a test case.
    Expected JSON: {
        "testCase": {...},
        "framework": "selenium"
    }
    """
    try:
        data = request.json
        logger.info(f"Received script generation request")
        
        # Validate request
        if not data or 'testCase' not in data:
            return jsonify({"error": "Invalid request. Test case data is required."}), 400
        
        # Extract parameters
        test_case = data.get('testCase')
        framework = data.get('framework', 'selenium')
        test_data = data.get('testData', {})
        
        # Use the TestScriptGenerator to generate the script
        script = test_script_generator.generate_script(test_case, test_data, framework)
        logger.info(f"Generated {framework} script")
        
        # Determine language based on framework
        language = "java" if framework == "selenium" else "javascript"
        
        return jsonify({
            "script": script,
            "language": language,
            "framework": framework
        }), 200
        
    except ValueError as e:
        logger.warning(f"Validation error in generate_script: {str(e)}")
        return jsonify({
            "error": "Validation Error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error generating script: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal Server Error",
            "message": "An error occurred while generating script"
        }), 500


if __name__ == '__main__':
    """Run the Flask application."""
    logger.info(f"Starting {Config.APP_NAME} v{Config.APP_VERSION}")
    logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    logger.info(f"Log level: {Config.LOG_LEVEL}")
    logger.info(f"Server starting on {Config.HOST}:{Config.PORT}")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )