from fastapi import APIRouter, Header
from datetime import datetime
import uuid

from app.models.input_models import AssessmentInput
from app.api.orchestrator import generate_discharge_report
from app.services.storage import ASSESSMENTS_DB
from app.services.auth_service import get_current_user
from fastapi import Depends

router = APIRouter()


@router.post("/assessments")
def create_assessment(
    payload: AssessmentInput,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    role = current_user["role"]

    """
    Create a discharge assessment with patient details.
    """

    # 1️⃣ Generate clinical output (patient data NOT used here)
    output = generate_discharge_report(payload)

    assessment_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    assessment_record = {
        "id": assessment_id,

        # ✅ patient details FROM FORM
        "patient": payload.patient.dict(),

        # clinical
        "input_data": payload.dict(exclude={"patient"}),
        "output_data": output,

        # user mapping
        "created_by_user_id": user_id,
        "created_by_role": role,

        "created_at": created_at
    }

    ASSESSMENTS_DB.append(assessment_record)

    return {
        "assessment_id": assessment_id,
        "patient": assessment_record["patient"],
        "created_by": {
            "user_id": user_id,
            "role": role
        },
        "created_at": created_at,
        "output": output
    }

@router.get("/assessments/{assessment_id}")
def get_assessment(
    assessment_id: str,
    current_user: dict = Depends(get_current_user)
):
    print("ASSESSMENTS_DB:", ASSESSMENTS_DB)
    user_id = current_user["user_id"]
    role = current_user["role"]
    for assessment in ASSESSMENTS_DB:
        if assessment["id"] == assessment_id:
            if assessment["created_by_user_id"] != user_id:
                return {"error": "Access denied"}

            return {
                "assessment_id": assessment["id"],
                "patient": assessment["patient"],
                "created_at": assessment["created_at"],
                "created_by": {
                    "user_id": user_id,
                    "role": role
                },
                "output": assessment["output_data"]
            }

    return {"error": "Assessment not found"}
