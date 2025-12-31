
from typing import List, Dict
from app.models.input_models import RespiratoryInput


def evaluate_respiratory_needs(respiratory: RespiratoryInput) -> List[Dict]:
    """
    Evaluate respiratory status and return equipment recommendations.
    """

    recommendations = []

    # If oxygen is needed
    if respiratory.on_oxygen or (
        respiratory.spo2 is not None and respiratory.spo2 < 88
    ):
        recommendations.append({
            "equipment": "Oxygen Concentrator",
            "category": "Essential"
        })

        # High flow oxygen → add cylinder
        if respiratory.oxygen_flow_lpm is not None and respiratory.oxygen_flow_lpm >= 5:
            recommendations.append({
                "equipment": "Oxygen Cylinder",
                "category": "Essential"
            })

        # Delivery interface
        recommendations.append({
            "equipment": "Nasal Cannula",
            "category": "Essential"
        })

    return recommendations
