from app.models.input_models import WoundCareInput


def evaluate_wound_care_needs(input: WoundCareInput):
    if input.dressings_required:
        return ["Dressing supplies"]
    return []
