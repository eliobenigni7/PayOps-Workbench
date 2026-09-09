# API

FastAPI backend for Payroll Ops Workbench.

```bash
cd apps/api
python3 -m pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload --port 8000
```

On startup the API creates SQLite tables and seeds the synthetic demo if the database is empty.

```text
GET  /health
GET  /meta
GET  /dashboard
POST /batches/import
GET  /batches/{id}/summary
GET  /exceptions
GET  /exceptions/{id}
POST /exceptions/{id}/resolve
POST /exceptions/{id}/investigate
GET  /insights
GET  /improvements
GET  /improvements/{id}
POST /improvements/{id}/status
```

Detection, scoring and routing live in `app/rules` and `app/scoring`. Route handlers do not decide whether a record is an exception.
