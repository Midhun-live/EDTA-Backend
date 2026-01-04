# app/models/input_models.py

from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import date


from pydantic import BaseModel
from typing import Optional


class RespiratoryInput(BaseModel):
    # Core oxygenation
    spo2: int
    on_oxygen: bool
    oxygen_flow_lpm: Optional[float] = None

    # Non-invasive ventilation
    on_niv: bool = False
    ipap: Optional[int] = None
    epap: Optional[int] = None
    peep: Optional[int] = None

    # Airway
    tracheostomy: bool = False
    requires_suctioning: bool = False




class MobilityStatus(str, Enum):
    BEDRIDDEN = "Bedridden"
    WHEELCHAIR_BOUND = "Wheelchair-bound"
    WALKS_WITH_ASSISTANCE = "Walks with assistance"
    INDEPENDENT = "Independent"


class MobilityInput(BaseModel):
    status: MobilityStatus


class PressureInjuryInput(BaseModel):
    has_pressure_sore: Optional[bool] = None
    prolonged_bed_rest: Optional[bool] = None
    
class FeedingMethod(str, Enum):
    ORAL = "Oral"
    RYLES_TUBE = "Ryle’s tube"
    PEG_TUBE = "PEG tube"


class FeedingInput(BaseModel):
    method: FeedingMethod

class CaregiverAvailability(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    NONE = "None"


class CognitiveInput(BaseModel):
    caregiver_availability: CaregiverAvailability
    cognitive_concerns: bool

class EliminationInput(BaseModel):
    can_use_toilet_independently: bool

class WoundCareInput(BaseModel):
    dressings_required: bool

class HomeLayout(str, Enum):
    SINGLE_FLOOR = "Single-floor"
    MULTI_FLOOR = "Multi-floor"


class HomeEnvironmentInput(BaseModel):
    layout: HomeLayout
    lift_available: bool

class AssessmentInput(BaseModel):
    patient_name: str
    age: int
    contact_number: str
    discharge_date: date    
    respiratory: RespiratoryInput
    mobility: MobilityInput
    pressure_injury: PressureInjuryInput
    feeding: FeedingInput
    cognitive: CognitiveInput
    elimination: EliminationInput
    wound_care: WoundCareInput
    home_environment: HomeEnvironmentInput

class CreateAssessmentRequest(BaseModel):
    patient_name: str
    assessment_input: AssessmentInput

