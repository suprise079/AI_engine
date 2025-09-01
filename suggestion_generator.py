import logging
import random
from typing import Dict, List, Any, Optional
from models import TestSuggestion

logger = logging.getLogger(__name__)

class SuggestionGenerator:
    """
    Enhanced suggestion generator with improved contextual awareness.
    Generates testing suggestions based on patterns detected in test actions.
    """
    
    def __init__(self, learning_mode=True):
        self.learning_mode = learning_mode
        
        # Store feedback for learning
        self.feedback_history = []
        
        # Suggestion templates by pattern type
        self.suggestion_templates = {
            "form_submission": self._generate_form_suggestions,
            "navigation_flow": self._generate_navigation_suggestions,
            "user_input": self._generate_input_suggestions,
            "error_states": self._generate_error_state_suggestions,
            "repeated_actions": self._generate_repeated_action_suggestions,
            "user_journey": self._generate_user_journey_suggestions,
            "performance_issues": self._generate_performance_suggestions,
        }
        
        # Track what suggestions have been given for a session
        self.session_suggestions = {}
        
        # Load learned suggestion effectiveness from feedback
        self.suggestion_effectiveness = {
            # Default effectiveness ratings - these will be updated through learning
            "form_submission": 0.85,
            "navigation_flow": 0.75,
            "user_input": 0.8,
            "error_states": 0.9,
            "repeated_actions": 0.7,
            "user_journey": 0.8,
            "performance_issues": 0.85
        }
    
    def generate_suggestions(self, action_sequence, patterns):
        """Generate testing suggestions based on detected patterns."""
        logger.info(f"Generating suggestions for {len(patterns)} patterns: {list(patterns.keys())}")
        
        if not patterns:
            return []
        
        session_id = action_sequence.session_id
        if session_id not in self.session_suggestions:
            self.session_suggestions[session_id] = set()
            
        suggestions = []
        
        # Generate suggestions for each pattern type found
        for pattern_type, pattern_data in patterns.items():
            if pattern_type in self.suggestion_templates and pattern_data:
                try:
                    pattern_suggestions = self.suggestion_templates[pattern_type](pattern_data, action_sequence)
                    logger.info(f"Generated {len(pattern_suggestions)} suggestions for pattern type {pattern_type}")
                    for suggestion in pattern_suggestions:
                        # Check if we've already given this suggestion
                        suggestion_key = f"{suggestion.title}:{suggestion.suggestion_type}"
                        if suggestion_key not in self.session_suggestions[session_id]:
                            suggestions.append(suggestion)
                            self.session_suggestions[session_id].add(suggestion_key)
                except Exception as e:
                    logger.error(f"Error generating suggestions for pattern type {pattern_type}: {str(e)}")
        
        # If no pattern-specific suggestions were generated, add a general suggestion
        if not suggestions:
            logger.info("No pattern-specific suggestions were generated, adding a general suggestion")
            general_suggestion = self._create_suggestion(
                "Explore validation scenarios",
                "Try testing with invalid inputs to verify validation behavior.",
                "VALIDATION",
                "MEDIUM",
                "Test with empty values, very long inputs, and special characters to ensure proper validation."
            )
            suggestions.append(general_suggestion)
        else:
            # Add general suggestions based on context
            try:
                general_suggestions = self._generate_general_suggestions(action_sequence)
                for suggestion in general_suggestions:
                    suggestion_key = f"{suggestion.title}:{suggestion.suggestion_type}"
                    if suggestion_key not in self.session_suggestions[session_id]:
                        suggestions.append(suggestion)
                        self.session_suggestions[session_id].add(suggestion_key)
            except Exception as e:
                logger.error(f"Error generating general suggestions: {str(e)}")
        
        # Sort by priority and effectiveness
        suggestions = self._prioritize_suggestions(suggestions)
        
        # Limit the number of suggestions to avoid overwhelming the tester
        final_suggestions = suggestions[:10]
        logger.info(f"Final suggestion count: {len(final_suggestions)}")
        
        return final_suggestions
    
    def _prioritize_suggestions(self, suggestions):
        """
        Sort suggestions by priority and effectiveness.
        Uses feedback data to determine which suggestions are most valuable.
        """
        # Calculate a score for each suggestion
        scored_suggestions = []
        for suggestion in suggestions:
            # Base score from priority (1-3)
            base_score = self._priority_value(suggestion.priority)
            
            # Adjust by effectiveness of this suggestion type
            effectiveness = self.suggestion_effectiveness.get(
                suggestion.suggestion_type, 0.75)
            
            final_score = base_score * effectiveness
            
            scored_suggestions.append((suggestion, final_score))
        
        # Sort by score (descending)
        scored_suggestions.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the suggestions
        return [s[0] for s in scored_suggestions]
    
    def _priority_value(self, priority):
        """Convert priority to numeric value for sorting."""
        priority_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return priority_map.get(priority, 0)
    
    def _generate_form_suggestions(self, forms, action_sequence):
        """Generate suggestions for form testing."""
        suggestions = []
        
        for form in forms:
            # Check form status
            if form.get("status") == "incomplete":
                suggestions.append(self._create_suggestion(
                    "Complete the unfinished form",
                    "Try completing and submitting the form that was started but not submitted.",
                    "EDGE_CASE",
                    "MEDIUM",
                    "Fill in all required fields in the form and submit it."
                ))
                
            elif form.get("status") == "submitted":
                # Validation testing
                suggestions.append(self._create_suggestion(
                    "Test form field validation",
                    "Try submitting the form with invalid inputs to test validation rules.",
                    "VALIDATION",
                    "HIGH",
                    "Try empty values, special characters, or very long text in form fields."
                ))
                
                # Check for specific field types and suggest accordingly
                field_types = set()
                for field in form.get("fields", []):
                    if "fieldType" in field:
                        field_types.add(field["fieldType"])
                
                if "password" in field_types:
                    suggestions.append(self._create_suggestion(
                        "Test password complexity requirements",
                        "Verify that the form enforces password requirements properly.",
                        "SECURITY",
                        "HIGH",
                        "Try passwords with different combinations of letters, numbers, and special characters."
                    ))
                
                if "email" in field_types:
                    suggestions.append(self._create_suggestion(
                        "Test email validation format",
                        "Check how the form validates email addresses.",
                        "VALIDATION",
                        "MEDIUM",
                        "Try various email formats including invalid ones like missing @ symbol or domain."
                    ))
                
                if "credit_card" in field_types:
                    suggestions.append(self._create_suggestion(
                        "Test credit card validation",
                        "Verify that credit card validation is working correctly.",
                        "PAYMENT",
                        "HIGH",
                        "Try different credit card types, invalid numbers, and expired dates."
                    ))
                
                # Check for missing required fields
                if form.get("missing_fields"):
                    missing = ", ".join(form.get("missing_fields"))
                    suggestions.append(self._create_suggestion(
                        f"Check for missing fields: {missing}",
                        f"The form might be missing important fields like {missing}.",
                        "EDGE_CASE",
                        "MEDIUM",
                        f"Verify that the application properly handles {missing} information."
                    ))
        
        return suggestions
    
    def _generate_navigation_suggestions(self, flow_data, action_sequence):
        """Generate suggestions for navigation flow testing."""
        suggestions = []
        
        if flow_data.get("unique_pages", 0) > 1:
            # Direct URL access testing
            suggestions.append(self._create_suggestion(
                "Test direct URL access",
                "Try accessing deeper pages directly via URL without going through the normal flow.",
                "SECURITY",
                "HIGH",
                f"Navigate directly to some of the deeper pages in the flow."
            ))
            
            # Back button testing
            suggestions.append(self._create_suggestion(
                "Test browser back button behavior",
                "Verify that using the browser's back button works correctly in the flow.",
                "UX",
                "MEDIUM",
                "Use the browser's back button at different points in the navigation flow."
            ))
            
            # Check for revisited pages
            revisited = flow_data.get("revisited_pages", {})
            if revisited:
                most_revisited = max(revisited.items(), key=lambda x: x[1])
                suggestions.append(self._create_suggestion(
                    "Investigate frequently revisited page",
                    f"The page {most_revisited[0]} was visited {most_revisited[1]} times. This may indicate navigation issues.",
                    "UX",
                    "MEDIUM",
                    "Verify that the user flow is clear and users don't need to revisit pages repeatedly."
                ))
            
            # Check for issues in flow
            flow_issues = flow_data.get("issues", [])
            for issue in flow_issues:
                if issue.get("type") == "short_page_visit":
                    suggestions.append(self._create_suggestion(
                        "Investigate very short page visit",
                        f"Page {issue.get('url')} was visited for only {issue.get('time_spent')} seconds. This may indicate confusion or errors.",
                        "UX",
                        "MEDIUM",
                        "Check if the page is functioning correctly and provides clear information to users."
                    ))
        
        return suggestions
    
    def _generate_input_suggestions(self, input_data, action_sequence):
        """Generate suggestions based on input patterns."""
        suggestions = []
        
        # Special character input testing
        suggestions.append(self._create_suggestion(
            "Test with special characters",
            "Verify the application properly handles special characters in inputs.",
            "VALIDATION",
            "HIGH",
            "Try inputs with <, >, &, \", ', /, \\, and international characters."
        ))
        
        # Long input testing
        suggestions.append(self._create_suggestion(
            "Test with maximum length inputs",
            "Verify the application properly handles very long inputs.",
            "EDGE_CASE",
            "MEDIUM",
            "Try entering inputs at or beyond the maximum allowed length."
        ))
        
        # Check cleared fields
        cleared_fields = input_data.get("cleared_fields", [])
        if cleared_fields:
            suggestions.append(self._create_suggestion(
                "Investigate field clearing behavior",
                "Some fields were cleared after data was entered. Verify this is expected behavior.",
                "UX",
                "MEDIUM",
                "Test how the application behaves when fields are cleared and re-entered."
            ))
        
        # Check input patterns
        input_patterns = input_data.get("input_patterns", {})
        for selector, pattern in input_patterns.items():
            if pattern == "progressive_input":
                suggestions.append(self._create_suggestion(
                    "Test auto-complete functionality",
                    "Multiple progressive inputs to the same field may indicate auto-complete functionality.",
                    "UX",
                    "LOW",
                    "Verify that auto-complete or suggestions work correctly for this field."
                ))
            elif pattern == "refinement":
                suggestions.append(self._create_suggestion(
                    "Test error correction handling",
                    "Multiple refinements to input might indicate confusion or error correction.",
                    "UX",
                    "MEDIUM",
                    "Check if the form provides clear guidance on expected input format."
                ))
        
        return suggestions
    
    def _generate_error_state_suggestions(self, error_data, action_sequence):
        """Generate suggestions based on detected error states."""
        suggestions = []
        
        # Create specific suggestions based on the error
        suggestions.append(self._create_suggestion(
            "Verify error handling and recovery",
            "Test the application's behavior when errors occur.",
            "ERROR_HANDLING",
            "HIGH",
            "Verify error messages are clear and provide appropriate recovery steps."
        ))
        
        # Check for repeated submission errors
        repeated_submissions = [e for e in error_data if e.get("type") == "repeated_submission"]
        if repeated_submissions:
            suggestions.append(self._create_suggestion(
                "Investigate form resubmission issues",
                "Multiple submissions of the same form were detected. This may indicate validation issues.",
                "ERROR_HANDLING",
                "HIGH",
                "Try to identify why the form needed to be submitted multiple times and if error messages are clear."
            ))
        
        # Check for specific error terms
        error_terms = set()
        for error in error_data:
            if "error_terms" in error:
                error_terms.update(error.get("error_terms", []))
        
        if "404" in error_terms or "not found" in error_terms:
            suggestions.append(self._create_suggestion(
                "Test for broken links or resources",
                "404 errors or 'not found' messages were detected. Verify all links are working.",
                "ERROR_HANDLING",
                "HIGH",
                "Check all links and resources in the application to ensure they're accessible."
            ))
            
        if "timeout" in error_terms or "unavailable" in error_terms:
            suggestions.append(self._create_suggestion(
                "Test application under load",
                "Timeout or unavailability errors were detected. Check application performance.",
                "PERFORMANCE",
                "HIGH",
                "Verify the application performs well under normal and high load conditions."
            ))
            
        return suggestions
    
    def _generate_repeated_action_suggestions(self, repeated_actions, action_sequence):
        """Generate suggestions based on repeated action patterns."""
        suggestions = []
        
        if not repeated_actions:
            return suggestions
        
        # General automation suggestion
        suggestions.append(self._create_suggestion(
            "Consider automating repetitive actions",
            "Repeated sequences of actions were detected that could be automated.",
            "AUTOMATION",
            "MEDIUM",
            "These repeated action patterns are good candidates for automated test scripts."
        ))
        
        # Specific suggestions for each repeated pattern
        for i, sequence in enumerate(repeated_actions[:3]):  # Limit to 3 suggestions
            actions_description = ", ".join([
                a.get("actionType", "unknown") for a in sequence.get("actions", [])
            ])
            
            suggestions.append(self._create_suggestion(
                f"Automate repeated action sequence #{i+1}",
                f"The sequence of actions ({actions_description}) repeats multiple times.",
                "AUTOMATION",
                "MEDIUM",
                f"Consider creating an automated test for this specific pattern to save testing time."
            ))
        
        return suggestions
    
    def _generate_user_journey_suggestions(self, journeys, action_sequence):
        """Generate suggestions based on detected user journeys."""
        suggestions = []
        
        if not journeys:
            return suggestions
        
        for journey in journeys:
            workflow_type = journey.get("workflow_type", "unknown")
            
            if workflow_type == "login":
                suggestions.append(self._create_suggestion(
                    "Test login edge cases",
                    "A login workflow was detected. Test various login scenarios.",
                    "SECURITY",
                    "HIGH",
                    "Try invalid credentials, locked accounts, and password reset flows."
                ))
                
                suggestions.append(self._create_suggestion(
                    "Test login security features",
                    "Verify that the login process is secure and follows best practices.",
                    "SECURITY",
                    "HIGH",
                    "Check for account lockout after failed attempts and secure password handling."
                ))
                
            elif workflow_type == "registration":
                suggestions.append(self._create_suggestion(
                    "Test registration validation",
                    "A registration workflow was detected. Test validation thoroughly.",
                    "VALIDATION",
                    "HIGH",
                    "Try registering with existing emails, weak passwords, and missing required fields."
                ))
                
                suggestions.append(self._create_suggestion(
                    "Test email verification flow",
                    "Verify that the email verification process works correctly.",
                    "INTEGRATION",
                    "MEDIUM",
                    "Check the verification email delivery and the account activation process."
                ))
                
            elif workflow_type == "checkout":
                suggestions.append(self._create_suggestion(
                    "Test payment edge cases",
                    "A checkout workflow was detected. Test various payment scenarios.",
                    "PAYMENT",
                    "HIGH",
                    "Try different payment methods, invalid card numbers, and expired cards."
                ))
                
                suggestions.append(self._create_suggestion(
                    "Verify order confirmation details",
                    "Check that the order confirmation shows correct information.",
                    "VALIDATION",
                    "MEDIUM",
                    "Verify that product details, prices, shipping, and taxes are displayed correctly."
                ))
                
            elif workflow_type == "search":
                suggestions.append(self._create_suggestion(
                    "Test search with various queries",
                    "A search workflow was detected. Test search functionality thoroughly.",
                    "FUNCTIONALITY",
                    "MEDIUM",
                    "Try searches with special characters, very long terms, and no results."
                ))
                
                suggestions.append(self._create_suggestion(
                    "Test search filters and sorting",
                    "Verify that search results can be filtered and sorted correctly.",
                    "FUNCTIONALITY",
                    "MEDIUM",
                    "Check that all filter options work and sort orders are applied correctly."
                ))
        
        return suggestions
    
    def _generate_performance_suggestions(self, performance_issues, action_sequence):
        """Generate suggestions based on detected performance issues."""
        suggestions = []
        
        if not performance_issues:
            return suggestions
        
        # General performance suggestion
        suggestions.append(self._create_suggestion(
            "Investigate potential performance issues",
            "Long delays between actions may indicate performance problems.",
            "PERFORMANCE",
            "HIGH",
            "Monitor page load times and responsiveness of the application."
        ))
        
        # Check for specific issues
        long_delays = [issue for issue in performance_issues if issue.get("delay", 0) > 10]
        if long_delays:
            worst_delay = max(long_delays, key=lambda x: x.get("delay", 0))
            suggestions.append(self._create_suggestion(
                "Investigate significant performance lag",
                f"A delay of {worst_delay.get('delay'):.1f} seconds was detected between actions.",
                "PERFORMANCE",
                "HIGH",
                "Check if this page or action is particularly resource-intensive and could be optimized."
            ))
        
        return suggestions
    
    def _generate_general_suggestions(self, action_sequence):
        """Generate general suggestions based on test context."""
        suggestions = []
        
        # Only add general suggestions if we have enough actions
        if action_sequence.get_action_count() < 5:
            return suggestions
            
        # Check for overall test characteristics
        actions = action_sequence.actions
        
        # Check if testing includes forms
        has_forms = any(a.get('actionType') == 'TYPE' for a in actions)
        
        # Check if testing includes multiple pages
        unique_urls = len(set(a.get('url') for a in actions if a.get('url')))
        
        # Responsive design testing
        if unique_urls > 1:
            suggestions.append(self._create_suggestion(
                "Test responsive design across pages",
                "Verify that all visited pages work correctly on different screen sizes.",
                "UX",
                "MEDIUM",
                "Resize the browser window or test on mobile devices to verify responsive behavior."
            ))
        
        # Accessibility testing
        if has_forms:
            suggestions.append(self._create_suggestion(
                "Check form accessibility",
                "Verify that forms are accessible to users with disabilities.",
                "ACCESSIBILITY",
                "MEDIUM",
                "Test keyboard navigation, screen reader compatibility, and proper form labeling."
            ))
        
        # Check if actions include search or filtering
        has_search = any('search' in (a.get('elementSelector') or '').lower() for a in actions)
        if has_search:
            suggestions.append(self._create_suggestion(
                "Test search with edge cases",
                "Verify that search functionality handles edge cases correctly.",
                "EDGE_CASE",
                "MEDIUM",
                "Try searches with no results, special characters, and very long search terms."
            ))
        
        # Check for potential security testing
        has_login = any('login' in (a.get('url') or '').lower() or 
                        'login' in (a.get('pageTitle') or '').lower() for a in actions)
        if has_login:
            suggestions.append(self._create_suggestion(
                "Test session handling and security",
                "Verify that user sessions are managed securely.",
                "SECURITY",
                "HIGH",
                "Test logout functionality, session timeouts, and access to restricted pages after logout."
            ))
        
        return suggestions
    
    def _create_suggestion(self, title, description, suggestion_type, priority, suggested_action=None):
        """Create a TestSuggestion object."""
        return TestSuggestion(
            title=title,
            description=description,
            suggestion_type=suggestion_type,
            priority=priority,
            suggested_action=suggested_action
        )
    
    def process_feedback(self, suggestion_id, status, feedback=None):
        """
        Process feedback on suggestions to improve the model.
        Updates the suggestion effectiveness based on user feedback.
        """
        from datetime import datetime
        
        feedback_data = {
            "suggestion_id": suggestion_id,
            "status": status,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to feedback history
        self.feedback_history.append(feedback_data)
        
        # Update suggestion effectiveness based on feedback
        if self.learning_mode:
            # Extract suggestion type from the ID (assuming format like "TYPE:123")
            suggestion_parts = str(suggestion_id).split(":")
            suggestion_type = suggestion_parts[0] if len(suggestion_parts) > 1 else None
            
            if suggestion_type and suggestion_type in self.suggestion_effectiveness:
                current_effectiveness = self.suggestion_effectiveness[suggestion_type]
                
                # Adjust effectiveness based on status
                if status == "IMPLEMENTED":
                    # Positive feedback - increase effectiveness
                    new_effectiveness = current_effectiveness * 1.05
                    if new_effectiveness > 1.0:
                        new_effectiveness = 1.0
                elif status == "SKIPPED":
                    # Negative feedback - decrease effectiveness
                    new_effectiveness = current_effectiveness * 0.95
                    if new_effectiveness < 0.1:
                        new_effectiveness = 0.1
                else:
                    # Neutral feedback - small adjustment
                    new_effectiveness = current_effectiveness
                
                # Update the effectiveness
                self.suggestion_effectiveness[suggestion_type] = new_effectiveness
                
                logger.info(f"Updated effectiveness for {suggestion_type}: {current_effectiveness} -> {new_effectiveness}")
        
        # Log the feedback
        logger.info(f"Received feedback for suggestion {suggestion_id}: status={status}")
        
        # Return success
        return True