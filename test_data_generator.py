import random
import string
import datetime
import json
import re
import logging
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class TestDataGenerator:
    """
    Enhanced test data generator for the AI-Driven Testing Assistant.
    Generates various types of test data for different testing scenarios.
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
        
        # Sample test data for specific types
        self.sample_data = {
            'first_names': ['John', 'Jane', 'Michael', 'Emma', 'David', 'Sophia', 'William', 'Olivia'],
            'last_names': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Garcia'],
            'domains': ['example.com', 'test.com', 'company.org', 'mail.com', 'domain.co.uk'],
            'countries': ['United States', 'Canada', 'United Kingdom', 'Germany', 'France', 'Australia', 'Japan', 'Brazil'],
            'currencies': ['USD', 'EUR', 'GBP', 'CAD', 'JPY', 'AUD', 'CNY', 'BRL'],
            'products': ['Laptop', 'Smartphone', 'Headphones', 'Tablet', 'Monitor', 'Keyboard', 'Mouse', 'Camera'],
            'credit_card_types': ['Visa', 'MasterCard', 'American Express', 'Discover'],
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
            ]
        }
        
        # Credit card test numbers (these are standard test numbers, not real cards)
        self.test_credit_cards = {
            'visa': '4111111111111111',
            'mastercard': '5555555555554444',
            'amex': '378282246310005',
            'discover': '6011111111111117'
        }
    
    def generate_form_data(self, form_fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate multiple sets of test data for a form.
        
        Args:
            form_fields: List of form field definitions with name, type, etc.
            
        Returns:
            List of test data sets for the form
        """
        logger.info(f"Generating form test data for {len(form_fields)} form fields")
        test_data_sets = []
        
        # Generate different sets of test data
        logger.debug("Generating valid data set...")
        valid_data = self._generate_valid_data(form_fields)
        test_data_sets.append(valid_data)
        logger.debug(f"Generated valid data: {len(valid_data)} fields")
        
        logger.debug("Generating boundary data set...")
        boundary_data = self._generate_boundary_data(form_fields)
        test_data_sets.append(boundary_data)
        logger.debug(f"Generated boundary data: {len(boundary_data)} fields")
        
        logger.debug("Generating invalid data set...")
        invalid_data = self._generate_invalid_data(form_fields)
        test_data_sets.append(invalid_data)
        logger.debug(f"Generated invalid data: {len(invalid_data)} fields")
        
        logger.debug("Generating special character data set...")
        special_char_data = self._generate_special_char_data(form_fields)
        test_data_sets.append(special_char_data)
        logger.debug(f"Generated special character data: {len(special_char_data)} fields")
        
        logger.debug("Generating empty data set...")
        empty_data = self._generate_empty_data(form_fields)
        test_data_sets.append(empty_data)
        logger.debug(f"Generated empty data: {len(empty_data)} fields")
        
        logger.debug("Generating international data set...")
        international_data = self._generate_international_data(form_fields)
        test_data_sets.append(international_data)
        logger.debug(f"Generated international data: {len(international_data)} fields")
        
        logger.info(f"Generated {len(test_data_sets)} test data sets for form with {len(form_fields)} fields")
        return test_data_sets
    
    def generate_test_scenario(self, scenario_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a complete test scenario based on the scenario type.
        
        Args:
            scenario_type: Type of scenario to generate (e.g., 'checkout', 'registration')
            context: Additional context for scenario generation
            
        Returns:
            Complete test scenario with all necessary data
        """
        logger.info(f"Generating test scenario: {scenario_type}")
        if context:
            logger.debug(f"Context provided: {list(context.keys())}")
        
        try:
            if scenario_type == 'checkout':
                scenario = self._generate_checkout_scenario(context)
            elif scenario_type == 'registration':
                scenario = self._generate_registration_scenario(context)
            elif scenario_type == 'login':
                scenario = self._generate_login_scenario(context)
            elif scenario_type == 'payment':
                scenario = self._generate_payment_scenario(context)
            elif scenario_type == 'search':
                scenario = self._generate_search_scenario(context)
            else:
                # Default to a generic scenario
                logger.debug(f"Using generic scenario generator for type: {scenario_type}")
                scenario = self._generate_generic_scenario(scenario_type, context)
            
            scenario_name = scenario.get('name', 'Unnamed')
            steps_count = len(scenario.get('steps', []))
            logger.info(f"Generated test scenario: {scenario_name} with {steps_count} steps")
            return scenario
        except Exception as e:
            logger.error(f"Error generating test scenario {scenario_type}: {str(e)}", exc_info=True)
            raise
    
    def generate_test_script(self, scenario: Dict[str, Any]) -> str:
        """
        Generate a test script based on a scenario.
        
        Args:
            scenario: The test scenario to convert to a script
            
        Returns:
            A formatted test script as a string
        """
        scenario_name = scenario.get('name', 'Untitled Test')
        logger.info(f"Generating test script for scenario: {scenario_name}")
        steps_count = len(scenario.get('steps', []))
        logger.debug(f"Scenario has {steps_count} steps")
        
        script = f"# Test Script: {scenario_name}\n\n"
        
        # Add description
        if 'description' in scenario:
            script += f"## Description\n{scenario['description']}\n\n"
        
        # Add preconditions
        if 'preconditions' in scenario:
            script += "## Preconditions\n"
            for idx, precondition in enumerate(scenario['preconditions'], 1):
                script += f"{idx}. {precondition}\n"
            script += "\n"
        
        # Add test steps
        if 'steps' in scenario:
            script += "## Test Steps\n"
            for idx, step in enumerate(scenario['steps'], 1):
                script += f"{idx}. {step['action']}\n"
                if 'expected' in step:
                    script += f"   - Expected: {step['expected']}\n"
                if 'data' in step:
                    script += f"   - Data: {json.dumps(step['data'], indent=3).replace('\\n', '\n')}\n"
            script += "\n"
        
        # Add expected results
        if 'expected_results' in scenario:
            script += "## Expected Results\n"
            for idx, result in enumerate(scenario['expected_results'], 1):
                script += f"{idx}. {result}\n"
            script += "\n"
        
        script_lines = len(script.split('\n'))
        logger.info(f"Generated test script: {script_lines} lines for scenario: {scenario_name}")
        return script
    
    def _generate_valid_data(self, form_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a set of valid data for the form fields."""
        data = {}
        for field in form_fields:
            field_type = self._infer_field_type(field)
            field_name = field.get("name", "")
            required = field.get("required", True)
            
            # Skip optional fields randomly to test partial form submissions
            if not required and random.random() < 0.3:
                continue
                
            data[field_name] = self._generate_valid_value(field_type, field_name)
        
        return {
            "name": "Valid Data",
            "description": "A set of valid values for all required form fields",
            "data": data
        }
    
    def _generate_boundary_data(self, form_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate boundary test data for the form fields."""
        data = {}
        for field in form_fields:
            field_type = self._infer_field_type(field)
            field_name = field.get("name", "")
            
            # Only generate boundary values for fields that have meaningful boundaries
            if field_type in ["text", "textarea", "email", "password", "number", "date"]:
                data[field_name] = self._generate_boundary_value(field_type, field_name)
            else:
                # Use valid values for fields without clear boundaries
                data[field_name] = self._generate_valid_value(field_type, field_name)
        
        return {
            "name": "Boundary Values",
            "description": "Values at or near the boundaries of what is valid",
            "data": data
        }
    
    def _generate_invalid_data(self, form_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate invalid test data for the form fields."""
        data = {}
        for field in form_fields:
            field_type = self._infer_field_type(field)
            field_name = field.get("name", "")
            required = field.get("required", True)
            
            # Only generate invalid values for required fields to avoid false positives
            if required:
                data[field_name] = self._generate_invalid_value(field_type, field_name)
            else:
                # Use empty string for optional fields
                data[field_name] = ""
        
        return {
            "name": "Invalid Data",
            "description": "Values that should be rejected by validation",
            "data": data
        }
    
    def _generate_special_char_data(self, form_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate test data with special characters."""
        data = {}
        special_chars = "<>&\"'\/\\\t\n"
        
        for field in form_fields:
            field_type = self._infer_field_type(field)
            field_name = field.get("name", "")
            
            # For text fields, add special characters
            if field_type in ["text", "textarea", "email", "password"]:
                base_value = self._generate_valid_value(field_type, field_name)
                if isinstance(base_value, str):
                    data[field_name] = f"{base_value}{special_chars}"
                else:
                    data[field_name] = base_value
            else:
                # For other fields, use valid values
                data[field_name] = self._generate_valid_value(field_type, field_name)
        
        return {
            "name": "Special Characters",
            "description": "Text values with potentially problematic special characters",
            "data": data
        }
    
    def _generate_empty_data(self, form_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate empty or null values for testing required field validation."""
        data = {}
        
        for field in form_fields:
            field_name = field.get("name", "")
            # Set empty string for all fields
            data[field_name] = ""
        
        return {
            "name": "Empty Values",
            "description": "Empty values to test required field validation",
            "data": data
        }
    
    def _generate_international_data(self, form_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate test data with international characters and formats."""
        data = {}
        
        for field in form_fields:
            field_type = self._infer_field_type(field)
            field_name = field.get("name", "")
            
            # Generate international values based on field type
            if field_type == "text" or field_type == "textarea":
                # Use some non-Latin characters
                data[field_name] = "国际测试 Интернациональный 국제적인"
            elif field_type == "email":
                # International domain email
                data[field_name] = f"user@例子.测试"
            elif field_type == "address":
                data[field_name] = "123 国际街, 北京, 中国"
            elif field_type == "name":
                data[field_name] = "张伟"
            elif field_type == "phone":
                # International phone format
                data[field_name] = "+86 123 4567 8901"
            elif field_type == "currency":
                data[field_name] = "¥"
            else:
                # Use valid values for other fields
                data[field_name] = self._generate_valid_value(field_type, field_name)
        
        return {
            "name": "International Data",
            "description": "Values with international characters and formats",
            "data": data
        }
    
    def _infer_field_type(self, field: Dict[str, Any]) -> str:
        """
        Infer the type of a form field based on its properties.
        
        Args:
            field: Field definition with properties
            
        Returns:
            Inferred field type
        """
        # If explicit type is provided
        if "type" in field:
            return field["type"]
        
        # Infer from name
        name = field.get("name", "").lower()
        
        # Common field name patterns
        patterns = {
            'email': ['email', 'e-mail', 'mail'],
            'password': ['password', 'pwd', 'pass'],
            'date': ['date', 'birthday', 'dob', 'born'],
            'time': ['time', 'hour'],
            'phone': ['phone', 'mobile', 'cell', 'tel'],
            'number': ['number', 'amount', 'price', 'quantity', 'qty', 'age', 'count'],
            'url': ['url', 'website', 'site', 'link', 'web'],
            'textarea': ['textarea', 'description', 'message', 'comment', 'bio', 'notes'],
            'checkbox': ['checkbox', 'check', 'agree', 'terms', 'subscribe'],
            'radio': ['radio', 'option', 'select-one'],
            'select': ['select', 'dropdown', 'country', 'state', 'reason'],
            'name': ['name', 'firstname', 'lastname', 'fullname'],
            'address': ['address', 'street', 'city', 'state', 'country', 'zip', 'postal'],
            'card': ['card', 'credit', 'debit', 'payment'],
            'file': ['file', 'upload', 'photo', 'picture', 'image', 'document'],
            'search': ['search', 'query', 'find', 'lookup']
        }
        
        # Check if the field name matches any pattern
        for field_type, keywords in patterns.items():
            if any(keyword in name for keyword in keywords):
                return field_type
        
        # Check for custom attributes
        if field.get("max") is not None or field.get("min") is not None:
            return "number"
        
        if field.get("maxlength") is not None:
            return "text"
        
        if field.get("options") is not None:
            return "select"
        
        # Default to text
        return "text"
    
    def _generate_valid_value(self, field_type: str, field_name: str = "") -> Union[str, int, bool]:
        """
        Generate a valid value for the given field type.
        
        Args:
            field_type: Type of field to generate data for
            field_name: Name of the field (optional, for context)
            
        Returns:
            A valid value for the field
        """
        # Handle common field types
        if field_type == "email":
            return f"{random.choice(['user', 'test', 'info', 'contact'])}{random.randint(1, 9999)}@{random.choice(self.sample_data['domains'])}"
            
        elif field_type == "password":
            # Create a reasonably secure password
            lowercase = ''.join(random.choices(string.ascii_lowercase, k=5))
            uppercase = ''.join(random.choices(string.ascii_uppercase, k=2))
            digits = ''.join(random.choices(string.digits, k=3))
            special = ''.join(random.choices('!@#$%^&*', k=1))
            password = lowercase + uppercase + digits + special
            # Shuffle the password
            password_list = list(password)
            random.shuffle(password_list)
            return ''.join(password_list)
            
        elif field_type == "date":
            # Generate a random date within the last 50 years
            days = random.randint(0, 365 * 50)
            date = datetime.date.today() - datetime.timedelta(days=days)
            return date.strftime("%Y-%m-%d")
            
        elif field_type == "time":
            return f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}"
            
        elif field_type == "phone":
            return f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"
            
        elif field_type == "number":
            # Check field name for context
            if "age" in field_name.lower():
                return random.randint(18, 80)
            elif "quantity" in field_name.lower() or "qty" in field_name.lower():
                return random.randint(1, 10)
            elif "price" in field_name.lower() or "amount" in field_name.lower():
                return round(random.uniform(10, 1000), 2)
            else:
                return random.randint(1, 1000)
                
        elif field_type == "url":
            domain = random.choice(self.sample_data['domains'])
            path = ''.join(random.choices(string.ascii_lowercase, k=8))
            return f"https://www.{domain}/{path}"
            
        elif field_type == "textarea":
            sentences = [
                "This is a sample text for the textarea field.",
                "It contains multiple sentences to simulate user input.",
                "The content is designed to test how the application handles multi-line text.",
                "This should provide good test coverage for textarea fields."
            ]
            # Use 1-4 sentences
            count = random.randint(1, 4)
            return ' '.join(sentences[:count])
            
        elif field_type == "checkbox":
            return random.choice([True, False])
            
        elif field_type == "radio" or field_type == "select":
            # Without specific options, return a generic option
            return f"option{random.randint(1, 5)}"
            
        elif field_type == "name":
            if "first" in field_name.lower():
                return random.choice(self.sample_data['first_names'])
            elif "last" in field_name.lower():
                return random.choice(self.sample_data['last_names'])
            else:
                first = random.choice(self.sample_data['first_names'])
                last = random.choice(self.sample_data['last_names'])
                return f"{first} {last}"
                
        elif field_type == "address":
            if "street" in field_name.lower() or "address" in field_name.lower():
                return f"{random.randint(1, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Park', 'Washington'])} {random.choice(['St', 'Ave', 'Blvd', 'Rd'])}"
            elif "city" in field_name.lower():
                return random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'San Diego', 'Dallas', 'San Francisco'])
            elif "state" in field_name.lower():
                return random.choice(['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'MI', 'GA', 'NC'])
            elif "zip" in field_name.lower() or "postal" in field_name.lower():
                return f"{random.randint(10000, 99999)}"
            elif "country" in field_name.lower():
                return random.choice(self.sample_data['countries'])
            else:
                # Generic address
                return f"{random.randint(1, 9999)} Main St, Anytown, US 12345"
                
        elif field_type == "card":
            if "number" in field_name.lower() or "card" in field_name.lower():
                return random.choice(list(self.test_credit_cards.values()))
            elif "cvv" in field_name.lower() or "cvc" in field_name.lower():
                return f"{random.randint(100, 999)}"
            elif "expiry" in field_name.lower() or "expiration" in field_name.lower():
                # Generate a future date within 5 years
                month = random.randint(1, 12)
                year = datetime.date.today().year + random.randint(1, 5)
                return f"{month:02d}/{year % 100:02d}"
            else:
                return random.choice(list(self.test_credit_cards.values()))
                
        elif field_type == "file":
            # Return file name only
            extensions = ['.jpg', '.png', '.pdf', '.doc', '.txt']
            return f"test_file{random.randint(1, 100)}{random.choice(extensions)}"
            
        elif field_type == "search":
            # Common search terms
            search_terms = [
                self.sample_data['products'],
                ['blue', 'red', 'green', 'black', 'white'],
                ['small', 'medium', 'large', 'extra large'],
                ['cheap', 'expensive', 'budget', 'premium']
            ]
            # Choose a category and a term
            category = random.choice(search_terms)
            return random.choice(category)
            
        elif field_type == "currency":
            return random.choice(self.sample_data['currencies'])
            
        else:  # Default to text
            # Generate a random string
            return ''.join(random.choices(string.ascii_letters + ' ', k=random.randint(5, 15)))
    
    def _generate_boundary_value(self, field_type: str, field_name: str = "") -> Union[str, int]:
        """Generate a boundary value for the given field type."""
        if field_type == "email":
            # Very long local part
            local_part = ''.join(random.choices(string.ascii_lowercase, k=64))
            return f"{local_part}@example.com"
            
        elif field_type == "password":
            # Minimum length password (usually 8 chars)
            return "Aa1!aaaa"
            
        elif field_type == "date":
            # Edge dates
            edge_dates = [
                datetime.date(2000, 2, 29).strftime("%Y-%m-%d"),  # Leap year
                datetime.date(9999, 12, 31).strftime("%Y-%m-%d"),  # Far future
                datetime.date(1900, 1, 1).strftime("%Y-%m-%d"),  # Far past
                datetime.date(2038, 1, 19).strftime("%Y-%m-%d")   # Unix timestamp limit
            ]
            return random.choice(edge_dates)
            
        elif field_type == "time":
            # Edge times
            edge_times = ["00:00", "23:59", "12:00"]
            return random.choice(edge_times)
            
        elif field_type == "phone":
            # Boundary cases for phone numbers
            phone_boundaries = [
                "+1" + "0" * 10,  # All zeros
                "+1" + "9" * 10,  # All nines
                "+12015550123",   # US test number format
                "+" + "9" * 15    # Maximum length
            ]
            return random.choice(phone_boundaries)
            
        elif field_type == "number":
            # Boundary numbers based on context
            if "age" in field_name.lower():
                return random.choice([0, 1, 17, 18, 65, 120])
            elif "quantity" in field_name.lower() or "qty" in field_name.lower():
                return random.choice([0, 1, 99, 100, 999, 1000])
            else:
                # General boundaries
                return random.choice([0, 1, -1, 999999999, -999999999])
                
        elif field_type == "url":
            # Long URL or unusual formats
            boundaries = [
                "https://example.com/" + "a" * 255,
                "https://subdomain.very-long-domain-name-to-test-boundary-conditions.co.uk/path/to/some/resource?param1=value1&param2=value2",
                "https://example.com:8080",
                "https://xn--bcher-kva.example.com"  # Internationalized domain
            ]
            return random.choice(boundaries)
            
        elif field_type == "textarea":
            # Very long text (most forms limit to 65535 chars)
            # Generate a smaller but still large sample (2000 chars)
            return ''.join(random.choices(string.ascii_letters + ' ', k=2000))
            
        elif field_type == "name":
            # Very long or very short names
            boundaries = [
                "A",
                "AB",
                "A-B",
                "O'Neil",
                "Mary-Jane Smith-Johnson",
                "Juan Carlos Fernández-Martínez de la Cruz"
            ]
            return random.choice(boundaries)
            
        elif field_type == "address":
            # Address boundary cases
            if "zip" in field_name.lower():
                return random.choice(["00000", "99999", "12345-6789"])
            else:
                return "123456789012345678901234567890 REALLY LONG STREET NAME THAT MIGHT CAUSE ISSUES IN SOME SYSTEMS AVE APT 42424242 FLOOR 99999"
                
        else:
            # Default to a long string for text fields
            return ''.join(random.choices(string.ascii_letters, k=255))
    
    def _generate_invalid_value(self, field_type: str, field_name: str = "") -> str:
        """Generate an invalid value for the given field type."""
        if field_type == "email":
            # Invalid email formats
            invalid_emails = [
                "not_an_email",
                "missing@domain",
                "@missing.prefix",
                "double@@at.com",
                "spaces in@email.com",
                "special#chars@invalid.com"
            ]
            return random.choice(invalid_emails)
            
        elif field_type == "password":
            # Too short or missing required elements
            return "pass"
            
        elif field_type == "date":
            # Invalid date formats
            invalid_dates = [
                "not-a-date",
                "2023/13/32",
                "32/13/2023",
                "31-02-2023",
                "2023-02-30"
            ]
            return random.choice(invalid_dates)
            
        elif field_type == "time":
            # Invalid time formats
            return random.choice(["25:00", "12:60", "not-a-time"])
            
        elif field_type == "phone":
            # Invalid phone formats
            return random.choice(["not-a-phone", "123", "+1abc4567890", "+1 (800) letters"])
            
        elif field_type == "number":
            # Invalid number formats
            if "price" in field_name.lower() or "amount" in field_name.lower():
                return random.choice(["0", "-1", "not-a-number", "$100"])
            else:
                return "not-a-number"
                
        elif field_type == "url":
            # Invalid URL formats
            return random.choice(["not-a-url", "http:/missing-slash", "https://no-tld", "www.just-subdomain"])
            
        elif field_type == "card":
            # Invalid card formats
            if "number" in field_name.lower():
                return random.choice(["1234123412341234", "not-a-card-number", "1234 5678 9012"])
            elif "cvv" in field_name.lower():
                return random.choice(["12", "1", "12345", "abc"])
            else:
                return "invalid-card-data"
                
        else:
            # For other types, an empty string might be invalid
            return ""
    
    def _generate_checkout_scenario(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a complete checkout test scenario."""
        if context is None:
            context = {}
            
        # Basic customer info
        first_name = random.choice(self.sample_data['first_names'])
        last_name = random.choice(self.sample_data['last_names'])
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(self.sample_data['domains'])}"
        
        # Product selection
        products = context.get('products', self.sample_data['products'])
        selected_products = random.sample(products, min(random.randint(1, 3), len(products)))
        
        # Payment method
        payment_methods = context.get('payment_methods', ['Credit Card', 'PayPal', 'Apple Pay'])
        payment_method = random.choice(payment_methods)
        
        # Create scenario
        scenario = {
            "name": "E-Commerce Checkout Flow",
            "description": "Test the complete checkout process from cart to order confirmation.",
            "preconditions": [
                "User is logged in",
                "Shopping cart contains items"
            ],
            "steps": [
                {
                    "action": "Navigate to shopping cart",
                    "expected": "Cart page displays with correct items"
                },
                {
                    "action": "Click 'Proceed to Checkout' button",
                    "expected": "Checkout form is displayed"
                },
                {
                    "action": "Enter shipping information",
                    "expected": "Form accepts valid shipping details",
                    "data": {
                        "firstName": first_name,
                        "lastName": last_name,
                        "email": email,
                        "address": f"{random.randint(100, 999)} Main St",
                        "city": "Anytown",
                        "state": "CA",
                        "zipCode": f"{random.randint(10000, 99999)}",
                        "country": "United States"
                    }
                },
                {
                    "action": "Select shipping method",
                    "expected": "Shipping options are displayed with correct prices",
                    "data": {
                        "shippingMethod": random.choice(["Standard", "Express", "Overnight"])
                    }
                },
                {
                    "action": f"Select payment method: {payment_method}",
                    "expected": f"{payment_method} payment form is displayed"
                }
            ],
            "expected_results": [
                "Order is successfully placed",
                "Order confirmation page displays with correct order details",
                "Confirmation email is sent to the customer"
            ]
        }
        
        # Add payment-specific steps
        if payment_method == "Credit Card":
            cc_type = random.choice(list(self.test_credit_cards.keys()))
            cc_number = self.test_credit_cards[cc_type]
            
            payment_step = {
                "action": "Enter credit card details",
                "expected": "Payment form validates the card details",
                "data": {
                    "cardType": cc_type.capitalize(),
                    "cardNumber": cc_number,
                    "expiryDate": f"{random.randint(1, 12):02d}/{datetime.date.today().year + random.randint(1, 5) % 100:02d}",
                    "cvv": f"{random.randint(100, 999)}"
                }
            }
            scenario["steps"].append(payment_step)
        elif payment_method == "PayPal":
            payment_step = {
                "action": "Click 'Pay with PayPal' button",
                "expected": "User is redirected to PayPal login page"
            }
            scenario["steps"].append(payment_step)
            
            login_step = {
                "action": "Log in to PayPal account",
                "expected": "PayPal payment confirmation page is displayed",
                "data": {
                    "email": f"paypal-{first_name.lower()}@{random.choice(self.sample_data['domains'])}",
                    "password": "Test1234!"
                }
            }
            scenario["steps"].append(login_step)
        
        # Add final confirmation step
        confirm_step = {
            "action": "Review order and click 'Place Order' button",
            "expected": "Order confirmation page is displayed with order number and details"
        }
        scenario["steps"].append(confirm_step)
        
        return scenario
    
    def _generate_registration_scenario(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a user registration test scenario."""
        if context is None:
            context = {}
            
        # Basic user info
        first_name = random.choice(self.sample_data['first_names'])
        last_name = random.choice(self.sample_data['last_names'])
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(self.sample_data['domains'])}"
        password = "P@ssw0rd" + str(random.randint(100, 999))
        
        # Create scenario
        scenario = {
            "name": "User Registration Flow",
            "description": "Test the complete user registration process.",
            "preconditions": [
                "User is not logged in",
                "User is on the website homepage"
            ],
            "steps": [
                {
                    "action": "Navigate to registration page",
                    "expected": "Registration form is displayed"
                },
                {
                    "action": "Enter registration information",
                    "expected": "Form accepts valid registration details",
                    "data": {
                        "firstName": first_name,
                        "lastName": last_name,
                        "email": email,
                        "password": password,
                        "confirmPassword": password
                    }
                },
                {
                    "action": "Accept terms and conditions",
                    "expected": "Checkbox can be checked",
                    "data": {
                        "termsAccepted": True
                    }
                },
                {
                    "action": "Click 'Register' button",
                    "expected": "Registration confirmation page is displayed"
                }
            ],
            "expected_results": [
                "User account is successfully created",
                "Confirmation email is sent to the user",
                "User is automatically logged in",
                "User is redirected to the dashboard or homepage"
            ]
        }
        
        # Add verification step if required
        if context.get('requires_verification', random.choice([True, False])):
            verification_step = {
                "action": "Click verification link in email",
                "expected": "Email verification success page is displayed"
            }
            scenario["steps"].append(verification_step)
            scenario["expected_results"].append("User account is marked as verified")
        
        return scenario
    
    def _generate_login_scenario(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a user login test scenario."""
        if context is None:
            context = {}
            
        # User credentials
        username = context.get('username', f"user{random.randint(1000, 9999)}")
        email = context.get('email', f"{username}@{random.choice(self.sample_data['domains'])}")
        password = context.get('password', "P@ssw0rd" + str(random.randint(100, 999)))
        
        # Create scenario
        scenario = {
            "name": "User Login Flow",
            "description": "Test the user login process.",
            "preconditions": [
                "User has a registered account",
                "User is not logged in"
            ],
            "steps": [
                {
                    "action": "Navigate to login page",
                    "expected": "Login form is displayed"
                },
                {
                    "action": "Enter login credentials",
                    "expected": "Form accepts input",
                    "data": {
                        "username": username,
                        "email": email,
                        "password": password
                    }
                },
                {
                    "action": "Click 'Login' button",
                    "expected": "User is authenticated and redirected to dashboard"
                }
            ],
            "expected_results": [
                "User is successfully logged in",
                "User is redirected to the dashboard or homepage",
                "User's session is properly created"
            ]
        }
        
        # Add remember me option if included
        if context.get('remember_me', random.choice([True, False])):
            remember_step = {
                "action": "Check 'Remember me' option",
                "expected": "Checkbox can be checked",
                "data": {
                    "rememberMe": True
                }
            }
            scenario["steps"].insert(2, remember_step)
            scenario["expected_results"].append("User session persists across browser restarts")
        
        return scenario
    
    def _generate_payment_scenario(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a payment processing test scenario."""
        if context is None:
            context = {}
            
        # Payment details
        payment_method = context.get('payment_method', random.choice(['Credit Card', 'PayPal', 'Bank Transfer']))
        amount = context.get('amount', round(random.uniform(10, 1000), 2))
        currency = context.get('currency', random.choice(self.sample_data['currencies']))
        
        # Create base scenario
        scenario = {
            "name": f"{payment_method} Payment Processing",
            "description": f"Test the payment processing flow using {payment_method}.",
            "preconditions": [
                "User is logged in",
                "User has items in cart or account requires payment"
            ],
            "steps": [
                {
                    "action": "Navigate to payment page",
                    "expected": "Payment options are displayed"
                },
                {
                    "action": f"Select {payment_method} as payment method",
                    "expected": f"{payment_method} payment form is displayed"
                }
            ],
            "expected_results": [
                "Payment is successfully processed",
                "Receipt is generated",
                "Confirmation is displayed to user"
            ]
        }
        
        # Add payment-method-specific steps
        if payment_method == "Credit Card":
            cc_type = random.choice(list(self.test_credit_cards.keys()))
            cc_number = self.test_credit_cards[cc_type]
            
            payment_details_step = {
                "action": "Enter credit card details",
                "expected": "Form accepts valid card details",
                "data": {
                    "cardholderName": f"{random.choice(self.sample_data['first_names'])} {random.choice(self.sample_data['last_names'])}",
                    "cardType": cc_type.capitalize(),
                    "cardNumber": cc_number,
                    "expiryDate": f"{random.randint(1, 12):02d}/{datetime.date.today().year + random.randint(1, 5) % 100:02d}",
                    "cvv": f"{random.randint(100, 999)}"
                }
            }
            scenario["steps"].append(payment_details_step)
            
            billing_step = {
                "action": "Enter billing address",
                "expected": "Form accepts valid address details",
                "data": {
                    "address": f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Maple'])} St",
                    "city": random.choice(['New York', 'Los Angeles', 'Chicago']),
                    "state": random.choice(['NY', 'CA', 'IL']),
                    "zipCode": f"{random.randint(10000, 99999)}",
                    "country": "United States"
                }
            }
            scenario["steps"].append(billing_step)
            
        elif payment_method == "PayPal":
            paypal_step = {
                "action": "Click 'Pay with PayPal' button",
                "expected": "User is redirected to PayPal site"
            }
            scenario["steps"].append(paypal_step)
            
            login_step = {
                "action": "Log in to PayPal",
                "expected": "PayPal payment confirmation page is displayed",
                "data": {
                    "email": f"paypal-user{random.randint(1000, 9999)}@{random.choice(self.sample_data['domains'])}",
                    "password": "PayP@l" + str(random.randint(100, 999))
                }
            }
            scenario["steps"].append(login_step)
            
        elif payment_method == "Bank Transfer":
            bank_step = {
                "action": "Enter bank account details",
                "expected": "Form accepts valid bank details",
                "data": {
                    "accountHolder": f"{random.choice(self.sample_data['first_names'])} {random.choice(self.sample_data['last_names'])}",
                    "accountNumber": f"{random.randint(1000000000, 9999999999)}",
                    "routingNumber": f"{random.randint(100000000, 999999999)}",
                    "bankName": random.choice(['Chase', 'Bank of America', 'Wells Fargo'])
                }
            }
            scenario["steps"].append(bank_step)
        
        # Add final confirmation step
        confirm_step = {
            "action": f"Confirm payment of {amount} {currency}",
            "expected": "Payment confirmation page is displayed"
        }
        scenario["steps"].append(confirm_step)
        
        return scenario
    
    def _generate_search_scenario(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a search functionality test scenario."""
        if context is None:
            context = {}
            
        # Search terms
        search_categories = context.get('categories', self.sample_data['products'])
        search_term = context.get('search_term', random.choice(search_categories))
        
        # Create scenario
        scenario = {
            "name": "Search Functionality Testing",
            "description": "Test the search feature with various queries and filters.",
            "preconditions": [
                "User is on the website"
            ],
            "steps": [
                {
                    "action": "Navigate to search page or focus on search bar",
                    "expected": "Search input is accessible"
                },
                {
                    "action": f"Enter search term: '{search_term}'",
                    "expected": "Search term is accepted",
                    "data": {
                        "searchQuery": search_term
                    }
                },
                {
                    "action": "Execute search (press Enter or click search button)",
                    "expected": "Search results page is displayed"
                }
            ],
            "expected_results": [
                "Search results are displayed",
                "Results are relevant to the search term",
                "Pagination works if there are many results",
                "Search statistics (number of results, time) are displayed"
            ]
        }
        
        # Add filtering step if included
        if context.get('include_filters', random.choice([True, False])):
            filters = {
                "priceRange": [random.randint(10, 50), random.randint(51, 200)],
                "category": random.choice(search_categories),
                "sortBy": random.choice(["relevance", "price_low_to_high", "price_high_to_low", "newest"])
            }
            
            filter_step = {
                "action": "Apply filters to search results",
                "expected": "Filtered results are displayed",
                "data": filters
            }
            scenario["steps"].append(filter_step)
            scenario["expected_results"].append("Filters are correctly applied to search results")
        
        # Add advanced search step if included
        if context.get('advanced_search', random.choice([True, False])):
            advanced_step = {
                "action": "Use advanced search options",
                "expected": "Advanced search form is displayed",
                "data": {
                    "exactPhrase": search_term,
                    "excludeWords": "unwanted term",
                    "dateRange": [
                        (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
                        datetime.date.today().strftime("%Y-%m-%d")
                    ]
                }
            }
            scenario["steps"].append(advanced_step)
            scenario["expected_results"].append("Advanced search parameters are correctly applied")
        
        return scenario
    
    def _generate_generic_scenario(self, scenario_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a generic test scenario based on type."""
        if context is None:
            context = {}
            
        # Create a basic scenario structure
        scenario = {
            "name": f"{scenario_type.capitalize()} Testing",
            "description": f"Test the {scenario_type} functionality.",
            "preconditions": [
                "User is logged in",
                f"User has access to {scenario_type} feature"
            ],
            "steps": [
                {
                    "action": f"Navigate to {scenario_type} page",
                    "expected": f"{scenario_type.capitalize()} interface is displayed"
                }
            ],
            "expected_results": [
                f"{scenario_type.capitalize()} functionality works as expected"
            ]
        }
        
        # Add a few generic steps
        for i in range(3):
            step = {
                "action": f"Perform action {i+1} related to {scenario_type}",
                "expected": f"System responds correctly to action {i+1}"
            }
            scenario["steps"].append(step)
        
        return scenario