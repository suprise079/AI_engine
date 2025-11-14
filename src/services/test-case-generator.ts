/**
 * Test Case Generator - Generates test cases from identified pages and components
 * Simplified TypeScript version maintaining core functionality
 */

import { Page, TestCase, TestStep, Action } from '../types';
import logger from '../config/logger';

export class TestCaseGenerator {
  // Test data reserved for future use
  // private testData = {
  //   email: ['user@example.com', 'test.user@domain.co', 'invalid-email', '', 'very.long.email.address.that.might.exceed.maximum.length.restrictions@example.com'],
  //   password: ['Password123!', 'short', '12345678', '', 'AVeryLongPasswordThatMightExceedMaximumLengthRestrictions1234567890!@#$%^&*()'],
  //   text: ['Sample text', '', 'Special chars: !@#$%^&*()', 'A very long text input that might exceed maximum length restrictions for this field'],
  //   number: ['42', '0', '-1', '999999', 'abc', ''],
  //   phone: ['1234567890', '+1-123-456-7890', '123', ''],
  //   name: ['John Smith', '', 'John-Smith', 'A very long name that might exceed maximum length restrictions']
  // };

  generateTestCases(pages: Page[], recordedActions: Action[] = []): TestCase[] {
    logger.info(`Generating test cases from ${pages.length} pages and ${recordedActions.length} recorded actions`);
    const testCases: TestCase[] = [];

    // Generate page-based test cases
    for (const page of pages) {
      const pageType = page.pageType || 'GENERIC';
      const pageName = page.pageName || 'Unknown';
      logger.info(`Processing page: ${pageName} (Type: ${pageType})`);

      let pageTestCases: TestCase[] = [];

      switch (pageType) {
        case 'LOGIN':
          pageTestCases = this.generateLoginTestCases(page, pages, recordedActions);
          break;
        case 'REGISTRATION':
          pageTestCases = this.generateRegistrationTestCases(page, pages, recordedActions);
          break;
        case 'CHECKOUT':
          pageTestCases = this.generateCheckoutTestCases(page, pages, recordedActions);
          break;
        case 'SEARCH':
          pageTestCases = this.generateSearchTestCases(page, pages, recordedActions);
          break;
        default:
          pageTestCases = this.generateGenericTestCases(page, pages, recordedActions);
      }

      logger.info(`Generated ${pageTestCases.length} test cases for page: ${pageName}`);
      testCases.push(...pageTestCases);
    }

    // Generate cross-page test cases
    if (pages.length >= 2) {
      const flowTestCases = this.generateUserFlowTestCases(pages, recordedActions);
      logger.info(`Generated ${flowTestCases.length} user flow test cases`);
      testCases.push(...flowTestCases);
    }

    logger.info(`Total test cases generated: ${testCases.length}`);
    return testCases;
  }

