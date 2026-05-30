from datetime import date
from math import sqrt

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Authority, Complaint, Contractor, MaintenanceRecord, ProjectRecord, RoadSegment
from schemas import (
    AuthoritySummary,
    ComplaintSummary,
    MaintenanceSummary,
    ProjectSummary,
    RoadDetail,
    RoadListItem,
)

router = APIRouter()


def road_list_item(road):
    return RoadListItem.model_validate(road)


def find_authority(db, road):
    authorities = db.query(Authority).all()
    for authority in authorities:
        road_types = authority.road_types_handled or []
        zones = authority.zones_handled or []
        if road.road_type in road_types and (road.zone in zones or road.road_type in {"NH", "Panchayat"}):
            return authority
    return None


@router.get("", response_model=list[RoadListItem])
def list_roads(db: Session = Depends(get_db)):
    roads = db.query(RoadSegment).order_by(RoadSegment.road_id).all()
    return [road_list_item(road) for road in roads]


@router.get("/search", response_model=list[RoadListItem])
def search_roads(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    roads = (
        db.query(RoadSegment)
        .filter(RoadSegment.road_name.ilike(f"%{q}%"))
        .order_by(RoadSegment.road_id)
        .all()
    )
    return [road_list_item(road) for road in roads]


@router.get("/nearby", response_model=list[RoadListItem])
def nearby_roads(
    lat: float,
    lng: float,
    radius_km: float = Query(1.0, gt=0),
    db: Session = Depends(get_db),
):
    roads = db.query(RoadSegment).all()
    nearby = []
    for road in roads:
        mid_lat = ((road.start_lat or 0) + (road.end_lat or 0)) / 2
        mid_lng = ((road.start_lng or 0) + (road.end_lng or 0)) / 2
        distance_km = sqrt((lat - mid_lat) ** 2 + (lng - mid_lng) ** 2) * 111
        if distance_km <= radius_km:
            nearby.append(road)
    return [road_list_item(road) for road in sorted(nearby, key=lambda item: item.road_id)]


@router.get("/{road_id}", response_model=RoadDetail)
def get_road(road_id: str, db: Session = Depends(get_db)):
    road = db.get(RoadSegment, road_id)
    if not road:
        raise HTTPException(status_code=404, detail="Road not found")

    project = (
        db.query(ProjectRecord)
        .filter(ProjectRecord.road_id == road_id)
        .order_by(ProjectRecord.end_date.desc().nullslast())
        .first()
    )
    contractor_name = None
    if project and project.contractor_id:
        contractor = db.get(Contractor, project.contractor_id)
        contractor_name = contractor.name if contractor else None

    maintenance = (
        db.query(MaintenanceRecord)
        .filter(MaintenanceRecord.road_id == road_id)
        .order_by(MaintenanceRecord.last_relaying_date.desc().nullslast())
        .first()
    )
    days_since_repair = None
    if maintenance and maintenance.last_relaying_date:
        days_since_repair = (date.today() - maintenance.last_relaying_date).days

    authority = find_authority(db, road)
    complaints = (
        db.query(Complaint)
        .filter(Complaint.road_id == road_id)
        .order_by(Complaint.created_at.desc())
        .all()
    )
    open_statuses = {"Submitted", "Routed", "Acknowledged", "In Progress"}

    return RoadDetail(
        road_id=road.road_id,
        road_name=road.road_name,
        road_type=road.road_type,
        zone=road.zone,
        ward=road.ward,
        length_km=road.length_km,
        start_lat=road.start_lat,
        start_lng=road.start_lng,
        end_lat=road.end_lat,
        end_lng=road.end_lng,
        health_score=road.health_score,
        latest_project=ProjectSummary(
            contractor_name=contractor_name,
            tender_id=project.tender_id,
            sanctioned_amount=project.sanctioned_amount,
            spent_amount=project.spent_amount,
            status=project.status,
        )
        if project
        else None,
        latest_maintenance=MaintenanceSummary(
            last_relaying_date=maintenance.last_relaying_date,
            activity_type=maintenance.activity_type,
            days_since_repair=days_since_repair,
        )
        if maintenance
        else None,
        assigned_authority=AuthoritySummary(
            department_name=authority.department_name,
            officer_name=authority.officer_name,
            designation=authority.designation,
            contact=authority.office_contact,
        )
        if authority
        else None,
        complaint_summary=ComplaintSummary(
            total_complaints=len(complaints),
            open_complaints=sum(1 for complaint in complaints if complaint.status in open_statuses),
            latest_descriptions=[complaint.description for complaint in complaints[:3] if complaint.description],
        ),
    )

