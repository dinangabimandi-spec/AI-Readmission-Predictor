import json
import random
from datetime import datetime, timedelta

# --- DOCTORS ---
DOCTORS = [
    {"id": "D001", "name": "Dr. Nirmal Perera", "specialization": "General Physician"},
    {"id": "D002", "name": "Dr. Tharindu Fernando", "specialization": "Cardiologist"},
    {"id": "D003", "name": "Dr. Sachini Wijesinghe", "specialization": "Endocrinologist"},
    {"id": "D004", "name": "Dr. Kasun Jayawardena", "specialization": "Pulmonologist"},
    {"id": "D005", "name": "Dr. Dinithi Silva", "specialization": "Geriatric Medicine"}
]

NURSES = [
    {"id": "N001", "name": "Nurse Malsha Fernando", "assigned_doctor": "Dr. Nirmal Perera"},
    {"id": "N002", "name": "Nurse Ishari Gunasekara", "assigned_doctor": "Dr. Tharindu Fernando"},
    {"id": "N003", "name": "Nurse Tharushi Jayasinghe", "assigned_doctor": "Dr. Sachini Wijesinghe"},
    {"id": "N004", "name": "Nurse Sanduni Perera", "assigned_doctor": "Dr. Kasun Jayawardena"},
    {"id": "N005", "name": "Nurse Nethmi Wickramasinghe", "assigned_doctor": "Dr. Dinithi Silva"}
]

RECEPTIONISTS = [
    {"id": "R001", "name": "Anjali Samarasinghe"},
    {"id": "R002", "name": "Kavinda Ranathunga"}
]

ADMIN = {"id": "A001", "name": "Admin"}

# --- Sri Lankan Names ---
FIRST_NAMES = [
    "Ranil", "Kamala", "Sunil", "Chandrika", "Nimal", "Deepani", "Gamini", "Samantha",
    "Lalitha", "Priyantha", "Kusum", "Bandula", "Anoma", "Chandrasiri", "Dammika",
    "Lakshmi", "Gamika", "Sujeewa", "Thilak", "Nilanthi", "Hema", "Siriwardena",
    "Anura", "Malkanthi", "Somasiri", "Geethani", "Herath", "Kanthi", "Piyal", "Ranjani",
    "Channa", "Daya", "Chandani", "Wimal", "Nadeeka", "Upul", "Iresha", "Gunasekera",
    "Janaka", "Premadasa", "Shirani", "Bandara", "Champa", "Karunaratne", "Indrani",
    "Siri", "Kumarasinghe", "Chithra", "Wijesinghe", "Kamal"
]

LAST_NAMES = [
    "Samarasinghe", "Perera", "Dissanayake", "De Silva", "Fernando", "Bandara",
    "Gunawardena", "Jayawardena", "Wijesinghe", "Kumara", "Herath", "Karunaratne",
    "Mendis", "Rathnayake", "Kariyawasam", "Abeywardena", "Gamage", "Senanayake",
    "Wickramasinghe", "Seneviratne", "Jayasuriya", "Weerasinghe", "Gunawardana",
    "Bandaranayake", "Kulasekara", "Amarasinghe", "Wijeratne", "Peiris", "Ranasinghe",
    "Premaratne", "Hettiarachchi", "Dias", "Siriwardena", "Mudalige", "Lokuhewa"
]

DIAGNOSES = [  # For history generation only, not for patient registration
    "Heart Disease", "Diabetes", "Pneumonia", "Asthma", "Hypertension", "COPD",
    "Stroke", "Kidney Disease", "Liver Disease", "Cancer", "Arthritis", "Depression"
]

EXISTING_DISEASES = [  # For history generation only
    "Diabetes", "Hypertension", "Heart Disease", "COPD", "Asthma", "Arthritis"
]

MEDICATIONS = [  # For history generation only
    "Aspirin", "Lisinopril", "Metformin", "Amoxicillin", "Ventolin", "Prednisone"
]

ALLERGIES = [  # For history generation only
    "Penicillin", "Sulfa", "Aspirin", "Ibuprofen", "Codeine"
]

def generate_nic():
    year = random.randint(1960, 2005)
    gender_digit = random.choice([1, 2])
    num = random.randint(1000, 9999)
    return f"{year}{gender_digit}{num:04d}"

def generate_phone():
    return f"0{random.randint(70, 78)}-{random.randint(1000000, 9999999)}"

