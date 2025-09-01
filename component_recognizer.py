import logging
from typing import List, Dict, Any, Optional
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

class ComponentRecognizer:
    """Recognizes UI components from recorded actions."""
    
    def __init__(self):
        self.component_patterns = {
            "form": self._detect_form_component,
            "button": self._detect_button_component,
            "input": self._detect_input_component,
            "select": self._detect_select_component,
            "link": self._detect_link_component,
            "table": self._detect_table_component,
            "navigation": self._detect_navigation_component,
            "checkbox": self._detect_checkbox_component,
            "radio": self._detect_radio_component
        }
        
        self.page_transition_markers = [
            "NAVIGATE",
            "SUBMIT",
            "PAGE_LOAD"
        ]
        
        # Patterns for recognizing component types based on selectors and attributes
        self.selector_patterns = {
            "button": [
                re.compile(r'button', re.IGNORECASE),
                re.compile(r'btn', re.IGNORECASE),
                re.compile(r'submit', re.IGNORECASE),
                re.compile(r'cancel', re.IGNORECASE)
            ],
            "input": [
                re.compile(r'input', re.IGNORECASE),
                re.compile(r'text', re.IGNORECASE),
                re.compile(r'field', re.IGNORECASE),
                re.compile(r'email', re.IGNORECASE),
                re.compile(r'password', re.IGNORECASE)
            ],
            "select": [
                re.compile(r'select', re.IGNORECASE),
                re.compile(r'dropdown', re.IGNORECASE),
                re.compile(r'combobox', re.IGNORECASE)
            ],
            "checkbox": [
                re.compile(r'checkbox', re.IGNORECASE),
                re.compile(r'check', re.IGNORECASE)
            ],
            "radio": [
                re.compile(r'radio', re.IGNORECASE)
            ],
            "link": [
                re.compile(r'link', re.IGNORECASE),
                re.compile(r'anchor', re.IGNORECASE)
            ],
            "table": [
                re.compile(r'table', re.IGNORECASE),
                re.compile(r'grid', re.IGNORECASE),
                re.compile(r'data-table', re.IGNORECASE)
            ],
            "form": [
                re.compile(r'form', re.IGNORECASE),
                re.compile(r'login-form', re.IGNORECASE),
                re.compile(r'registration-form', re.IGNORECASE),
                re.compile(r'signup-form', re.IGNORECASE)
            ]
        }
        
        # Common form field types for classification
        self.field_types = {
            "text": re.compile(r'text|input|field', re.IGNORECASE),
            "email": re.compile(r'email|e-mail', re.IGNORECASE),
            "password": re.compile(r'password|pwd|pass', re.IGNORECASE),
            "number": re.compile(r'number|num|qty|quantity|amount', re.IGNORECASE),
            "date": re.compile(r'date|calendar|dob|birth', re.IGNORECASE),
            "time": re.compile(r'time|hour|minute', re.IGNORECASE),
            "tel": re.compile(r'tel|phone|mobile|cell', re.IGNORECASE),
            "url": re.compile(r'url|website|web|link', re.IGNORECASE),
            "search": re.compile(r'search|find|query', re.IGNORECASE),
            "file": re.compile(r'file|upload|attachment', re.IGNORECASE)
        }
    
    def identify_pages_and_components(self, actions):
        """Main method to identify pages and their components."""
        pages = []
        current_page = None
        page_actions = []
        
        # First pass: split actions into page groups
        for action in actions:
            if self._is_page_transition(action):
                if current_page and page_actions:
                    # Complete the current page
                    components = self._extract_components(page_actions)
                    current_page["components"] = components
                    pages.append(current_page)
                
                # Start a new page
                current_page = self._create_page_from_action(action)
                page_actions = [action]
            elif current_page:
                # Add to current page's actions
                page_actions.append(action)
        
        # Don't forget the last page
        if current_page and page_actions:
            components = self._extract_components(page_actions)
            current_page["components"] = components
            pages.append(current_page)
        
        # Second pass: refine component identification
        refined_pages = self._refine_page_components(pages)
        
        return refined_pages
    
    def _is_page_transition(self, action):
        """Determine if an action represents a transition to a new page."""
        return action.get('actionType') in self.page_transition_markers
    
    def _create_page_from_action(self, action):
        """Create a page object from a navigation action."""
        url = action.get('url', '')
        title = action.get('pageTitle', '')
        
        # If no title, try to generate one from URL
        if not title and url:
            # Extract domain and path
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                path = parsed_url.path
                
                # Generate title from path if available, otherwise use domain
                if path and path != '/':
                    # Remove leading/trailing slashes and convert to title case
                    path_parts = path.strip('/').split('/')
                    title = ' '.join(part.capitalize() for part in path_parts)
                else:
                    title = domain
            except:
                title = "Unknown Page"
        
        # Generate page type from title or URL
        page_type = self._determine_page_type(title, url)
        
        # Create identification rules
        identification_rules = {
            "url_contains": [self._extract_key_term(url)],
            "title_contains": [self._extract_key_term(title)]
        }
        
        return {
            "pageName": title or "Unknown Page",
            "urlPattern": url,
            "pageType": page_type,
            "identificationRules": identification_rules,
            "components": []
        }
    
    def _determine_page_type(self, title, url):
        """Determine the type of page based on title and URL."""
        title_lower = (title or "").lower()
        url_lower = (url or "").lower()
        
        # Check for common page types
        if any(term in title_lower or term in url_lower for term in ['login', 'signin', 'sign-in']):
            return "LOGIN"
        elif any(term in title_lower or term in url_lower for term in ['register', 'signup', 'sign-up', 'registration']):
            return "REGISTRATION"
        elif any(term in title_lower or term in url_lower for term in ['checkout', 'payment', 'billing']):
            return "CHECKOUT"
        elif any(term in title_lower or term in url_lower for term in ['search', 'results', 'find']):
            return "SEARCH"
        elif any(term in title_lower or term in url_lower for term in ['dashboard', 'home', 'main']):
            return "DASHBOARD"
        elif any(term in title_lower or term in url_lower for term in ['profile', 'account', 'settings']):
            return "PROFILE"
        elif any(term in title_lower or term in url_lower for term in ['confirm', 'success', 'thank', 'complete']):
            return "CONFIRMATION"
        else:
            return "GENERIC"
    
    def _extract_key_term(self, text):
        """Extract a key term from text for identification rules."""
        if not text:
            return ""
            
        # Remove common prefixes and TLD
        text = re.sub(r'^https?://(www\.)?', '', text)
        text = re.sub(r'\.(com|org|net|io|gov|edu).*$', '', text)
        
        # Get the most specific part (last path segment or domain)
        parts = re.split(r'[/\-_]', text)
        filtered_parts = [p for p in parts if p and len(p) > 2]
        
        return filtered_parts[-1] if filtered_parts else text
    
    def _extract_components(self, actions):
        """Extract UI components from a list of actions."""
        components = []
        seen_selectors = set()
        
        for action in actions:
            action_type = action.get('actionType')
            selector = action.get('elementSelector')
            
            # Skip actions without selectors or already processed selectors
            if not selector or selector in seen_selectors:
                continue
                
            seen_selectors.add(selector)
            
            # Create a component based on the action type
            if action_type in ['CLICK', 'SUBMIT']:
                component = self._detect_button_component(action)
            elif action_type == 'TYPE':
                component = self._detect_input_component(action)
            elif action_type == 'SELECT':
                component = self._detect_select_component(action)
            elif action_type == 'CHANGE':
                # Handle checkboxes and radios
                element_type = action.get('elementType', '').lower()
                if 'checkbox' in element_type:
                    component = self._detect_checkbox_component(action)
                elif 'radio' in element_type:
                    component = self._detect_radio_component(action)
                else:
                    component = self._detect_input_component(action)
            else:
                # For other action types, use generic detection
                component = self._detect_generic_component(action)
            
            if component:
                components.append(component)
        
        return components
    
    def _detect_form_component(self, action):
        """Detect a form component from an action."""
        selector = action.get('elementSelector')
        element_type = action.get('elementType')
        element_value = action.get('elementValue')
        description = action.get('description')
        
        # Determine form name
        name = element_value or description or "Form"
        
        # Clean up name if needed
        if name == "Form" and selector:
            # Try to extract a better name from the selector
            match = re.search(r'#([a-zA-Z0-9_-]+)', selector)
            if match:
                name = ' '.join(word.capitalize() for word in re.split(r'[-_]', match.group(1)))
                if not 'form' in name.lower():
                    name += " Form"
        
        # Forms typically contain fields and have submission behavior
        expected_behavior = "Collects and submits user input"
        
        return {
            "name": name.strip(),
            "selector": selector,
            "componentType": "form",
            "validationRules": None,
            "expectedBehavior": expected_behavior,
            "dataType": None,
            "isRequired": None,
            "children": []  # Forms can contain child components
        }
    
    def _detect_button_component(self, action):
        """Detect a button component from an action."""
        selector = action.get('elementSelector')
        element_type = action.get('elementType')
        element_value = action.get('elementValue')
        description = action.get('description')
        
        # Determine button name
        name = element_value or description or "Button"
        
        # Clean up name if needed
        if name == "Button" and selector:
            # Try to extract a better name from the selector
            match = re.search(r'#([a-zA-Z0-9_-]+)', selector)
            if match:
                name = ' '.join(word.capitalize() for word in re.split(r'[-_]', match.group(1)))
        
        # Determine if it's a submit button
        expected_behavior = "Submits form" if action.get('actionType') == 'SUBMIT' or 'submit' in selector.lower() else "Performs action"
        
        return {
            "name": name.strip(),
            "selector": selector,
            "componentType": "button",
            "validationRules": None,
            "expectedBehavior": expected_behavior,
            "dataType": None,
            "isRequired": None
        }
    
    def _detect_input_component(self, action):
        """Detect an input component from an action."""
        selector = action.get('elementSelector')
        element_type = action.get('elementType')
        input_data = action.get('inputData')
        
        # Determine input type
        data_type = "text"  # Default
        is_required = True  # Assume required by default
        
        # Check if it's a specific type of input
        if element_type:
            lowercase_type = element_type.lower()
            if 'password' in lowercase_type:
                data_type = "password"
            elif 'email' in lowercase_type:
                data_type = "email"
            elif 'number' in lowercase_type:
                data_type = "number"
            elif 'tel' in lowercase_type or 'phone' in lowercase_type:
                data_type = "tel"
            elif 'date' in lowercase_type:
                data_type = "date"
        
        # If element_type wasn't specific enough, check the selector
        if data_type == "text" and selector:
            for field_type, pattern in self.field_types.items():
                if pattern.search(selector):
                    data_type = field_type
                    break
        
        # Determine field name from selector
        name = self._extract_field_name(selector) or "Input Field"
        
        return {
            "name": name,
            "selector": selector,
            "componentType": "input",
            "validationRules": None,
            "expectedBehavior": f"Accepts {data_type} input",
            "dataType": data_type,
            "isRequired": is_required
        }
    
    def _detect_select_component(self, action):
        """Detect a select dropdown component from an action."""
        selector = action.get('elementSelector')
        input_data = action.get('inputData')
        
        # Determine name
        name = self._extract_field_name(selector) or "Dropdown"
        
        return {
            "name": name,
            "selector": selector,
            "componentType": "select",
            "validationRules": None,
            "expectedBehavior": "Displays options for selection",
            "dataType": "select",
            "isRequired": True
        }
    
    def _detect_checkbox_component(self, action):
        """Detect a checkbox component from an action."""
        selector = action.get('elementSelector')
        
        # Determine name
        name = self._extract_field_name(selector) or "Checkbox"
        
        return {
            "name": name,
            "selector": selector,
            "componentType": "checkbox",
            "validationRules": None,
            "expectedBehavior": "Toggles boolean state",
            "dataType": "boolean",
            "isRequired": False
        }
    
    def _detect_radio_component(self, action):
        """Detect a radio button component from an action."""
        selector = action.get('elementSelector')
        
        # Determine name
        name = self._extract_field_name(selector) or "Radio Button"
        
        return {
            "name": name,
            "selector": selector,
            "componentType": "radio",
            "validationRules": None,
            "expectedBehavior": "Selects one option from a group",
            "dataType": "option",
            "isRequired": True
        }
    
    def _detect_link_component(self, action):
        """Detect a link component from an action."""
        selector = action.get('elementSelector')
        element_value = action.get('elementValue')
        
        # Determine name
        name = element_value or self._extract_field_name(selector) or "Link"
        
        return {
            "name": name,
            "selector": selector,
            "componentType": "link",
            "validationRules": None,
            "expectedBehavior": "Navigates to another page",
            "dataType": None,
            "isRequired": None
        }
    
    def _detect_table_component(self, action):
        """Detect a table component from an action."""
        selector = action.get('elementSelector')
        
        # Determine name
        name = self._extract_field_name(selector) or "Data Table"
        
        return {
            "name": name,
            "selector": selector,
            "componentType": "table",
            "validationRules": None,
            "expectedBehavior": "Displays tabular data",
            "dataType": "table",
            "isRequired": None
        }
    
    def _detect_navigation_component(self, action):
        """Detect a navigation component from an action."""
        selector = action.get('elementSelector')
        
        # Determine name
        name = self._extract_field_name(selector) or "Navigation"
        
        return {
            "name": name,
            "selector": selector,
            "componentType": "navigation",
            "validationRules": None,
            "expectedBehavior": "Provides navigation controls",
            "dataType": None,
            "isRequired": None
        }
    
    def _detect_generic_component(self, action):
        """Detect a generic component from an action."""
        selector = action.get('elementSelector')
        if not selector:
            return None
            
        element_type = action.get('elementType')
        
        # Try to infer component type from selector
        component_type = "unknown"
        for type_name, patterns in self.selector_patterns.items():
            for pattern in patterns:
                if pattern.search(selector):
                    component_type = type_name
                    break
            if component_type != "unknown":
                break
        
        # Also consider element_type if available
        if element_type:
            element_type_lower = element_type.lower()
            if 'button' in element_type_lower:
                component_type = 'button'
            elif 'input' in element_type_lower:
                component_type = 'input'
            elif 'select' in element_type_lower:
                component_type = 'select'
            elif 'checkbox' in element_type_lower:
                component_type = 'checkbox'
            elif 'radio' in element_type_lower:
                component_type = 'radio'
            elif 'link' in element_type_lower or 'a' == element_type_lower:
                component_type = 'link'
            elif 'table' in element_type_lower:
                component_type = 'table'
            elif 'form' in element_type_lower:
                component_type = 'form'
        
        # Determine name
        name = self._extract_field_name(selector) or f"{component_type.capitalize()} Component"
        
        return {
            "name": name,
            "selector": selector,
            "componentType": component_type,
            "validationRules": None,
            "expectedBehavior": "Interacts with user",
            "dataType": None,
            "isRequired": None
        }
    
    def _extract_field_name(self, selector):
        """Extract a field name from a selector."""
        if not selector:
            return None
            
        # Try to extract from id
        id_match = re.search(r'#([a-zA-Z0-9_-]+)', selector)
        if id_match:
            raw_name = id_match.group(1)
            # Convert camelCase or snake_case to readable form
            if '_' in raw_name:
                return ' '.join(word.capitalize() for word in raw_name.split('_'))
            else:
                # Insert spaces before capital letters
                name = re.sub(r'([a-z])([A-Z])', r'\1 \2', raw_name)
                return name.capitalize()
        
        # Try to extract from name attribute
        name_match = re.search(r'\[name=[\'"]([^\'"]+)[\'"]\]', selector)
        if name_match:
            raw_name = name_match.group(1)
            # Convert to readable form
            if '_' in raw_name:
                return ' '.join(word.capitalize() for word in raw_name.split('_'))
            else:
                # Insert spaces before capital letters
                name = re.sub(r'([a-z])([A-Z])', r'\1 \2', raw_name)
                return name.capitalize()
        
        # Try to extract from class
        class_match = re.search(r'\.([a-zA-Z0-9_-]+)', selector)
        if class_match:
            raw_name = class_match.group(1)
            # Convert to readable form
            if '_' in raw_name or '-' in raw_name:
                return ' '.join(word.capitalize() for word in re.split(r'[_-]', raw_name))
            else:
                # Insert spaces before capital letters
                name = re.sub(r'([a-z])([A-Z])', r'\1 \2', raw_name)
                return name.capitalize()
        
        return None
    
    def _refine_page_components(self, pages):
        """Refine the identified components for each page."""
        for page in pages:
            components = page.get("components", [])
            
            # Group similar components
            grouped_components = defaultdict(list)
            for component in components:
                type_key = component.get("componentType", "unknown")
                grouped_components[type_key].append(component)
            
            # Refine names for disambiguation when there are multiple components of same type
            for component_type, type_components in grouped_components.items():
                if len(type_components) > 1:
                    for i, component in enumerate(type_components):
                        # Check if we need more specific naming
                        if "Field" not in component["name"] and component["componentType"] == "input":
                            component["name"] += " Field"
                        
                        # Add the component's data type to the name if available
                        if component.get("dataType") and component["dataType"] not in component["name"]:
                            component["name"] += f" ({component['dataType'].capitalize()})"
            
            # Look for form relationships
            forms = self._identify_forms(components)
            if forms:
                # Add form information to components
                for form_id, form_info in forms.items():
                    for component_selector in form_info["components"]:
                        for component in components:
                            if component["selector"] == component_selector:
                                component["formId"] = form_id
        
        return pages
    
    def _identify_forms(self, components):
        """Identify forms and their related components."""
        # This implementation is incomplete - it only checks for submit buttons
        # Let's enhance it to detect actual form structures
        
        forms = {}
        form_id = 1
        
        # Group components by DOM proximity and relationships
        grouped_components = self._group_components_by_proximity(components)
        
        for group in grouped_components:
            # Check if group contains input fields and a submit button
            input_fields = [c for c in group if c["componentType"] in ["input", "select", "checkbox", "radio"]]
            submit_buttons = [c for c in group if c["componentType"] == "button" and 
                            ("submit" in c["name"].lower() or "login" in c["name"].lower() or 
                            "register" in c["name"].lower() or "save" in c["name"].lower())]
            
            if input_fields and submit_buttons:
                form_components = [c["selector"] for c in group]
                form_name = f"Form {form_id}"
                
                # Try to derive a more meaningful name from the submit button or fields
                if submit_buttons:
                    form_name = submit_buttons[0]["name"].replace("Button", "Form")
                
                forms[f"form_{form_id}"] = {
                    "name": form_name,
                    "components": form_components,
                    "fields": len(input_fields),
                    "submitButton": submit_buttons[0]["selector"] if submit_buttons else None
                }
                form_id += 1
        
        return forms
    
    def _extract_form_attribute(self, selector):
        """Extract form attribute from a selector if present."""
        form_match = re.search(r'\[form=[\'"]([^\'"]+)[\'"]\]', selector)
        if form_match:
            return form_match.group(1)
        return None

    def _are_selectors_related(self, selector1, selector2):
        """Determine if two selectors are likely related (in the same form)."""
        # Check if they share common parent patterns
        parts1 = selector1.split(' ')
        parts2 = selector2.split(' ')
        
        # Check for common ancestry
        common_parts = min(len(parts1), len(parts2)) - 1
        if common_parts > 0 and parts1[:common_parts] == parts2[:common_parts]:
            return True
        
        return False

    def _group_components_by_proximity(self, components):
        """Group components by their proximity in the DOM and semantic relationships."""
        groups = []
        processed = set()
        
        # First pass: group by form attributes
        for component in components:
            if component["selector"] in processed:
                continue
                
            # Check if component has form attribute
            form_attr = self._extract_form_attribute(component["selector"])
            if form_attr:
                # Find all components with the same form attribute
                form_group = [component]
                processed.add(component["selector"])
                
                for other in components:
                    if other["selector"] != component["selector"] and other["selector"] not in processed:
                        other_form_attr = self._extract_form_attribute(other["selector"])
                        if other_form_attr == form_attr:
                            form_group.append(other)
                            processed.add(other["selector"])
                
                if len(form_group) > 1:
                    groups.append(form_group)
        
        # Second pass: group by selector proximity
        for component in components:
            if component["selector"] in processed:
                continue
                
            related_group = [component]
            processed.add(component["selector"])
            
            for other in components:
                if other["selector"] != component["selector"] and other["selector"] not in processed:
                    if self._are_selectors_related(component["selector"], other["selector"]):
                        related_group.append(other)
                        processed.add(other["selector"])
            
            if len(related_group) > 1:
                groups.append(related_group)
        
        return groups