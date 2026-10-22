from contextlib import asynccontextmanager
from io import BytesIO
from typing import List, Optional
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, select

from app.change_service import process_batch
from app.config import POLL_ENABLED, POLL_INTERVAL_SECONDS
from app.db import engine, init_db
from app.models import ChangeLog, InventoryItem
from app.poller import run_poll_cycle


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler = BackgroundScheduler()
    if POLL_ENABLED:
        scheduler.add_job(run_poll_cycle, "interval", seconds=POLL_INTERVAL_SECONDS)
        scheduler.start()
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)


app = FastAPI(title="Change Data Management Service (CDMS)", lifespan=lifespan)


@app.exception_handler(OperationalError)
async def database_unavailable(request: Request, exc: OperationalError):
    return JSONResponse(status_code=503, content={"detail": "Database unavailable"})


@app.post("/api/v1/cdc/webhook")
def receive_webhook(items: List[InventoryItem]):
    return process_batch(items, "WEBHOOK")


@app.post("/api/v1/cdc/upload-excel")
def upload_excel(file: UploadFile = File(...)):
    try:
        rows = pd.read_excel(BytesIO(file.file.read())).to_dict(orient="records")
        items = [InventoryItem(**row) for row in rows]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Excel file: {exc}") from exc
    return process_batch(items, "EXCEL")


@app.get("/api/v1/changes")
def list_changes(sku: Optional[str] = None, limit: int = 50):
    stmt = select(ChangeLog).order_by(ChangeLog.id.desc()).limit(limit)
    if sku:
        stmt = stmt.where(ChangeLog.sku == sku)
    with Session(engine) as session:
        return session.exec(stmt).all()


@app.get("/health")
def health_check():
    with Session(engine) as session:
        session.exec(select(1))
    return {"status": "ok"}