def generate_email(first, last):
    return f"{first.lower()}.{last.lower()}@email.com"

def generate_risk_factors(patient):
    factors = []
    if patient['age'] > 65: factors.append("Advanced age (>65)")
    if 'Diabetes' in patient['existing_diseases']: factors.append("Diabetes")
    if 'Heart Disease' in patient['existing_diseases']: factors.append("Heart disease")
    if 'Hypertension' in patient['existing_diseases']: factors.append("Hypertension")
    if 'COPD' in patient['existing_diseases']: factors.append("COPD")
    if patient['previous_admissions'] >= 3: factors.append(f"Multiple admissions ({patient['previous_admissions']})")
    if patient['length_of_stay'] > 7: factors.append("Extended stay (>7 days)")
    if len(patient['current_medications']) > 5: factors.append("Multiple medications (>5)")
    if not factors: factors.append("No significant risk factors identified.")
    return ', '.join(factors)

def generate_patients(count=100):
    patients = {}
    doctor_names = [d['name'] for d in DOCTORS]
    today = datetime.now().date()
    
    for i in range(count):
        pid = f"P{2000 + i}"
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        age = random.randint(18, 90)
        gender = random.choice(["Male", "Female"])
        assigned_doctor = random.choice(doctor_names)
        
        for d in DOCTORS:
            if d['name'] == assigned_doctor:
                dept = d['specialization'].replace(" Specialist", "")
                break
        
        admission_date = today - timedelta(days=random.randint(1, 30))
        is_admitted = random.random() < 0.3
        
        if is_admitted:
            discharge_date = None
            length_of_stay = (today - admission_date).days
            status = "Admitted"
        else:
            stay_days = random.randint(1, 14)
            discharge_date = admission_date + timedelta(days=stay_days)
            if discharge_date > today:
                discharge_date = today - timedelta(days=random.randint(1, 3))
            length_of_stay = (discharge_date - admission_date).days
            if length_of_stay < 1:
                length_of_stay = 1
            status = "Discharged"
        
        # ✅ MEDICAL FIELDS ARE NOW EMPTY - Nurse will fill them during assessment
        patients[pid] = {
            "full_name": f"{first} {last}",
            "age": age,
            "nic": generate_nic(),
            "gender": gender,
            "address": f"{random.randint(1, 200)}, {random.choice(['Lake Road', 'Galle Road', 'Kandy Road', 'Main Street', 'Temple Road', 'Station Road'])}, {random.choice(['Colombo', 'Kandy', 'Galle', 'Negombo', 'Jaffna', 'Kurunegala', 'Ratnapura', 'Badulla', 'Matara', 'Anuradhapura'])}",
            "phone": generate_phone(),
            "email": generate_email(first, last),
            # --- MEDICAL INFO - EMPTY (Nurse fills later) ---
            "diagnosis": "",
            "secondary_diagnosis": "",
            "existing_diseases": [],
            "previous_admissions": random.randint(0, 7),
            "current_medications": [],
            "allergies": [],
            # --- Hospital Info ---
            "admission_date": admission_date.strftime('%Y-%m-%d'),
            "discharge_date": discharge_date.strftime('%Y-%m-%d') if discharge_date else "",
            "length_of_stay": length_of_stay,
            "assigned_doctor": assigned_doctor,
            "assigned_department": dept,
            "status": status,
            # --- Additional fields for assessment (will be set by nurse) ---
            "mobility_status": "",
            "family_support": "",
            "lives_alone": False,
            "recovery_status": ""
        }
    return patients

def generate_staff_db():
    staff = []
    for d in DOCTORS:
        staff.append({
            "id": d['id'],
            "name": d['name'],
            "role": "Doctor",
            "specialization": d['specialization'],
            "username": d['id'].lower(),
            "password": "doc123",
            "department": d['specialization'].replace(" Specialist", "")
        })
    for n in NURSES:
        staff.append({
            "id": n['id'],
            "name": n['name'],
            "role": "Nurse",
            "assigned_doctor": n['assigned_doctor'],
            "username": n['id'].lower(),
            "password": "nurse123"
        })
    for r in RECEPTIONISTS:
        staff.append({
            "id": r['id'],
            "name": r['name'],
            "role": "Receptionist",
            "username": r['id'].lower(),
            "password": "rec123"
        })
    staff.append({
        "id": "A001",
        "name": "Admin",
        "role": "Administrator",
        "username": "admin",
        "password": "admin123"
    })
    return staff

