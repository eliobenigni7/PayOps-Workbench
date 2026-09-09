# Implementation Plan

## Phase 1 — Static product prototype

Goal: make the product understandable before writing domain logic.

Build:

- app shell;
- dashboard;
- review queue;
- exception detail;
- resolution drawer;
- insights;
- improvement opportunity.

Use static TypeScript fixtures.

**Exit criterion:** 4 portfolio-quality screenshots can be captured.

## Phase 2 — Deterministic domain engine

Implement:

- CSV import;
- normalization;
- rule interface;
- initial rule set;
- priority scoring;
- auto-clear vs review routing;
- audit trace.

**Exit criterion:** same input always produces same queue and score breakdown.

## Phase 3 — Persistence + resolution loop

Implement:

- SQLite models;
- exception states;
- structured resolution reasons;
- audit history;
- metrics derived from outcomes.

**Exit criterion:** resolving a case immediately updates Insights.

## Phase 4 — AI-assisted investigation

Implement one provider adapter and a mock provider.

Inputs must be structured:

- triggered rules;
- relevant employee history;
- related HR events;
- current record.

Outputs must be structured:

- explanation;
- evidence summary;
- suggested checks;
- confidence;
- limitations.

**Exit criterion:** AI cannot change case state and the app is useful with AI disabled.

## Phase 5 — Improvement engine

Start deterministic / heuristic, not AI-first.

Aggregate exception outcomes by cause and compute:

- frequency;
- handling time;
- monthly effort;
- trend;
- false-positive rate;
- potential effort removed.

Then optionally use AI to draft the prose of an improvement proposal.

## Phase 6 — README polish

Add:

- 4 screenshots;
- 90-second demo GIF/video link;
- architecture diagram;
- design principles;
- "why not autonomous AI" section;
- measured demo results.