  private generateLoginTestCases(page: Page, _allPages: Page[], _recordedActions: Action[]): TestCase[] {
    const testCases: TestCase[] = [];
    const components = page.components || [];

    const usernameField = this.findComponentByTypeAndName(components, 'input', ['username', 'email', 'user']);
    const passwordField = this.findComponentByTypeAndName(components, 'input', ['password', 'pass']);
    const loginButton = this.findComponentByTypeAndName(components, 'button', ['login', 'sign in', 'submit']);

    if (usernameField && passwordField && loginButton) {
      // Valid login
      testCases.push({
        name: 'Valid Login Test',
        description: 'Verify that a user can login with valid credentials',
        preconditions: ['User has a valid account'],
        steps: [
          { action: `Navigate to ${page.pageName}`, expectedResult: 'Login page is displayed', pageId: page.id, stepType: 'NAVIGATION' },
          { action: `Enter valid username in ${usernameField.name}`, expectedResult: 'Username is accepted', componentId: usernameField.id, inputData: '{{valid_username}}', stepType: 'INTERACTION' },
          { action: `Enter valid password in ${passwordField.name}`, expectedResult: 'Password is accepted', componentId: passwordField.id, inputData: '{{valid_password}}', stepType: 'INTERACTION' },
          { action: `Click ${loginButton.name}`, expectedResult: 'User is logged in and redirected to dashboard', componentId: loginButton.id, stepType: 'INTERACTION' }
        ],
        expectedResult: 'User is successfully logged in',
        category: 'Authentication',
        priority: 'HIGH'
      });

      // Invalid login
      testCases.push({
        name: 'Invalid Login Test',
        description: 'Verify that a user cannot login with invalid credentials',
        preconditions: ['User has a registered account'],
        steps: [
          { action: `Navigate to ${page.pageName}`, expectedResult: 'Login page is displayed', pageId: page.id, stepType: 'NAVIGATION' },
          { action: `Enter invalid username in ${usernameField.name}`, expectedResult: 'Username is accepted', componentId: usernameField.id, inputData: '{{invalid_username}}', stepType: 'INTERACTION' },
          { action: `Enter invalid password in ${passwordField.name}`, expectedResult: 'Password is accepted', componentId: passwordField.id, inputData: '{{invalid_password}}', stepType: 'INTERACTION' },
          { action: `Click ${loginButton.name}`, expectedResult: 'Error message is displayed', componentId: loginButton.id, stepType: 'INTERACTION' }
        ],
        expectedResult: 'User is not logged in and an appropriate error message is displayed',
        category: 'Authentication',
        priority: 'HIGH'
      });
    }

    return testCases;
  }

  private generateRegistrationTestCases(page: Page, _allPages: Page[], _recordedActions: Action[]): TestCase[] {
    const testCases: TestCase[] = [];
    const components = page.components || [];

    const emailField = this.findComponentByTypeAndName(components, 'input', ['email']);
    const passwordField = this.findComponentByTypeAndName(components, 'input', ['password', 'pass']);
    const registerButton = this.findComponentByTypeAndName(components, 'button', ['register', 'sign up', 'create', 'submit']);

    if ((emailField || this.findComponentByTypeAndName(components, 'input', ['username'])) && passwordField && registerButton) {
      const steps: TestStep[] = [
        { action: `Navigate to ${page.pageName}`, expectedResult: 'Registration page is displayed', pageId: page.id, stepType: 'NAVIGATION' }
      ];

      if (emailField) {
        steps.push({ action: `Enter valid email in ${emailField.name}`, expectedResult: 'Email is accepted', componentId: emailField.id, inputData: '{{valid_email}}', stepType: 'INTERACTION' });
      }

      steps.push(
        { action: `Enter valid password in ${passwordField.name}`, expectedResult: 'Password is accepted', componentId: passwordField.id, inputData: '{{valid_password}}', stepType: 'INTERACTION' },
        { action: `Click ${registerButton.name}`, expectedResult: 'Registration is successful', componentId: registerButton.id, stepType: 'INTERACTION' }
      );

      testCases.push({
        name: 'Valid Registration Test',
        description: 'Verify that a user can register with valid information',
        preconditions: ['User does not have an existing account'],
        steps,
        expectedResult: 'User account is created successfully',
        category: 'Registration',
        priority: 'HIGH'
      });
    }

    return testCases;
  }

  private generateCheckoutTestCases(page: Page, _allPages: Page[], _recordedActions: Action[]): TestCase[] {
    const testCases: TestCase[] = [];
    const components = page.components || [];

    const paymentFields = components.filter(c => c.componentType === 'input' && 
      ['card', 'credit', 'payment', 'ccv', 'cvv', 'expiry'].some(term => c.name.toLowerCase().includes(term)));
    const orderButton = this.findComponentByTypeAndName(components, 'button', ['place order', 'submit', 'pay', 'checkout', 'complete']);

    if (paymentFields.length > 0 && orderButton) {
      const steps: TestStep[] = [
        { action: `Navigate to ${page.pageName}`, expectedResult: 'Checkout page is displayed with items and total', pageId: page.id, stepType: 'NAVIGATION' }
      ];

      for (const field of paymentFields.slice(0, 3)) {
        steps.push({ action: `Enter valid ${field.name}`, expectedResult: 'Information is accepted', componentId: field.id, inputData: '{{valid_payment_data}}', stepType: 'INTERACTION' });
      }

      steps.push({ action: `Click ${orderButton.name}`, expectedResult: 'Order is processed', componentId: orderButton.id, stepType: 'INTERACTION' });

      testCases.push({
        name: 'Successful Checkout Test',
        description: 'Verify that a user can complete the checkout process',
        preconditions: ['User has items in their cart', 'User is logged in (if required)'],
        steps,
        expectedResult: 'Order is placed successfully and confirmation is shown',
        category: 'E-commerce',
        priority: 'HIGH'
      });
    }

    return testCases;
  }

