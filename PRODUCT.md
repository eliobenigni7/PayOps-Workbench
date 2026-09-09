# Product Brief

## Working name

**Payroll Ops Workbench**

Repository slug: `payroll-ops-workbench`

## One-line pitch

An internal operations workbench that turns high-volume payroll data into a prioritized human review queue, combines deterministic controls with AI-assisted investigation, and identifies recurring bottlenecks worth eliminating upstream.

## User

Primary user: Payroll / Operations Specialist.

Secondary user: Operations Lead / Process Improvement owner.

## Problem

Operational teams often review large batches manually because:

- the cost of missing an exception is high;
- data arrives from multiple sources;
- exceptions are heterogeneous;
- prioritization is weak;
- resolution outcomes are captured inconsistently;
- recurring issues are treated case-by-case instead of eliminated at the source.

## Jobs to be done

### Operator

- Show me only the cases that deserve attention.
- Tell me why a case is in my queue.
- Put the most important cases first.
- Give me enough context to resolve it quickly.
- Make my decision traceable.

### Operations Lead

- Show me where the team is spending manual effort.
- Tell me which rules are noisy or ineffective.
- Identify recurring causes that can be removed upstream.
- Quantify the potential impact of fixing them.

## Non-goals

- statutory payroll calculation;
- legal interpretation;
- autonomous payroll approval;
- replacing a payroll specialist;
- enterprise workflow orchestration;
- production-grade identity/RBAC in the first portfolio version.

## Product principles

1. **Deterministic before probabilistic.**
2. **Human accountability at the resolution boundary.**
3. **Explain every score.**
4. **Capture structured feedback.**
5. **Measure work removed, not features shipped.**
6. **Fix recurring causes upstream.**
7. **Progressive solution complexity.**

## MVP screens

1. Operations Control Center
2. Review Queue
3. Exception Detail
4. Resolution Drawer
5. Insights
6. Improvement Opportunity

## Demo dataset

All data is fictional. Build 40–100 records with a mix of:

- clean cases;
- missing bank details;
- unusual salary variation;
- duplicate bonus;
- implausible overtime;
- missing supporting HR event;
- manual override;
- duplicate employee/month record.

## Success signal

A Jet HR interviewer should be able to infer three things without explanation:

- the builder understands operational bottlenecks;
- the builder knows where AI should and should not be used;
- the builder thinks in terms of business impact and continuous improvement.
