/**
 * Component Recognizer - Recognizes UI components from recorded actions
 */

import { Action, Page, Component } from '../types';
import logger from '../config/logger';
import { URL } from 'url';

export class ComponentRecognizer {
  private pageTransitionMarkers: string[] = ['NAVIGATE', 'SUBMIT', 'PAGE_LOAD'];
  
  private selectorPatterns: Record<string, RegExp[]> = {
    button: [
      /button/i,
      /btn/i,
      /submit/i,
      /cancel/i
    ],
    input: [
      /input/i,
      /text/i,
      /field/i,
      /email/i,
      /password/i
    ],
    select: [
      /select/i,
      /dropdown/i,
      /combobox/i
    ],
    checkbox: [
      /checkbox/i,
      /check/i
    ],
    radio: [
      /radio/i
    ],
    link: [
      /link/i,
      /anchor/i
    ],
    table: [
      /table/i,
      /grid/i,
      /data-table/i
    ],
    form: [
      /form/i,
      /login-form/i,
      /registration-form/i,
      /signup-form/i
    ]
  };

  private fieldTypes: Record<string, RegExp> = {
    text: /text|input|field/i,
    email: /email|e-mail/i,
    password: /password|pwd|pass/i,
    number: /number|num|qty|quantity|amount/i,
    date: /date|calendar|dob|birth/i,
    time: /time|hour|minute/i,
    tel: /tel|phone|mobile|cell/i,
    url: /url|website|web|link/i,
    search: /search|find|query/i,
    file: /file|upload|attachment/i
  };

  identifyPagesAndComponents(actions: Action[]): Page[] {
    logger.info(`Starting page and component identification for ${actions.length} actions`);
    const pages: Page[] = [];
    let currentPage: Page | null = null;
    let pageActions: Action[] = [];

    // First pass: split actions into page groups
    for (const action of actions) {
      if (this.isPageTransition(action)) {
        if (currentPage && pageActions.length > 0) {
          // Complete the current page
          const components = this.extractComponents(pageActions);
          currentPage.components = components;
          pages.push(currentPage);
        }

        // Start a new page
        currentPage = this.createPageFromAction(action);
        pageActions = [action];
      } else if (currentPage) {
        // Add to current page's actions
        pageActions.push(action);
      }
    }

    // Don't forget the last page
    if (currentPage && pageActions.length > 0) {
      const components = this.extractComponents(pageActions);
      currentPage.components = components;
      pages.push(currentPage);
    }

    // Second pass: refine component identification
    logger.info(`Identified ${pages.length} pages before refinement`);
    const refinedPages = this.refinePageComponents(pages);

    // Log final results
    const totalComponents = refinedPages.reduce((sum, page) => sum + page.components.length, 0);
    logger.info(`Final result: ${refinedPages.length} pages with ${totalComponents} total components`);
    for (let i = 0; i < refinedPages.length; i++) {
      const page = refinedPages[i];
      const components = page.components;
      logger.info(`Page ${i + 1}: ${page.pageName} (${page.pageType}) - ${components.length} components`);
      for (let j = 0; j < Math.min(5, components.length); j++) {
        logger.debug(`  Component ${j + 1}: ${components[j].name} (${components[j].componentType})`);
      }
    }

    return refinedPages;
  }

  private isPageTransition(action: Action): boolean {
    return this.pageTransitionMarkers.includes(action.actionType);
  }

  private createPageFromAction(action: Action): Page {
    let url = action.url || '';
    let title = action.pageTitle || '';

    // If no title, try to generate one from URL
    if (!title && url) {
      try {
        const parsedUrl = new URL(url);
        const domain = parsedUrl.hostname;
        const path = parsedUrl.pathname;

        // Generate title from path if available, otherwise use domain
        if (path && path !== '/') {
          // Remove leading/trailing slashes and convert to title case
          const pathParts = path.replace(/^\/|\/$/g, '').split('/');
          title = pathParts.map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(' ');
        } else {
          title = domain;
        }
      } catch {
        title = 'Unknown Page';
      }
    }

    // Generate page type from title or URL
    const pageType = this.determinePageType(title, url);

    // Create identification rules
    const identificationRules = {
      url_contains: [this.extractKeyTerm(url)],
      title_contains: [this.extractKeyTerm(title)]
    };

    return {
      pageName: title || 'Unknown Page',
      urlPattern: url,
      pageType: pageType,
      identificationRules: identificationRules,
      components: []
    };
  }

