from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.auth_models import SignupRequest, LoginRequest, TokenResponse
from app.services.auth_service import signup, login

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=TokenResponse)
def signup_api(payload: SignupRequest, db: Session = Depends(get_db)):
    token = signup(
        db=db,
        name=payload.name,
        email=payload.email,
        role=payload.role,
        password=payload.password
    )
    return {"access_token": token}


@router.post("/login", response_model=TokenResponse)
def login_api(payload: LoginRequest, db: Session = Depends(get_db)):
    token = login(db, payload.email, payload.password)
    return {"access_token": token}
