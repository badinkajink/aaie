from typing import TypedDict, Required
import pydantic

class InteractionMetadata(TypedDict, total=False):
    diagnosis: Required[str | None]
    diagnosis_success: Required[bool]
    interaction_duration: Required[int]
    num_symptoms_recovered: Required[int]
    confidence_history: Required[list]
    model: str

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

class Conversation(TypedDict, total=False):
    """Conversation data structure."""
    profile: Required[Profile]
    patient_history: Required[list[Message]]
    doctor_history: Required[list[Message]]
    patient_is_first: bool

class Symptom(pydantic.BaseModel):
    """Diagnosis data structure."""
    doctor_note: str
    term: str
    desc: str

class SymptomCheck(pydantic.BaseModel):
    """Symptom check data structure."""
    match_details: list[Symptom]
    found_symptoms_history: list[int]
    found_symptoms: int

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
    diagnosis_relayed_to_patient: bool
    response_to_patient: str

class PatientResponse(pydantic.BaseModel):
    """Structured response from the patient."""
    response: str