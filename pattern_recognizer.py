import logging
from collections import defaultdict
import re
from typing import Dict, List, Any, Optional, Set, Tuple
import datetime

logger = logging.getLogger(__name__)

class PatternRecognizer:
    """
    Enhanced pattern recognition for test actions with improved detection logic.
    """
    
    def __init__(self):
        """Initialize the test data generator with common values and patterns."""
        # Regular expressions for common field patterns
        self.patterns = {
            'email': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            'phone': r'^\+?[0-9]{10,15}$',
            'zip_code': r'^\d{5}(-\d{4})?$',
            'credit_card': r'^[0-9]{13,19}$',
            'date': r'^\d{4}-\d{2}-\d{2}$',
            'url': r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        }
        
        # Common error keywords to detect
        self.error_keywords = [
            'error', 'failed', 'invalid', 'not found', 'not authorized',
            'denied', 'exception', 'timeout', 'unavailable', '404', '500',
            'sorry', 'problem', 'cannot', 'unable', 'warning'
        ]
        
        # Common form field names and patterns
        self.form_field_patterns = {
            'email': re.compile(r'email|e-mail', re.IGNORECASE),
            'password': re.compile(r'password|pwd', re.IGNORECASE),
            'username': re.compile(r'username|user|login', re.IGNORECASE),
            'name': re.compile(r'name|fullname|firstname|lastname', re.IGNORECASE),
            'address': re.compile(r'address|street|city|state|zip|postal', re.IGNORECASE),
            'phone': re.compile(r'phone|mobile|cell|tel', re.IGNORECASE),
            'credit_card': re.compile(r'card|credit|payment|cvv|cvc|expir', re.IGNORECASE),
            'search': re.compile(r'search|find|query', re.IGNORECASE)
        }
        
    def find_patterns(self, action_sequence):
        """Analyze action sequence to find patterns."""
        if not action_sequence or not action_sequence.actions:
            return {}
        
        # Define pattern detector methods
        pattern_detectors = {
            'form_submission': self._detect_form_submissions,
            'navigation_flow': self._detect_navigation_patterns,
            'user_input': self._detect_input_patterns,
            'error_states': self._detect_error_conditions,
            'repeated_actions': self._detect_repeated_actions,
            'user_journey': self._detect_user_journey,
            'performance_issues': self._detect_performance_issues
        }
        
        results = {}
        
        # Call each pattern detector method
        for pattern_name, detector_method in pattern_detectors.items():
            try:
                pattern_result = detector_method(action_sequence)
                if pattern_result:
                    results[pattern_name] = pattern_result
            except Exception as e:
                logger.error(f"Error detecting {pattern_name} patterns: {str(e)}")
                
        return results

    def _parse_timestamp(self, timestamp_str):
        """
        Parse a timestamp string with flexible format detection.
        
        Args:
            timestamp_str: String representation of timestamp
            
        Returns:
            datetime object or None if parsing fails
        """
        if not timestamp_str:
            return None
            
        # Try different formats, from most to least specific
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO format with milliseconds and Z
            "%Y-%m-%dT%H:%M:%S.%f",   # ISO format with milliseconds
            "%Y-%m-%dT%H:%M:%S",      # ISO format without milliseconds
            "%Y-%m-%d %H:%M:%S",      # Standard format without T
            "%Y-%m-%d",               # Just date
            "%Y-%m",                  # Year and month
            "%Y"                      # Just year
        ]
        
        # Try each format until one works
        for fmt in formats:
            try:
                # For partial formats like just the year, add default values
                if fmt == "%Y":
                    year = int(timestamp_str)
                    return datetime.datetime(year, 1, 1, 0, 0, 0)
                elif fmt == "%Y-%m":
                    return datetime.datetime.strptime(timestamp_str, fmt).replace(day=1, hour=0, minute=0, second=0)
                elif fmt == "%Y-%m-%d":
                    return datetime.datetime.strptime(timestamp_str, fmt).replace(hour=0, minute=0, second=0)
                else:
                    return datetime.datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
                
        # If we get here, none of the formats worked
        logger.warning(f"Could not parse timestamp: {timestamp_str}")
        return None
    
    def _get_timestamp_string(self, timestamp_value):
        """
        Safely extract a timestamp string from a value that might be a list or string.
        
        Args:
            timestamp_value: The timestamp value which could be a string or a list
            
        Returns:
            A string representation of the timestamp, or None if it can't be extracted
        """
        if timestamp_value is None:
            return None
            
        # If it's already a string, return it (but ensure it's properly formatted)
        if isinstance(timestamp_value, str):
            # Check if the timestamp is complete
            if len(timestamp_value) >= 19 and 'T' in timestamp_value:
                return timestamp_value
            # Handle incomplete timestamps (like just '2025')
            elif timestamp_value.isdigit() and len(timestamp_value) == 4:
                # If only a year is provided, return None instead of trying to parse it
                logger.warning(f"Incomplete timestamp detected: '{timestamp_value}'. Expected ISO format.")
                return None
            return timestamp_value
            
        # If it's a list, get the first element that's a string
        if isinstance(timestamp_value, list):
            for item in timestamp_value:
                if isinstance(item, str):
                    # Also check format for list items
                    if len(item) >= 19 and 'T' in item:
                        return item
                    elif item.isdigit() and len(item) == 4:
                        logger.warning(f"Incomplete timestamp detected in list: '{item}'. Expected ISO format.")
                        return None
                    return item
            # If no string found, use the first element and convert to string
            if timestamp_value:
                str_val = str(timestamp_value[0])
                # Check format here too
                if len(str_val) >= 19 and 'T' in str_val:
                    return str_val
                elif str_val.isdigit() and len(str_val) == 4:
                    logger.warning(f"Incomplete timestamp detected in list conversion: '{str_val}'. Expected ISO format.")
                    return None
                return str_val
                
        # Any other case, try string conversion but validate format
        try:
            str_val = str(timestamp_value)
            if len(str_val) >= 19 and 'T' in str_val:
                return str_val
            elif str_val.isdigit() and len(str_val) == 4:
                logger.warning(f"Incomplete timestamp detected in conversion: '{str_val}'. Expected ISO format.")
                return None
            return str_val
        except:
            return None
    
    def _detect_form_submissions(self, action_sequence):
        """
        Detect form submission patterns.
        Returns a list of forms with their fields and submission details.
        """
        forms = []
        current_form = {"fields": [], "submit": None}
        
        # Map field selectors to their types for better insights
        field_types = {}
        
        for i, action in enumerate(action_sequence.actions):
            action_type = action.get('actionType')
            
            # Reset form if we navigate to a new page
            if action_type == 'NAVIGATE' and current_form["fields"]:
                # If we have fields but no submit, consider it as an incomplete form
                if not current_form["submit"]:
                    current_form["status"] = "incomplete"
                    forms.append(current_form.copy())
                current_form = {"fields": [], "submit": None}
                
            # Capture input fields
            if action_type == 'TYPE' or action_type == 'SELECT':
                selector = action.get('elementSelector')
                element_type = action.get('elementType')
                value = action.get('inputData')
                
                # Try to determine the field type
                field_type = self._determine_field_type(selector, element_type)
                field_types[selector] = field_type
                
                field = {
                    "selector": selector,
                    "type": element_type,
                    "fieldType": field_type,
                    "value": value
                }
                current_form["fields"].append(field)
            
            # Detect form submission
            elif action_type == 'SUBMIT' or (action_type == 'CLICK' and 
                    (action.get('elementType') in ['button', 'input'] or 
                     'submit' in (action.get('elementValue') or '').lower() or
                     'login' in (action.get('elementValue') or '').lower() or
                     'register' in (action.get('elementValue') or '').lower() or
                     'send' in (action.get('elementValue') or '').lower() or
                     'continue' in (action.get('elementValue') or '').lower())):
                
                if current_form["fields"]:
                    current_form["submit"] = {
                        "selector": action.get('elementSelector'),
                        "description": action.get('description')
                    }
                    current_form["status"] = "submitted"
                    
                    # Analyze form completeness
                    required_fields = ['email', 'username', 'password', 'name']
                    field_types_in_form = set(field.get('fieldType') for field in current_form["fields"])
                    missing_fields = [field for field in required_fields if field not in field_types_in_form]
                    
                    if missing_fields:
                        current_form["missing_fields"] = missing_fields
                    
                    forms.append(current_form.copy())
                    
                # Reset for next form
                current_form = {"fields": [], "submit": None}
        
        # If we have a form in progress at the end, add it too
        if current_form["fields"] and not current_form["submit"]:
            current_form["status"] = "incomplete"
            forms.append(current_form)
        
        return forms if forms else None
    
    def _determine_field_type(self, selector, element_type):
        """Determine the type of form field based on selector and element type."""
        if not selector:
            return "unknown"
            
        selector_lower = selector.lower()
        
        # Check against common patterns
        for field_type, pattern in self.form_field_patterns.items():
            if pattern.search(selector_lower):
                return field_type
        
        # Check element type
        if element_type == 'password':
            return 'password'
        elif element_type == 'email':
            return 'email'
        elif element_type == 'checkbox':
            return 'checkbox'
        elif element_type == 'radio':
            return 'radio'
        elif element_type == 'select':
            return 'select'
        
        return "text"
    
    def _detect_navigation_patterns(self, action_sequence):
        """
        Detect patterns in navigation flow.
        Returns sequence of pages visited and identifies potential flow issues.
        """
        navigations = []
        for action in action_sequence.actions:
            if action.get('actionType') == 'NAVIGATE':
                navigations.append({
                    "url": action.get('url'),
                    "title": action.get('pageTitle'),
                    "timestamp": action.get('actionTime')
                })
            elif action.get('actionType') == 'CLICK' and action.get('description', '').startswith('Navigated to'):
                # Some clicks result in navigation
                navigations.append({
                    "url": action.get('url'),
                    "title": action.get('pageTitle'),
                    "timestamp": action.get('actionTime'),
                    "triggered_by": "click"
                })
        
        if len(navigations) <= 1:
            return None
            
        # Calculate time spent on each page
        for i in range(len(navigations) - 1):
            current = navigations[i]
            next_nav = navigations[i + 1]
            
            # Get timestamp strings safely
            current_timestamp = self._get_timestamp_string(current.get('timestamp'))
            next_timestamp = self._get_timestamp_string(next_nav.get('timestamp'))
            
            if current_timestamp and next_timestamp:
                try:
                    # Use our new flexible timestamp parser
                    current_time = self._parse_timestamp(current_timestamp)
                    next_time = self._parse_timestamp(next_timestamp)
                    
                    if current_time and next_time:
                        time_spent = (next_time - current_time).total_seconds()
                        current["time_spent"] = time_spent
                except Exception as e:
                    logger.warning(f"Error calculating time spent: {str(e)}")
        
        # Analyze the flow
        flow_analysis = {
            "pages": navigations,
            "unique_pages": len(set(n.get('url') for n in navigations)),
            "revisited_pages": self._find_revisited_pages(navigations)
        }
        
        # Check for potential issues in the flow
        flow_issues = []
        
        # Check for pages with very short time spent (less than 2 seconds)
        for nav in navigations:
            if nav.get('time_spent') is not None and nav.get('time_spent') < 2.0:
                flow_issues.append({
                    "type": "short_page_visit",
                    "url": nav.get('url'),
                    "time_spent": nav.get('time_spent')
                })
        
        if flow_issues:
            flow_analysis["issues"] = flow_issues
        
        return flow_analysis
    
    def _find_revisited_pages(self, navigations):
        """Find pages that are visited multiple times."""
        url_count = defaultdict(int)
        for nav in navigations:
            url = nav.get('url')
            if url:
                url_count[url] += 1
        
        return {url: count for url, count in url_count.items() if count > 1}
    
    def _detect_input_patterns(self, action_sequence):
        """
        Detect patterns in user input actions.
        Identifies potential validation issues or data input patterns.
        """
        inputs = [a for a in action_sequence.actions if a.get('actionType') == 'TYPE']
        
        if not inputs:
            return None
            
        input_analysis = {
            "total_inputs": len(inputs),
            "input_fields": defaultdict(list),
            "input_patterns": {}
        }
        
        # Group inputs by field selector
        for input_action in inputs:
            selector = input_action.get('elementSelector', '')
            value = input_action.get('inputData', '')
            
            input_analysis["input_fields"][selector].append(value)
            
            # Look for patterns in input values
            field_values = input_analysis["input_fields"][selector]
            if len(field_values) >= 2:
                input_analysis["input_patterns"][selector] = self._analyze_input_pattern(field_values)
        
        # Find fields that were cleared after input
        cleared_fields = []
        for i in range(len(action_sequence.actions) - 1):
            current = action_sequence.actions[i]
            next_action = action_sequence.actions[i + 1]
            
            if (current.get('actionType') == 'TYPE' and 
                next_action.get('actionType') == 'TYPE' and 
                current.get('elementSelector') == next_action.get('elementSelector') and
                (next_action.get('inputData') or '') == ''):
                
                cleared_fields.append({
                    "selector": current.get('elementSelector'),
                    "original_value": current.get('inputData')
                })
        
        if cleared_fields:
            input_analysis["cleared_fields"] = cleared_fields
        
        return input_analysis if input_analysis["input_fields"] else None
    
    def _analyze_input_pattern(self, values):
        """Analyze patterns in multiple inputs to the same field."""
        if not values or len(values) < 2:
            return "insufficient_data"
            
        # Check if all values are similar in length
        lengths = [len(str(v)) for v in values]
        length_diff = max(lengths) - min(lengths)
        if length_diff <= 2:
            return "consistent_length"
            
        # Check if values get progressively longer (user adding more details)
        if all(lengths[i] <= lengths[i+1] for i in range(len(lengths)-1)):
            return "progressive_input"
            
        # Check if values get shorter (user refining input)
        if all(lengths[i] >= lengths[i+1] for i in range(len(lengths)-1)):
            return "refinement"
            
        # Default pattern
        return "varied_input"
    
    def _detect_error_conditions(self, action_sequence):
        """
        Detect potential error conditions in the application.
        Looks for error messages in page titles, URLs, and content.
        """
        potential_errors = []
        
        for action in action_sequence.actions:
            # Check page title and URL for error indicators
            page_title = action.get('pageTitle', '').lower()
            url = action.get('url', '').lower()
            description = action.get('description', '').lower()
            
            # Check if any error keyword is in the title, URL, or description
            error_terms = [kw for kw in self.error_keywords 
                         if kw in page_title or kw in url or kw in description]
            
            if error_terms:
                potential_errors.append({
                    "action": action,
                    "error_terms": error_terms
                })
        
        # Look for patterns of form submission followed by immediate re-submission
        # This often indicates an error occurred
        for i in range(len(action_sequence.actions) - 3):
            if (action_sequence.actions[i].get('actionType') == 'SUBMIT' or 
                action_sequence.actions[i].get('actionType') == 'CLICK' and 
                'submit' in (action_sequence.actions[i].get('elementValue') or '').lower()):
                
                # Check if there's another submission within a few actions
                for j in range(i+1, min(i+4, len(action_sequence.actions))):
                    if (action_sequence.actions[j].get('actionType') == 'SUBMIT' or 
                        action_sequence.actions[j].get('actionType') == 'CLICK' and 
                        'submit' in (action_sequence.actions[j].get('elementValue') or '').lower()):
                        
                        potential_errors.append({
                            "type": "repeated_submission",
                            "first_action": action_sequence.actions[i],
                            "second_action": action_sequence.actions[j]
                        })
                        break
        
        return potential_errors if potential_errors else None
    
    def _detect_repeated_actions(self, action_sequence):
        """
        Detect repeated sequences of actions that might indicate repetitive tasks.
        These are good candidates for automation.
        """
        if len(action_sequence.actions) < 4:
            return None
            
        actions = action_sequence.actions
        repeated_sequences = []
        
        # Look for repeating patterns of 2-4 actions
        for pattern_length in range(2, 5):
            if len(actions) < pattern_length * 2:
                continue
                
            for i in range(len(actions) - pattern_length * 2 + 1):
                pattern_actions = actions[i:i+pattern_length]
                
                # Check if this pattern repeats elsewhere
                for j in range(i + pattern_length, len(actions) - pattern_length + 1):
                    comparison_actions = actions[j:j+pattern_length]
                    
                    if self._are_action_sequences_similar(pattern_actions, comparison_actions):
                        repeated_sequences.append({
                            "length": pattern_length,
                            "first_occurrence": i,
                            "second_occurrence": j,
                            "actions": pattern_actions
                        })
        
        if not repeated_sequences:
            return None
            
        # Remove overlapping sequences, keeping the longest ones
        repeated_sequences.sort(key=lambda x: x["length"], reverse=True)
        filtered_sequences = []
        
        for seq in repeated_sequences:
            overlaps = False
            for filtered_seq in filtered_sequences:
                if (seq["first_occurrence"] >= filtered_seq["first_occurrence"] and 
                    seq["first_occurrence"] < filtered_seq["first_occurrence"] + filtered_seq["length"]):
                    overlaps = True
                    break
                if (seq["second_occurrence"] >= filtered_seq["second_occurrence"] and 
                    seq["second_occurrence"] < filtered_seq["second_occurrence"] + filtered_seq["length"]):
                    overlaps = True
                    break
            
            if not overlaps:
                filtered_sequences.append(seq)
        
        return filtered_sequences if filtered_sequences else None
    
    def _are_action_sequences_similar(self, seq1, seq2):
        """Check if two action sequences are similar enough to be considered repeating."""
        if len(seq1) != len(seq2):
            return False
            
        for i in range(len(seq1)):
            if seq1[i].get('actionType') != seq2[i].get('actionType'):
                return False
            
            # For click actions, check if they're on similar elements
            if seq1[i].get('actionType') == 'CLICK':
                selector1 = seq1[i].get('elementSelector', '')
                selector2 = seq2[i].get('elementSelector', '')
                
                # If both selectors exist but are completely different, sequences are not similar
                if selector1 and selector2 and not self._are_selectors_similar(selector1, selector2):
                    return False
        
        return True
    
    def _are_selectors_similar(self, selector1, selector2):
        """Check if two CSS selectors might target similar elements."""
        # This is a simplified check - in a real system, you'd use DOM understanding
        
        # If selectors are identical, they're similar
        if selector1 == selector2:
            return True
            
        # If they're different element types, they're not similar
        s1_parts = selector1.split('.')
        s2_parts = selector2.split('.')
        
        if s1_parts[0] != s2_parts[0]:
            return False
            
        # If they have at least one common class, they might be similar
        s1_classes = set(s1_parts[1:])
        s2_classes = set(s2_parts[1:])
        
        return len(s1_classes.intersection(s2_classes)) > 0
    
    def _detect_user_journey(self, action_sequence):
        """
        Identify complete user journeys or workflows in the action sequence.
        """
        # Define common workflow patterns
        workflows = {
            "login": {
                "start_indicators": [
                    {"url_contains": ["login", "signin"]},
                    {"title_contains": ["login", "sign in"]}
                ],
                "required_actions": [
                    {"actionType": "TYPE", "field_type": "username"},
                    {"actionType": "TYPE", "field_type": "password"},
                    {"actionType": "SUBMIT"}
                ],
                "end_indicators": [
                    {"url_contains": ["dashboard", "account", "profile", "home"]},
                    {"title_contains": ["dashboard", "account", "welcome", "home"]}
                ]
            },
            "registration": {
                "start_indicators": [
                    {"url_contains": ["register", "signup", "join"]},
                    {"title_contains": ["register", "sign up", "create account"]}
                ],
                "required_actions": [
                    {"actionType": "TYPE", "field_type": "email"},
                    {"actionType": "TYPE", "field_type": "password"},
                    {"actionType": "SUBMIT"}
                ],
                "end_indicators": [
                    {"url_contains": ["success", "welcome", "dashboard", "verify"]},
                    {"title_contains": ["success", "welcome", "verification", "complete"]}
                ]
            },
            "checkout": {
                "start_indicators": [
                    {"url_contains": ["cart", "basket", "checkout"]},
                    {"title_contains": ["cart", "basket", "checkout", "payment"]}
                ],
                "required_actions": [
                    {"actionType": "TYPE", "field_type": "name"},
                    {"actionType": "TYPE", "field_type": "address"},
                    {"actionType": "TYPE", "field_type": "credit_card"},
                    {"actionType": "SUBMIT"}
                ],
                "end_indicators": [
                    {"url_contains": ["confirmation", "success", "thank", "receipt", "order"]},
                    {"title_contains": ["confirmation", "success", "thank you", "receipt", "order"]}
                ]
            },
            "search": {
                "start_indicators": [
                    {"url_contains": ["search", "find"]},
                    {"title_contains": ["search", "find", "results"]}
                ],
                "required_actions": [
                    {"actionType": "TYPE", "field_type": "search"},
                    {"actionType": "SUBMIT"}
                ],
                "end_indicators": [
                    {"url_contains": ["result", "search"]},
                    {"title_contains": ["result", "found"]}
                ]
            }
        }
        
        # Analyze the action sequence for each workflow type
        detected_journeys = []
        
        for workflow_name, workflow_pattern in workflows.items():
            journey = self._detect_workflow(action_sequence, workflow_pattern)
            if journey:
                journey["workflow_type"] = workflow_name
                detected_journeys.append(journey)
        
        return detected_journeys if detected_journeys else None
    
    def _detect_workflow(self, action_sequence, workflow_pattern):
        """
        Detect if a specific workflow pattern exists in the action sequence.
        """
        actions = action_sequence.actions
        workflow_start = -1
        workflow_end = -1
        
        # Find potential workflow starts
        for i, action in enumerate(actions):
            if self._matches_workflow_indicator(action, workflow_pattern["start_indicators"]):
                workflow_start = i
                break
        
        if workflow_start == -1:
            return None
        
        # Find potential workflow ends after the start
        for i in range(workflow_start + 1, len(actions)):
            if self._matches_workflow_indicator(actions[i], workflow_pattern["end_indicators"]):
                workflow_end = i
                break
        
        # If we found both start and end, check for required actions in between
        if workflow_start != -1 and workflow_end != -1:
            workflow_actions = actions[workflow_start:workflow_end+1]
            
            # Check if all required actions are present
            required_actions_found = True
            for required_action in workflow_pattern["required_actions"]:
                if not self._contains_required_action(workflow_actions, required_action):
                    required_actions_found = False
                    break
            
            if required_actions_found:
                return {
                    "start_index": workflow_start,
                    "end_index": workflow_end,
                    "actions": workflow_actions,
                    "duration": len(workflow_actions)
                }
        
        return None
    
    def _matches_workflow_indicator(self, action, indicators):
        """Check if an action matches any of the workflow indicators."""
        url = action.get('url', '').lower()
        title = action.get('pageTitle', '').lower()
        
        for indicator in indicators:
            if "url_contains" in indicator:
                for term in indicator["url_contains"]:
                    if term in url:
                        return True
            
            if "title_contains" in indicator:
                for term in indicator["title_contains"]:
                    if term in title:
                        return True
        
        return False
    
    def _contains_required_action(self, actions, required_action):
        """Check if the list of actions contains a required action type."""
        action_type = required_action.get("actionType")
        field_type = required_action.get("field_type")
        
        for action in actions:
            if action.get('actionType') == action_type:
                # If field type is specified, check the element selector
                if field_type and action.get('elementSelector'):
                    element_selector = action.get('elementSelector').lower()
                    pattern = self.form_field_patterns.get(field_type)
                    
                    if pattern and pattern.search(element_selector):
                        return True
                # If no field type is required, any matching action type is sufficient
                elif not field_type:
                    return True
        
        return False
    
    def _detect_performance_issues(self, action_sequence):
        """
        Detect potential performance issues from timing between actions.
        """
        actions = action_sequence.actions
        if len(actions) < 3:
            return None
            
        # Look for long delays between actions
        action_delays = []
        
        for i in range(len(actions) - 1):
            current = actions[i]
            next_action = actions[i + 1]
            
            # Get timestamp strings safely
            current_timestamp = self._get_timestamp_string(current.get('actionTime'))
            next_timestamp = self._get_timestamp_string(next_action.get('actionTime'))
            
            if current_timestamp and next_timestamp:
                try:
                    # Use our new flexible timestamp parser
                    current_time = self._parse_timestamp(current_timestamp)
                    next_time = self._parse_timestamp(next_timestamp)
                    
                    if current_time and next_time:
                        delay = (next_time - current_time).total_seconds()
                        
                        # If delay is more than 5 seconds, it might indicate a performance issue
                        if delay > 5.0:
                            action_delays.append({
                                "first_action": current,
                                "second_action": next_action,
                                "delay": delay
                            })
                except Exception as e:
                    logger.warning(f"Error calculating delay between actions: {str(e)}")
        
        return action_delays if action_delays else None