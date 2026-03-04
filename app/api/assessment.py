from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
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

from fastapi.responses import StreamingResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

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

router = APIRouter()


from fastapi import Body
from app.models.input_models import AssessmentInput
from fastapi.encoders import jsonable_encoder

def generate_assessment_pdf_buffer(assessment: AssessmentRecord) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    # ✅ Metadata at top
    elements.append(Paragraph("EDTA Assessment Report", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Account Holder: {assessment.user.name}", styles["Normal"]))
    elements.append(Paragraph(f"Account Email: {assessment.user.email}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Patient Name: {assessment.patient_name}", styles["Normal"]))
    elements.append(Paragraph(f"Age: {assessment.patient_age}", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

from fastapi import UploadFile

async def send_assessment_email_with_pdf(assessment: AssessmentRecord):
    pdf_buffer = generate_assessment_pdf_buffer(assessment)
    pdf_buffer.seek(0)
    
    pdf_attachment = UploadFile(
        filename=f"assessment_{assessment.id}.pdf",
        file=pdf_buffer,
        headers={"content-type": "application/pdf"}
    )

    message = MessageSchema(
        subject="New EDTA Assessment Created",
        recipients=["midhunchakkaravarthy07@gmail.com"],
        body=f"""
        A new assessment has been created.

        Account Holder: {assessment.user.name}
        Account Email: {assessment.user.email}

        The assessment PDF is attached.
        """,
        subtype="plain",
        attachments=[pdf_attachment]
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception as e:
        print("Email sending failed:", e)

@router.post("/assessments")
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

    share_url = f"https://your-frontend.vercel.app/share/{record.share_id}"
    background_tasks.add_task(send_assessment_email_with_pdf, record)

    return {
        "assessment_id": record.id,
        "share_token": record.share_token,
        "share_id": record.share_id,
        "share_url": share_url,
        "patient": record.patient,
        "created_at": record.created_at,
        "output": record.output_data,
    }

@router.get("/share/{share_id}")
def get_shared_assessment(share_id: str, db: Session = Depends(get_db)):
    assessment = (
        db.query(AssessmentRecord)
        .filter(AssessmentRecord.share_id == share_id)
        .first()
    )

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return assessment.output_data


@router.get("/assessments/my")
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


@router.get("/assessments/{id}/pdf")
def download_assessment_pdf(id: str, db: Session = Depends(get_db)):
    assessment = db.query(AssessmentRecord).filter(
        AssessmentRecord.id == id
    ).first()

    if not assessment:
        raise HTTPException(status_code=404, detail="Not Found")

    buffer = generate_assessment_pdf_buffer(assessment)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=assessment_{id}.pdf"
        },
    )


@router.get("/assessments/{assessment_id}")
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


@router.get("/assessments")
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

@router.get("/share/{token}")
def get_shared_assessment_by_token(token: str, db: Session = Depends(get_db)):
    assessment = db.query(AssessmentRecord).filter(
        AssessmentRecord.share_token == token
    ).first()

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return assessment

    return assessment
