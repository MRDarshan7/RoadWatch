import os
import re
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from supabase import create_client

from database import get_db
from models import Authority, Complaint, RoadSegment
from schemas import ComplaintCreate, ComplaintCreateResponse, ComplaintDetail, UploadImageResponse

router = APIRouter()

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_IMAGE_SIZE = 5 * 1024 * 1024
STORAGE_BUCKET = "complaint-media"


def complaint_detail(db, complaint):
    authority_name = None
    assigned_officer = None
    if complaint.assigned_authority_id:
        authority = db.get(Authority, complaint.assigned_authority_id)
        if authority:
            authority_name = authority.department_name
            assigned_officer = authority.officer_name

    road = db.get(RoadSegment, complaint.road_id) if complaint.road_id else None

    issue_types = complaint.issue_types_json or []
    if not issue_types and complaint.issue_type:
        issue_types = [complaint.issue_type]

    return ComplaintDetail(
        complaint_id=complaint.complaint_id,
        road_id=complaint.road_id,
        road_name=road.road_name if road else None,
        road_type=road.road_type if road else None,
        issue_type=complaint.issue_type,
        issue_types=issue_types,
        severity=complaint.severity,
        description=complaint.description,
        media_url=complaint.media_url,
        lat=complaint.lat,
        lng=complaint.lng,
        status=complaint.status,
        assigned_authority_id=complaint.assigned_authority_id,
        assigned_authority_name=authority_name,
        assigned_officer=assigned_officer,
        sla_deadline=complaint.sla_deadline,
        created_at=complaint.created_at,
    )


def get_supabase_client():
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_role_key or service_role_key.startswith("["):
        raise HTTPException(
            status_code=500,
            detail="SUPABASE_SERVICE_ROLE_KEY is required for server-side image uploads.",
        )
    return create_client(supabase_url, service_role_key)


def sanitize_filename(filename):
    name = Path(filename or "complaint-image").name
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._") or "complaint-image"


def ensure_issue_types_column(db):
    columns = {column["name"] for column in inspect(db.bind).get_columns("complaints")}
    if "issue_types_json" in columns:
        return

    dialect = db.bind.dialect.name
    if dialect == "postgresql":
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS issue_types_json JSONB"))
    else:
        db.execute(text("ALTER TABLE complaints ADD COLUMN issue_types_json JSON"))
    db.commit()


@router.post("/upload-image", response_model=UploadImageResponse)
async def upload_complaint_image(file: UploadFile = File(...)):
    extension = ALLOWED_IMAGE_TYPES.get(file.content_type or "")
    original_extension = Path(file.filename or "").suffix.lower()
    if not extension or original_extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(status_code=400, detail="Only jpg, jpeg, png, and webp images are allowed")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image must be 5MB or smaller")

    safe_name = sanitize_filename(file.filename)
    storage_path = f"complaints/{uuid4()}_{safe_name}"
    supabase = get_supabase_client()

    try:
        supabase.storage.from_(STORAGE_BUCKET).upload(
            storage_path,
            content,
            file_options={"content-type": file.content_type, "upsert": "false"},
        )
        public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Image upload failed: {exc}") from exc

    return UploadImageResponse(media_url=public_url)


@router.post("", response_model=ComplaintCreateResponse)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    ensure_issue_types_column(db)
    road = db.get(RoadSegment, payload.road_id)
    if not road:
        raise HTTPException(status_code=404, detail="Road not found")

    created_at = datetime.utcnow()
    complaint = Complaint(
        complaint_id=str(uuid4()),
        road_id=payload.road_id,
        issue_type=payload.issue_types[0],
        issue_types_json=payload.issue_types,
        severity=payload.severity,
        description=payload.description,
        media_url=payload.media_url,
        lat=payload.lat,
        lng=payload.lng,
        status="Submitted",
        created_at=created_at,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return ComplaintCreateResponse(
        complaint_id=complaint.complaint_id,
        status=complaint.status,
        created_at=complaint.created_at,
        road_name=road.road_name,
        message="Your complaint has been submitted successfully.",
    )


@router.get("/{complaint_id}", response_model=ComplaintDetail)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    ensure_issue_types_column(db)
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint_detail(db, complaint)


@router.get("/road/{road_id}", response_model=list[ComplaintDetail])
def get_road_complaints(road_id: str, db: Session = Depends(get_db)):
    ensure_issue_types_column(db)
    complaints = (
        db.query(Complaint)
        .filter(Complaint.road_id == road_id)
        .order_by(Complaint.created_at.desc())
        .all()
    )
    return [complaint_detail(db, complaint) for complaint in complaints]
