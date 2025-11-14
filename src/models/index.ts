/**
 * Data models for AI Engine
 */

import { Action } from '../types';

export class ActionSequenceModel {
  sessionId: number | string;
  actions: Action[];

  constructor(sessionId: number | string, actions: Action[]) {
    this.sessionId = sessionId;
    this.actions = actions;
  }

  getActionsByType(actionType: string): Action[] {
    return this.actions.filter(a => a.actionType === actionType);
  }

  getNavigationSequence(): Array<[string | undefined, string | undefined]> {
    const navigations = this.getActionsByType('NAVIGATE');
    return navigations.map(n => [n.url, n.pageTitle]);
  }

  getActionCount(): number {
    return this.actions.length;
  }

  getUniquePages(): string[] {
    const urls = this.actions
      .map(a => a.url)
      .filter((url): url is string => url !== undefined);
    return Array.from(new Set(urls));
  }
}

export class TestSuggestionModel {
  title: string;
  description: string;
  suggestionType: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  suggestedAction?: string;

  constructor(
    title: string,
    description: string,
    suggestionType: string,
    priority: 'HIGH' | 'MEDIUM' | 'LOW',
    suggestedAction?: string
  ) {
    this.title = title;
    this.description = description;
    this.suggestionType = suggestionType;
    this.priority = priority;
    this.suggestedAction = suggestedAction;
  }

  toDict(): {
    title: string;
    description: string;
    suggestionType: string;
    priority: string;
    suggestedAction?: string;
  } {
    return {
      title: this.title,
      description: this.description,
      suggestionType: this.suggestionType,
      priority: this.priority,
      suggestedAction: this.suggestedAction
    };
  }
}

