import json
import random
from datetime import datetime, timedelta

random.seed(11)

# ---- Load staff ----
with open('staff_db.json', 'r') as f:
    STAFF_DB = json.load(f)

doctors = [s for s in STAFF_DB if s['role'] == 'Doctor']
nurses = [s for s in STAFF_DB if s['role'] == 'Nurse']

if not doctors or not nurses:
    raise SystemExit("No doctors/nurses found in staff_db.json — check the file first.")

for i, nurse in enumerate(nurses):
    nurse['assigned_doctor'] = doctors[i % len(doctors)]['name']

with open('staff_db.json', 'w') as f:
    json.dump(STAFF_DB, f, indent=2)

print("Nurses assigned to doctors:")
for n in nurses:
    print(f"   {n['name']} -> {n['assigned_doctor']}")

# ---- Import the REAL care plan + risk logic from the live app ----
from app import generate_medical_care_plan, predict_readmission

MALE_NAMES = ["Sunil Perera", "Kasun Bandara", "Nimal Gunasekara", "Ruwan Fernando",
              "Chaminda Silva", "Anura Jayasuriya", "Priyantha Herath", "Tharindu Kumara",
              "Lakshman Wickramasinghe", "Ajith Rathnayake", "Buddhika Ranasinghe",
              "Sampath Wijesinghe", "Nuwan Karunaratne", "Roshan Weerasinghe", "Mahesh Dissanayake",
              "Dilshan Amarasekara", "Janaka Ekanayake", "Thusitha Gamage", "Gayan Wickramarachchi",
              "Sanjeewa Rajapaksa", "Chandana Abeysekara", "Upul Senanayake", "Indika Munasinghe",
              "Prasad Liyanage", "Ranga Kodikara"]
FEMALE_NAMES = ["Kamala Perera", "Nadeeka Bandara", "Sanduni Fernando", "Ishara Silva",
                "Chathurika Jayasuriya", "Malsha Herath", "Dilrukshi Kumara",
                "Nethmi Wickramasinghe", "Tharushi Rathnayake", "Geethani Amarasinghe",
                "Anoma Ranasinghe", "Sachini Wijesinghe", "Iresha Karunaratne", "Kumudu Weerasinghe",
                "Vidya Dissanayake", "Nirosha Amarasekara", "Rukmali Ekanayake", "Sujeewa Gamage",
                "Champika Wickramarachchi", "Yashoda Rajapaksa", "Sriyani Abeysekara",
                "Manel Senanayake", "Chithra Munasinghe", "Kanchana Liyanage", "Pushpa Kodikara"]

DIAGNOSES = ["Heart Disease", "Diabetes", "Pneumonia", "Hypertension", "COPD",
             "Stroke", "Kidney Disease", "Asthma"]

used_names = set()

def pick_name(gender):
    pool = MALE_NAMES if gender == 'Male' else FEMALE_NAMES
    available = [n for n in pool if n not in used_names]
    name = random.choice(available) if available else random.choice(pool)
    used_names.add(name)
    return name

def random_patient_base():
    gender = random.choice(['Male', 'Female'])
    name = pick_name(gender)
    existing = random.sample(DIAGNOSES, k=random.randint(0, 3))
    primary = random.choice(DIAGNOSES)
    return {
        "full_name": name,
        "age": random.randint(28, 82),
        "nic": f"{random.randint(700000000,999999999)}V",
        "gender": gender,
        "address": "Colombo, Sri Lanka",
        "phone": f"07{random.randint(10000000,99999999)}",
        "email": name.lower().replace(' ', '.') + "@email.com",
        "diagnosis": primary,
        "secondary_diagnosis": random.choice(DIAGNOSES + [""]),
        "existing_diseases": existing,
        "previous_admissions": random.randint(0, 5),
        "current_medications": random.sample(
            ["Metformin", "Aspirin", "Atorvastatin", "Lisinopril", "Furosemide", "Insulin", "Amlodipine"],
            k=random.randint(1, 4)
        ),
        "allergies": random.choice([[], ["Penicillin"], ["Sulfa drugs"]]),
        "length_of_stay": 0,
        "assigned_department": "General Medicine",
        "recovery_status": random.choice(["Good", "Fair", "Poor"]),
        "mobility_status": random.choice(["Independent", "Assisted", "Bedridden"]),
        "medication_compliance_risk": random.choice(["Low", "Medium", "High"]),
        "family_support": random.choice(["Strong", "Moderate", "Weak"]),
        "lives_alone": random.choice([True, False]),
        "transportation_access": random.choice([True, False]),
    }

with open('patients_db.json', 'r') as f:
    PATIENT_DB = json.load(f)
with open('history.json', 'r') as f:
    history = json.load(f)
with open('alerts.json', 'r') as f:
    alerts = json.load(f)

existing_ids = [int(k.replace('P', '')) for k in PATIENT_DB.keys()] if PATIENT_DB else []
next_id = (max(existing_ids) + 1) if existing_ids else 2000

def new_id():
    global next_id
    pid = f"P{next_id}"
    next_id += 1
    return pid

