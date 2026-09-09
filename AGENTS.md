# AGENTS.md

This repository is a portfolio project for an Operations Excellence / product-builder role.

## Mission

Implement the product defined in `PRODUCT.md`, `DESIGN.md` and `ARCHITECTURE.md` without expanding scope unnecessarily.

## Non-negotiable product rules

1. Deterministic rules are the authority for detection/routing.
2. AI is advisory and cannot resolve, approve or mutate payroll records.
3. Every risk score must expose its component breakdown.
4. Every human resolution must capture a structured reason.
5. Insights must be derived from operational data, not invented AI commentary.
6. Use synthetic data only.
7. The app must still be valuable with the AI provider disabled.
8. Never implement statutory payroll calculations or claim legal correctness.

## Non-negotiable design rules

Read `DESIGN.md` before implementing UI.

- light, high-trust UI;
- Jet HR-inspired lime accent;
- no purple AI gradients;
- no glassmorphism;
- no giant chatbot;
- no dashboard decoration without operational meaning;
- tables must remain dense and fast;
- AI panel is secondary to evidence and deterministic checks.

## Engineering principles

- modular monolith;
- Next.js + TypeScript web app;
- FastAPI + Python backend;
- SQLite first;
- explicit types/schemas;
- tests around rule/scoring behavior;
- no microservices;
- no vector DB unless a real retrieval requirement exists;
- no background infrastructure unless the feature requires it.

## Recommended implementation order

1. static UI with fixtures;
2. domain schema;
3. deterministic rules;
4. scoring;
5. persistence;
6. resolution workflow;
7. insights;
8. AI adapter;
9. improvement proposals;
10. polish and screenshots.

## Definition of done for MVP

A reviewer can:

- open the dashboard;
- see a processed batch and the auto-clear/review split;
- filter the review queue;
- open a critical exception;
- understand exactly why it is critical;
- optionally ask for AI-assisted investigation;
- resolve the case manually;
- see the structured resolution reflected in insights;
- open a recurring issue and understand its estimated improvement opportunity.
