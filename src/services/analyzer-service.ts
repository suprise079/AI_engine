
/**
 * Create prompt for bug reasoning analysis
 */
export function createBugReasoningPrompt(
    bugResult: any,
    observations: any,
    actionContext?: any
  ): string {
    const obsStr = typeof observations === 'string' 
      ? observations 
      : JSON.stringify(observations, null, 2);
  
    return `You are a QA expert analyzing a potential bug detected during manual testing.
  
  BUG DETECTION RESULT:
  - Type: ${bugResult.type || 'UNKNOWN'}
  - Is Bug: ${bugResult.isBug ? 'Yes' : 'No'}
  - Is Suspicious: ${bugResult.isSuspicious ? 'Yes' : 'No'}
  - Initial Reason: ${bugResult.reason || 'No reason provided'}
  - Severity: ${bugResult.severity || 'UNKNOWN'}
  
  OBSERVATIONS (What actually happened):
  ${obsStr}
  
  ${actionContext ? `ACTION CONTEXT:\n${JSON.stringify(actionContext, null, 2)}\n` : ''}
  
  Your task:
  1. Analyze the observations to understand WHY this bug was detected
  2. Provide enhanced reasoning that explains the root cause
  3. Assess if the severity is appropriate
  4. Provide actionable recommendations
  
  Return your response as JSON only, with this structure:
  {
    "reasoning": "Detailed explanation of why this is a bug and what evidence supports it",
    "severity": "LOW|MEDIUM|HIGH|CRITICAL",
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "confidence": "LOW|MEDIUM|HIGH",
    "context": {
      "rootCause": "What likely caused this issue",
      "impact": "What impact this has on users",
      "reproducibility": "How likely this is to happen again"
    }
  }
  
  Focus on:
  - Explaining the evidence from observations
  - Connecting the bug type to the actual observations
  - Providing actionable next steps
  - Being concise but thorough`;
  }
