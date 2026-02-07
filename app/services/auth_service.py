from datetime import datetime, timedelta
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt

from app.models.users import User

# =====================================================
# JWT configuration
# =====================================================
SECRET_KEY = "CHANGE_THIS_SECRET"  # move to .env later
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# =====================================================
# Password hashing (ARGON2 — FINAL FIX)
# =====================================================
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


# =====================================================
# JWT helpers
# =====================================================
def create_access_token(payload: dict) -> str:
    to_encode = payload.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# =====================================================
# Auth services
# =====================================================
def signup(
    db: Session,
    name: str,
    email: str,
    role: str,
    password: str
) -> str:
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        name=name,
        email=email,
        role=role,
        password_hash=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return create_access_token({
        "sub": user.id,
        "email": user.email,
        "role": user.role
    })


def login(db: Session, email: str, password: str) -> str:
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return create_access_token({
        "sub": user.id,
        "email": user.email,
        "role": user.role
    })
