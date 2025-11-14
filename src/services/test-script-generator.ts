/**
 * Test Script Generator - Generates test scripts for various frameworks
 * Simplified TypeScript version maintaining core functionality
 */

import { TestCase } from '../types';
import logger from '../config/logger';

export class TestScriptGenerator {
  private testDataTemplates: Record<string, Record<string, string>> = {
    selenium: {
      valid_username: 'testuser',
      valid_password: 'Password123!',
      valid_email: 'test@example.com',
      invalid_username: 'us',
      invalid_password: 'pass',
      invalid_email: 'not-an-email',
      search_term: 'test product',
      no_results_search_term: 'xyznotfound123'
    },
    cypress: {
      valid_username: 'testuser',
      valid_password: 'Password123!',
      valid_email: 'test@example.com',
      invalid_username: 'us',
      invalid_password: 'pass',
      invalid_email: 'not-an-email',
      search_term: 'test product',
      no_results_search_term: 'xyznotfound123'
    },
    playwright: {
      valid_username: 'testuser',
      valid_password: 'Password123!',
      valid_email: 'test@example.com',
      invalid_username: 'us',
      invalid_password: 'pass',
      invalid_email: 'not-an-email',
      search_term: 'test product',
      no_results_search_term: 'xyznotfound123'
    }
  };

  generateScript(testCase: TestCase, testData: Record<string, any>, framework: string = 'selenium'): string {
    const testName = testCase.name || 'Unknown Test';
    logger.info(`Generating ${framework} script for test case: ${testName}`);

    switch (framework) {
      case 'selenium':
        return this.generateSeleniumScript(testCase, testData);
      case 'cypress':
        return this.generateCypressScript(testCase, testData);
      case 'playwright':
        return this.generatePlaywrightScript(testCase, testData);
      default:
        throw new Error(`Unsupported framework: ${framework}`);
    }
  }

  private generateSeleniumScript(testCase: TestCase, testData: Record<string, any>): string {
    const className = this.sanitizeClassName(testCase.name || 'GeneratedTest');
    const lines: string[] = [
      'import org.openqa.selenium.By;',
      'import org.openqa.selenium.WebDriver;',
      'import org.openqa.selenium.WebElement;',
      'import org.openqa.selenium.chrome.ChromeDriver;',
      'import org.openqa.selenium.support.ui.ExpectedConditions;',
      'import org.openqa.selenium.support.ui.WebDriverWait;',
      'import java.time.Duration;',
      'import org.junit.jupiter.api.AfterEach;',
      'import org.junit.jupiter.api.BeforeEach;',
      'import org.junit.jupiter.api.Test;',
      '',
      `public class ${className} {`,
      '    private WebDriver driver;',
      '    private WebDriverWait wait;',
      '',
      '    @BeforeEach',
      '    public void setUp() {',
      '        driver = new ChromeDriver();',
      '        driver.manage().window().maximize();',
      '        wait = new WebDriverWait(driver, Duration.ofSeconds(10));',
      '    }',
      '',
      '    @Test',
      `    public void ${this.sanitizeMethodName(testCase.name || 'testMethod')}() {`
    ];

    // Add test data
    lines.push('        // Test data');
    const template = this.testDataTemplates.selenium;
    for (const [key, value] of Object.entries(template)) {
      const dataValue = testData[key] || value;
      lines.push(`        String ${key} = "${dataValue}";`);
    }
    lines.push('');

    // Add test steps
    lines.push('        // Test steps');
    for (const step of testCase.steps) {
      if (step.stepType === 'NAVIGATION') {
        lines.push(`        // ${step.action}`);
        lines.push(`        driver.get("${step.url || 'https://example.com'}");`);
        lines.push(`        System.out.println("${step.expectedResult}");`);
        lines.push('');
      } else if (step.stepType === 'INTERACTION') {
        lines.push(`        // ${step.action}`);
        const selector = step.componentId ? `By.id("${step.componentId}")` : 'By.tagName("input")';
        
        if (step.action.toLowerCase().includes('click')) {
          lines.push(`        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(${selector}));`);
          lines.push('        element.click();');
        } else if (step.action.toLowerCase().includes('enter') || step.action.toLowerCase().includes('type')) {
          const inputData = this.processInputData(step.inputData || '', template);
          lines.push(`        WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated(${selector}));`);
          lines.push('        element.clear();');
          lines.push(`        element.sendKeys(${inputData});`);
        }
        lines.push(`        System.out.println("${step.expectedResult}");`);
        lines.push('');
      }
    }

    lines.push('    }');
    lines.push('');
    lines.push('    @AfterEach');
    lines.push('    public void tearDown() {');
    lines.push('        if (driver != null) {');
    lines.push('            driver.quit();');
    lines.push('        }');
    lines.push('    }');
    lines.push('}');

    return lines.join('\n');
  }

