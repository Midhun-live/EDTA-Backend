from typing import List, Dict
from app.models.input_models import FeedingInput, FeedingMethod


def evaluate_feeding_needs(input):
    equipment = []

    if input.method in ["Ryles", "PEG"]:
        equipment.append("Feeding pump")
        equipment.append("Feeding consumables")

    return {"equipment": equipment}

