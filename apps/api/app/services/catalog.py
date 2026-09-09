from __future__ import annotations

from dataclasses import dataclass

from app.domain.enums import IssueType


@dataclass(frozen=True)
class IssuePlaybook:
    title: str
    hypothesis: str
    intervention: str
    effort: str
    impact: str
    kpis: tuple[str, ...]
    prevention_rate: float
    default_handling_minutes: float


PLAYBOOKS: dict[IssueType, IssuePlaybook] = {
    IssueType.MISSING_BANK_INFORMATION: IssuePlaybook(
        title="IBAN mancante",
        hypothesis="I dati bancari non sono obbligatori nel momento in cui l'onboarding dipendente viene chiuso.",
        intervention="Aggiungere un controllo di completezza prima che l'onboarding possa essere marcato come completato.",
        effort="low",
        impact="Ridurre le eccezioni a valle sui dati bancari del 70–90%.",
        kpis=("conteggio mensile eccezioni", "tempo medio di gestione", "tasso di completamento onboarding"),
        prevention_rate=0.8,
        default_handling_minutes=6.2,
    ),
    IssueType.SALARY_DISCREPANCY: IssuePlaybook(
        title="Variazione retributiva senza tracciabilità completa",
        hypothesis="Le variazioni retributive arrivano in payroll prima che l'evento HR corrispondente sia scritto a sistema.",
        intervention="Bloccare la chiusura payroll quando una variazione >10% non ha un evento HR collegato.",
        effort="medium",
        impact="Ridurre le review su anomalie retributive intercettando gli eventi mancanti alla fonte.",
        kpis=("conteggio anomalie retributive", "tasso di eventi mancanti", "tempo alla prima review"),
        prevention_rate=0.55,
        default_handling_minutes=8.4,
    ),
    IssueType.MISSING_HR_EVENT: IssuePlaybook(
        title="Variazioni retributive senza evento HR di supporto",
        hypothesis="HR e payroll non condividono un contratto eventi obbligatorio per i cambi retribuzione.",
        intervention="Rendere l'evento di cambio retribuzione un campo obbligatorio nell'export HR usato per il payroll.",
        effort="medium",
        impact="Dare evidenza all'operatore invece di ricostruire l'intento dai numeri.",
        kpis=("eccezioni per evento mancante", "tasso di falsi positivi", "tempo medio di gestione"),
        prevention_rate=0.7,
        default_handling_minutes=7.8,
    ),
    IssueType.BONUS_ANOMALY: IssuePlaybook(
        title="Bonus una tantum senza codice motivo",
        hypothesis="I bonus si possono inserire senza un motivo strutturato, quindi gli importi anomali sono indistinguibili dagli errori.",
        intervention="Richiedere un codice motivo e la conferma del manager sopra una soglia.",
        effort="low",
        impact="Far passare in auto-clear i bonus attesi e tenere in coda solo le vere anomalie.",
        kpis=("volume eccezioni bonus", "tasso segnati come attesi", "ore di gestione manuale"),
        prevention_rate=0.6,
        default_handling_minutes=7.0,
    ),
    IssueType.OVERTIME_ISSUE: IssuePlaybook(
        title="Straordinari implausibili",
        hypothesis="Lo straordinario è un numero libero, senza controllo su calendario o approvazione.",
        intervention="Porre un tetto a 20 ore, salvo ticket di eccezione approvato.",
        effort="low",
        impact="Impedire che valori estremi di straordinario arrivino in review payroll.",
        kpis=("conteggio eccezioni straordinario", "ore sopra soglia", "tempo ciclo di approvazione"),
        prevention_rate=0.75,
        default_handling_minutes=5.5,
    ),
    IssueType.MANUAL_OVERRIDE: IssuePlaybook(
        title="Override manuali non strutturati",
        hypothesis="Gli override sono usati come workaround e raramente hanno un motivo riutilizzabile.",
        intervention="Sostituire il testo libero con una lista controllata e una data di scadenza.",
        effort="medium",
        impact="Trasformare il volume di override in un segnale di processo misurabile, non in lavoro nascosto.",
        kpis=("conteggio override", "dipendenti ripetuti", "completezza dei reason code"),
        prevention_rate=0.4,
        default_handling_minutes=4.8,
    ),
    IssueType.DUPLICATE_RECORD: IssuePlaybook(
        title="Righe dipendente/periodo duplicate",
        hypothesis="I feed di due sistemi sorgente vengono concatenati senza una chiave unica dipendente-periodo.",
        intervention="Imporre un vincolo unique su dipendente + periodo prima di accettare il batch.",
        effort="low",
        impact="Eliminare il rischio di doppio pagamento in ingest, non in review specialistica.",
        kpis=("conteggio duplicati", "tasso di rifiuto in ingest", "esposizione finanziaria evitata"),
        prevention_rate=0.95,
        default_handling_minutes=9.0,
    ),
}

BASELINE_REVIEW_SECONDS = 20.25
OPERATORS = ("Sofia Bianchi", "Paolo Ricci", "Giulia Neri")
