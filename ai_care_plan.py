import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ai_generate_care_plan(patient_data, risk_result):
    """
    Calls Gemini to generate a personalized care plan.
    Returns the SAME structure your templates already expect.
    """
    prompt = f"""
You are a clinical assistant helping generate a post-discharge care plan.

Patient details:
- Age: {patient_data.get('Age')}
- Gender: {patient_data.get('Gender', '')}
- Diagnosis: {patient_data.get('Diagnosis', '')}
- Existing conditions: {patient_data.get('existing_diseases', [])}
- Current medications: {patient_data.get('current_medications', [])}
- Previous admissions: {patient_data.get('Previous_Admissions', 0)}
- Length of stay: {patient_data.get('Length_of_Stay', 0)} days
- Mobility status: {patient_data.get('mobility_status', '')}
- Family support: {patient_data.get('family_support', '')}
- Lives alone: {patient_data.get('lives_alone', '')}
- Readmission risk level: {risk_result.get('risk_level')}
- Risk score: {risk_result.get('risk_score')}%

Generate a care plan as STRICT JSON with exactly these keys, each a list of short,
clear instruction strings (3-6 items per key, no explanations, just the plan):

{{
  "follow_up": [],
  "medication": [],
  "monitoring": [],
  "dietary": [],
  "exercise": [],
  "lifestyle": [],
  "support": [],
  "emergency": []
}}

Only return the JSON object. No extra text.
"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            max_output_tokens=2048
        )
    )

    plan = json.loads(response.text)

    required_keys = ["follow_up", "medication", "monitoring", "dietary",
                      "exercise", "lifestyle", "support", "emergency"]
    for key in required_keys:
        if key not in plan or not isinstance(plan[key], list):
            plan[key] = []

    # Reject hollow/empty plans so the caller falls back to the rule-based plan
    total_items = sum(len(plan[key]) for key in required_keys)
    if total_items < len(required_keys):
        raise ValueError("AI returned an empty or incomplete care plan")

    return plan