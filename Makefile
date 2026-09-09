.PHONY: api web test seed

api:
	cd apps/api && python3 -m uvicorn app.main:app --reload --port 8000

web:
	cd apps/web && npm run dev

test:
	cd apps/api && python3 -m pytest -q
	cd apps/web && npm run typecheck

compose:
	docker compose up --build
