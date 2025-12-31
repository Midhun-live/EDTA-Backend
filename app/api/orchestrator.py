# app/services/orchestrator.py

from app.models.input_models import AssessmentInput
from app.services.respiratory import evaluate_respiratory_needs
from app.services.mobility import evaluate_mobility_needs
from app.services.pressure_injury import evaluate_pressure_injury_needs
from app.services.feeding import evaluate_feeding_needs
from app.services.cognitive import evaluate_cognitive_supervision_needs
from app.services.elimination import evaluate_elimination_needs
from app.services.wound_care import evaluate_wound_care_needs
from app.services.home_environment import evaluate_home_environment_needs


def generate_discharge_report(assessment: AssessmentInput) -> dict:
    recommendations = []
    care_instructions = []

    # Respiratory
    if assessment.respiratory:
        recommendations.extend(
            evaluate_respiratory_needs(assessment.respiratory)
        )

    # Mobility
    if assessment.mobility:
        recommendations.extend(
            evaluate_mobility_needs(assessment.mobility)
        )

    # Pressure Injury
    if assessment.pressure_injury:
        pressure_result = evaluate_pressure_injury_needs(assessment.pressure_injury)
        recommendations.extend(pressure_result["equipment"])
        care_instructions.extend(pressure_result["care_instructions"])

    #Feeding and Swallowing
    if assessment.feeding:
        recommendations.extend(
            evaluate_feeding_needs(assessment.feeding)
        )
    
    if assessment.cognitive:
        cognitive_result = evaluate_cognitive_supervision_needs(assessment.cognitive)
        recommendations.extend(cognitive_result["equipment"])
        care_instructions.extend(cognitive_result["care_advice"])
    
    if assessment.elimination:
        recommendations.extend(
            evaluate_elimination_needs(assessment.elimination)
        )

    if assessment.wound_care:
        recommendations.extend(
            evaluate_wound_care_needs(assessment.wound_care)
        )

    if assessment.home_environment and assessment.mobility:
        home_result = evaluate_home_environment_needs(
            assessment.home_environment,
            assessment.mobility
        )
        care_instructions.extend(home_result["care_advice"])
    
    return {
        "equipment_recommended": recommendations,
        "care_instructions": care_instructions
    }
