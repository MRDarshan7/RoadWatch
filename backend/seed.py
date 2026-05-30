import json
from datetime import date
from pathlib import Path

from database import SessionLocal, create_tables
from models import (
    Authority,
    Complaint,
    Contractor,
    MaintenanceRecord,
    ProjectRecord,
    RoadSegment,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(filename):
    with (DATA_DIR / filename).open(encoding="utf-8") as file:
        return json.load(file)


def parse_date(value):
    return date.fromisoformat(value) if value else None


def seed_roads(records):
    return [
        RoadSegment(
            road_id=record["road_id"],
            road_name=record["road_name"],
            road_type=record["road_type"],
            zone=record["zone"],
            ward=record["ward"],
            length_km=record["length_km"],
            start_lat=record["coordinates"]["start"][0],
            start_lng=record["coordinates"]["start"][1],
            end_lat=record["coordinates"]["end"][0],
            end_lng=record["coordinates"]["end"][1],
            health_score=record["health_score"],
        )
        for record in records
    ]


def seed_projects(records):
    return [
        ProjectRecord(
            project_id=record["project_id"],
            road_id=record["road_id"],
            contractor_id=record["contractor_id"],
            tender_id=record["tender_id"],
            sanctioned_amount=record["sanctioned_amount"],
            spent_amount=record["spent_amount"],
            start_date=parse_date(record["start_date"]),
            end_date=parse_date(record["end_date"]),
            status=record["status"],
        )
        for record in records
    ]


def seed_maintenance(records):
    return [
        MaintenanceRecord(
            maintenance_id=record["maintenance_id"],
            road_id=record["road_id"],
            last_relaying_date=parse_date(record["last_relaying_date"]),
            activity_type=record["activity_type"],
            cost=record["cost"],
            contractor_id=record["contractor_id"],
            next_scheduled=parse_date(record["next_scheduled"]),
        )
        for record in records
    ]


def seed_authorities(records):
    return [Authority(**record) for record in records]


def seed_contractors(records):
    return [Contractor(**record) for record in records]


def clear_existing_data(db):
    db.query(Complaint).delete()
    db.query(MaintenanceRecord).delete()
    db.query(ProjectRecord).delete()
    db.query(RoadSegment).delete()
    db.query(Authority).delete()
    db.query(Contractor).delete()


def insert_records(db, label, records):
    db.bulk_save_objects(records)
    print(f"Seeding {label}... {len(records)} inserted")


def main():
    create_tables()

    roads = seed_roads(load_json("roads.json"))
    contractors = seed_contractors(load_json("contractors.json"))
    authorities = seed_authorities(load_json("authorities.json"))
    projects = seed_projects(load_json("projects.json"))
    maintenance = seed_maintenance(load_json("maintenance.json"))

    db = SessionLocal()
    try:
        clear_existing_data(db)
        insert_records(db, "roads", roads)
        insert_records(db, "contractors", contractors)
        insert_records(db, "authorities", authorities)
        insert_records(db, "projects", projects)
        insert_records(db, "maintenance", maintenance)
        db.commit()
        print("Seed complete")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