  private generateSearchTestCases(page: Page, _allPages: Page[], _recordedActions: Action[]): TestCase[] {
    const testCases: TestCase[] = [];
    const components = page.components || [];

    const searchField = this.findComponentByTypeAndName(components, 'input', ['search', 'query', 'find']);
    const searchButton = this.findComponentByTypeAndName(components, 'button', ['search', 'find', 'go']);

    if (searchField) {
      const steps: TestStep[] = [
        { action: `Navigate to ${page.pageName}`, expectedResult: 'Search page is displayed', pageId: page.id, stepType: 'NAVIGATION' },
        { action: `Enter search term in ${searchField.name}`, expectedResult: 'Search term is entered', componentId: searchField.id, inputData: '{{search_term}}', stepType: 'INTERACTION' }
      ];

      if (searchButton) {
        steps.push({ action: `Click ${searchButton.name}`, expectedResult: 'Search results are displayed', componentId: searchButton.id, stepType: 'INTERACTION' });
      } else {
        steps.push({ action: 'Press Enter key in search field', expectedResult: 'Search results are displayed', componentId: searchField.id, stepType: 'INTERACTION' });
      }

      testCases.push({
        name: 'Basic Search Functionality Test',
        description: 'Verify that the search functionality works correctly',
        preconditions: [],
        steps,
        expectedResult: 'Search results are displayed and relevant to the search term',
        category: 'Search',
        priority: 'HIGH'
      });
    }

    return testCases;
  }

  private generateGenericTestCases(page: Page, _allPages: Page[], _recordedActions: Action[]): TestCase[] {
    const testCases: TestCase[] = [];

    testCases.push({
      name: `${page.pageName} Load Test`,
      description: `Verify that ${page.pageName} loads correctly`,
      preconditions: [],
      steps: [
        { action: `Navigate to ${page.pageName}`, expectedResult: `${page.pageName} is displayed correctly with all elements`, pageId: page.id, stepType: 'NAVIGATION' }
      ],
      expectedResult: 'Page loads with all components displayed correctly',
      category: 'UI',
      priority: 'MEDIUM'
    });

    return testCases;
  }

  private generateUserFlowTestCases(pages: Page[], _recordedActions: Action[]): TestCase[] {
    const testCases: TestCase[] = [];

    if (pages.length >= 3) {
      const steps: TestStep[] = [];
      for (let i = 0; i < Math.min(5, pages.length); i++) {
        steps.push({
          action: `Navigate to ${pages[i].pageName}`,
          expectedResult: `${pages[i].pageName} is displayed correctly`,
          pageId: pages[i].id,
          stepType: 'NAVIGATION'
        });
      }

      testCases.push({
        name: 'End-to-End User Flow Test',
        description: 'Verify the complete end-to-end user flow through the application',
        preconditions: [],
        steps,
        expectedResult: 'User can navigate through the entire flow successfully',
        category: 'User Flow',
        priority: 'HIGH'
      });
    }

    return testCases;
  }

  private findComponentByTypeAndName(components: any[], componentType: string, nameKeywords: string[]): any | null {
    for (const component of components) {
      if (component.componentType === componentType) {
        const componentName = (component.name || '').toLowerCase();
        if (nameKeywords.some(keyword => componentName.includes(keyword.toLowerCase()))) {
          return component;
        }
      }
    }

    for (const component of components) {
      if (component.componentType === componentType) {
        return component;
      }
    }

    return null;
  }
}

