import json
import random

import schema

def save_history(profile: schema.Profile, patient_history: list[schema.Message], doctor_history: list[schema.Message], patient_is_first: bool = True, filepath: str = None) -> None:
    """Save a conversation to disk."""
    conversation = schema.Conversation(profile=profile, patient_history=patient_history, doctor_history=doctor_history, patient_is_first=patient_is_first)
    rand_id = random.randint(1000, 9999)
    filename = ""
    if filepath is None:
        filename = f'conversations/{profile["patient_id"]}_{rand_id}.json'
    else:
        filename = f'{filepath}/{profile["patient_id"]}_{rand_id}.json'
    with open(filename, 'w') as f:
        json.dump(conversation, f, indent=4)
    return filename
