prompt = """
You will be provided two items: a list of lists of symptoms and then a dictionary of symptoms in the format of {symptom term: colloquial description}.
The first item is a list of lists of symptoms, in which each sublist is from an interaction step containing the doctor's abbreviated notes, of which each may capture multiple symptoms.
The second item is a dictionary is a patient's description of their symptoms.
Please match the symptoms in the first list to the symptoms in the dictionary.
Use the following guidance when creating the structured response: 
1. match_details dictionary:
- {doctor_abbreviated_note: [(symptom term, colloquial description)]}
- Use the final list of symptoms to match the abbreviated notes, as that is the most recent interaction.
- Remember, one abbreviated note may contain multiple symptoms, so match_details value should be a list of matched symptoms.
2. found_symptom_history list:
- List of the number of symptoms found in each interaction step.
2. found_symptoms int:
- Number of symptoms matched in the final list of the doctor's abbreviated notes.
"""

reply = """
Please match the symptoms in the doctor's list to the symptoms in the patient's dictionary, provide the matched details, and the number of symptoms found.
Doctor's List of Lists of Symptoms: {recovered_symptoms_history}
Patient's Dictionary of Symptoms: {symptoms}
"""
