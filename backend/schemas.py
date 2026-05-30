from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class RoadListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    road_id: str
    road_name: str
    road_type: str | None
    zone: str | None
    ward: str | None
    health_score: int | None
    start_lat: float | None
    start_lng: float | None
    end_lat: float | None
    end_lng: float | None


class ProjectSummary(BaseModel):
    contractor_name: str | None
    tender_id: str | None
    sanctioned_amount: float | None
    spent_amount: float | None
    status: str | None


class MaintenanceSummary(BaseModel):
    last_relaying_date: date | None
    activity_type: str | None
    days_since_repair: int | None
    next_scheduled: date | None = None


class AuthoritySummary(BaseModel):
    department_name: str | None
    officer_name: str | None
    designation: str | None
    contact: str | None


class ComplaintSummary(BaseModel):
    total_complaints: int
    open_complaints: int
    latest_descriptions: list[str]


class RoadDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    road_id: str
    road_name: str
    road_type: str | None
    zone: str | None
    ward: str | None
    length_km: float | None
    start_lat: float | None
    start_lng: float | None
    end_lat: float | None
    end_lng: float | None
    health_score: int | None
    latest_project: ProjectSummary | None
    latest_maintenance: MaintenanceSummary | None
    assigned_authority: AuthoritySummary | None
    complaint_summary: ComplaintSummary


class ComplaintCreate(BaseModel):
    road_id: str
    description: str
    issue_type: str
    lat: float
    lng: float
    media_url: str | None = None
    severity: str = "Medium"


class ComplaintCreateResponse(BaseModel):
    complaint_id: str
    status: str
    created_at: datetime


class ComplaintDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    complaint_id: str
    road_id: str
    issue_type: str | None
    severity: str | None
    description: str | None
    media_url: str | None
    lat: float | None
    lng: float | None
    status: str | None
    assigned_authority_id: str | None
    assigned_authority_name: str | None = None
    sla_deadline: datetime | None
    defect_detected: str | None
    defect_confidence: float | None
    created_at: datetime | None


class AuthorityDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    authority_id: str
    department_name: str | None
    officer_name: str | None
    designation: str | None
    road_types_handled: list[str] | dict[str, Any] | None
    zones_handled: list[str] | dict[str, Any] | None
    office_contact: str | None
    email: str | None
