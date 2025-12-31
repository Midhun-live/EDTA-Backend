from fastapi import APIRouter
from app.models.input_models import AssessmentInput
from app.api.orchestrator import generate_discharge_report

router = APIRouter()

@router.post("/assessment")
def submit_assessment(payload: AssessmentInput):
    report=generate_discharge_report(payload)
    return report
