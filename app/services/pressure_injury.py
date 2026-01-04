from app.models.input_models import PressureInjuryInput


def evaluate_pressure_injury_needs(input: PressureInjuryInput):
    if input.has_pressure_sore or input.prolonged_bed_rest:
        return ["Air mattress"]
    return []
