from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.auth_models import SignupRequest, LoginRequest, TokenResponse, ForgotPasswordOTPRequest, VerifyOTPRequest, ResetPasswordOTPRequest
from app.services.auth_service import signup, login, hash_password
from datetime import datetime, timedelta
from app.models.users import User
from email.mime.text import MIMEText
import smtplib
import random

router = APIRouter(prefix="/auth", tags=["Auth"])

def send_email_otp(to_email: str, otp: str):
    sender_email = "eldersmilesllp@gmail.com"
    sender_password = "eepw bwfe fpvw rpae"

    msg = MIMEText(f"Your OTP is: {otp}")
    msg["Subject"] = "Password Reset OTP"
    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

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

@router.post("/forgot-password-otp")
def send_otp(payload: ForgotPasswordOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    # Always return success (security)
    if not user:
        return {"message": "If email exists, OTP sent"}

    otp = str(random.randint(100000, 999999))

    user.reset_otp = otp
    user.reset_otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    user.otp_verified = False

    db.commit()

    # TODO: Send email here
    send_email_otp(user.email, otp)

    return {"message": "If email exists, OTP sent"}

@router.post("/verify-otp")
def verify_otp(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not user.reset_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if user.reset_otp != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if not user.reset_otp_expiry or user.reset_otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    user.otp_verified = True
    db.commit()

    return {"message": "OTP verified"}

@router.post("/reset-password-otp")
def reset_password_otp(payload: ResetPasswordOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not user.otp_verified:
        raise HTTPException(status_code=400, detail="OTP not verified")

    user.password_hash = hash_password(payload.new_password)

    # Clear OTP data
    user.reset_otp = None
    user.reset_otp_expiry = None
    user.otp_verified = False

    db.commit()

    return {"message": "Password reset successful"}