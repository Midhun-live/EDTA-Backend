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

def generate_discharge_report(assessment):
    equipment = []
    advice = []

    equipment += evaluate_respiratory_needs(assessment.respiratory)
    equipment += evaluate_mobility_needs(assessment.mobility)
    equipment += evaluate_pressure_injury_needs(assessment.pressure_injury)
    equipment += evaluate_feeding_needs(assessment.feeding)
    equipment += evaluate_elimination_needs(assessment.elimination)
    equipment += evaluate_wound_care_needs(assessment.wound_care)

    cog_equipment, cog_advice = evaluate_cognitive_supervision_needs(assessment.cognitive)
    equipment += cog_equipment
    advice += cog_advice

    advice += evaluate_home_environment_needs(
        assessment.home_environment,
        assessment.mobility
    )

    return {
        "equipment_recommended": list(dict.fromkeys(equipment)),
        "care_instructions": advice
    }
