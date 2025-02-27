"""Test if the schema works with structured responses"""
import os
import openai
import schema
import doctor_prompt_structured as dp

client = openai.OpenAI(api_key=os.getenv("CORRELL_API_KEY"))

dc = {'gender': 'man', 'ethnicity': 'asian', 'confidence_threshold': 0.8, 'interaction_steps': 5}
p = dp.prompt.format(**dc)

messages = [{'role': 'system', 'content': p}]

client.beta.chat.completions.parse(
   model = 'gpt-4o-mini',
   messages=messages,
   temperature=0.7,
   response_format=schema.DoctorResponse)