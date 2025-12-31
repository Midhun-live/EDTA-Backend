from typing import List, Dict
from app.models.input_models import PressureInjuryInput


def evaluate_pressure_injury_needs(pressure: PressureInjuryInput) -> Dict:
    """
    Evaluate pressure injury risk.
    Returns equipment + care instructions.
    """
    equipment = []
    care_instructions = []

    if pressure.has_pressure_sore or pressure.prolonged_bed_rest:
        equipment.append({
            "equipment": "Air Mattress",
            "category": "Essential"
        })

        care_instructions.append(
            "Reposition patient at least every 4 hours to prevent pressure injury."
        )

    return {
        "equipment": equipment,
        "care_instructions": care_instructions
    }
