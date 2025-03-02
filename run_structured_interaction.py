from collections import OrderedDict
import dotenv
import random
import numpy as np
import json
import pickle
import os
import numpy as np
import pandas as pd
import itertools
import openai
import schema
import save
import instructor
from google import generativeai as gemini
from prompts.patient_prompt import prompt as pp
from prompts.doctor_prompt_structured import prompt as dp
from prompts.symptom_check_prompt import prompt as scp
from prompts.symptom_check_prompt import reply as scr

env_file = '.env'
dotenv.load_dotenv(env_file, override=True)
gemini.configure(api_key=os.getenv("GEMINI_API_KEY"))

openai_api = openai.OpenAI(api_key=os.getenv("CORRELL_API_KEY"))
gemini_api = gemini.GenerativeModel(model_name='gemini-2.0-flash-lite')

openai_client = instructor.from_openai(client=openai_api)
gemini_client = instructor.from_gemini(client=gemini_api, mode=instructor.Mode.GEMINI_JSON)

# Change me to test another model
use_openai = True
if use_openai:
    unstructured_client = openai_api
    client = openai_client
    model = 'gpt-4o-mini'
    call_doctor_kwargs = {
        'model': model,
        'temperature': 0.7,
    }
    call_patient_kwargs = {
        'model': model,
        'temperature': 0.7,
    }
else:
    unstructured_client = gemini_api
    client = gemini_client
    model = 'gemini-2.0-flash-lite'
    call_doctor_kwargs = {}
    call_patient_kwargs = {}

import sys

def call_doctor(messages: list[schema.Message]) -> schema.DoctorResponse:
    response = client.completions.create(
        messages=messages,
        response_model=schema.DoctorResponse,
        **call_doctor_kwargs
    )
    return response

def call_patient(messages: list[schema.Message]) -> str:
    response = client.completions.create(
        messages=messages,
        response_model=schema.PatientResponse,
        **call_patient_kwargs
    )
    return response.response

def call_openai_symptom_check(messages: list[schema.Message]) -> schema.SymptomCheck:
    response = openai_client.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.4,
        response_model=schema.SymptomCheck
    )
    return response


def get_diagnosis_confidence(diagnosis_history: list[str, float]) -> dict[str, float]:
    all_diagnoses = {d.diagnosis for step in diagnosis_history for d in step}
    diagnosis_confidence = {d: [] for d in all_diagnoses}
    
    for step in diagnosis_history:
        step_conf_dict = {d.diagnosis: d.confidence for d in step}
        for d in all_diagnoses:
            diagnosis_confidence[d].append(step_conf_dict.get(d, np.nan))  # Use NaN if missing

    return diagnosis_confidence
if __name__ == '__main__':
    doctor_histories: dict[int, list[schema.Message]] = {}
    patient_histories: dict[int, list[schema.Message]] = {}

    start = int(sys.argv[1])
    end = int(sys.argv[2])
    fp = str(sys.argv[3])

    patient_profiles = pickle.load(open('patient_profiles.pkl', 'rb'))
    threshold = 0.8
    steps = 8
    num_profiles = 10 # how many interactions to run out of 240 profiles
    # patient_profiles: dict[int, schema.Profile] = OrderedDict(itertools.islice(patient_profiles.items(), num_profiles))
    # start = 0
    # end = 60 # the last profile id to run up to
    patient_profiles = OrderedDict(itertools.islice(patient_profiles.items(), start, end))
    print(f"Processing profiles {start} to {end}...")

    # Iterate through patient profiles
    for i, profile in patient_profiles.items():
        doctor_config = {
            "gender": profile["gender"],
            "ethnicity": profile["ethnicity"],
            "confidence_threshold": threshold,
            "interaction_steps": steps
        }

        # Initialize metadata
        metadata = profile['interaction_metadata']
        metadata.update({
            "diagnosis": None,
            "diagnosis_success": False,
            "interaction_duration": 0,
            "num_symptoms_recovered": 0,
            "confidence_history": [],
            'model': model,
        })
        
        # Format prompts
        pp_copy = pp.format(**profile)
        dp_copy = dp.format(**doctor_config)
        
        # Initialize conversation histories
        doctor_history: list[schema.Message] = [{"role": "system", "content": dp_copy}]
        patient_history: list[schema.Message] = [{"role": "system", "content": pp_copy}]

        doctor_reply = "Hi, I'll be your doctor today. What brings you in?"
        doctor_responses = []
        next_response_is_last = False

        pid = profile['patient_id']
        print(f"Beginning conversation with patient {pid}: {profile['ethnicity']} {profile['gender']} (verbosity: {profile['verbosity']})")
        
        # Run interaction loop
        for step in range(steps):
            metadata["interaction_duration"] += 1
            
            # Update the patient history
            patient_history.append({"role": "user", "content": doctor_reply})

            # Patient response
            patient_reply = call_patient(patient_history)

            # Update patient conversation history
            patient_history.append({"role": "assistant", "content": patient_reply})

            # Update doctor conversation history
            doctor_history.append({"role": "user", "content": patient_reply})

            # Doctor response
            doctor_response = call_doctor(doctor_history)
            doctor_responses.append(doctor_response)

            # Update doctor conversation history with its full reply
            doctor_history.append({"role": "assistant", "content": doctor_response.model_dump_json()})
            
            if len(doctor_response.diagnosis_rankings):
                diagnosis = max(doctor_response.diagnosis_rankings,  key=lambda x: x.confidence)
                metadata['diagnosis'] = diagnosis.diagnosis
                metadata['confidence_history'].append(diagnosis.confidence)
            
            if doctor_response.diagnosis_relayed_to_patient:
                break

            doctor_reply = doctor_response.response_to_patient

        metadata["diagnosis_success"] = metadata['diagnosis'].lower() == 'melanoma'

        recovered_symptoms_history = [d.known_symptoms for d in doctor_responses]
        symptoms = {**profile['revealed_symptoms'], **profile['hidden_symptoms']}
        scr_copy = scr.format(recovered_symptoms_history=recovered_symptoms_history, symptoms=symptoms)
        symptom_check: list[schema.Message] = [{"role": "system", "content": scp}]
        symptom_check.append({"role": "user", "content": scr_copy})

        symptom_check_response = call_openai_symptom_check(symptom_check)
        metadata['num_symptoms_recovered'] = symptom_check_response.found_symptoms
        metadata['num_symptoms_recovered_history'] = symptom_check_response.found_symptoms_history

        diagnosis_history = [d.diagnosis_rankings for d in doctor_responses]
        metadata['diagnosis_confidence_history'] = get_diagnosis_confidence(diagnosis_history)

        # Store updated metadata
        profile['interaction_metadata'] = metadata

        # Store conversation histories
        doctor_histories[i] = doctor_history
        patient_histories[i] = patient_history
        filename = save.save_history(patient_profiles[pid], patient_histories[pid], doctor_histories[pid], filepath=fp)
        print(f'Conversation saved to {filename}')