import logging
from typing import List, Dict, Any, Optional, Set
import re
import json
import random
from datetime import datetime

logger = logging.getLogger(__name__)

class TestCaseGenerator:
    """Generates test cases from identified pages and components."""
    
    def __init__(self):
        self.test_case_patterns = {
            "LOGIN": self._generate_login_test_cases,
            "REGISTRATION": self._generate_registration_test_cases,
            "CHECKOUT": self._generate_checkout_test_cases,
            "FORM_VALIDATION": self._generate_form_validation_test_cases,
            "NAVIGATION": self._generate_navigation_test_cases,
            "SEARCH": self._generate_search_test_cases,
            "DATA_DRIVEN": self._generate_data_driven_test_cases
        }
        
        # Common test data patterns
        self.test_data = {
            "email": ["user@example.com", "test.user@domain.co", "invalid-email", "", "very.long.email.address.that.might.exceed.maximum.length.restrictions@example.com"],
            "password": ["Password123!", "short", "12345678", "", "AVeryLongPasswordThatMightExceedMaximumLengthRestrictions1234567890!@#$%^&*()"],
            "text": ["Sample text", "", "Special chars: !@#$%^&*()", "A very long text input that might exceed maximum length restrictions for this field"],
            "number": ["42", "0", "-1", "999999", "abc", ""],
            "phone": ["1234567890", "+1-123-456-7890", "123", ""],
            "name": ["John Smith", "", "John-Smith", "A very long name that might exceed maximum length restrictions"]
        }
    
    def generate_test_cases(self, pages, recorded_actions):
        """Generate test cases from pages and recorded actions."""
        test_cases = []
        
        # Generate page-based test cases
        for page in pages:
            page_type = page.get("pageType", "GENERIC")
            
            # Get generator for this page type
            generator = self.test_case_patterns.get(page_type, self._generate_generic_test_cases)
            
            # Generate test cases for this page
            page_test_cases = generator(page, pages, recorded_actions)
            test_cases.extend(page_test_cases)
        
        # Generate cross-page test cases
        flow_test_cases = self._generate_user_flow_test_cases(pages, recorded_actions)
        test_cases.extend(flow_test_cases)
        
        return test_cases
    
    def _generate_login_test_cases(self, page, all_pages, recorded_actions):
        """Generate test cases for login pages."""
        test_cases = []
        components = page.get("components", [])
        
        # Find username/email field
        username_field = self._find_component_by_type_and_name(components, "input", ["username", "email", "user"])
        
        # Find password field
        password_field = self._find_component_by_type_and_name(components, "input", ["password", "pass"])
        
        # Find login button
        login_button = self._find_component_by_type_and_name(components, "button", ["login", "sign in", "submit"])
        
        if username_field and password_field and login_button:
            # Valid login test case
            test_cases.append({
                "name": "Valid Login Test",
                "description": "Verify that a user can login with valid credentials",
                "preconditions": ["User has a valid account"],
                "steps": [
                    {
                        "action": f"Navigate to {page.get('pageName', 'Login Page')}",
                        "expectedResult": "Login page is displayed",
                        "pageId": page.get("id"),
                        "stepType": "NAVIGATION"
                    },
                    {
                        "action": f"Enter valid username in {username_field.get('name', 'Username Field')}",
                        "expectedResult": "Username is accepted",
                        "componentId": username_field.get("id"),
                        "inputData": "{{valid_username}}",
                        "stepType": "INTERACTION"
                    },
                    {
                        "action": f"Enter valid password in {password_field.get('name', 'Password Field')}",
                        "expectedResult": "Password is accepted",
                        "componentId": password_field.get("id"),
                        "inputData": "{{valid_password}}",
                        "stepType": "INTERACTION"
                    },
                    {
                        "action": f"Click {login_button.get('name', 'Login Button')}",
                        "expectedResult": "User is logged in and redirected to dashboard",
                        "componentId": login_button.get("id"),
                        "stepType": "INTERACTION"
                    }
                ],
                "expectedResult": "User is successfully logged in",
                "category": "Authentication",
                "priority": "HIGH"
            })
            
            # Invalid login test case
            test_cases.append({
                "name": "Invalid Login Test",
                "description": "Verify that a user cannot login with invalid credentials",
                "preconditions": ["User has a registered account"],
                "steps": [
                    {
                        "action": f"Navigate to {page.get('pageName', 'Login Page')}",
                        "expectedResult": "Login page is displayed",
                        "pageId": page.get("id"),
                        "stepType": "NAVIGATION"
                    },
                    {
                        "action": f"Enter invalid username in {username_field.get('name', 'Username Field')}",
                        "expectedResult": "Username is accepted",
                        "componentId": username_field.get("id"),
                        "inputData": "{{invalid_username}}",
                        "stepType": "INTERACTION"
                    },
                    {
                        "action": f"Enter invalid password in {password_field.get('name', 'Password Field')}",
                        "expectedResult": "Password is accepted",
                        "componentId": password_field.get("id"),
                        "inputData": "{{invalid_password}}",
                        "stepType": "INTERACTION"
                    },
                    {
                        "action": f"Click {login_button.get('name', 'Login Button')}",
                        "expectedResult": "Error message is displayed",
                        "componentId": login_button.get("id"),
                        "stepType": "INTERACTION"
                    }
                ],
                "expectedResult": "User is not logged in and an appropriate error message is displayed",
                "category": "Authentication",
                "priority": "HIGH"
            })
            
            # Empty fields validation test case
            test_cases.append({
                "name": "Login Fields Validation Test",
                "description": "Verify that login form properly validates empty fields",
                "preconditions": [],
                "steps": [
                    {
                        "action": f"Navigate to {page.get('pageName', 'Login Page')}",
                        "expectedResult": "Login page is displayed",
                        "pageId": page.get("id"),
                        "stepType": "NAVIGATION"
                    },
                    {
                        "action": f"Leave {username_field.get('name', 'Username Field')} empty",
                        "expectedResult": "No input is entered",
                        "componentId": username_field.get("id"),
                        "inputData": "",
                        "stepType": "INTERACTION"
                    },
                    {
                        "action": f"Leave {password_field.get('name', 'Password Field')} empty",
                        "expectedResult": "No input is entered",
                        "componentId": password_field.get("id"),
                        "inputData": "",
                        "stepType": "INTERACTION"
                    },
                    {
                        "action": f"Click {login_button.get('name', 'Login Button')}",
                        "expectedResult": "Validation error messages are displayed",
                        "componentId": login_button.get("id"),
                        "stepType": "INTERACTION"
                    }
                ],
                "expectedResult": "Form validation prevents empty submission and displays appropriate error messages",
                "category": "Validation",
                "priority": "MEDIUM"
            })
        
        return test_cases
    
    def _generate_registration_test_cases(self, page, all_pages, recorded_actions):
        """Generate test cases for registration pages."""
        test_cases = []
        components = page.get("components", [])
        
        # Find email field
        email_field = self._find_component_by_type_and_name(components, "input", ["email"])
        
        # Find username field (if separate from email)
        username_field = self._find_component_by_type_and_name(components, "input", ["username", "user", "login"])
        
        # Find password fields
        password_field = self._find_component_by_type_and_name(components, "input", ["password", "pass"])
        confirm_password_field = self._find_component_by_type_and_name(components, "input", ["confirm", "verify"])
        
        # Find registration button
        register_button = self._find_component_by_type_and_name(components, "button", ["register", "sign up", "create", "submit"])
        
        # If we found the key components, create test cases
        if (email_field or username_field) and password_field and register_button:
            # Valid registration test case
            steps = [
                {
                    "action": f"Navigate to {page.get('pageName', 'Registration Page')}",
                    "expectedResult": "Registration page is displayed",
                    "pageId": page.get("id"),
                    "stepType": "NAVIGATION"
                }
            ]
            
            if email_field:
                steps.append({
                    "action": f"Enter valid email in {email_field.get('name', 'Email Field')}",
                    "expectedResult": "Email is accepted",
                    "componentId": email_field.get("id"),
                    "inputData": "{{valid_email}}",
                    "stepType": "INTERACTION"
                })
                
            if username_field:
                steps.append({
                    "action": f"Enter valid username in {username_field.get('name', 'Username Field')}",
                    "expectedResult": "Username is accepted",
                    "componentId": username_field.get("id"),
                    "inputData": "{{valid_username}}",
                    "stepType": "INTERACTION"
                })
                
            steps.append({
                "action": f"Enter valid password in {password_field.get('name', 'Password Field')}",
                "expectedResult": "Password is accepted",
                "componentId": password_field.get("id"),
                "inputData": "{{valid_password}}",
                "stepType": "INTERACTION"
            })
                
            if confirm_password_field:
                steps.append({
                    "action": f"Confirm password in {confirm_password_field.get('name', 'Confirm Password Field')}",
                    "expectedResult": "Matching password is accepted",
                    "componentId": confirm_password_field.get("id"),
                    "inputData": "{{valid_password}}",
                    "stepType": "INTERACTION"
                })
                
            steps.append({
                "action": f"Click {register_button.get('name', 'Register Button')}",
                "expectedResult": "Registration is successful",
                "componentId": register_button.get("id"),
                "stepType": "INTERACTION"
            })
            
            test_cases.append({
                "name": "Valid Registration Test",
                "description": "Verify that a user can register with valid information",
                "preconditions": ["User does not have an existing account"],
                "steps": steps,
                "expectedResult": "User account is created successfully",
                "category": "Registration",
                "priority": "HIGH"
            })
            
            # Add validation test case for duplicate email/username
            validation_steps = [
                {
                    "action": f"Navigate to {page.get('pageName', 'Registration Page')}",
                    "expectedResult": "Registration page is displayed",
                    "pageId": page.get("id"),
                    "stepType": "NAVIGATION"
                }
            ]
            
            if email_field:
                validation_steps.append({
                    "action": f"Enter existing email in {email_field.get('name', 'Email Field')}",
                    "expectedResult": "Email is accepted",
                    "componentId": email_field.get("id"),
                    "inputData": "{{existing_email}}",
                    "stepType": "INTERACTION"
                })
                
            if username_field:
                validation_steps.append({
                    "action": f"Enter existing username in {username_field.get('name', 'Username Field')}",
                    "expectedResult": "Username is accepted",
                    "componentId": username_field.get("id"),
                    "inputData": "{{existing_username}}",
                    "stepType": "INTERACTION"
                })
                
            validation_steps.append({
                "action": f"Enter valid password in {password_field.get('name', 'Password Field')}",
                "expectedResult": "Password is accepted",
                "componentId": password_field.get("id"),
                "inputData": "{{valid_password}}",
                "stepType": "INTERACTION"
            })
                
            if confirm_password_field:
                validation_steps.append({
                    "action": f"Confirm password in {confirm_password_field.get('name', 'Confirm Password Field')}",
                    "expectedResult": "Matching password is accepted",
                    "componentId": confirm_password_field.get("id"),
                    "inputData": "{{valid_password}}",
                    "stepType": "INTERACTION"
                })
                
            validation_steps.append({
                "action": f"Click {register_button.get('name', 'Register Button')}",
                "expectedResult": "Error message is displayed",
                "componentId": register_button.get("id"),
                "stepType": "INTERACTION"
            })
            
            test_cases.append({
                "name": "Duplicate Account Validation Test",
                "description": "Verify that the registration form prevents creating duplicate accounts",
                "preconditions": ["An account with the test email/username already exists"],
                "steps": validation_steps,
                "expectedResult": "Registration fails with appropriate error message about duplicate account",
                "category": "Validation",
                "priority": "HIGH"
            })
        
        return test_cases
    
    def _generate_checkout_test_cases(self, page, all_pages, recorded_actions):
        """Generate test cases for checkout pages."""
        test_cases = []
        components = page.get("components", [])
        
        # Find key components for checkout process
        payment_fields = [c for c in components if c.get("componentType") == "input" and 
                          any(term in c.get("name", "").lower() for term in ["card", "credit", "payment", "ccv", "cvv", "expiry"])]
        
        address_fields = [c for c in components if c.get("componentType") == "input" and 
                         any(term in c.get("name", "").lower() for term in ["address", "street", "city", "zip", "postal"])]
        
        # Find submit/place order button
        order_button = self._find_component_by_type_and_name(components, "button", ["place order", "submit", "pay", "checkout", "complete"])
        
        if payment_fields and order_button:
            # Create successful checkout test case
            steps = [
                {
                    "action": f"Navigate to {page.get('pageName', 'Checkout Page')}",
                    "expectedResult": "Checkout page is displayed with items and total",
                    "pageId": page.get("id"),
                    "stepType": "NAVIGATION"
                }
            ]
            
            # Add steps for address fields if present
            for field in address_fields:
                steps.append({
                    "action": f"Enter valid {field.get('name', 'address information')}",
                    "expectedResult": "Information is accepted",
                    "componentId": field.get("id"),
                    "inputData": "{{valid_address_data}}",
                    "stepType": "INTERACTION"
                })
            
            # Add steps for payment fields
            for field in payment_fields:
                steps.append({
                    "action": f"Enter valid {field.get('name', 'payment information')}",
                    "expectedResult": "Information is accepted",
                    "componentId": field.get("id"),
                    "inputData": "{{valid_payment_data}}",
                    "stepType": "INTERACTION"
                })
            
            # Add submit step
            steps.append({
                "action": f"Click {order_button.get('name', 'Place Order Button')}",
                "expectedResult": "Order is processed",
                "componentId": order_button.get("id"),
                "stepType": "INTERACTION"
            })
            
            test_cases.append({
                "name": "Successful Checkout Test",
                "description": "Verify that a user can complete the checkout process",
                "preconditions": ["User has items in their cart", "User is logged in (if required)"],
                "steps": steps,
                "expectedResult": "Order is placed successfully and confirmation is shown",
                "category": "E-commerce",
                "priority": "HIGH"
            })
            
            # Create invalid payment test case
            payment_steps = [
                {
                    "action": f"Navigate to {page.get('pageName', 'Checkout Page')}",
                    "expectedResult": "Checkout page is displayed with items and total",
                    "pageId": page.get("id"),
                    "stepType": "NAVIGATION"
                }
            ]
            
            # Add steps for address fields if present (valid data)
            for field in address_fields:
                payment_steps.append({
                    "action": f"Enter valid {field.get('name', 'address information')}",
                    "expectedResult": "Information is accepted",
                    "componentId": field.get("id"),
                    "inputData": "{{valid_address_data}}",
                    "stepType": "INTERACTION"
                })
            
            # Add steps for payment fields (invalid data)
            payment_field = payment_fields[0]  # Use first payment field for invalid data
            payment_steps.append({
                "action": f"Enter invalid {payment_field.get('name', 'payment information')}",
                "expectedResult": "Information is entered",
                "componentId": payment_field.get("id"),
                "inputData": "{{invalid_payment_data}}",
                "stepType": "INTERACTION"
            })
            
            # Add submit step
            payment_steps.append({
                "action": f"Click {order_button.get('name', 'Place Order Button')}",
                "expectedResult": "Error message is displayed",
                "componentId": order_button.get("id"),
                "stepType": "INTERACTION"
            })
            
            test_cases.append({
                "name": "Invalid Payment Information Test",
                "description": "Verify that checkout process validates payment information",
                "preconditions": ["User has items in their cart", "User is logged in (if required)"],
                "steps": payment_steps,
                "expectedResult": "Order is not placed and appropriate error message is displayed",
                "category": "Validation",
                "priority": "HIGH"
            })
        
        return test_cases
    
    def _generate_form_validation_test_cases(self, page, all_pages, recorded_actions):
        """Generate test cases for form validation."""
        test_cases = []
        components = page.get("components", [])
        
        # Find input fields and their submit button
        input_fields = [c for c in components if c.get("componentType") == "input"]
        select_fields = [c for c in components if c.get("componentType") == "select"]
        required_fields = [c for c in components if c.get("isRequired") == True]
        submit_button = self._find_component_by_type_and_name(components, "button", ["submit", "save", "create", "update"])
        
        if input_fields and submit_button:
            # Create a form field validation test
            steps = [
                {
                    "action": f"Navigate to {page.get('pageName', 'Form Page')}",
                    "expectedResult": "Form is displayed",
                    "pageId": page.get("id"),
                    "stepType": "NAVIGATION"
                }
            ]
            
            # Add steps for required fields (empty input)
            for field in required_fields[:3]:  # Limit to first 3 fields to avoid too many steps
                steps.append({
                    "action": f"Leave {field.get('name', 'Field')} empty",
                    "expectedResult": "No input is entered",
                    "componentId": field.get("id"),
                    "inputData": "",
                    "stepType": "INTERACTION"
                })
            
            # Add submit step
            steps.append({
                "action": f"Click {submit_button.get('name', 'Submit Button')}",
                "expectedResult": "Validation errors are displayed",
                "componentId": submit_button.get("id"),
                "stepType": "INTERACTION"
            })
            
            test_cases.append({
                "name": "Required Fields Validation Test",
                "description": "Verify that the form validates required fields",
                "preconditions": [],
                "steps": steps,
                "expectedResult": "Form submission is prevented and validation errors are displayed for empty required fields",
                "category": "Validation",
                "priority": "MEDIUM"
            })
            
            # Create a field format validation test (if applicable)
            format_fields = [c for c in components if c.get("dataType") in ["email", "phone", "date", "number"]]
            
            if format_fields:
                format_steps = [
                    {
                        "action": f"Navigate to {page.get('pageName', 'Form Page')}",
                        "expectedResult": "Form is displayed",
                        "pageId": page.get("id"),
                        "stepType": "NAVIGATION"
                    }
                ]
                
                # Add steps for format fields (invalid format)
                for field in format_fields[:3]:  # Limit to first 3 fields
                    data_type = field.get("dataType", "text")
                    format_steps.append({
                        "action": f"Enter invalid format in {field.get('name', 'Field')} ({data_type})",
                        "expectedResult": "Invalid input is entered",
                        "componentId": field.get("id"),
                        "inputData": f"{{invalid_{data_type}}}",
                        "stepType": "INTERACTION"
                    })
                
                # Add submit step
                format_steps.append({
                    "action": f"Click {submit_button.get('name', 'Submit Button')}",
                    "expectedResult": "Format validation errors are displayed",
                    "componentId": submit_button.get("id"),
                    "stepType": "INTERACTION"
                })
                
                test_cases.append({
                    "name": "Field Format Validation Test",
                    "description": "Verify that the form validates field formats (email, phone, etc.)",
                    "preconditions": [],
                    "steps": format_steps,
                    "expectedResult": "Form submission is prevented and format validation errors are displayed",
                    "category": "Validation",
                    "priority": "MEDIUM"
                })
        
        return test_cases
    
    def _generate_navigation_test_cases(self, page, all_pages, recorded_actions):
        """Generate test cases for navigation flows."""
        test_cases = []
        
        # If we have multiple pages, create a navigation flow test
        if len(all_pages) >= 2:
            # Create a navigation path through the pages
            steps = []
            for i, p in enumerate(all_pages[:5]):  # Limit to first 5 pages
                steps.append({
                    "action": f"Navigate to {p.get('pageName', f'Page {i+1}')}",
                    "expectedResult": f"{p.get('pageName', f'Page {i+1}')} is displayed correctly",
                    "pageId": p.get("id"),
                    "stepType": "NAVIGATION"
                })
            
            test_cases.append({
                "name": "Basic Navigation Flow Test",
                "description": "Verify that the application navigation flow works correctly",
                "preconditions": [],
                "steps": steps,
                "expectedResult": "All pages in the navigation flow are accessible and display correctly",
                "category": "Navigation",
                "priority": "MEDIUM"
            })
            
            # Create a browser back button test
            if len(all_pages) >= 3:
                back_steps = []
                # Navigate forward through first 3 pages
                for i, p in enumerate(all_pages[:3]):
                    back_steps.append({
                        "action": f"Navigate to {p.get('pageName', f'Page {i+1}')}",
                        "expectedResult": f"{p.get('pageName', f'Page {i+1}')} is displayed correctly",
                        "pageId": p.get("id"),
                        "stepType": "NAVIGATION"
                    })
                
                # Then use browser back button
                back_steps.append({
                    "action": "Click browser back button",
                    "expectedResult": f"{all_pages[1].get('pageName', 'Previous page')} is displayed",
                    "pageId": None,
                    "stepType": "NAVIGATION"
                })
                
                # Then use forward button
                back_steps.append({
                    "action": "Click browser forward button",
                    "expectedResult": f"{all_pages[2].get('pageName', 'Current page')} is displayed",
                    "pageId": None,
                    "stepType": "NAVIGATION"
                })
                
                test_cases.append({
                    "name": "Browser Navigation Button Test",
                    "description": "Verify that browser back and forward buttons work correctly",
                    "preconditions": [],
                    "steps": back_steps,
                    "expectedResult": "Browser navigation buttons work as expected within the application",
                    "category": "Navigation",
                    "priority": "MEDIUM"
                })
        
        return test_cases
    
    def _generate_search_test_cases(self, page, all_pages, recorded_actions):
        """Generate test cases for search functionality."""
        test_cases = []
        components = page.get("components", [])
        
        # Find search field and button
        search_field = self._find_component_by_type_and_name(components, "input", ["search", "query", "find"])
        search_button = self._find_component_by_type_and_name(components, "button", ["search", "find", "go"])
        
        if search_field:
            # Create basic search test
            steps = [
                {
                    "action": f"Navigate to {page.get('pageName', 'Search Page')}",
                    "expectedResult": "Search page is displayed",
                    "pageId": page.get("id"),
                    "stepType": "NAVIGATION"
                },
                {
                    "action": f"Enter search term in {search_field.get('name', 'Search Field')}",
                    "expectedResult": "Search term is entered",
                    "componentId": search_field.get("id"),
                    "inputData": "{{search_term}}",
                    "stepType": "INTERACTION"
                }
            ]
            
            # Add search button click if found, otherwise assume pressing Enter
            if search_button:
                steps.append({
                    "action": f"Click {search_button.get('name', 'Search Button')}",
                    "expectedResult": "Search results are displayed",
                    "componentId": search_button.get("id"),
                    "stepType": "INTERACTION"
                })
            else:
                steps.append({
                    "action": "Press Enter key in search field",
                    "expectedResult": "Search results are displayed",
                    "componentId": search_field.get("id"),
                    "stepType": "INTERACTION"
                })
            
            test_cases.append({
                "name": "Basic Search Functionality Test",
                "description": "Verify that the search functionality works correctly",
                "preconditions": [],
                "steps": steps,
                "expectedResult": "Search results are displayed and relevant to the search term",
                "category": "Search",
                "priority": "HIGH"
            })
            
            # Create no results search test
            no_results_steps = [
                {
                    "action": f"Navigate to {page.get('pageName', 'Search Page')}",
                    "expectedResult": "Search page is displayed",
                    "pageId": page.get("id"),
                    "stepType": "NAVIGATION"
                },
                {
                    "action": f"Enter a search term that will not match any results in {search_field.get('name', 'Search Field')}",
                    "expectedResult": "Search term is entered",
                    "componentId": search_field.get("id"),
                    "inputData": "{{no_results_search_term}}",
                    "stepType": "INTERACTION"
                }
            ]
            
            # Add search button click if found, otherwise assume pressing Enter
            if search_button:
                no_results_steps.append({
                    "action": f"Click {search_button.get('name', 'Search Button')}",
                    "expectedResult": "No results message is displayed",
                    "componentId": search_button.get("id"),
                    "stepType": "INTERACTION"
                })
            else:
                no_results_steps.append({
                    "action": "Press Enter key in search field",
                    "expectedResult": "No results message is displayed",
                    "componentId": search_field.get("id"),
                    "stepType": "INTERACTION"
                })
            
            test_cases.append({
                "name": "No Results Search Test",
                "description": "Verify that the search functionality handles no results correctly",
                "preconditions": [],
                "steps": no_results_steps,
                "expectedResult": "No results message is displayed when search term has no matches",
                "category": "Search",
                "priority": "MEDIUM"
            })
        
        return test_cases
    
    def _generate_data_driven_test_cases(self, page, all_pages, recorded_actions):
        """Generate data-driven test cases."""
        test_cases = []
        components = page.get("components", [])
        
        # Find key input fields
        input_fields = [c for c in components if c.get("componentType") == "input"]
        submit_button = self._find_component_by_type_and_name(components, "button", ["submit", "save", "send", "create"])
        
        if input_fields and submit_button and len(input_fields) >= 2:
            # Create a data-driven test case template
            field_steps = []
            
            # Add steps for each input field
            for field in input_fields[:5]:  # Limit to first 5 fields
                data_type = field.get("dataType", "text")
                placeholder = f"{{{{{data_type}_data}}}}"
                
                field_steps.append({
                    "action": f"Enter data in {field.get('name', 'Field')}",
                    "expectedResult": "Data is entered correctly",
                    "componentId": field.get("id"),
                    "inputData": placeholder,
                    "stepType": "INTERACTION"
                })
            
            # Add submit step
            field_steps.append({
                "action": f"Click {submit_button.get('name', 'Submit Button')}",
                "expectedResult": "Form is submitted",
                "componentId": submit_button.get("id"),
                "stepType": "INTERACTION"
            })
            
            test_cases.append({
                "name": "Data-Driven Form Submission Test",
                "description": "Test form submission with multiple data sets",
                "preconditions": [],
                "steps": field_steps,
                "expectedResult": "Form processes each data set correctly",
                "category": "Data-Driven",
                "priority": "MEDIUM",
                "isDataDriven": True
            })
        
        return test_cases
    
    def _generate_generic_test_cases(self, page, all_pages, recorded_actions):
        """Generate generic test cases for any page type."""
        test_cases = []
        components = page.get("components", [])
        
        # Basic page load test
        test_cases.append({
            "name": f"{page.get('pageName', 'Page')} Load Test",
            "description": f"Verify that {page.get('pageName', 'the page')} loads correctly",
            "preconditions": [],
            "steps": [
                {
                    "action": f"Navigate to {page.get('pageName', 'Page')}",
                    "expectedResult": f"{page.get('pageName', 'Page')} is displayed correctly with all elements",
                    "pageId": page.get("id"),
                    "stepType": "NAVIGATION"
                }
            ],
            "expectedResult": "Page loads with all components displayed correctly",
            "category": "UI",
            "priority": "MEDIUM"
        })
        
        # Component interaction test
        interactive_components = [c for c in components if c.get("componentType") in ["button", "input", "select", "checkbox", "radio"]]
        
        if interactive_components:
            steps = [
                {
                    "action": f"Navigate to {page.get('pageName', 'Page')}",
                    "expectedResult": f"{page.get('pageName', 'Page')} is displayed",
                    "pageId": page.get("id"),
                    "stepType": "NAVIGATION"
                }
            ]
            
            # Add interaction steps for key components
            for component in interactive_components[:5]:  # Limit to first 5 components
                component_type = component.get("componentType")
                
                if component_type == "button":
                    steps.append({
                        "action": f"Click {component.get('name', 'Button')}",
                        "expectedResult": "Action is performed",
                        "componentId": component.get("id"),
                        "stepType": "INTERACTION"
                    })
                elif component_type == "input":
                    data_type = component.get("dataType", "text")
                    steps.append({
                        "action": f"Enter data in {component.get('name', 'Field')}",
                        "expectedResult": "Data is entered correctly",
                        "componentId": component.get("id"),
                        "inputData": f"{{{{{data_type}_data}}}}",
                        "stepType": "INTERACTION"
                    })
                elif component_type == "select":
                    steps.append({
                        "action": f"Select an option from {component.get('name', 'Dropdown')}",
                        "expectedResult": "Option is selected",
                        "componentId": component.get("id"),
                        "inputData": "{{select_option}}",
                        "stepType": "INTERACTION"
                    })
                elif component_type in ["checkbox", "radio"]:
                    steps.append({
                        "action": f"Toggle {component.get('name', 'Option')}",
                        "expectedResult": "Option state is changed",
                        "componentId": component.get("id"),
                        "stepType": "INTERACTION"
                    })
            
            test_cases.append({
                "name": f"{page.get('pageName', 'Page')} Component Interaction Test",
                "description": f"Verify interactions with components on {page.get('pageName', 'the page')}",
                "preconditions": [],
                "steps": steps,
                "expectedResult": "All component interactions work as expected",
                "category": "Interaction",
                "priority": "MEDIUM"
            })
        
        return test_cases
    
    def _generate_user_flow_test_cases(self, pages, recorded_actions):
        """Generate test cases for user flows across multiple pages."""
        test_cases = []
        
        if len(pages) < 2:
            return test_cases
            
        # Try to identify common user flows based on page types
        
        # Login → Dashboard flow
        login_page = next((p for p in pages if p.get("pageType") == "LOGIN"), None)
        dashboard_page = next((p for p in pages if p.get("pageType") == "DASHBOARD"), None)
        
        if login_page and dashboard_page:
            # Find login components
            login_components = login_page.get("components", [])
            username_field = self._find_component_by_type_and_name(login_components, "input", ["username", "email", "user"])
            password_field = self._find_component_by_type_and_name(login_components, "input", ["password", "pass"])
            login_button = self._find_component_by_type_and_name(login_components, "button", ["login", "sign in", "submit"])
            
            if username_field and password_field and login_button:
                steps = [
                    {
                        "action": f"Navigate to {login_page.get('pageName', 'Login Page')}",
                        "expectedResult": "Login page is displayed",
                        "pageId": login_page.get("id"),
                        "stepType": "NAVIGATION"
                    },
                    {
                        "action": f"Enter valid username in {username_field.get('name', 'Username Field')}",
                        "expectedResult": "Username is accepted",
                        "componentId": username_field.get("id"),
                        "inputData": "{{valid_username}}",
                        "stepType": "INTERACTION"
                    },
                    {
                        "action": f"Enter valid password in {password_field.get('name', 'Password Field')}",
                        "expectedResult": "Password is accepted",
                        "componentId": password_field.get("id"),
                        "inputData": "{{valid_password}}",
                        "stepType": "INTERACTION"
                    },
                    {
                        "action": f"Click {login_button.get('name', 'Login Button')}",
                        "expectedResult": "User is logged in",
                        "componentId": login_button.get("id"),
                        "stepType": "INTERACTION"
                    },
                    {
                        "action": "Verify dashboard elements",
                        "expectedResult": f"{dashboard_page.get('pageName', 'Dashboard')} is displayed with user information",
                        "pageId": dashboard_page.get("id"),
                        "stepType": "VALIDATION"
                    }
                ]
                
                test_cases.append({
                    "name": "Login to Dashboard Flow Test",
                    "description": "Verify the complete user flow from login to dashboard",
                    "preconditions": ["User has a valid account"],
                    "steps": steps,
                    "expectedResult": "User can successfully log in and access the dashboard",
                    "category": "User Flow",
                    "priority": "HIGH"
                })
        
        # Registration → Confirmation flow
        registration_page = next((p for p in pages if p.get("pageType") == "REGISTRATION"), None)
        confirmation_page = next((p for p in pages if p.get("pageType") == "CONFIRMATION"), None)
        
        if registration_page and confirmation_page:
            # Create a test case for the registration flow
            reg_components = registration_page.get("components", [])
            email_field = self._find_component_by_type_and_name(reg_components, "input", ["email"])
            password_field = self._find_component_by_type_and_name(reg_components, "input", ["password", "pass"])
            register_button = self._find_component_by_type_and_name(reg_components, "button", ["register", "sign up", "create", "submit"])
            
            if email_field and password_field and register_button:
                steps = [
                    {
                        "action": f"Navigate to {registration_page.get('pageName', 'Registration Page')}",
                        "expectedResult": "Registration page is displayed",
                        "pageId": registration_page.get("id"),
                        "stepType": "NAVIGATION"
                    },
                    {
                        "action": f"Enter valid email in {email_field.get('name', 'Email Field')}",
                        "expectedResult": "Email is accepted",
                        "componentId": email_field.get("id"),
                        "inputData": "{{valid_email}}",
                        "stepType": "INTERACTION"
                    },
                    {
                        "action": f"Enter valid password in {password_field.get('name', 'Password Field')}",
                        "expectedResult": "Password is accepted",
                        "componentId": password_field.get("id"),
                        "inputData": "{{valid_password}}",
                        "stepType": "INTERACTION"
                    },
                    {
                        "action": f"Click {register_button.get('name', 'Register Button')}",
                        "expectedResult": "Registration is processed",
                        "componentId": register_button.get("id"),
                        "stepType": "INTERACTION"
                    },
                    {
                        "action": "Verify confirmation elements",
                        "expectedResult": f"{confirmation_page.get('pageName', 'Confirmation Page')} is displayed with success message",
                        "pageId": confirmation_page.get("id"),
                        "stepType": "VALIDATION"
                    }
                ]
                
                test_cases.append({
                    "name": "Registration to Confirmation Flow Test",
                    "description": "Verify the complete user flow from registration to confirmation",
                    "preconditions": ["User does not have an existing account"],
                    "steps": steps,
                    "expectedResult": "User can successfully register and receive confirmation",
                    "category": "User Flow",
                    "priority": "HIGH"
                })
        
        # Generic E2E test if we have 3+ pages
        if len(pages) >= 3:
            steps = []
            for i, page in enumerate(pages[:5]):  # Limit to first 5 pages
                # Add navigation step
                steps.append({
                    "action": f"Navigate to {page.get('pageName', f'Page {i+1}')}",
                    "expectedResult": f"{page.get('pageName', f'Page {i+1}')} is displayed correctly",
                    "pageId": page.get("id"),
                    "stepType": "NAVIGATION"
                })
                
                # Add interaction with a key component if available
                components = page.get("components", [])
                key_component = None
                
                # Try to find a button first
                button = self._find_component_by_type_and_name(components, "button", ["submit", "continue", "next", "save"])
                if button:
                    key_component = button
                # If no button, try to find an input field
                elif not key_component:
                    input_field = next((c for c in components if c.get("componentType") == "input"), None)
                    if input_field:
                        key_component = input_field
                
                if key_component:
                    comp_type = key_component.get("componentType")
                    if comp_type == "button":
                        steps.append({
                            "action": f"Click {key_component.get('name', 'Button')}",
                            "expectedResult": "Action is performed",
                            "componentId": key_component.get("id"),
                            "stepType": "INTERACTION"
                        })
                    elif comp_type == "input":
                        data_type = key_component.get("dataType", "text")
                        steps.append({
                            "action": f"Enter data in {key_component.get('name', 'Field')}",
                            "expectedResult": "Data is entered correctly",
                            "componentId": key_component.get("id"),
                            "inputData": f"{{{{{data_type}_data}}}}",
                            "stepType": "INTERACTION"
                        })
            
            if steps:
                test_cases.append({
                    "name": "End-to-End User Flow Test",
                    "description": "Verify the complete end-to-end user flow through the application",
                    "preconditions": [],
                    "steps": steps,
                    "expectedResult": "User can navigate through the entire flow successfully",
                    "category": "User Flow",
                    "priority": "HIGH"
                })
        
        return test_cases
    
    def _find_component_by_type_and_name(self, components, component_type, name_keywords):
        """
        Find a component by its type and name keywords.
        
        Args:
            components: List of components to search
            component_type: Type of component to find (e.g., "input", "button")
            name_keywords: List of keywords to search for in the component name
            
        Returns:
            Matching component or None if not found
        """
        # First try to find an exact match with both type and name
        for component in components:
            if component.get("componentType") == component_type:
                component_name = component.get("name", "").lower()
                if any(keyword.lower() in component_name for keyword in name_keywords):
                    return component
        
        # If no exact match, try just matching the component type
        for component in components:
            if component.get("componentType") == component_type:
                return component
        
        return None