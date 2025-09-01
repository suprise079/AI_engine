from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import json
import datetime
from pattern_recognizer import PatternRecognizer
from suggestion_generator import SuggestionGenerator
from component_recognizer import ComponentRecognizer
from test_case_generator import TestCaseGenerator
from test_script_generator import TestScriptGenerator
from models import ActionSequence, TestSuggestion

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize AI components
pattern_recognizer = PatternRecognizer()
suggestion_generator = SuggestionGenerator()
component_recognizer = ComponentRecognizer()
test_case_generator = TestCaseGenerator()
test_script_generator = TestScriptGenerator()

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
    return jsonify({"status": "healthy"}), 200

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
        
    except Exception as e:
        logger.error(f"Error analyzing actions: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error analyzing actions: {str(e)}"}), 500


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
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error processing feedback: {str(e)}"}), 500

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
        
    except Exception as e:
        logger.error(f"Error detecting pages: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error detecting pages: {str(e)}"}), 500

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
        
    except Exception as e:
        logger.error(f"Error generating test cases: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error generating test cases: {str(e)}"}), 500

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
        
    except Exception as e:
        logger.error(f"Error generating script: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error generating script: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)