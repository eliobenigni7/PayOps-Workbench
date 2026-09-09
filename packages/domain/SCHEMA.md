# Domain Schema

## Batch

- `id`
- `period`
- `source`
- `status`
- `record_count`
- `created_at`
- `processed_at`

## EmployeeRecord

Synthetic portfolio fields:

- `id`
- `batch_id`
- `employee_id`
- `employee_name`
- `team`
- `gross_salary`
- `previous_gross_salary`
- `regular_hours`
- `overtime_hours`
- `bonus_amount`
- `iban_present`
- `salary_change_event`
- `manual_override`

## RuleResult

- `rule_id`
- `record_id`
- `triggered`
- `severity`
- `message`
- `score_contribution`
- `evidence`

## Exception

- `id`
- `record_id`
- `status`
- `priority`
- `risk_score`
- `financial_exposure`
- `created_at`
- `assigned_to`

## PriorityBreakdown

- `exception_id`
- `component`
- `value`
- `explanation`

## ReviewResolution

- `exception_id`
- `outcome`
- `reason_code`
- `note`
- `resolved_by`
- `resolved_at`

## AIInvestigation

- `exception_id`
- `summary`
- `evidence[]`
- `suggested_checks[]`
- `confidence`
- `limitations[]`
- `provider`
- `model`
- `prompt_version`
- `created_at`

## ImprovementOpportunity

- `id`
- `issue_type`
- `monthly_occurrences`
- `avg_handling_minutes`
- `monthly_effort_hours`
- `root_cause_hypothesis`
- `suggested_intervention`
- `implementation_effort`
- `expected_impact`
- `measurement_kpis[]`
- `status`
