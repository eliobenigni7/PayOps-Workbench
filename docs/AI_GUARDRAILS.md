# AI Guardrails

## Role of AI

AI is a copilot for investigation and communication, not an operational authority.

### Allowed

- explain triggered deterministic rules;
- summarize evidence already provided;
- connect related synthetic events;
- suggest a checklist of next verifications;
- draft improvement-proposal prose from computed metrics.

### Forbidden

- approve payroll;
- resolve exceptions;
- edit source data;
- suppress deterministic rules;
- infer legal entitlement;
- invent evidence;
- silently access data outside the case context.

## Structured output

Suggested contract:

```json
{
  "summary": "string",
  "evidence": ["string"],
  "suggested_checks": ["string"],
  "confidence": 0.0,
  "limitations": ["string"]
}
```

## Evaluation

Create a small fixed evaluation set for AI output covering:

- no invented evidence;
- triggered rules correctly represented;
- next-step suggestions are actionable;
- uncertainty is surfaced;
- no autonomous approval language.

## UI rule

Always show:

> AI suggestions are informational only. Final resolution requires operator confirmation.
