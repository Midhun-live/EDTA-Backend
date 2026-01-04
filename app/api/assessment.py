from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.models.input_models import AssessmentInput
from app.models.assessment_record import AssessmentRecord
from app.api.orchestrator import generate_discharge_report
from app.services.auth_service import get_current_user
from app.db.deps import get_db

router = APIRouter()


@router.post("/assessments")
def create_assessment(
    payload: AssessmentInput,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    assessment_id = str(uuid.uuid4())

    # 1️⃣ Generate clinical output
    output = generate_discharge_report(payload)

    # 2️⃣ Patient JSON (JSON-safe)
    patient_data = {
        "name": payload.patient_name,
        "age": payload.age,
        "contact_number": payload.contact_number,
        "discharge_date": payload.discharge_date.isoformat()
        if payload.discharge_date else None,
    }

    # 3️⃣ ORM record
    record = AssessmentRecord(
        id=assessment_id,
        user_id=current_user["user_id"],
        patient=patient_data,
        input_data=payload.model_dump(
            exclude={
                "patient_name",
                "age",
                "contact_number",
                "discharge_date"
            }
        ),
        output_data=output,
        created_at=datetime.utcnow(),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "assessment_id": record.id,
        "patient": record.patient,
        "created_at": record.created_at,
        "output": record.output_data,
    }



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
            AssessmentRecord.user_id == current_user["user_id"],
        )
        .first()
    )

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {
        "assessment_id": assessment.id,
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
        .filter(AssessmentRecord.user_id == current_user["user_id"])
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
