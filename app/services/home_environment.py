from app.models.input_models import HomeEnvironmentInput, MobilityInput


def evaluate_home_environment_needs(home: HomeEnvironmentInput, mobility: MobilityInput):
    advice = []

    if (
        home.layout == "Multi-floor"
        and not home.lift_available
        and mobility.status != "Independent"
    ):
        advice.append("Ground floor setup advised")
        advice.append("Avoid stair use")

    return advice