def generate_history(patients, count=50):
    history = []
    doctor_names = [d['name'] for d in DOCTORS]
    statuses = ['Approved', 'Pending', 'Rejected']
    today = datetime.now()
    
    for _ in range(count):
        pid = random.choice(list(patients.keys()))
        patient = patients[pid]
        
        # Skip if not discharged (no assessment yet)
        if patient.get('status') != 'Discharged':
            continue
        
        # Generate dummy medical data for history only (not for patient record)
        # This is for historical risk scores, not for current patient data
        base_score = 20
        if patient['age'] > 65: base_score += 15
        # Use random factors to simulate risk
        if random.random() < 0.3: base_score += 10
        if random.random() < 0.25: base_score += 10
        if random.random() < 0.35: base_score += 8
        if random.random() < 0.15: base_score += 8
        if patient['previous_admissions'] >= 3: base_score += 10
        if patient['length_of_stay'] > 7: base_score += 8
        
        risk_score = min(98, base_score + random.randint(-10, 15))
        if risk_score > 70: level = "High Risk"
        elif risk_score > 40: level = "Medium Risk"
        else: level = "Low Risk"
        
        # Generate some dummy risk factors for history
        risk_factors = []
        if patient['age'] > 65: risk_factors.append("Advanced age (>65)")
        if random.random() < 0.3: risk_factors.append("Diabetes")
        if random.random() < 0.25: risk_factors.append("Heart disease")
        if random.random() < 0.35: risk_factors.append("Hypertension")
        if random.random() < 0.15: risk_factors.append("COPD")
        if patient['previous_admissions'] >= 3: risk_factors.append(f"Multiple admissions ({patient['previous_admissions']})")
        if patient['length_of_stay'] > 7: risk_factors.append("Extended stay (>7 days)")
        if not risk_factors: risk_factors.append("No significant risk factors identified.")
        
        discharge_date = patient.get('discharge_date')
        if discharge_date:
            try:
                base_date = datetime.strptime(discharge_date, '%Y-%m-%d')
                if base_date > today:
                    base_date = today - timedelta(days=random.randint(1, 10))
            except:
                base_date = today - timedelta(days=random.randint(1, 10))
        else:
            base_date = today - timedelta(days=random.randint(1, 10))
        
        timestamp = base_date + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59))
        
        history.append({
            "patient_id": pid,
            "patient_name": patient['full_name'],
            "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "risk_score": risk_score,
            "risk_level": level,
            "risk_factors": ', '.join(risk_factors),
            "care_plan_summary": f"Follow-up within {7 if level == 'High Risk' else 14 if level == 'Medium Risk' else 30} days",
            "doctor": patient.get('assigned_doctor', random.choice(doctor_names)),
            "assigned_by": random.choice(["Nurse Malsha Fernando", "Nurse Ishari Gunasekara", "Nurse Tharushi Jayasinghe", "Nurse Sanduni Perera", "Nurse Nethmi Wickramasinghe"]),
            "status": random.choice(statuses),
            "doctor_notes": "",
            "follow_up_days": 7 if level == 'High Risk' else 14 if level == 'Medium Risk' else 30
        })
    
    history.sort(key=lambda x: x['timestamp'], reverse=True)
    return history

# --- RUN ---
print("🔄 Generating complete dataset with EMPTY medical fields...")

patients = generate_patients(100)
staff = generate_staff_db()
history = generate_history(patients, 50)

with open('patients_db.json', 'w') as f:
    json.dump(patients, f, indent=2)
print(f"✅ 100 patients saved (medical fields EMPTY)")

with open('staff_db.json', 'w') as f:
    json.dump(staff, f, indent=2)
print(f"✅ Staff saved")

with open('history.json', 'w') as f:
    json.dump(history, f, indent=2)
print(f"✅ 50 history entries saved")

with open('alerts.json', 'w') as f:
    json.dump([], f)
with open('activities.json', 'w') as f:
    json.dump([], f)
with open('follow_ups.json', 'w') as f:
    json.dump([], f)

print("\n📊 Summary:")
print(f"  - Patients: 100 (medical fields EMPTY)")
print(f"  - Doctors: 5")
print(f"  - Nurses: 5")
print(f"  - Receptionists: 2")
print(f"  - Admin: 1")
print("\n✅ Medical information will be entered by Nurses during assessment.")