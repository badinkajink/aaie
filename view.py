"""View conversation histories

Usage: streamlit run view.py
"""
import streamlit as st
import json
import pathlib
from typing import cast
import itertools
import schema

CONVERSATIONS_DIR: pathlib.Path = pathlib.Path(__file__).parent / 'conversations'

def load_conversation_list() -> list[str]:
    """Load available conversation filenames."""
    return sorted([file.name for file in CONVERSATIONS_DIR.iterdir() if file.suffix == '.json'])

def load_conversation(file_name: str) -> list[tuple[str | None, str | None]]:
    """Load a single conversation from JSON."""
    file: pathlib.Path = CONVERSATIONS_DIR / file_name
    with file.open('r', encoding='utf-8') as f:
        data = cast(schema.Conversation, json.load(f))

    patient_history = data['patient_history']
    doctor_history = data['doctor_history']

    doctor_messages: list[str] = []
    patient_messages: list[str] = []

    for h in doctor_history:
        if h['role'] != 'assistant':
            continue
        message = json.loads(h['content'])
        message = schema.DoctorResponse(**message)
        doctor_messages.append(message.response_to_patient)

    for h in patient_history:
        if h['role'] != 'assistant':
            continue
        patient_messages.append(h['content'])

    return list(itertools.zip_longest(doctor_messages, patient_messages, fillvalue=None))

# Streamlit UI
st.title('AI Conversation Viewer')

# Load conversation list
conversation_files: list[str] = load_conversation_list()

if conversation_files:
    # Searchable selection
    selected_file: str = st.selectbox('Select a conversation:', conversation_files)

    # Load selected conversation
    conversation_data = load_conversation(selected_file)

    # Display conversation in chat format
    st.subheader(f'Conversation: {selected_file}')

    chat_style = """
        <style>
            .chat-container {
                max-width: 700px;
                margin: auto;
            }
            .doctor, .patient {
                padding: 10px 15px;
                border-radius: 10px;
                margin: 5px 0;
                max-width: 75%;
            }
            .doctor {
                background-color: #DCF8C6;
                align-self: flex-start;
            }
            .patient {
                background-color: #EAEAEA;
                align-self: flex-end;
            }
            .message-box {
                display: flex;
                flex-direction: column;
            }
        </style>
    """
    st.markdown(chat_style, unsafe_allow_html=True)
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    for doctor_msg, patient_msg in conversation_data:
        if doctor_msg:
            st.markdown(f'<div class="message-box"><div class="doctor"><strong>Doctor:</strong> {doctor_msg}</div></div>', unsafe_allow_html=True)
        if patient_msg:
            st.markdown(f'<div class="message-box" style="align-items: flex-end;"><div class="patient"><strong>Patient:</strong> {patient_msg}</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning('No conversations found.')
