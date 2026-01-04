from fastapi import APIRouter, HTTPException, Depends
from app.models.auth_models import (
    SignupRequest,
    LoginRequest,
    AuthResponse,
    UserResponse
)
from app.services.auth_service import (
    USERS_DB,
    hash_password,
    verify_password,
    create_access_token,
    get_user_by_email
)
import uuid

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignupRequest):
    if get_user_by_email(payload.email):
        raise HTTPException(status_code=400, detail="User already exists")

    user_id = str(uuid.uuid4())

    user = {
        "id": user_id,
        "name": payload.name,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "role": payload.role,
        "created_at": None
    }

    USERS_DB.append(user)

    token = create_access_token({
        "user_id": user_id,
        "role": payload.role
    })

    return {"access_token": token}


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    user = get_user_by_email(payload.email)

    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": user["id"],
        "role": user["role"]
    })

    return {"access_token": token}

@router.get("/me", response_model=UserResponse)
def get_me():
    # TEMP: will be implemented after auth middleware
    return {
        "id": "temp",
        "name": "Demo User",
        "email": "demo@edta.app",
        "role": "Nurse"
    }
