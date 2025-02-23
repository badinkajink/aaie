import json
import random

import schema

def save_history(profile: schema.Profile, patient_history: list[schema.Message], doctor_history: list[schema.Message]) -> None:
    """Save a conversation to disk."""
    conversation = schema.Conversation(profile=profile, patient_history=patient_history, doctor_history=doctor_history)
    rand_id = random.randint(1000, 9999)
    with open(f'conversations/{profile["patient_id"]}_{rand_id}.json', 'w') as f:
        json.dump(conversation, f, indent=4)
