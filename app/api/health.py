from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from fastapi import Response


router = APIRouter()

@router.api_route("/health/db", methods=["GET", "HEAD"])
def db_health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return Response(status_code=200)
