# User Flows

## Flow A — Review a critical exception

1. Operator lands on Control Center.
2. Clicks `14 Critical` or opens the Review Queue.
3. Queue opens pre-filtered to critical cases.
4. Operator opens `EMP-1042 · Salary anomaly`.
5. Detail explains the current value, historical baseline and triggered checks.
6. Operator expands `Why is this critical?` to inspect score components.
7. Optional: operator opens AI-assisted investigation.
8. Operator resolves with a structured reason.
9. Case leaves the open queue and audit event is created.

## Flow B — Identify recurring friction

1. Operations Lead opens Insights.
2. Sees `Missing bank information` is the largest source of avoidable effort.
3. Opens the issue type.
4. Sees monthly cases, handling time and trend.
5. Opens suggested improvement opportunity.
6. Reads root-cause hypothesis and expected impact.
7. Marks opportunity as `Investigate`, `Planned`, `Implemented` or `Dismissed`.

## Flow C — AI unavailable

1. Operator opens an exception.
2. AI provider is offline/unconfigured.
3. Deterministic evidence, score breakdown and resolution workflow remain fully available.
4. AI panel shows a quiet unavailable state; no workflow is blocked.
