from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Authority
from schemas import AuthorityDetail

router = APIRouter()


@router.get("", response_model=list[AuthorityDetail])
def list_authorities(db: Session = Depends(get_db)):
    return [AuthorityDetail.model_validate(authority) for authority in db.query(Authority).all()]


@router.get("/{authority_id}", response_model=AuthorityDetail)
def get_authority(authority_id: str, db: Session = Depends(get_db)):
    authority = db.get(Authority, authority_id)
    if not authority:
        raise HTTPException(status_code=404, detail="Authority not found")
    return AuthorityDetail.model_validate(authority)

