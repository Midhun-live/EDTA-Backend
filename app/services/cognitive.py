from app.models.input_models import CognitiveInput


def evaluate_cognitive_supervision_needs(input: CognitiveInput):
    equipment = []
    advice = []

    if input.cognitive_concerns or input.caregiver_availability == "None":
        equipment.append("Full-time caregiver")
        advice.append("Night supervision advised")

    return equipment, advice
