from app.models.input_models import MobilityInput


def evaluate_mobility_needs(mobility: MobilityInput):
    equipment = []

    if mobility.status == "Bedridden":
        equipment.extend([
            "Hospital bed (semi-fowler)",
            "Air mattress",
            "Bedside commode"
        ])

    elif mobility.status == "Wheelchair-bound":
        equipment.extend([
            "Wheelchair",
            "Bedside commode"
        ])

    elif mobility.status == "Walks with assistance":
        equipment.append("Walker / walking stick")

    return equipment
