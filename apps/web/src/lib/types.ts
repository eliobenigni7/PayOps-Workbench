export type Priority = "critical" | "high" | "medium" | "low";
export type ExceptionStatus = "open" | "resolved" | "requested_info" | "escalated";

export type ExceptionListItem = {
  id: string;
  employee_id: string;
  employee_name: string;
  team: string;
  issue_label: string;
  issue_type: string;
  priority: Priority;
  risk_score: number;
  financial_exposure: number;
  age_hours: number;
  assigned_to: string | null;
  status: ExceptionStatus;
  has_ai_investigation: boolean;
  period: string;
  batch_id?: string;
};

export type DashboardPayload = {
  batch: {
    id: string;
    period: string;
    source: string;
    status: string;
    processed_at: string | null;
    record_count: number;
  };
  processed: number;
  auto_cleared: number;
  auto_cleared_rate: number;
  needs_review: number;
  review_rate: number;
  critical: number;
  critical_delta: number;
  effort_avoided_minutes: number;
  effort_avoided_label: string;
  baseline_seconds_per_record: number;
  queue_preview: ExceptionListItem[];
  top_causes: CauseRow[];
  oldest_unresolved: ExceptionListItem[];
  open_count: number;
  ai_available: boolean;
  batches: { id: string; period: string; record_count: number }[];
};

export type CauseRow = {
  issue_type: string;
  label: string;
  occurrences: number;
  share: number;
  previous_occurrences?: number;
  trend?: string;
  monthly_effort_hours?: number;
  avg_handling_minutes?: number;
  false_positive_rate?: number;
  current_occurrences?: number;
};

export type ExceptionDetail = ExceptionListItem & {
  record: {
    id: string;
    employee_id: string;
    employee_name: string;
    team: string;
    period: string;
    gross_salary: number;
    previous_gross_salary: number;
    avg_6m_gross: number;
    regular_hours: number;
    overtime_hours: number;
    bonus_amount: number;
    iban_present: boolean;
    salary_change_event: boolean;
    manual_override: boolean;
  };
  context_panel: {
    title: string;
    rows: { label: string; value: string | number; format?: string; tone?: string }[];
  };
  triggered_rules: {
    rule_id: string;
    severity: string;
    message: string;
    issue_type: string;
    evidence: Record<string, unknown>;
  }[];
  priority_breakdown: { component: string; value: number; explanation: string }[];
  hr_events: { type: string; present: boolean; note: string }[];
  resolution: {
    outcome: string;
    outcome_label: string;
    reason_code: string;
    reason_label: string;
    note: string | null;
    resolved_by: string;
    resolved_at: string;
    handling_minutes: number;
  } | null;
  investigation: Investigation | null;
  ai_available: boolean;
  audit: { id: string; event_type: string; actor: string; payload: Record<string, unknown>; created_at: string }[];
};

export type Investigation = {
  id: string;
  summary: string;
  evidence: string[];
  suggested_checks: string[];
  confidence: number;
  limitations: string[];
  provider: string;
  model: string;
  prompt_version: string;
  created_at: string;
};

export type Opportunity = {
  id: string;
  issue_type: string;
  title: string;
  monthly_occurrences: number;
  avg_handling_minutes: number;
  monthly_effort_hours: number;
  false_positive_rate: number;
  trend: string;
  root_cause_hypothesis: string;
  suggested_intervention: string;
  implementation_effort: string;
  expected_impact: string;
  measurement_kpis: string[];
  expected_effort_removed_hours: number;
  status: string;
  impact_label: string;
  effort_label: string;
};

export type InsightsPayload = {
  hero_question: string;
  period: string;
  previous_period?: string | null;
  top_causes: CauseRow[];
  effort_by_issue: CauseRow[];
  rule_quality: {
    rule_id: string;
    trigger_count: number;
    resolved_count: number;
    confirmed_issue_rate: number | null;
    false_positive_rate: number | null;
    avg_handling_minutes: number | null;
  }[];
  resolution_mix: Record<string, number>;
  opportunities: Opportunity[];
  methodology: { baseline_review_seconds: number; note: string };
};

export type MetaPayload = {
  operators: string[];
  issue_types: { value: string; label: string }[];
  outcomes: { value: string; label: string }[];
  reason_codes: { value: string; label: string }[];
  ai_available: boolean;
};
