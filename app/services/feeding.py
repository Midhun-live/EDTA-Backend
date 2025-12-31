from typing import List, Dict
from app.models.input_models import FeedingInput, FeedingMethod


def evaluate_feeding_needs(feeding: FeedingInput) -> List[Dict]:
    recommendations = []

    if feeding.method in (
        FeedingMethod.RYLES_TUBE,
        FeedingMethod.PEG_TUBE
    ):
        recommendations.extend([
            {
                "equipment": "Feeding Pump",
                "category": "Optional"
            },
            {
                "equipment": "Syringes and Feeding Consumables",
                "category": "Essential"
            }
        ])

    return recommendations
