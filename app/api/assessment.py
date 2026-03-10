from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.models.input_models import AssessmentInput
from app.models.assessment_record import AssessmentRecord
from app.api.orchestrator import generate_discharge_report
from app.db.deps import get_current_user
from app.db.deps import get_db

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os

from fastapi.responses import StreamingResponse, Response
from io import BytesIO

from app.services.pdf_service import generate_assessment_pdf

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

router = APIRouter(prefix="/assessments", tags=["assessments"])
share_router = APIRouter(prefix="/share")


from fastapi import Body
from app.models.input_models import AssessmentInput
from fastapi.encoders import jsonable_encoder

import tempfile
import os

async def send_assessment_email(assessment: AssessmentRecord):
    pdf_bytes = generate_assessment_pdf(assessment, assessment.user)

    file_stream = BytesIO(pdf_bytes)
    upload_file = UploadFile(
        filename="assessment_report.pdf",
        file=file_stream,
        headers={"content-type": "application/pdf"}
    )

    message = MessageSchema(
        subject="EDTA Assessment Report",
        recipients=["midhunchakkaravarthy07@gmail.com"],
        body="Assessment report attached.",
        subtype="plain",
        attachments=[upload_file]
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception as e:
        print("Email sending failed:", e)

@router.post("")
async def create_assessment(
    background_tasks: BackgroundTasks,
    payload: AssessmentInput = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    output = generate_discharge_report(payload)

    record = AssessmentRecord(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        patient={
            "name": payload.patient_name,
            "age": payload.age,
            "contact_number": payload.contact_number,
            "discharge_date": payload.discharge_date.isoformat(),
        },
        input_data=jsonable_encoder(payload),
        output_data=jsonable_encoder(output),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    if not record.share_token:
        record.share_token = str(uuid.uuid4())
        db.commit()

    share_url = f"https://your-frontend.vercel.app/share/{record.share_token}"
    
    background_tasks.add_task(send_assessment_email, record)

    return {
        "assessment_id": record.id,
        "share_token": record.share_token,
        "share_url": share_url,
        "patient": record.patient,
        "created_at": record.created_at,
        "output": record.output_data,
    }




@router.get("/my")
def get_my_assessments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Fetch a minimal list of assessments owned by the logged-in user.
    """
    records = (
        db.query(AssessmentRecord)
        .filter(AssessmentRecord.user_id == current_user.id)
        .order_by(AssessmentRecord.created_at.desc())
        .all()
    )

    return [
        {
            "assessment_id": r.id,
            "patient_name": r.patient.get("name") if r.patient else "Unknown",
            "age": r.patient.get("age") if r.patient else None,
            "discharge_date": r.patient.get("discharge_date") if r.patient else None,
            "created_at": r.created_at,
        }
        for r in records
    ]


@router.get("/{assessment_id}/pdf")
def download_pdf(assessment_id: str, db: Session = Depends(get_db)):
    assessment = db.query(AssessmentRecord).filter(
        AssessmentRecord.id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
        
    pdf_bytes = generate_assessment_pdf(assessment, assessment.user)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="assessment_report.pdf"'
        }
    )


@router.get("/{assessment_id}")
def get_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Fetch a single assessment (only if owned by user)
    """

    assessment = (
        db.query(AssessmentRecord)
        .filter(
            AssessmentRecord.id == assessment_id,
            AssessmentRecord.user_id == current_user.id,
        )
        .first()
    )

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if not assessment.share_token:
        assessment.share_token = str(uuid.uuid4())
        db.commit()

    return {
        "assessment_id": assessment.id,
        "share_token": assessment.share_token,
        "patient": assessment.patient,
        "created_at": assessment.created_at,
        "output": assessment.output_data,
    }


@router.get("")
def list_assessments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all assessments created by logged-in user
    """

    records = (
        db.query(AssessmentRecord)
        .filter(AssessmentRecord.user_id == current_user.id)
        .order_by(AssessmentRecord.created_at.desc())
        .all()
    )

    return [
        {
            "assessment_id": r.id,
            "patient": r.patient,
            "created_at": r.created_at,
        }
        for r in records
    ]

@share_router.get("/{share_token}")
def get_shared_assessment(share_token: str, db: Session = Depends(get_db)):
    assessment = db.query(AssessmentRecord).filter(
        AssessmentRecord.share_token == share_token
    ).first()

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {
        "patient": assessment.patient,
        "created_at": assessment.created_at,
        "output": assessment.output_data
    }
