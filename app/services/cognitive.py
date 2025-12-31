from typing import List, Dict
from app.models.input_models import CognitiveInput, CaregiverAvailability


def evaluate_cognitive_supervision_needs(cognitive: CognitiveInput) -> Dict:
    """
    Evaluate supervision needs based on caregiver availability
    and cognitive concerns.
    """

    equipment = []
    care_advice = []

    if (
        cognitive.caregiver_availability == CaregiverAvailability.NONE
        or cognitive.cognitive_concerns
    ):
        equipment.append({
            "equipment": "Full-time Caregiver Support",
            "category": "Essential"
        })

        care_advice.append(
            "Night-time supervision is advised to ensure patient safety."
        )

    return {
        "equipment": equipment,
        "care_advice": care_advice
    }