  private determinePageType(title: string, url: string): string {
    const titleLower = (title || '').toLowerCase();
    const urlLower = (url || '').toLowerCase();

    const loginTerms = ['login', 'signin', 'sign-in'];
    const registerTerms = ['register', 'signup', 'sign-up', 'registration'];
    const checkoutTerms = ['checkout', 'payment', 'billing'];
    const searchTerms = ['search', 'results', 'find'];
    const dashboardTerms = ['dashboard', 'home', 'main'];
    const profileTerms = ['profile', 'account', 'settings'];
    const confirmationTerms = ['confirm', 'success', 'thank', 'complete'];

    if (loginTerms.some(term => titleLower.includes(term) || urlLower.includes(term))) {
      return 'LOGIN';
    } else if (registerTerms.some(term => titleLower.includes(term) || urlLower.includes(term))) {
      return 'REGISTRATION';
    } else if (checkoutTerms.some(term => titleLower.includes(term) || urlLower.includes(term))) {
      return 'CHECKOUT';
    } else if (searchTerms.some(term => titleLower.includes(term) || urlLower.includes(term))) {
      return 'SEARCH';
    } else if (dashboardTerms.some(term => titleLower.includes(term) || urlLower.includes(term))) {
      return 'DASHBOARD';
    } else if (profileTerms.some(term => titleLower.includes(term) || urlLower.includes(term))) {
      return 'PROFILE';
    } else if (confirmationTerms.some(term => titleLower.includes(term) || urlLower.includes(term))) {
      return 'CONFIRMATION';
    } else {
      return 'GENERIC';
    }
  }

  private extractKeyTerm(text: string): string {
    if (!text) {
      return '';
    }

    // Remove common prefixes and TLD
    let cleaned = text.replace(/^https?:\/\/(www\.)?/, '').replace(/\.(com|org|net|io|gov|edu).*$/, '');

    // Get the most specific part (last path segment or domain)
    const parts = cleaned.split(/[/\-_]/);
    const filteredParts = parts.filter(p => p && p.length > 2);

    return filteredParts.length > 0 ? filteredParts[filteredParts.length - 1] : cleaned;
  }

  private extractComponents(actions: Action[]): Component[] {
    const components: Component[] = [];
    const seenSelectors = new Set<string>();

    for (const action of actions) {
      const actionType = action.actionType;
      const selector = action.elementSelector;

      // Skip actions without selectors or already processed selectors
      if (!selector || seenSelectors.has(selector)) {
        continue;
      }

      seenSelectors.add(selector);

      // Create a component based on the action type
      let component: Component | null = null;

      if (actionType === 'CLICK' || actionType === 'SUBMIT') {
        component = this.detectButtonComponent(action);
      } else if (actionType === 'TYPE') {
        component = this.detectInputComponent(action);
      } else if (actionType === 'SELECT') {
        component = this.detectSelectComponent(action);
      } else if (actionType === 'CHANGE') {
        // Handle checkboxes and radios
        const elementType = (action.elementType || '').toLowerCase();
        if (elementType.includes('checkbox')) {
          component = this.detectCheckboxComponent(action);
        } else if (elementType.includes('radio')) {
          component = this.detectRadioComponent(action);
        } else {
          component = this.detectInputComponent(action);
        }
      } else {
        // For other action types, use generic detection
        component = this.detectGenericComponent(action);
      }

      if (component) {
        components.push(component);
      }
    }

    return components;
  }

  // Reserved for future use - form component detection
  /*
  private _detectFormComponent(action: Action): Component {
    const selector = action.elementSelector || '';
    const elementValue = action.elementValue;
    const description = action.description;

    // Determine form name
    let name = elementValue || description || 'Form';

    // Clean up name if needed
    if (name === 'Form' && selector) {
      const match = selector.match(/#([a-zA-Z0-9_-]+)/);
      if (match) {
        name = match[1].split(/[-_]/).map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
        if (!name.toLowerCase().includes('form')) {
          name += ' Form';
        }
      }
    }

    return {
      name: name.trim(),
      selector: selector,
      componentType: 'form',
      validationRules: null,
      expectedBehavior: 'Collects and submits user input',
      dataType: undefined,
      isRequired: undefined,
      children: []
    };
  }
  */

