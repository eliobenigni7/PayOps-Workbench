from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings
from app.db.session import SessionLocal, init_db
from app.seed import seed_if_empty

app = FastAPI(title="Payroll Ops Workbench", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_if_empty(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
