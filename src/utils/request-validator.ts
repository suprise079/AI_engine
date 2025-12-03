/**
 * Common request validation utilities
 */

/**
 * Validates that a value is a non-empty array
 */
export function isValidArray(value: any): boolean {
  return Array.isArray(value) && value.length > 0;
}

/**
 * Validates that a value is a non-empty string
 */
export function isValidString(value: any): boolean {
  return typeof value === 'string' && value.trim().length > 0;
}

/**
 * Validates that a value is a valid object
 */
export function isValidObject(value: any): boolean {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