  private detectButtonComponent(action: Action): Component {
    const selector = action.elementSelector || '';
    const elementValue = action.elementValue;
    const description = action.description;

    // Determine button name
    let name = elementValue || description || 'Button';

    // Clean up name if needed
    if (name === 'Button' && selector) {
      const match = selector.match(/#([a-zA-Z0-9_-]+)/);
      if (match) {
        name = match[1].split(/[-_]/).map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
      }
    }

    // Determine if it's a submit button
    const expectedBehavior = (action.actionType === 'SUBMIT' || selector.toLowerCase().includes('submit'))
      ? 'Submits form'
      : 'Performs action';

    return {
      name: name.trim(),
      selector: selector,
      componentType: 'button',
      validationRules: null,
      expectedBehavior: expectedBehavior,
      dataType: undefined,
      isRequired: undefined
    };
  }

  private detectInputComponent(action: Action): Component {
    const selector = action.elementSelector || '';
    const elementType = action.elementType;

    // Determine input type
    let dataType = 'text'; // Default
    const isRequired = true; // Assume required by default

    // Check if it's a specific type of input
    if (elementType) {
      const lowercaseType = elementType.toLowerCase();
      if (lowercaseType.includes('password')) {
        dataType = 'password';
      } else if (lowercaseType.includes('email')) {
        dataType = 'email';
      } else if (lowercaseType.includes('number')) {
        dataType = 'number';
      } else if (lowercaseType.includes('tel') || lowercaseType.includes('phone')) {
        dataType = 'tel';
      } else if (lowercaseType.includes('date')) {
        dataType = 'date';
      }
    }

    // If element_type wasn't specific enough, check the selector
    if (dataType === 'text' && selector) {
      for (const [fieldType, pattern] of Object.entries(this.fieldTypes)) {
        if (pattern.test(selector)) {
          dataType = fieldType;
          break;
        }
      }
    }

    // Determine field name from selector
    const name = this.extractFieldName(selector) || 'Input Field';

    return {
      name: name,
      selector: selector,
      componentType: 'input',
      validationRules: null,
      expectedBehavior: `Accepts ${dataType} input`,
      dataType: dataType,
      isRequired: isRequired
    };
  }

  private detectSelectComponent(action: Action): Component {
    const selector = action.elementSelector || '';
    const name = this.extractFieldName(selector) || 'Dropdown';

    return {
      name: name,
      selector: selector,
      componentType: 'select',
      validationRules: null,
      expectedBehavior: 'Displays options for selection',
      dataType: 'select',
      isRequired: true
    };
  }

  private detectCheckboxComponent(action: Action): Component {
    const selector = action.elementSelector || '';
    const name = this.extractFieldName(selector) || 'Checkbox';

    return {
      name: name,
      selector: selector,
      componentType: 'checkbox',
      validationRules: null,
      expectedBehavior: 'Toggles boolean state',
      dataType: 'boolean',
      isRequired: false
    };
  }

  private detectRadioComponent(action: Action): Component {
    const selector = action.elementSelector || '';
    const name = this.extractFieldName(selector) || 'Radio Button';

    return {
      name: name,
      selector: selector,
      componentType: 'radio',
      validationRules: null,
      expectedBehavior: 'Selects one option from a group',
      dataType: 'option',
      isRequired: true
    };
  }

  // Reserved for future use - link, table, and navigation component detection
  /*
  private _detectLinkComponent(action: Action): Component {
    const selector = action.elementSelector || '';
    const elementValue = action.elementValue;
    const name = elementValue || this.extractFieldName(selector) || 'Link';

    return {
      name: name,
      selector: selector,
      componentType: 'link',
      validationRules: null,
      expectedBehavior: 'Navigates to another page',
      dataType: undefined,
      isRequired: undefined
    };
  }

  private _detectTableComponent(action: Action): Component {
    const selector = action.elementSelector || '';
    const name = this.extractFieldName(selector) || 'Data Table';

    return {
      name: name,
      selector: selector,
      componentType: 'table',
      validationRules: null,
      expectedBehavior: 'Displays tabular data',
      dataType: 'table',
      isRequired: undefined
    };
  }

  private _detectNavigationComponent(action: Action): Component {
    const selector = action.elementSelector || '';
    const name = this.extractFieldName(selector) || 'Navigation';

    return {
      name: name,
      selector: selector,
      componentType: 'navigation',
      validationRules: null,
      expectedBehavior: 'Provides navigation controls',
      dataType: undefined,
      isRequired: undefined
    };
  }
  */

  private detectGenericComponent(action: Action): Component | null {
    const selector = action.elementSelector;
    if (!selector) {
      return null;
    }

    const elementType = action.elementType;

    // Try to infer component type from selector
    let componentType = 'unknown';
    for (const [typeName, patterns] of Object.entries(this.selectorPatterns)) {
      for (const pattern of patterns) {
        if (pattern.test(selector)) {
          componentType = typeName;
          break;
        }
      }
      if (componentType !== 'unknown') {
        break;
      }
    }

    // Also consider element_type if available
    if (elementType) {
      const elementTypeLower = elementType.toLowerCase();
      if (elementTypeLower.includes('button')) {
        componentType = 'button';
      } else if (elementTypeLower.includes('input')) {
        componentType = 'input';
      } else if (elementTypeLower.includes('select')) {
        componentType = 'select';
      } else if (elementTypeLower.includes('checkbox')) {
        componentType = 'checkbox';
      } else if (elementTypeLower.includes('radio')) {
        componentType = 'radio';
      } else if (elementTypeLower.includes('link') || elementTypeLower === 'a') {
        componentType = 'link';
      } else if (elementTypeLower.includes('table')) {
        componentType = 'table';
      } else if (elementTypeLower.includes('form')) {
        componentType = 'form';
      }
    }

    // Determine name
    const name = this.extractFieldName(selector) || `${componentType.charAt(0).toUpperCase() + componentType.slice(1)} Component`;

    return {
      name: name,
      selector: selector,
      componentType: componentType,
      validationRules: null,
      expectedBehavior: 'Interacts with user',
      dataType: undefined,
      isRequired: undefined
    };
  }

  private extractFieldName(selector: string | undefined): string | null {
    if (!selector) {
      return null;
    }

    // Try to extract from id
    const idMatch = selector.match(/#([a-zA-Z0-9_-]+)/);
    if (idMatch) {
      const rawName = idMatch[1];
      // Convert camelCase or snake_case to readable form
      if (rawName.includes('_')) {
        return rawName.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
      } else {
        // Insert spaces before capital letters
        const name = rawName.replace(/([a-z])([A-Z])/g, '$1 $2');
        return name.charAt(0).toUpperCase() + name.slice(1);
      }
    }

    // Try to extract from name attribute
    const nameMatch = selector.match(/\[name=['"]([^'"]+)['"]\]/);
    if (nameMatch) {
      const rawName = nameMatch[1];
      // Convert to readable form
      if (rawName.includes('_')) {
        return rawName.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
      } else {
        // Insert spaces before capital letters
        const name = rawName.replace(/([a-z])([A-Z])/g, '$1 $2');
        return name.charAt(0).toUpperCase() + name.slice(1);
      }
    }

    // Try to extract from class
    const classMatch = selector.match(/\.([a-zA-Z0-9_-]+)/);
    if (classMatch) {
      const rawName = classMatch[1];
      // Convert to readable form
      if (rawName.includes('_') || rawName.includes('-')) {
        return rawName.split(/[_-]/).map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
      } else {
        // Insert spaces before capital letters
        const name = rawName.replace(/([a-z])([A-Z])/g, '$1 $2');
        return name.charAt(0).toUpperCase() + name.slice(1);
      }
    }

    return null;
  }

  private refinePageComponents(pages: Page[]): Page[] {
    for (const page of pages) {
      const components = page.components;

      // Group similar components
      const groupedComponents: Record<string, Component[]> = {};
      for (const component of components) {
        const typeKey = component.componentType || 'unknown';
        if (!groupedComponents[typeKey]) {
          groupedComponents[typeKey] = [];
        }
        groupedComponents[typeKey].push(component);
      }

      // Refine names for disambiguation when there are multiple components of same type
      for (const [_componentType, typeComponents] of Object.entries(groupedComponents)) {
        if (typeComponents.length > 1) {
          for (const component of typeComponents) {
            // Check if we need more specific naming
            if (!component.name.includes('Field') && component.componentType === 'input') {
              component.name += ' Field';
            }

            // Add the component's data type to the name if available
            if (component.dataType && !component.name.includes(component.dataType)) {
              component.name += ` (${component.dataType.charAt(0).toUpperCase() + component.dataType.slice(1)})`;
            }
          }
        }
      }

      // Look for form relationships
      const forms = this.identifyForms(components);
      if (Object.keys(forms).length > 0) {
        // Add form information to components
        for (const [formId, formInfo] of Object.entries(forms)) {
          for (const componentSelector of formInfo.components) {
            for (const component of components) {
              if (component.selector === componentSelector) {
                component.formId = formId;
              }
            }
          }
        }
      }
    }

    return pages;
  }

  private identifyForms(components: Component[]): Record<string, { name: string; components: string[]; fields: number; submitButton: string | null }> {
    const forms: Record<string, { name: string; components: string[]; fields: number; submitButton: string | null }> = {};
    let formId = 1;

    // Group components by DOM proximity and relationships
    const groupedComponents = this.groupComponentsByProximity(components);

    for (const group of groupedComponents) {
      // Check if group contains input fields and a submit button
      const inputFields = group.filter(c => ['input', 'select', 'checkbox', 'radio'].includes(c.componentType));
      const submitButtons = group.filter(c => 
        c.componentType === 'button' && 
        (c.name.toLowerCase().includes('submit') || 
         c.name.toLowerCase().includes('login') || 
         c.name.toLowerCase().includes('register') || 
         c.name.toLowerCase().includes('save'))
      );

      if (inputFields.length > 0 && submitButtons.length > 0) {
        const formComponents = group.map(c => c.selector);
        let formName = `Form ${formId}`;

        // Try to derive a more meaningful name from the submit button or fields
        if (submitButtons.length > 0) {
          formName = submitButtons[0].name.replace('Button', 'Form');
        }

        forms[`form_${formId}`] = {
          name: formName,
          components: formComponents,
          fields: inputFields.length,
          submitButton: submitButtons[0]?.selector || null
        };
        formId++;
      }
    }

    return forms;
  }

  private extractFormAttribute(selector: string): string | null {
    const formMatch = selector.match(/\[form=['"]([^'"]+)['"]\]/);
    return formMatch ? formMatch[1] : null;
  }

  private areSelectorsRelated(selector1: string, selector2: string): boolean {
    // Check if they share common parent patterns
    const parts1 = selector1.split(' ');
    const parts2 = selector2.split(' ');

    // Check for common ancestry
    const commonParts = Math.min(parts1.length, parts2.length) - 1;
    if (commonParts > 0 && parts1.slice(0, commonParts).join(' ') === parts2.slice(0, commonParts).join(' ')) {
      return true;
    }

    return false;
  }

  private groupComponentsByProximity(components: Component[]): Component[][] {
    const groups: Component[][] = [];
    const processed = new Set<string>();

    // First pass: group by form attributes
    for (const component of components) {
      if (processed.has(component.selector)) {
        continue;
      }

      // Check if component has form attribute
      const formAttr = this.extractFormAttribute(component.selector);
      if (formAttr) {
        // Find all components with the same form attribute
        const formGroup = [component];
        processed.add(component.selector);

        for (const other of components) {
          if (other.selector !== component.selector && !processed.has(other.selector)) {
            const otherFormAttr = this.extractFormAttribute(other.selector);
            if (otherFormAttr === formAttr) {
              formGroup.push(other);
              processed.add(other.selector);
            }
          }
        }

        if (formGroup.length > 1) {
          groups.push(formGroup);
        }
      }
    }

    // Second pass: group by selector proximity
    for (const component of components) {
      if (processed.has(component.selector)) {
        continue;
      }

      const relatedGroup = [component];
      processed.add(component.selector);

      for (const other of components) {
        if (other.selector !== component.selector && !processed.has(other.selector)) {
          if (this.areSelectorsRelated(component.selector, other.selector)) {
            relatedGroup.push(other);
            processed.add(other.selector);
          }
        }
      }

      if (relatedGroup.length > 1) {
        groups.push(relatedGroup);
      }
    }

    return groups;
  }
}

