from app.models.input_models import RespiratoryInput


def evaluate_respiratory_needs(resp: RespiratoryInput):
    equipment = []

    # Oxygen logic (EDTA)
    if resp.on_oxygen or resp.spo2_category == "<88":
        equipment.append("Oxygen concentrator (5L)")
        equipment.append("Nasal cannula")

        if resp.oxygen_flow_lpm is not None and resp.oxygen_flow_lpm > 5:
            equipment.append("Oxygen cylinders")

    # NIV
    if resp.on_niv:
        equipment.append(
            f"NIV with IPAP {resp.ipap}, EPAP {resp.epap}, PEEP {resp.peep}"
        )

    # Tracheostomy
    if resp.tracheostomy:
        equipment.append("Tracheostomy care bundle")

    # Suction
    if resp.requires_suctioning:
        equipment.append("Mobile suction apparatus")

    return equipment
