from app.models.input_models import EliminationInput


def evaluate_elimination_needs(input: EliminationInput):
    if not input.can_use_toilet_independently:
        return ["Bedside commode", "Urinal / bedpan"]
    return []
