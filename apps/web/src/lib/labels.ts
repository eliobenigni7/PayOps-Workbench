export const PRIORITY_LABELS: Record<string, string> = {
  critical: "Critico",
  high: "Alto",
  medium: "Medio",
  low: "Basso",
};

export const STATUS_LABELS: Record<string, string> = {
  open: "Aperto",
  resolved: "Risolto",
  requested_info: "Info richiesta",
  escalated: "Escalato",
};

export const TREND_LABELS: Record<string, string> = {
  up: "In aumento",
  down: "In calo",
  stable: "Stabile",
};

export const IMPROVEMENT_STATUS_LABELS: Record<string, string> = {
  detected: "Rilevato",
  investigate: "Da indagare",
  planned: "Pianificato",
  implemented: "Implementato",
  dismissed: "Scartato",
};

export const COMPONENT_LABELS: Record<string, string> = {
  severity: "Gravità",
  financial_exposure: "Esposizione finanziaria",
  rule_confidence: "Affidabilità della regola",
  missing_support_event: "Evento di supporto mancante",
};

export const AUDIT_LABELS: Record<string, string> = {
  batch_imported: "Batch importato",
  exception_opened: "Eccezione aperta",
  exception_resolved: "Eccezione risolta",
  ai_investigation_requested: "Investigation AI richiesta",
};

export const ACTOR_LABELS: Record<string, string> = {
  system: "sistema",
  operator: "operatore",
};

export const RULE_LABELS: Record<string, string> = {
  MISSING_IBAN: "IBAN mancante",
  SALARY_VARIATION: "Variazione retribuzione",
  MISSING_SALARY_EVENT: "Evento retribuzione mancante",
  OUTSIDE_HISTORICAL_RANGE: "Fuori range storico",
  IMPLAUSIBLE_OVERTIME: "Straordinario implausibile",
  UNUSUAL_BONUS: "Bonus anomalo",
  MANUAL_OVERRIDE: "Override manuale",
  DUPLICATE_RECORD: "Record duplicato",
};

export const SEVERITY_LABELS: Record<string, string> = {
  critical: "Critico",
  high: "Alto",
  medium: "Medio",
  low: "Basso",
};

export function whyPriority(priority: string): string {
  if (priority === "critical") return "Perché è critico?";
  if (priority === "high") return "Perché è alto?";
  if (priority === "medium") return "Perché è medio?";
  return "Perché è in coda?";
}

export function labelOf(map: Record<string, string>, value: string): string {
  return map[value] ?? value;
}
