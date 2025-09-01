import logging
import re
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

class TestScriptGenerator:
    """Generates test scripts for various frameworks based on test cases."""
    
    def __init__(self):
        self.generators = {
            "selenium": self._generate_selenium_script,
            "cypress": self._generate_cypress_script,
            "playwright": self._generate_playwright_script,
            "selenium_page_objects": self._generate_selenium_page_objects
        }
        
        # Common variable names by data type
        self.variable_names = {
            "username": "username",
            "email": "email",
            "password": "password",
            "text": "inputText",
            "number": "inputNumber",
            "select": "selectedOption",
            "checkbox": "isChecked",
            "date": "dateValue",
            "search": "searchTerm"
        }
        
        # Test data templates for different frameworks
        self.test_data_templates = {
            "selenium": {
                "valid_username": "testuser",
                "valid_password": "Password123!",
                "valid_email": "test@example.com",
                "invalid_username": "us",
                "invalid_password": "pass",
                "invalid_email": "not-an-email",
                "search_term": "test product",
                "no_results_search_term": "xyznotfound123"
            },
            "cypress": {
                "valid_username": "testuser",
                "valid_password": "Password123!",
                "valid_email": "test@example.com",
                "invalid_username": "us",
                "invalid_password": "pass",
                "invalid_email": "not-an-email",
                "search_term": "test product",
                "no_results_search_term": "xyznotfound123"
            },
            "playwright": {
                "valid_username": "testuser",
                "valid_password": "Password123!",
                "valid_email": "test@example.com",
                "invalid_username": "us",
                "invalid_password": "pass",
                "invalid_email": "not-an-email",
                "search_term": "test product",
                "no_results_search_term": "xyznotfound123"
            }
        }
    
    def generate_script(self, test_case, test_data, framework="selenium"):
        """
        Generate a test script for the given test case using the specified framework.
        
        Args:
            test_case: The test case object with steps and page/component references
            test_data: Test data to be used in the script
            framework: The framework to generate the script for (selenium, cypress, playwright)
            
        Returns:
            The generated test script as a string
        """
        if framework not in self.generators:
            raise ValueError(f"Unsupported framework: {framework}")
            
        return self.generators[framework](test_case, test_data)
    
    def _generate_selenium_script(self, test_case, test_data):
        """
        Generate a Selenium WebDriver test script in Java.
        
        Args:
            test_case: The test case object
            test_data: Test data for the test case
            
        Returns:
            Selenium Java test script
        """
        # Create a sanitized class name from the test case name
        class_name = self._sanitize_class_name(test_case.get("name", "GeneratedTest"))
        
        # Initialize the script with imports and class definition
        script = [
            "import org.openqa.selenium.By;",
            "import org.openqa.selenium.WebDriver;",
            "import org.openqa.selenium.WebElement;",
            "import org.openqa.selenium.chrome.ChromeDriver;",
            "import org.openqa.selenium.support.ui.ExpectedConditions;",
            "import org.openqa.selenium.support.ui.WebDriverWait;",
            "import org.openqa.selenium.support.ui.Select;",
            "import java.time.Duration;",
            "import org.junit.jupiter.api.AfterEach;",
            "import org.junit.jupiter.api.BeforeEach;",
            "import org.junit.jupiter.api.Test;",
            "import org.junit.jupiter.api.Assertions;",
            "",
            f"public class {class_name} {{",
            "    private WebDriver driver;",
            "    private WebDriverWait wait;",
            "",
            "    @BeforeEach",
            "    public void setUp() {",
            "        driver = new ChromeDriver();",
            "        driver.manage().window().maximize();",
            "        wait = new WebDriverWait(driver, Duration.ofSeconds(10));",
            "    }",
            "",
            "    @Test",
            f"    public void {self._sanitize_method_name(test_case.get('name', 'testMethod'))}() {{"
        ]
        
        # Add test data variables
        script.append("        // Test data")
        for key, value in self.test_data_templates["selenium"].items():
            if key in test_data:
                # Use provided test data if available
                script.append(f"        String {key} = \"{test_data[key]}\";")
            else:
                # Otherwise use the template data
                script.append(f"        String {key} = \"{value}\";")
        script.append("")
        
        # Process test steps
        script.append("        // Test steps")
        for step in test_case.get("steps", []):
            step_type = step.get("stepType", "INTERACTION")
            input_data = step.get("inputData", "")
            
            # Replace test data placeholders
            if input_data and input_data.startswith("{{") and input_data.endswith("}}"):
                data_var = input_data[2:-2]  # Remove {{ and }}
                input_data = data_var  # Use the variable name directly
            
            # Generate code for each step type
            if step_type == "NAVIGATION":
                url = step.get("url", "")
                if not url:
                    # If URL not provided, use a placeholder or derive from page name
                    page_name = step.get("action", "").replace("Navigate to ", "")
                    url = f"https://example.com/{page_name.lower().replace(' ', '_')}"
                
                script.append(f"        // {step.get('action', 'Navigate to page')}")
                script.append(f"        driver.get(\"{url}\");")
                script.append(f"        System.out.println(\"{step.get('expectedResult', 'Page loaded')}\");")
                script.append("")
                
            elif step_type == "INTERACTION":
                component_id = step.get("componentId")
                selector = self._generate_selector_for_component(component_id, step)
                
                script.append(f"        // {step.get('action', 'Interact with element')}")
                
                # Different handling based on action type
                action_lower = step.get("action", "").lower()
                
                if "click" in action_lower:
                    script.append(f"        WebElement element = wait.until(ExpectedConditions.elementToBeClickable({selector}));")
                    script.append(f"        element.click();")
                    
                elif "enter" in action_lower or "type" in action_lower:
                    script.append(f"        WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated({selector}));")
                    script.append(f"        element.clear();")
                    script.append(f"        element.sendKeys({input_data});")
                    
                elif "select" in action_lower:
                    script.append(f"        WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated({selector}));")
                    script.append(f"        Select dropdown = new Select(element);")
                    script.append(f"        dropdown.selectByVisibleText({input_data});")
                    
                script.append(f"        System.out.println(\"{step.get('expectedResult', 'Action performed')}\");")
                script.append("")
                
            elif step_type == "VALIDATION":
                # Add validation code
                script.append(f"        // {step.get('action', 'Validate result')}")
                script.append(f"        // TODO: Add assertions to validate {step.get('expectedResult', 'expected result')}")
                script.append(f"        // Example: Assertions.assertTrue(driver.getPageSource().contains(\"Success\"));")
                script.append("")
        
        # Add verification for the final expected result
        script.append("        // Verify final expected result")
        script.append(f"        System.out.println(\"Expected result: {test_case.get('expectedResult', 'Test completed')}\");")
        script.append("        // TODO: Add final verification steps")
        script.append("")
        
        # Close the method and class
        script.append("    }")
        script.append("")
        script.append("    @AfterEach")
        script.append("    public void tearDown() {")
        script.append("        if (driver != null) {")
        script.append("            driver.quit();")
        script.append("        }")
        script.append("    }")
        script.append("}")
        
        return "\n".join(script)
    
    def _generate_cypress_script(self, test_case, test_data):
        """
        Generate a Cypress test script in JavaScript.
        
        Args:
            test_case: The test case object
            test_data: Test data for the test case
            
        Returns:
            Cypress JavaScript test script
        """
        # Initialize the script
        script = [
            "// Cypress test script",
            f"// Test: {test_case.get('name', 'Generated Test')}",
            f"// Description: {test_case.get('description', 'Generated test case')}",
            "",
            "describe('" + test_case.get('name', 'Generated Test').replace("'", "\\'") + "', () => {",
            "  // Test data",
        ]
        
        # Add test data
        for key, value in self.test_data_templates["cypress"].items():
            if key in test_data:
                # Use provided test data if available
                script.append(f"  const {key} = '{test_data[key]}';")
            else:
                # Otherwise use the template data
                script.append(f"  const {key} = '{value}';")
        script.append("")
        
        # Start the test
        script.append("  it('" + test_case.get('description', 'should complete the test flow').replace("'", "\\'") + "', () => {")
        
        # Process preconditions if any
        if test_case.get("preconditions"):
            script.append("    // Preconditions")
            for precondition in test_case.get("preconditions"):
                script.append(f"    // - {precondition}")
            script.append("")
        
        # Process test steps
        for step in test_case.get("steps", []):
            step_type = step.get("stepType", "INTERACTION")
            input_data = step.get("inputData", "")
            
            # Replace test data placeholders
            if input_data and input_data.startswith("{{") and input_data.endswith("}}"):
                data_var = input_data[2:-2]  # Remove {{ and }}
                input_data = data_var  # Use the variable name directly
            
            # Generate code for each step type
            if step_type == "NAVIGATION":
                url = step.get("url", "")
                if not url:
                    # If URL not provided, use a placeholder or derive from page name
                    page_name = step.get("action", "").replace("Navigate to ", "")
                    url = f"/{page_name.lower().replace(' ', '_')}"
                
                script.append(f"    // {step.get('action', 'Navigate to page')}")
                script.append(f"    cy.visit('{url}');")
                script.append(f"    cy.log('{step.get('expectedResult', 'Page loaded')}');")
                script.append("")
                
            elif step_type == "INTERACTION":
                component_id = step.get("componentId")
                selector = self._generate_cypress_selector(component_id, step)
                
                script.append(f"    // {step.get('action', 'Interact with element')}")
                
                # Different handling based on action type
                action_lower = step.get("action", "").lower()
                
                if "click" in action_lower:
                    script.append(f"    cy.get('{selector}').click();")
                    
                elif "enter" in action_lower or "type" in action_lower:
                    script.append(f"    cy.get('{selector}').clear().type({input_data});")
                    
                elif "select" in action_lower:
                    script.append(f"    cy.get('{selector}').select({input_data});")
                    
                script.append(f"    cy.log('{step.get('expectedResult', 'Action performed')}');")
                script.append("")
                
            elif step_type == "VALIDATION":
                # Add validation code
                script.append(f"    // {step.get('action', 'Validate result')}")
                script.append(f"    // TODO: Add assertions to validate {step.get('expectedResult', 'expected result')}")
                script.append(f"    // Example: cy.contains('Success').should('be.visible');")
                script.append("")
        
        # Add verification for the final expected result
        script.append("    // Verify final expected result")
        script.append(f"    cy.log('Expected result: {test_case.get('expectedResult', 'Test completed')}');")
        script.append("    // TODO: Add final verification steps")
        
        # Close the test and describe blocks
        script.append("  });")
        script.append("});")
        
        return "\n".join(script)
    
    def _generate_playwright_script(self, test_case, test_data):
        """
        Generate a Playwright test script in JavaScript.
        
        Args:
            test_case: The test case object
            test_data: Test data for the test case
            
        Returns:
            Playwright JavaScript test script
        """
        # Initialize the script
        script = [
            "// Playwright test script",
            f"// Test: {test_case.get('name', 'Generated Test')}",
            f"// Description: {test_case.get('description', 'Generated test case')}",
            "",
            "const { test, expect } = require('@playwright/test');",
            "",
            "// Test data",
        ]
        
        # Add test data
        for key, value in self.test_data_templates["playwright"].items():
            if key in test_data:
                # Use provided test data if available
                script.append(f"const {key} = '{test_data[key]}';")
            else:
                # Otherwise use the template data
                script.append(f"const {key} = '{value}';")
        script.append("")
        
        # Start the test
        test_name = test_case.get('name', 'Generated Test').replace("'", "\\'")
        script.append(f"test('{test_name}', async ({{'page'}}) => {{")
        
        # Process preconditions if any
        if test_case.get("preconditions"):
            script.append("  // Preconditions")
            for precondition in test_case.get("preconditions"):
                script.append(f"  // - {precondition}")
            script.append("")
        
        # Process test steps
        for step in test_case.get("steps", []):
            step_type = step.get("stepType", "INTERACTION")
            input_data = step.get("inputData", "")
            
            # Replace test data placeholders
            if input_data and input_data.startswith("{{") and input_data.endswith("}}"):
                data_var = input_data[2:-2]  # Remove {{ and }}
                input_data = data_var  # Use the variable name directly
            
            # Generate code for each step type
            if step_type == "NAVIGATION":
                url = step.get("url", "")
                if not url:
                    # If URL not provided, use a placeholder or derive from page name
                    page_name = step.get("action", "").replace("Navigate to ", "")
                    url = f"/{page_name.lower().replace(' ', '_')}"
                
                script.append(f"  // {step.get('action', 'Navigate to page')}")
                script.append(f"  await page.goto('{url}');")
                script.append(f"  console.log('{step.get('expectedResult', 'Page loaded')}');")
                script.append("")
                
            elif step_type == "INTERACTION":
                component_id = step.get("componentId")
                selector = self._generate_playwright_selector(component_id, step)
                
                script.append(f"  // {step.get('action', 'Interact with element')}")
                
                # Different handling based on action type
                action_lower = step.get("action", "").lower()
                
                if "click" in action_lower:
                    script.append(f"  await page.click('{selector}');")
                    
                elif "enter" in action_lower or "type" in action_lower:
                    script.append(f"  await page.fill('{selector}', {input_data});")
                    
                elif "select" in action_lower:
                    script.append(f"  await page.selectOption('{selector}', {input_data});")
                    
                script.append(f"  console.log('{step.get('expectedResult', 'Action performed')}');")
                script.append("")
                
            elif step_type == "VALIDATION":
                # Add validation code
                script.append(f"  // {step.get('action', 'Validate result')}")
                script.append(f"  // TODO: Add assertions to validate {step.get('expectedResult', 'expected result')}")
                script.append(f"  // Example: await expect(page.locator('text=Success')).toBeVisible();")
                script.append("")
        
        # Add verification for the final expected result
        script.append("  // Verify final expected result")
        script.append(f"  console.log('Expected result: {test_case.get('expectedResult', 'Test completed')}');")
        script.append("  // TODO: Add final verification steps")
        
        # Close the test block
        script.append("});")
        
        return "\n".join(script)
    
    def _generate_selenium_page_objects(self, test_case, test_data):
        """
        Generate a Selenium Page Object Model test script in Java.
        
        Args:
            test_case: The test case object
            test_data: Test data for the test case
            
        Returns:
            Selenium Page Object Model Java test script
        """
        # Extract unique pages from the test case steps
        pages = {}
        for step in test_case.get("steps", []):
            page_id = step.get("pageId")
            page_name = None
            
            if page_id:
                # Extract page name from action or use a default
                action = step.get("action", "")
                if "Navigate to " in action:
                    page_name = action.replace("Navigate to ", "")
                
                if page_name and page_id not in pages:
                    pages[page_id] = self._sanitize_class_name(page_name)
        
        # Create a sanitized class name from the test case name
        test_class_name = self._sanitize_class_name(test_case.get("name", "GeneratedTest"))
        
        # Generate page object classes
        page_objects = []
        for page_id, page_name in pages.items():
            page_objects.append(self._generate_page_object_class(page_id, page_name, test_case))
        
        # Initialize the test script with imports and class definition
        script = [
            "import org.openqa.selenium.WebDriver;",
            "import org.openqa.selenium.chrome.ChromeDriver;",
            "import org.junit.jupiter.api.AfterEach;",
            "import org.junit.jupiter.api.BeforeEach;",
            "import org.junit.jupiter.api.Test;",
            "import org.junit.jupiter.api.Assertions;",
            "",
            f"public class {test_class_name} {{",
            "    private WebDriver driver;",
            "",
            "    @BeforeEach",
            "    public void setUp() {",
            "        driver = new ChromeDriver();",
            "        driver.manage().window().maximize();",
            "    }",
            "",
            "    @Test",
            f"    public void {self._sanitize_method_name(test_case.get('name', 'testMethod'))}() {{"
        ]
        
        # Add test data variables
        script.append("        // Test data")
        for key, value in self.test_data_templates["selenium"].items():
            if key in test_data:
                # Use provided test data if available
                script.append(f"        String {key} = \"{test_data[key]}\";")
            else:
                # Otherwise use the template data
                script.append(f"        String {key} = \"{value}\";")
        script.append("")
        
        # Process test steps using page objects
        current_page = None
        script.append("        // Test steps")
        
        for step in test_case.get("steps", []):
            step_type = step.get("stepType", "INTERACTION")
            input_data = step.get("inputData", "")
            
            # Replace test data placeholders
            if input_data and input_data.startswith("{{") and input_data.endswith("}}"):
                data_var = input_data[2:-2]  # Remove {{ and }}
                input_data = data_var  # Use the variable name directly
            
            # Generate code for each step type
            if step_type == "NAVIGATION":
                page_id = step.get("pageId")
                if page_id in pages:
                    page_name = pages[page_id]
                    script.append(f"        // {step.get('action', 'Navigate to page')}")
                    
                    # If this is a new page, create it
                    if current_page != page_name:
                        current_page = page_name
                        url = step.get("url", "")
                        if not url:
                            # If URL not provided, use a placeholder or derive from page name
                            url = f"https://example.com/{page_name.lower().replace(' ', '_')}"
                        
                        script.append(f"        {page_name}Page {page_name.lower()}Page = new {page_name}Page(driver);")
                        script.append(f"        {page_name.lower()}Page.navigateTo();")
                    
                    script.append(f"        System.out.println(\"{step.get('expectedResult', 'Page loaded')}\");")
                    script.append("")
                
            elif step_type == "INTERACTION":
                if current_page:
                    component_id = step.get("componentId")
                    
                    script.append(f"        // {step.get('action', 'Interact with element')}")
                    
                    # Different handling based on action type
                    action_lower = step.get("action", "").lower()
                    
                    if "click" in action_lower:
                        method_name = self._derive_method_name(action_lower, "click")
                        script.append(f"        {current_page.lower()}Page.{method_name}();")
                        
                    elif "enter" in action_lower or "type" in action_lower:
                        method_name = self._derive_method_name(action_lower, "enter")
                        script.append(f"        {current_page.lower()}Page.{method_name}({input_data});")
                        
                    elif "select" in action_lower:
                        method_name = self._derive_method_name(action_lower, "select")
                        script.append(f"        {current_page.lower()}Page.{method_name}({input_data});")
                        
                    script.append(f"        System.out.println(\"{step.get('expectedResult', 'Action performed')}\");")
                    script.append("")
                
            elif step_type == "VALIDATION":
                if current_page:
                    # Add validation code
                    script.append(f"        // {step.get('action', 'Validate result')}")
                    script.append(f"        // TODO: Add assertions to validate {step.get('expectedResult', 'expected result')}")
                    script.append(f"        // Example: Assertions.assertTrue({current_page.lower()}Page.verifySuccess());")
                    script.append("")
        
        # Add verification for the final expected result
        script.append("        // Verify final expected result")
        script.append(f"        System.out.println(\"Expected result: {test_case.get('expectedResult', 'Test completed')}\");")
        script.append("        // TODO: Add final verification steps")
        script.append("")
        
        # Close the method and class
        script.append("    }")
        script.append("")
        script.append("    @AfterEach")
        script.append("    public void tearDown() {")
        script.append("        if (driver != null) {")
        script.append("            driver.quit();")
        script.append("        }")
        script.append("    }")
        script.append("}")
        
        # Combine all code
        full_script = "\n\n".join(page_objects) + "\n\n" + "\n".join(script)
        
        return full_script
    
    def _generate_page_object_class(self, page_id, page_name, test_case):
        """
        Generate a Page Object class for the given page.
        
        Args:
            page_id: ID of the page
            page_name: Name of the page
            test_case: The test case object
            
        Returns:
            Page Object class code
        """
        # Collect components for this page
        components = {}
        for step in test_case.get("steps", []):
            if step.get("pageId") == page_id and step.get("componentId"):
                component_id = step.get("componentId")
                action = step.get("action", "")
                
                # Skip if this component is already processed
                if component_id in components:
                    continue
                
                # Derive component name from action
                component_name = self._derive_component_name(action)
                if component_name:
                    components[component_id] = component_name
        
        # Generate the page object class
        class_code = [
            f"import org.openqa.selenium.By;",
            f"import org.openqa.selenium.WebDriver;",
            f"import org.openqa.selenium.WebElement;",
            f"import org.openqa.selenium.support.ui.ExpectedConditions;",
            f"import org.openqa.selenium.support.ui.WebDriverWait;",
            f"import org.openqa.selenium.support.ui.Select;",
            f"import java.time.Duration;",
            f"",
            f"public class {page_name}Page {{",
            f"    private WebDriver driver;",
            f"    private WebDriverWait wait;",
            f""
        ]
        
        # Add URL (derived from page name)
        url = f"https://example.com/{page_name.lower().replace(' ', '_')}"
        class_code.append(f"    private String pageUrl = \"{url}\";")
        class_code.append("")
        
        # Add locators for components
        class_code.append("    // Page locators")
        for component_id, component_name in components.items():
            selector = f"By.id(\"{component_id}\")"  # Default to ID selector
            class_code.append(f"    private By {component_name}Locator = {selector};")
        class_code.append("")
        
        # Add constructor
        class_code.append("    // Constructor")
        class_code.append("    public " + page_name + "Page(WebDriver driver) {")
        class_code.append("        this.driver = driver;")
        class_code.append("        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));")
        class_code.append("    }")
        class_code.append("")
        
        # Add navigation method
        class_code.append("    // Navigation")
        class_code.append("    public void navigateTo() {")
        class_code.append("        driver.get(pageUrl);")
        class_code.append("    }")
        class_code.append("")
        
        # Add methods for each component
        class_code.append("    // Page methods")
        
        # Find the actions related to this page
        for step in test_case.get("steps", []):
            if step.get("pageId") == page_id and step.get("componentId") and step.get("componentId") in components:
                component_id = step.get("componentId")
                component_name = components[component_id]
                action = step.get("action", "")
                action_lower = action.lower()
                step_type = step.get("stepType", "INTERACTION")
                
                if step_type == "INTERACTION":
                    # Generate appropriate method based on the action
                    if "click" in action_lower:
                        method_name = self._derive_method_name(action_lower, "click")
                        class_code.append(f"    public void {method_name}() {{")
                        class_code.append(f"        WebElement element = wait.until(ExpectedConditions.elementToBeClickable({component_name}Locator));")
                        class_code.append(f"        element.click();")
                        class_code.append(f"    }}")
                        class_code.append("")
                        
                    elif "enter" in action_lower or "type" in action_lower:
                        method_name = self._derive_method_name(action_lower, "enter")
                        class_code.append(f"    public void {method_name}(String text) {{")
                        class_code.append(f"        WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated({component_name}Locator));")
                        class_code.append(f"        element.clear();")
                        class_code.append(f"        element.sendKeys(text);")
                        class_code.append(f"    }}")
                        class_code.append("")
                        
                    elif "select" in action_lower:
                        method_name = self._derive_method_name(action_lower, "select")
                        class_code.append(f"    public void {method_name}(String option) {{")
                        class_code.append(f"        WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated({component_name}Locator));")
                        class_code.append(f"        Select dropdown = new Select(element);")
                        class_code.append(f"        dropdown.selectByVisibleText(option);")
                        class_code.append(f"    }}")
                        class_code.append("")
        
        # Add verification method
        class_code.append("    // Verification methods")
        class_code.append("    public boolean verifyPageLoaded() {")
        class_code.append("        return driver.getTitle().contains(\"" + page_name + "\");")
        class_code.append("    }")
        class_code.append("")
        
        class_code.append("    public boolean verifySuccess() {")
        class_code.append("        // TODO: Implement success verification logic")
        class_code.append("        return true;")
        class_code.append("    }")
        class_code.append("")
        
        # Close the class
        class_code.append("}")
        
        return "\n".join(class_code)
    
    def _sanitize_class_name(self, name):
        """
        Convert a test case name to a valid Java class name.
        
        Args:
            name: The original name
            
        Returns:
            A valid Java class name
        """
        if not name:
            return "GeneratedTest"
            
        # Remove invalid characters and spaces
        sanitized = re.sub(r'[^a-zA-Z0-9 ]', '', name)
        
        # Convert to CamelCase
        words = sanitized.split()
        class_name = ''.join(word.capitalize() for word in words)
        
        # Ensure it starts with a letter
        if not class_name or not class_name[0].isalpha():
            class_name = "Test" + class_name
            
        # Ensure it's not empty
        if not class_name:
            class_name = "GeneratedTest"
            
        return class_name
    
    def _sanitize_method_name(self, name):
        """
        Convert a test case name to a valid Java method name.
        
        Args:
            name: The original name
            
        Returns:
            A valid Java method name
        """
        if not name:
            return "testMethod"
            
        # Remove invalid characters and spaces
        sanitized = re.sub(r'[^a-zA-Z0-9 ]', '', name)
        
        # Convert to camelCase
        words = sanitized.split()
        if not words:
            return "testMethod"
            
        method_name = words[0].lower()
        for word in words[1:]:
            method_name += word.capitalize()
            
        # Ensure it starts with a letter
        if not method_name[0].isalpha():
            method_name = "test" + method_name
            
        return method_name
    
    def _generate_selector_for_component(self, component_id, step):
        """
        Generate a Selenium selector for the component.
        
        Args:
            component_id: ID of the component
            step: The test step with additional component info
            
        Returns:
            Selenium selector code
        """
        if component_id:
            # If we have a component ID, use it
            return f"By.id(\"{component_id}\")"
        
        # Otherwise, try to derive a selector from the step action
        action = step.get("action", "")
        element_type = step.get("elementType", "").lower()
        
        # Look for element type hints in the action
        if "Username" in action or "username" in action:
            return "By.cssSelector(\"input[name='username'], input[id='username'], input[type='text'][placeholder*='username']\")"
        elif "Password" in action or "password" in action:
            return "By.cssSelector(\"input[name='password'], input[id='password'], input[type='password']\")"
        elif "Email" in action or "email" in action:
            return "By.cssSelector(\"input[name='email'], input[id='email'], input[type='email']\")"
        elif "Login" in action or "login" in action or "Sign In" in action:
            return "By.cssSelector(\"button[type='submit'], input[type='submit'], button:contains('Login'), button:contains('Sign In')\")"
        # Consider element type if provided
        elif element_type == "text" or element_type == "input":
            return "By.tagName(\"input\")"
        elif element_type == "button":
            return "By.tagName(\"button\")"
        elif element_type == "select":
            return "By.tagName(\"select\")"
        elif element_type == "checkbox":
            return "By.cssSelector(\"input[type='checkbox']\")"
        elif element_type == "radio":
            return "By.cssSelector(\"input[type='radio']\")"
        elif element_type == "link":
            return "By.tagName(\"a\")"
        else:
            # Generic selector based on action text
            element_name = re.sub(r'[^a-zA-Z0-9]', '', action.lower())
            return f"By.id(\"{element_name}\")"
        
            
    def _generate_cypress_selector(self, component_id, step):
        """
        Generate a Cypress selector for the component.
        
        Args:
            component_id: ID of the component
            step: The test step with additional component info
            
        Returns:
            Cypress selector
        """
        if component_id:
            # If we have a component ID, use it
            return f"#{component_id}"
        
        # Otherwise, try to derive a selector from the step action and element type
        action = step.get("action", "")
        element_type = step.get("elementType", "").lower()
        
        # Look for element type hints in the action
        if "Username" in action or "username" in action:
            return "input[name='username'], input#username, input[placeholder*='username']"
        elif "Password" in action or "password" in action:
            return "input[name='password'], input#password, input[type='password']"
        elif "Email" in action or "email" in action:
            return "input[name='email'], input#email, input[type='email']"
        elif "Login" in action or "login" in action or "Sign In" in action:
            return "button[type='submit'], input[type='submit'], button:contains('Login'), button:contains('Sign In')"
        # Consider element type if provided
        elif element_type == "text" or element_type == "input":
            return "input"
        elif element_type == "button":
            return "button"
        elif element_type == "select":
            return "select"
        elif element_type == "checkbox":
            return "input[type='checkbox']"
        elif element_type == "radio":
            return "input[type='radio']"
        elif element_type == "link":
            return "a"
        else:
            # Generate a data-testid selector as a fallback
            element_name = re.sub(r'[^a-zA-Z0-9]', '', action.lower())
            return f"[data-testid='{element_name}']"
    
    def _generate_playwright_selector(self, component_id, step):
        """
        Generate a Playwright selector for the component.
        
        Args:
            component_id: ID of the component
            step: The test step with additional component info
            
        Returns:
            Playwright selector
        """
        if component_id:
            # If we have a component ID, use it
            return f"#{component_id}"
        
        # Otherwise, try to derive a selector from the step action and element type
        action = step.get("action", "")
        element_type = step.get("elementType", "").lower()
        
        # Look for element type hints in the action
        if "Username" in action or "username" in action:
            return "input[name='username'], input#username, input[placeholder*='username']"
        elif "Password" in action or "password" in action:
            return "input[name='password'], input#password, input[type='password']"
        elif "Email" in action or "email" in action:
            return "input[name='email'], input#email, input[type='email']"
        elif "Login" in action or "login" in action or "Sign In" in action:
            return "button[type='submit'], input[type='submit'], text=Login, text=Sign In"
        # Consider element type if provided
        elif element_type == "text" or element_type == "input":
            return "input"
        elif element_type == "button":
            return "button"
        elif element_type == "select":
            return "select"
        elif element_type == "checkbox":
            return "input[type='checkbox']"
        elif element_type == "radio":
            return "input[type='radio']"
        elif element_type == "link":
            return "a"
        else:
            # Generate a data-testid selector as a fallback
            element_name = re.sub(r'[^a-zA-Z0-9]', '', action.lower())
            return f"[data-testid='{element_name}']"
    
    def _derive_method_name(self, action, action_type):
        """
        Derive a method name from the action text.
        
        Args:
            action: The action text
            action_type: The type of action (click, enter, select)
            
        Returns:
            A method name
        """
        # Clean up the action text
        cleaned = re.sub(r'[^a-zA-Z0-9 ]', '', action.lower())
        
        # Extract the component name
        component_name = None
        
        if action_type == "click":
            match = re.search(r'click\s+(?:on\s+)?(?:the\s+)?([a-z0-9 ]+)', cleaned)
            if match:
                component_name = match.group(1)
        elif action_type == "enter":
            match = re.search(r'(?:enter|type)\s+(?:[a-z0-9 ]+\s+in\s+(?:the\s+)?|in\s+(?:the\s+)?)([a-z0-9 ]+)', cleaned)
            if match:
                component_name = match.group(1)
        elif action_type == "select":
            match = re.search(r'select\s+(?:[a-z0-9 ]+\s+from\s+(?:the\s+)?|from\s+(?:the\s+)?)([a-z0-9 ]+)', cleaned)
            if match:
                component_name = match.group(1)
        
        # Convert to camelCase method name
        if component_name:
            words = component_name.split()
            method_name = action_type
            for word in words:
                if word not in ["the", "a", "an"]:
                    method_name += word.capitalize()
        else:
            # If we couldn't parse a component name, use a generic method name
            method_name = action_type + "Element"
        
        return method_name
    
    def _derive_component_name(self, action):
        """
        Derive a component name from the action text.
        
        Args:
            action: The action text
            
        Returns:
            A component name or None if not found
        """
        # Clean up the action text
        cleaned = action.lower()
        
        # Try different patterns to extract the component name
        patterns = [
            r'click\s+(?:on\s+)?(?:the\s+)?([a-z0-9 ]+\b)',
            r'(?:enter|type)\s+(?:[a-z0-9 ]+\s+in\s+(?:the\s+)?|in\s+(?:the\s+)?)([a-z0-9 ]+\b)',
            r'select\s+(?:[a-z0-9 ]+\s+from\s+(?:the\s+)?|from\s+(?:the\s+)?)([a-z0-9 ]+\b)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, cleaned)
            if match:
                component_text = match.group(1).strip()
                # Remove common words
                for word in ["button", "field", "input", "select", "dropdown", "checkbox", "the", "a", "an"]:
                    component_text = re.sub(rf'\b{word}\b', '', component_text).strip()
                
                # Convert to camelCase
                if component_text:
                    words = component_text.split()
                    component_name = words[0].lower()
                    for word in words[1:]:
                        component_name += word.capitalize()
                    return component_name
        
        return None