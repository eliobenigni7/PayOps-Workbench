# Synthetic Data Dictionary

All rows are fictional and exist only to support the portfolio demo.

| Field | Type | Meaning |
|---|---|---|
| employee_id | string | synthetic identifier |
| employee_name | string | fictional name |
| team | string | fictional department |
| period | YYYY-MM | payroll period |
| gross_salary | decimal | current synthetic gross salary |
| previous_gross_salary | decimal | previous-period comparator |
| regular_hours | decimal | regular hours in demo dataset |
| overtime_hours | decimal | overtime hours |
| bonus_amount | decimal | one-off bonus amount |
| iban_present | boolean | whether bank information is present |
| salary_change_event | boolean | whether an upstream HR change event exists |
| manual_override | boolean | synthetic manual override flag |
