from typing import List, Dict
from app.models.input_models import WoundCareInput


def evaluate_wound_care_needs(wound: WoundCareInput) -> List[Dict]:
    recommendations = []

    if wound.dressings_required:
        recommendations.append({
            "equipment": "Dressing Supplies",
            "category": "Essential"
        })

    return recommendations
