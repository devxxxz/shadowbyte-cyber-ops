from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, get_db
from .models import Asset, AssessmentJob, AuditEvent
from .schemas import AssetCreate, AssetOut, JobOut
from .assessments import run_dns_tls_check

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.allowed_origins.split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.get("/")
def root():
    return {"name": settings.app_name, "version": "0.1.0", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "api"}

@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(select(1))
        return {"status": "ready", "database": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")

@app.get("/api/assets", response_model=list[AssetOut])
def list_assets(db: Session = Depends(get_db)):
    return list(db.scalars(select(Asset).order_by(Asset.id.desc())).all())

@app.post("/api/assets", response_model=AssetOut, status_code=201)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    if payload.authorized and not payload.authorization_note.strip():
        raise HTTPException(status_code=422, detail="Authorization note is required when marking an asset authorized.")
    existing = db.scalar(select(Asset).where(Asset.hostname == payload.hostname))
    if existing:
        raise HTTPException(status_code=409, detail="This hostname is already registered.")
    asset = Asset(
        hostname=payload.hostname,
        display_name=payload.display_name.strip(),
        authorized=payload.authorized,
        authorization_note=payload.authorization_note.strip(),
    )
    db.add(asset)
    db.flush()
    db.add(AuditEvent(action="asset.created", subject=asset.hostname, detail={"authorized": asset.authorized}))
    db.commit()
    db.refresh(asset)
    return asset

@app.get("/api/jobs", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return list(db.scalars(select(AssessmentJob).order_by(AssessmentJob.id.desc())).all())

@app.post("/api/assets/{asset_id}/assessments", response_model=JobOut, status_code=201)
def create_assessment(asset_id: int, db: Session = Depends(get_db)):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found.")
    if not asset.authorized or not asset.authorization_note.strip():
        raise HTTPException(status_code=403, detail="Assessment blocked: asset authorization is not recorded.")
    job = AssessmentJob(asset_id=asset.id, profile="dns_tls", status="running")
    db.add(job)
    db.flush()
    db.add(AuditEvent(action="assessment.started", subject=asset.hostname, detail={"job_id": job.id, "profile": "dns_tls"}))
    try:
        job.findings = run_dns_tls_check(asset.hostname, settings.max_assessment_timeout_seconds)
        job.status = "completed"
    except Exception as exc:
        job.status = "failed"
        job.error = type(exc).__name__
    job.finished_at = datetime.now(timezone.utc)
    db.add(AuditEvent(action="assessment.finished", subject=asset.hostname, detail={"job_id": job.id, "status": job.status}))
    db.commit()
    db.refresh(job)
    return job
