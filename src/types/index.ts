/**
 * TypeScript type definitions for AI Engine
 */

export interface Action {
  id?: number;
  actionType: string;
  sequenceNumber?: number;
  url?: string;
  pageTitle?: string;
  elementSelector?: string;
  elementType?: string;
  actionData?: string;
  inputData?: string;
  actionTime?: string;
  description?: string;
  elementValue?: string;
  observations?: string; // JSON string of observations: {ui, network, consoleErrors, timing}
}

export interface ActionSequence {
  sessionId: number | string;
  actions: Action[];
}

export interface TestSuggestion {
  title: string;
  description: string;
  suggestionType: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  suggestedAction?: string;
}

export interface Page {
  pageName: string;
  urlPattern: string;
  pageType: string;
  identificationRules?: {
    url_contains?: string[];
    title_contains?: string[];
  };
  components: Component[];
  id?: string;
}

export interface Component {
  name: string;
  selector: string;
  componentType: string;
  validationRules?: any;
  expectedBehavior?: string;
  dataType?: string;
  isRequired?: boolean;
  children?: Component[];
  formId?: string;
  id?: string;
}

export interface TestCase {
  name: string;
  description: string;
  preconditions?: string[];
  steps: TestStep[];
  expectedResult: string;
  category: string;
  priority: string;
  isDataDriven?: boolean;
}

export interface TestStep {
  action: string;
  expectedResult: string;
  pageId?: string;
  componentId?: string;
  inputData?: string;
  stepType: string;
  url?: string;
}

export interface FeedbackData {
  suggestionId: number | string;
  status: string;
  feedback?: string;
}

