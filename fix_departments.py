import json
import random

random.seed(3)

DEPARTMENTS = ["General Medicine", "Cardiology", "Endocrinology", "Nephrology", "Pulmonology"]

with open('patients_db.json', 'r') as f:
    PATIENT_DB = json.load(f)

for pid, data in PATIENT_DB.items():
    data['assigned_department'] = random.choice(DEPARTMENTS)

with open('patients_db.json', 'w') as f:
    json.dump(PATIENT_DB, f, indent=2)

print(f"Updated departments for {len(PATIENT_DB)} patients.")