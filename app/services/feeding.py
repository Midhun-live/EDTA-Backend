from app.models.input_models import FeedingInput, FeedingMethod


def evaluate_feeding_needs(feeding: FeedingInput):
    equipment = []

    if feeding.method in (
        FeedingMethod.RYLES_TUBE,
        FeedingMethod.PEG_TUBE
    ):
        equipment.append("Feeding pump")
        equipment.append("Feeding consumables")

    return equipment
