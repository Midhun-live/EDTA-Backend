from typing import List, Dict
from app.models.input_models import EliminationInput


def evaluate_elimination_needs(elimination: EliminationInput) -> List[Dict]:
    recommendations = []

    if not elimination.can_use_toilet_independently:
        recommendations.extend([
            {
                "equipment": "Bedside Commode",
                "category": "Essential"
            },
            {
                "equipment": "Urinal / Bedpan",
                "category": "Essential"
            }
        ])

    return recommendations