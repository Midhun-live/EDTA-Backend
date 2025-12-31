from typing import List, Dict
from app.models.input_models import MobilityInput, MobilityStatus


def evaluate_mobility_needs(mobility: MobilityInput) -> List[Dict]:
    recommendations = []

    if mobility.status == MobilityStatus.BEDRIDDEN:
        recommendations.extend([
            {
                "equipment": "Hospital Bed (Semi-Fowler)",
                "category": "Essential"
            },
            {
                "equipment": "Air Mattress",
                "category": "Essential"
            },
            {
                "equipment": "Bedside Commode",
                "category": "Essential"
            }
        ])

    elif mobility.status == MobilityStatus.WHEELCHAIR_BOUND:
        recommendations.extend([
            {
                "equipment": "Wheelchair",
                "category": "Essential"
            },
            {
                "equipment": "Bedside Commode",
                "category": "Essential"
            }
        ])

    elif mobility.status == MobilityStatus.WALKS_WITH_ASSISTANCE:
        recommendations.append({
            "equipment": "Walker / Walking Stick",
            "category": "Recommended"
        })

    # Independent → no equipment

    return recommendations