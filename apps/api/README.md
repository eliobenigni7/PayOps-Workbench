# API

Target: FastAPI + Python.

Suggested first endpoints:

```text
POST /batches/import
GET  /batches/{id}/summary
GET  /exceptions
GET  /exceptions/{id}
POST /exceptions/{id}/resolve
POST /exceptions/{id}/investigate
GET  /insights
GET  /improvements
GET  /improvements/{id}
```

Keep detection/scoring domain logic out of route handlers.
