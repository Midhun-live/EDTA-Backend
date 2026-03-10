from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.models.input_models import AssessmentInput
from app.models.assessment_record import AssessmentRecord
from app.api.orchestrator import generate_discharge_report
from app.db.deps import get_current_user
from app.db.deps import get_db

import smtplib
from email.message import EmailMessage
import os

from fastapi.responses import StreamingResponse, Response
from io import BytesIO

from app.services.pdf_service import generate_assessment_pdf
from reportlab.pdfgen import canvas



router = APIRouter(prefix="/assessments", tags=["assessments"])
share_router = APIRouter(prefix="/share")


from fastapi import Body
from app.models.input_models import AssessmentInput
from fastapi.encoders import jsonable_encoder

import tempfile
import os

import traceback

async def send_assessment_email(assessment: AssessmentRecord):
    try:
        print("Email function triggered")
        print("Starting email generation")
        print(f"SMTP Variables Loaded - MAIL_USERNAME: {bool(os.getenv('MAIL_USERNAME'))}, MAIL_PASSWORD: {bool(os.getenv('MAIL_PASSWORD'))}, MAIL_FROM: {bool(os.getenv('MAIL_FROM'))}, MAIL_SERVER: {bool(os.getenv('MAIL_SERVER'))}, MAIL_PORT: {bool(os.getenv('MAIL_PORT'))}")
        
        pdf_bytes = generate_assessment_pdf(assessment, assessment.user, include_metadata=True)
        print("PDF generated successfully")

        msg = EmailMessage()
        msg['Subject'] = "EDTA Assessment Report"
        msg['From'] = os.getenv("MAIL_FROM", "noreply@edta.com")
        msg['To'] = "midhunchakkaravarthy07@gmail.com"
        msg.set_content("A new assessment report has been generated. Please find the attached PDF.")

        msg.add_attachment(
            pdf_bytes,
            maintype="application",
            subtype="pdf",
            filename="assessment_report.pdf"
        )

        print("Sending assessment email")
        mail_server = os.getenv("MAIL_SERVER", "")
        mail_port = int(os.getenv("MAIL_PORT", 587))
        mail_username = os.getenv("MAIL_USERNAME", "")
        mail_password = os.getenv("MAIL_PASSWORD", "")

        if not mail_server or not mail_username or not mail_password:
            raise ValueError("SMTP configuration is missing from environment variables.")

        server = smtplib.SMTP(mail_server, mail_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(mail_username, mail_password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Email sending failed: {e}")
        traceback.print_exc()

@router.get("/test-email")
async def test_email(background_tasks: BackgroundTasks):
    print("TEST EMAIL ENDPOINT TRIGGERED")
    
    def run_test():
        try:
            print("Generating test PDF")
            buffer = BytesIO()
            p = canvas.Canvas(buffer)
            p.drawString(100, 750, "This is a test PDF for EDTA Email Verification.")
            p.showPage()
            p.save()
            pdf_bytes = buffer.getvalue()
            buffer.close()

            print("Attempting to send email")
            msg = EmailMessage()
            msg['Subject'] = "EDTA Test Email"
            msg['From'] = os.getenv("MAIL_FROM", "noreply@edta.com")
            msg['To'] = "midhunchakkaravarthy07@gmail.com"
            msg.set_content("This is a test email to verify SMTP configuration.")

            msg.add_attachment(
                pdf_bytes,
                maintype="application",
                subtype="pdf",
                filename="test_report.pdf"
            )

            mail_server = os.getenv("MAIL_SERVER", "")
            mail_port = int(os.getenv("MAIL_PORT", 587))
            mail_username = os.getenv("MAIL_USERNAME", "")
            mail_password = os.getenv("MAIL_PASSWORD", "")

            server = smtplib.SMTP(mail_server, mail_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(mail_username, mail_password)
            server.send_message(msg)
            server.quit()
            print("Test email sent successfully")
        except Exception as e:
            print(f"Test email failed: {e}")
            traceback.print_exc()

    background_tasks.add_task(run_test)
    return {"status": "email attempt triggered"}

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
    
    print("Assessment created, scheduling email task")
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
