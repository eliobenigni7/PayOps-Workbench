# Decision Log

## D001 — Deterministic detection before AI

**Decision:** exception detection and priority contributions are deterministic.

**Why:** reproducibility, testability, trust and explainability matter more than model cleverness in a high-consequence workflow.

## D002 — Human resolution boundary

**Decision:** only a human can resolve a case.

**Why:** the project demonstrates augmentation and safe automation, not autonomous payroll processing.

## D003 — SQLite first

**Decision:** use SQLite for the portfolio version.

**Why:** the project has no concurrency or scale requirement that justifies database infrastructure.

## D004 — No generic chatbot

**Decision:** AI is embedded in exception context as an investigation panel.

**Why:** the user's job is to resolve an operational case, not have an open-ended conversation.

## D005 — Insights before "process mining"

**Decision:** derive simple recurring-friction metrics before introducing process-mining terminology/algorithms.

**Why:** the business question is "what manual work should we eliminate?"; implementation complexity should follow evidence.
