import pandas as pd
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from difflib import get_close_matches

# Load Excel
disease_data = pd.read_csv("disease_data.csv")

# Normalize column names: strip spaces, lowercase
disease_data.columns = disease_data.columns.str.strip().str.lower()

# Print columns to check
print("Columns in Excel:", disease_data.columns.tolist())

# Normalize disease names for matching
disease_list = disease_data['disease_name'].str.lower().tolist()

def get_info(disease, column):
    disease_lower = disease.lower()
    
    # Exact match
    row = disease_data[disease_data['disease_name'].str.lower() == disease_lower]
    if not row.empty:
        return str(row.iloc[0][column])
    
    # Close match
    matches = get_close_matches(disease_lower, disease_list, n=1, cutoff=0.6)
    if matches:
        row = disease_data[disease_data['disease_name'].str.lower() == matches[0]]
        return str(row.iloc[0][column])
    
    return f"Sorry, I don't have information about '{disease}'."

class ActionProvideDiseaseInfo(Action):
    def name(self):
        return "action_provide_disease_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict):

        disease = tracker.get_slot("disease")
        intent = tracker.latest_message['intent'].get('name')

        if not disease:
            dispatcher.utter_message(text="Please tell me which disease you are asking about.")
            return []

        intent_to_column = {
            "ask_symptoms": "normal_symptoms",
            "ask_alert": "alerting_symptoms",
            "ask_treatment": "treatment",
            "ask_medicine": "medicine",
            "ask_home_remedy": "home_remedy",
            "ask_prevention": "prevention",
            "ask_duration": "duration",
            "ask_danger": "is_danger"
        }

        if intent in intent_to_column:
            column = intent_to_column[intent]
            info = get_info(disease, column)
            dispatcher.utter_message(text=f"{intent.replace('ask_', '').capitalize()} for {disease}: {info}")
        else:
            dispatcher.utter_message(text="I’m not sure how to answer that.")

        return []
