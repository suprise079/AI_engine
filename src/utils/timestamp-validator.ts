/**
 * Timestamp validation utilities
 */

import { Action } from '../types';
import logger from '../config/logger';

/**
 * Validates and fixes timestamps in action objects
 * Handles various timestamp formats including array format and ISO strings
 */
export function validateTimestamp(action: Action): Action {
  if (!action.actionTime) {
    action.actionTime = new Date().toISOString();
    return action;
  }

  const timestamp = action.actionTime;

  // Handle array-format timestamps like [2025, 3, 30, 18, 32, 55, 567000000]
  if (Array.isArray(timestamp) && timestamp.length >= 6) {
    try {
      const [year, month, day, hour, minute, second] = timestamp;
      const microsecond = timestamp.length > 6 ? Math.floor(timestamp[6] / 1000) : 0;
      const dt = new Date(year, month - 1, day, hour, minute, second, microsecond);
      action.actionTime = dt.toISOString();
      return action;
    } catch (e) {
      logger.warn(`Could not parse timestamp: ${timestamp}. Using current time.`);
      action.actionTime = new Date().toISOString();
      return action;
    }
  }

  // Check if it's a complete ISO format timestamp
  if (typeof timestamp === 'string') {
    if (timestamp.includes('T') && timestamp.length >= 19) {
      return action;
    }
    // If it's just a year or incomplete timestamp, replace it
    if (/^\d{4}$/.test(timestamp)) {
      logger.warn(`Fixing incomplete timestamp: ${timestamp}`);
      action.actionTime = new Date().toISOString();
      return action;
    }
  }

  // Try to parse the timestamp
  try {
    const parsed = new Date(timestamp as string);
    if (!isNaN(parsed.getTime())) {
      action.actionTime = parsed.toISOString();
      return action;
    }
  } catch (e) {
    // Ignore
  }

  logger.warn(`Could not parse timestamp: ${timestamp}. Using current time.`);
  action.actionTime = new Date().toISOString();
  return action;
}

