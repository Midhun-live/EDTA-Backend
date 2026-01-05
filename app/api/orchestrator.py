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
    from app.services.respiratory import evaluate_respiratory_needs
    from app.services.mobility import evaluate_mobility_needs
    from app.services.pressure_injury import evaluate_pressure_injury_needs
    from app.services.feeding import evaluate_feeding_needs
    from app.services.cognitive import evaluate_cognitive_supervision_needs
    from app.services.elimination import evaluate_elimination_needs
    from app.services.wound_care import evaluate_wound_care_needs
    from app.services.home_environment import evaluate_home_environment_needs

    resp_eq = evaluate_respiratory_needs(assessment.respiratory)
    mob_eq = evaluate_mobility_needs(assessment.mobility)
    press_eq = evaluate_pressure_injury_needs(assessment.pressure_injury)
    feed_eq = evaluate_feeding_needs(assessment.feeding)
    elim_eq = evaluate_elimination_needs(assessment.elimination)
    wound_eq = evaluate_wound_care_needs(assessment.wound_care)

    cog_eq, cog_adv = evaluate_cognitive_supervision_needs(assessment.cognitive)
    home_adv = evaluate_home_environment_needs(
        assessment.home_environment,
        assessment.mobility
    )

    return {
        "respiratory": {
            "equipment": resp_eq,
            "care_instructions": []
        },
        "mobility": {
            "equipment": mob_eq
        },
        "pressure_injury": {
            "equipment": press_eq
        },
        "feeding": {
            "equipment": feed_eq
        },
        "cognitive": {
            "equipment": cog_eq,
            "care_instructions": cog_adv
        },
        "elimination": {
            "equipment": elim_eq
        },
        "wound_care": {
            "equipment": wound_eq
        },
        "home_environment": {
            "care_instructions": home_adv
        }
    }
