# app/models/input_models.py

from pydantic import BaseModel
from typing import Optional
from enum import Enum


class RespiratoryInput(BaseModel):
    spo2: Optional[int] = None
    on_oxygen: Optional[bool] = None
    oxygen_flow_lpm: Optional[int] = None



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
    respiratory: RespiratoryInput
    mobility: MobilityInput
    pressure_injury: PressureInjuryInput
    feeding: FeedingInput
    cognitive: CognitiveInput
    elimination: EliminationInput
    wound_care: WoundCareInput
    home_environment: HomeEnvironmentInput