  private generateCypressScript(testCase: TestCase, testData: Record<string, any>): string {
    const lines: string[] = [
      `// Cypress test script`,
      `// Test: ${testCase.name || 'Generated Test'}`,
      '',
      `describe('${(testCase.name || 'Generated Test').replace(/'/g, "\\'")}', () => {`,
      '  // Test data'
    ];

    const template = this.testDataTemplates.cypress;
    for (const [key, value] of Object.entries(template)) {
      const dataValue = testData[key] || value;
      lines.push(`  const ${key} = '${dataValue}';`);
    }
    lines.push('');

    lines.push(`  it('${(testCase.description || 'should complete the test flow').replace(/'/g, "\\'")}', () => {`);

    for (const step of testCase.steps) {
      if (step.stepType === 'NAVIGATION') {
        lines.push(`    // ${step.action}`);
        lines.push(`    cy.visit('${step.url || '/'}');`);
        lines.push(`    cy.log('${step.expectedResult}');`);
        lines.push('');
      } else if (step.stepType === 'INTERACTION') {
        lines.push(`    // ${step.action}`);
        const selector = step.componentId ? `#${step.componentId}` : 'input';
        
        if (step.action.toLowerCase().includes('click')) {
          lines.push(`    cy.get('${selector}').click();`);
        } else if (step.action.toLowerCase().includes('enter') || step.action.toLowerCase().includes('type')) {
          const inputData = this.processInputData(step.inputData || '', template);
          lines.push(`    cy.get('${selector}').clear().type(${inputData});`);
        }
        lines.push(`    cy.log('${step.expectedResult}');`);
        lines.push('');
      }
    }

    lines.push('  });');
    lines.push('});');

    return lines.join('\n');
  }

  private generatePlaywrightScript(testCase: TestCase, testData: Record<string, any>): string {
    const lines: string[] = [
      `// Playwright test script`,
      `// Test: ${testCase.name || 'Generated Test'}`,
      '',
      "const { test, expect } = require('@playwright/test');",
      '',
      '// Test data'
    ];

    const template = this.testDataTemplates.playwright;
    for (const [key, value] of Object.entries(template)) {
      const dataValue = testData[key] || value;
      lines.push(`const ${key} = '${dataValue}';`);
    }
    lines.push('');

    lines.push(`test('${(testCase.name || 'Generated Test').replace(/'/g, "\\'")}', async ({ page }) => {`);

    for (const step of testCase.steps) {
      if (step.stepType === 'NAVIGATION') {
        lines.push(`  // ${step.action}`);
        lines.push(`  await page.goto('${step.url || '/'}');`);
        lines.push(`  console.log('${step.expectedResult}');`);
        lines.push('');
      } else if (step.stepType === 'INTERACTION') {
        lines.push(`  // ${step.action}`);
        const selector = step.componentId ? `#${step.componentId}` : 'input';
        
        if (step.action.toLowerCase().includes('click')) {
          lines.push(`  await page.click('${selector}');`);
        } else if (step.action.toLowerCase().includes('enter') || step.action.toLowerCase().includes('type')) {
          const inputData = this.processInputData(step.inputData || '', template);
          lines.push(`  await page.fill('${selector}', ${inputData});`);
        }
        lines.push(`  console.log('${step.expectedResult}');`);
        lines.push('');
      }
    }

    lines.push('});');

    return lines.join('\n');
  }

  private processInputData(inputData: string, _template: Record<string, string>): string {
    if (inputData.startsWith('{{') && inputData.endsWith('}}')) {
      const varName = inputData.slice(2, -2);
      return varName;
    }
    return `"${inputData}"`;
  }

  private sanitizeClassName(name: string): string {
    return name.replace(/[^a-zA-Z0-9 ]/g, '').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('') || 'GeneratedTest';
  }

  private sanitizeMethodName(name: string): string {
    const words = name.replace(/[^a-zA-Z0-9 ]/g, '').split(' ');
    if (words.length === 0) return 'testMethod';
    return words[0].toLowerCase() + words.slice(1).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('');
  }
}