def build_assessed_patient(doctor_name, nurse_name, status, admission_days_ago, force_risk=None):
    p = random_patient_base()
    p['assigned_doctor'] = doctor_name
    admit_date = datetime.now() - timedelta(days=admission_days_ago)
    discharge_date = admit_date + timedelta(days=random.randint(3, 15))
    p['admission_date'] = admit_date.strftime('%Y-%m-%d')
    p['discharge_date'] = discharge_date.strftime('%Y-%m-%d')
    p['length_of_stay'] = (discharge_date - admit_date).days
    p['status'] = 'Discharged'

    patient_for_ai = {
        'Patient_ID': 'TEMP', 'Age': p['age'], 'Gender': p['gender'], 'Diagnosis': p['diagnosis'],
        'Previous_Admissions': p['previous_admissions'], 'Length_of_Stay': p['length_of_stay'],
        'Medications_Count': len(p['current_medications']),
        'Has_Diabetes': 1 if 'Diabetes' in p['existing_diseases'] else 0,
        'Has_Heart_Disease': 1 if 'Heart Disease' in p['existing_diseases'] else 0,
        'Has_Hypertension': 1 if 'Hypertension' in p['existing_diseases'] else 0,
        'Has_COPD': 1 if 'COPD' in p['existing_diseases'] else 0,
        'Recovery_Status': p['recovery_status'], 'Mobility_Status': p['mobility_status'],
        'Medication_Compliance_Risk': p['medication_compliance_risk'], 'Family_Support': p['family_support'],
        'Lives_Alone': 1 if p['lives_alone'] else 0,
        'Has_Transportation_Access': 1 if p['transportation_access'] else 0,
        'recovery_status': p['recovery_status'], 'family_support': p['family_support'],
        'mobility_status': p['mobility_status'], 'lives_alone': p['lives_alone'],
        'existing_diseases': p['existing_diseases'], 'current_medications': p['current_medications']
    }

    risk_result = predict_readmission(patient_for_ai)
    if force_risk:
        risk_result['risk_level'] = force_risk
        risk_result['risk_score'] = {'High Risk': 78.5, 'Medium Risk': 52.0, 'Low Risk': 20.0}[force_risk]

    care_plan = generate_medical_care_plan(patient_for_ai, risk_result)

    entry = {
        'patient_name': p['full_name'],
        'timestamp': (datetime.now() - timedelta(days=max(admission_days_ago - 1, 0))).strftime('%Y-%m-%d %H:%M:%S'),
        'risk_score': risk_result['risk_score'], 'risk_level': risk_result['risk_level'],
        'risk_factors': ', '.join(risk_result['risk_factors']),
        'care_plan_summary': ', '.join(care_plan['follow_up'][:2]),
        'doctor': doctor_name, 'assigned_by': nurse_name, 'status': status,
        'doctor_notes': '',
        'follow_up_days': 7 if risk_result['risk_level'] == 'High Risk' else 14 if risk_result['risk_level'] == 'Medium Risk' else 30,
        'medical_care_plan': care_plan
    }
    return p, entry

# 10 patient "recipes" per doctor = 50 total across 5 doctors
RECIPES = [
    {"kind": "admitted"},
    {"kind": "admitted"},
    {"kind": "assessed", "status": "Pending", "days": (5, 10), "risk": "High Risk", "alert": True},
    {"kind": "assessed", "status": "Pending", "days": (5, 10), "risk": "Medium Risk"},
    {"kind": "assessed", "status": "Pending", "days": (5, 10), "risk": "Low Risk"},
    {"kind": "assessed", "status": "Approved", "days": (10, 20), "risk": "High Risk", "sent": True},
    {"kind": "assessed", "status": "Approved", "days": (10, 20), "risk": "Medium Risk", "sent": True},
    {"kind": "assessed", "status": "Approved", "days": (10, 20), "risk": "Medium Risk", "sent": False},
    {"kind": "assessed", "status": "Approved", "days": (10, 25), "risk": "Low Risk", "sent": True},
    {"kind": "assessed", "status": "Rejected", "days": (8, 15), "risk": "Medium Risk"},
]

print("\nGenerating 10 demo patients for each doctor (50 total)...")

for doc in doctors:
    doctor_name = doc['name']
    nurse_name = next((n['name'] for n in nurses if n['assigned_doctor'] == doctor_name), "Unassigned Nurse")

    for recipe in RECIPES:
        pid = new_id()

        if recipe["kind"] == "admitted":
            p = random_patient_base()
            p['assigned_doctor'] = doctor_name
            p['admission_date'] = (datetime.now() - timedelta(days=random.randint(1, 4))).strftime('%Y-%m-%d')
            p['discharge_date'] = ""
            p['status'] = 'Admitted'
            PATIENT_DB[pid] = p
            continue

        days_ago = random.randint(*recipe["days"])
        p, entry = build_assessed_patient(doctor_name, nurse_name, recipe["status"], days_ago, force_risk=recipe.get("risk"))
        entry['patient_id'] = pid
        if "sent" in recipe:
            entry['email_sent'] = recipe["sent"]
            entry['sms_sent'] = recipe["sent"]
        PATIENT_DB[pid] = p
        history.append(entry)

        if recipe.get("alert"):
            alerts.append({
                'patient_id': pid, 'patient_name': p['full_name'], 'risk_score': entry['risk_score'],
                'timestamp': entry['timestamp'], 'assigned_doctor': doctor_name, 'status': 'unread',
                'message': f"HIGH RISK: {p['full_name']} ({entry['risk_score']}%)"
            })

    print(f"   {doctor_name} (nurse: {nurse_name}) -> 10 patients created")

with open('patients_db.json', 'w') as f:
    json.dump(PATIENT_DB, f, indent=2)
with open('history.json', 'w') as f:
    json.dump(history, f, indent=2)
with open('alerts.json', 'w') as f:
    json.dump(alerts, f, indent=2)

print(f"\nDone! Created {len(doctors) * 10} patients across {len(doctors)} doctors.")