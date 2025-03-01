from typing import TypedDict
import pydantic

class InteractionMetadata(TypedDict):
    diagnosis: str | None
    diagnosis_success: bool
    interaction_duration: int
    num_symptoms_recovered: int
    confidence_history: list

class Profile(TypedDict):
    patient_id: int
    ethnicity: str
    gender: str
    diagnosis: str
    revealed_symptoms: dict[str, str]
    hidden_symptoms: dict[str, str]
    interaction_metadata: InteractionMetadata

class Message(TypedDict):
    role: str
    content: str

class Conversation(TypedDict):
    """Conversation data structure."""
    profile: Profile
    patient_history: list[Message]
    doctor_history: list[Message]


class Diagnosis(pydantic.BaseModel):
    """Diagnosis data structure."""
    diagnosis: str
    confidence: float

class DoctorResponse(pydantic.BaseModel):
    """Structured response from the doctor."""
    interaction_step: int
    free_form_thoughts: str
    known_symptoms: list[str]
    diagnosis_rankings: list[Diagnosis]
    symptoms_to_verify_or_refute: list[str]
    response_to_patient: str
