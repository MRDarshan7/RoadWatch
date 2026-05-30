from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Authority, Complaint, RoadSegment
from schemas import ComplaintCreate, ComplaintCreateResponse, ComplaintDetail

router = APIRouter()


def complaint_detail(db, complaint):
    authority_name = None
    if complaint.assigned_authority_id:
        authority = db.get(Authority, complaint.assigned_authority_id)
        authority_name = authority.department_name if authority else None

    return ComplaintDetail(
        complaint_id=complaint.complaint_id,
        road_id=complaint.road_id,
        issue_type=complaint.issue_type,
        severity=complaint.severity,
        description=complaint.description,
        media_url=complaint.media_url,
        lat=complaint.lat,
        lng=complaint.lng,
        status=complaint.status,
        assigned_authority_id=complaint.assigned_authority_id,
        assigned_authority_name=authority_name,
        sla_deadline=complaint.sla_deadline,
        defect_detected=complaint.defect_detected,
        defect_confidence=complaint.defect_confidence,
        created_at=complaint.created_at,
    )


@router.post("", response_model=ComplaintCreateResponse)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    if not db.get(RoadSegment, payload.road_id):
        raise HTTPException(status_code=404, detail="Road not found")

    created_at = datetime.now()
    complaint = Complaint(
        complaint_id=str(uuid4()),
        road_id=payload.road_id,
        issue_type=payload.issue_type,
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
    )


@router.get("/{complaint_id}", response_model=ComplaintDetail)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint_detail(db, complaint)


@router.get("/road/{road_id}", response_model=list[ComplaintDetail])
def get_road_complaints(road_id: str, db: Session = Depends(get_db)):
    complaints = (
        db.query(Complaint)
        .filter(Complaint.road_id == road_id)
        .order_by(Complaint.created_at.desc())
        .all()
    )
    return [complaint_detail(db, complaint) for complaint in complaints]

