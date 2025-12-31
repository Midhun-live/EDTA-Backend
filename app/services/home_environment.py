from typing import Dict, List
from app.models.input_models import (
    HomeEnvironmentInput,
    MobilityInput,
    MobilityStatus,
    HomeLayout
)


def evaluate_home_environment_needs(
    home: HomeEnvironmentInput,
    mobility: MobilityInput
) -> Dict:
    """
    Evaluate home safety based on layout and mobility.
    """

    advice: List[str] = []

    poor_mobility = mobility.status in (
        MobilityStatus.BEDRIDDEN,
        MobilityStatus.WHEELCHAIR_BOUND
    )

    if (
        home.layout == HomeLayout.MULTI_FLOOR
        and not home.lift_available
        and poor_mobility
    ):
        advice.extend([
            "Ground-floor living arrangement is advised.",
            "Avoid stair use to reduce fall risk."
        ])

    return {
        "care_advice": advice
    }
