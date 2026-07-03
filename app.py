from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, flash
import pandas as pd
import joblib
import os
import json
from datetime import datetime
import random
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

app = Flask(__name__)
app.secret_key = 'suwa-setha-hospital-secret-key-2026'

# --- 1. LOAD DATA ---
def load_patient_db():
    if os.path.exists('patients_db.json'):
        with open('patients_db.json', 'r') as f:
            return json.load(f)
    return {}

def load_staff_db():
    if os.path.exists('staff_db.json'):
        with open('staff_db.json', 'r') as f:
            return json.load(f)
    return {}

def load_history():
    if os.path.exists('history.json'):
        with open('history.json', 'r') as f:
            return json.load(f)
    return []

def load_alerts():
    if os.path.exists('alerts.json'):
        with open('alerts.json', 'r') as f:
            return json.load(f)
    return []

def load_activities():
    if os.path.exists('activities.json'):
        with open('activities.json', 'r') as f:
            return json.load(f)
    return []

def load_followups():
    if os.path.exists('follow_ups.json'):
        with open('follow_ups.json', 'r') as f:
            return json.load(f)
    return []

PATIENT_DB = load_patient_db()
STAFF_DB = load_staff_db()
history = load_history()
alerts = load_alerts()
activities = load_activities()
followups = load_followups()

# --- 2. SAVE HELPERS ---
def save_patients():
    with open('patients_db.json', 'w') as f:
        json.dump(PATIENT_DB, f, indent=2)

def save_staff():
    with open('staff_db.json', 'w') as f:
        json.dump(STAFF_DB, f, indent=2)

def save_history():
    with open('history.json', 'w') as f:
        json.dump(history, f, indent=2)

def save_alerts(data):
    with open('alerts.json', 'w') as f:
        json.dump(data, f, indent=2)

def save_activity(text):
    acts = load_activities()
    acts.append({"text": text, "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    if len(acts) > 100:
        acts = acts[-100:]
    with open('activities.json', 'w') as f:
        json.dump(acts, f, indent=2)

def save_followup(data):
    fups = load_followups()
    fups.append(data)
    with open('follow_ups.json', 'w') as f:
        json.dump(fups, f, indent=2)

# --- 3. LOAD AI MODEL ---
try:
    model_data = joblib.load('readmission_model.pkl')
    model = model_data['model']
    scaler = model_data['scaler']
    encoders = model_data['encoders']
    feature_columns = model_data['feature_columns']
    print("✅ AI Model loaded!")
except:
    print("⚠️ AI Model not found.")
    model = None
    scaler = None
    encoders = {}
    feature_columns = []

# --- 4. AI FUNCTIONS ---
def predict_readmission(patient_data):
    if model is None:
        return {'risk_score': 0, 'risk_level': 'Offline', 'risk_color': 'gray', 'risk_factors': [], 'priority': 'Unknown'}

    df = pd.DataFrame([patient_data])
    try:
        df['Diagnosis_Encoded'] = encoders['Diagnosis'].transform(df['Diagnosis'])
        df['Gender_Encoded'] = encoders['Gender'].transform(df['Gender'])
    except:
        df['Diagnosis_Encoded'] = 0
        df['Gender_Encoded'] = 0

    X = df[feature_columns]
    X_scaled = scaler.transform(X)
    probability = model.predict_proba(X_scaled)[0][1]
    risk_score = round(probability * 100, 1)

    if risk_score > 70:
        risk_level, risk_color, priority = 'High Risk', '#EF4444', "Critical"
    elif risk_score > 40:
        risk_level, risk_color, priority = 'Medium Risk', '#F59E0B', "Medium"
    else:
        risk_level, risk_color, priority = 'Low Risk', '#10B981', "Low"

    risk_factors = []
    if patient_data.get('Age', 0) > 65:
        risk_factors.append("Advanced age (>65)")
    if patient_data.get('Has_Diabetes', 0) == 1:
        risk_factors.append("Diabetes")
    if patient_data.get('Has_Heart_Disease', 0) == 1:
        risk_factors.append("Heart disease")
    if patient_data.get('Has_Hypertension', 0) == 1:
        risk_factors.append("Hypertension")
    if patient_data.get('Has_COPD', 0) == 1:
        risk_factors.append("COPD")
    if patient_data.get('Previous_Admissions', 0) >= 3:
        risk_factors.append(f"Multiple admissions ({patient_data['Previous_Admissions']})")
    if patient_data.get('Length_of_Stay', 0) > 7:
        risk_factors.append("Extended stay (>7 days)")
    if patient_data.get('Medications_Count', 0) > 5:
        risk_factors.append("Multiple medications (>5)")
    if patient_data.get('recovery_status') == 'Poor':
        risk_factors.append("Poor recovery status")
    if patient_data.get('family_support') == 'Weak':
        risk_factors.append("Weak family support")
    if not risk_factors:
        risk_factors = ["No significant risk factors identified."]

    return {'risk_score': risk_score, 'risk_level': risk_level, 'risk_color': risk_color, 'risk_factors': risk_factors, 'priority': priority}

# --- 4b. ENHANCED MEDICAL CARE PLAN GENERATOR ---
def generate_medical_care_plan(patient_data, risk_result):
    """
    Generates a comprehensive medical care plan with 7 sections.
    """
    plan = {
        'follow_up': [],
        'medication': [],
        'monitoring': [],
        'dietary': [],
        'exercise': [],
        'lifestyle': [],
        'emergency': []
    }

    # 1. FOLLOW-UP SCHEDULE (Based on risk level)
    if risk_result['risk_level'] == 'High Risk':
        plan['follow_up'] = [
            "Schedule a follow-up appointment within 7 days",
            "Phone check-in within 24 hours by the nursing team",
            "Home health nurse visit within 48 hours",
            "Arrange cardiology/endocrinology review if applicable"
        ]
    elif risk_result['risk_level'] == 'Medium Risk':
        plan['follow_up'] = [
            "Schedule a follow-up appointment within 14 days",
            "Phone check-in within 72 hours",
            "Monitor symptoms and report any changes"
        ]
    else:
        plan['follow_up'] = [
            "Schedule a routine follow-up appointment within 30 days",
            "Regular monitoring as per standard protocol"
        ]

    # 2. MEDICATION PLAN (From patient's current medications)
    meds = patient_data.get('current_medications', [])
    if meds:
        plan['medication'] = ["Continue prescribed medications:"]
        for med in meds[:5]:
            plan['medication'].append(f"• {med} — as per prescription")
        plan['medication'].append("Do not skip doses. Set daily reminders.")
        plan['medication'].append("Do not stop or change medications without consulting the doctor.")
    else:
        plan['medication'] = [
            "Follow the medication schedule provided in your discharge summary.",
            "Take all medications as prescribed by your doctor."
        ]
    plan['medication'].append("Bring all medications to your follow-up appointment.")

    # 3. MONITORING INSTRUCTIONS (Based on existing diseases)
    existing = patient_data.get('existing_diseases', [])
    monitoring = []

    if 'Diabetes' in existing:
        monitoring.append("Diabetes Monitoring: Check blood glucose levels twice daily (morning and evening). Maintain a log.")
    if 'Hypertension' in existing:
        monitoring.append("Blood Pressure: Monitor blood pressure daily. Record readings in a diary.")
    if 'Heart Disease' in existing:
        monitoring.append("Cardiac Monitoring: Monitor for chest pain, shortness of breath, or palpitations. Keep a symptom diary.")
    if 'COPD' in existing:
        monitoring.append("Respiratory Monitoring: Monitor oxygen saturation using a pulse oximeter twice daily.")

    if not monitoring:
        monitoring = ["General Monitoring: Monitor general health and report any unusual symptoms immediately."]

    monitoring.append("Temperature monitoring twice daily — report fever above 38°C.")
    monitoring.append("Weight monitoring daily — report sudden weight gain or loss.")
    monitoring.append("Maintain a symptom diary to track any changes.")
    plan['monitoring'] = monitoring

    # 4. DIETARY ADVICE (Based on conditions)
    dietary = [
        "Heart Health: Reduce salt and saturated fat intake.",
        "Eat balanced meals with fruits, vegetables, and whole grains.",
        "Choose lean proteins (fish, chicken, legumes).",
        "Limit sugar, processed foods, and unhealthy fats.",
        "Drink at least 8 glasses (2 liters) of water daily."
    ]
    if 'Diabetes' in existing:
        dietary.append("Diabetes Management: Follow diabetic meal plan — monitor carbohydrate intake.")
        dietary.append("Avoid sugary drinks and high-GI foods.")
    if 'Heart Disease' in existing:
        dietary.append("Avoid saturated fats and trans fats.")
    plan['dietary'] = dietary

    # 5. PHYSICAL ACTIVITY (Based on mobility status)
    mobility = patient_data.get('mobility_status', '')
    exercise = [
        "Light physical activity for 30 minutes daily (e.g., walking, light stretching).",
        "Start slowly and gradually increase activity levels."
    ]
    if mobility == 'Bedridden':
        exercise = [
            "Bed-based exercises as advised by the physiotherapist.",
            "Change position every 2 hours to prevent bedsores.",
            "Passive range of motion exercises for joints."
        ]
    elif mobility == 'Assisted':
        exercise.append("Walk with assistance or walking aids.")
        exercise.append("Physiotherapy sessions as scheduled.")
    else:
        exercise.append("Independent mobility — maintain regular walking routine.")
    exercise.append("Avoid strenuous activity until cleared by the doctor.")
    plan['exercise'] = exercise

    # 6. LIFESTYLE & SUPPORT
    lifestyle = [
        "Sleep: Get 7-8 hours of quality sleep nightly.",
        "Alcohol: Avoid alcohol consumption completely.",
        "Smoking: Quit smoking immediately — seek support if needed.",
        "Stress: Practice stress management (deep breathing, meditation)."
    ]

    support = [
        "Support: Ensure family or caregiver availability for daily assistance.",
        "Keep a health diary to track symptoms, medications, and appointments.",
        "Keep emergency contacts readily accessible."
    ]

    if patient_data.get('family_support') == 'Weak':
        support.append("Community Support: Arrange community support services or home care aid.")
    if patient_data.get('lives_alone') == 'Yes':
        support.append("Lives Alone: Set up daily check-in calls with family or healthcare provider.")

    plan['lifestyle'] = lifestyle
    plan['support'] = support

    # 7. EMERGENCY ADVICE (Based on risk level)
    if risk_result['risk_level'] == 'High Risk':
        plan['emergency'] = [
            "URGENT: Visit the nearest hospital immediately if you experience:",
            "• Chest pain or severe shortness of breath",
            "• Severe dizziness or fainting",
            "• Difficulty speaking or weakness on one side of the body",
            "• Uncontrolled bleeding or severe pain",
            "Emergency Contact: Call Suwa Setha Hospital Hotline at +94 11 234 5678 (24/7)"
        ]
    else:
        plan['emergency'] = [
            "Contact your general practitioner if you experience any unusual symptoms.",
            "Visit the nearest clinic if symptoms worsen.",
            "Emergency Contact: Suwa Setha Hospital Hotline: +94 11 234 5678"
        ]

    return plan

# --- 5. AUTHENTICATION ---
def get_user_by_username(username):
    for s in STAFF_DB:
        if s.get('username') == username:
            return s
    return None

def check_role_access(required_roles):
    if 'user' not in session:
        return False
    user = session['user']
    return user.get('role') in required_roles

# --- 6. ROUTES ---

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = get_user_by_username(username)
        if user and user.get('password') == password:
            session['user'] = user
            session['username'] = username
            save_activity(f"🔐 {user['name']} ({user['role']}) logged in")
            flash(f'✅ Welcome, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user' in session:
        save_activity(f"👋 {session['user']['name']} logged out")
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    role = user['role']

    total_patients = len(PATIENT_DB)
    high_risk = sum(1 for h in history if h.get('risk_level') == 'High Risk')
    medium_risk = sum(1 for h in history if h.get('risk_level') == 'Medium Risk')
    low_risk = sum(1 for h in history if h.get('risk_level') == 'Low Risk')

    recent_activities = activities[-20:][::-1] if activities else []
    current_alerts = load_alerts()

    if role == 'Administrator':
        return render_template('dashboard.html',
            user=user, total_patients=total_patients, high_risk=high_risk,
            medium_risk=medium_risk, low_risk=low_risk,
            activities=recent_activities, alerts=current_alerts,
            staff=STAFF_DB, now=datetime.now())

    elif role == 'Receptionist':
        patients_list = []
        for pid, data in PATIENT_DB.items():
            patients_list.append({
                'id': pid, 'name': data['full_name'], 'doctor': data.get('assigned_doctor', 'Unassigned'),
                'admission_date': data.get('admission_date', ''), 'discharge_date': data.get('discharge_date', ''),
                'status': data.get('status', 'Admitted')
            })
        return render_template('receptionist_dashboard.html', user=user, patients=patients_list, now=datetime.now())

    elif role == 'Doctor':
        doctor_name = user['name']
        patients_list = []
        for pid, data in PATIENT_DB.items():
            if data.get('assigned_doctor') == doctor_name:
                latest = None
                for h in history:
                    if h['patient_id'] == pid:
                        latest = h
                        break

                status = latest.get('status', 'Not Assessed') if latest else 'Not Assessed'

                if status == 'Draft':
                    continue

                patients_list.append({
                    'id': pid,
                    'name': data['full_name'],
                    'risk_score': latest.get('risk_score', 0) if latest else 0,
                    'risk_level': latest.get('risk_level', 'Not Assessed') if latest else 'Not Assessed',
                    'status': status,
                    'assigned_by': latest.get('assigned_by', '') if latest else ''
                })

        risk_order = {'High Risk': 0, 'Medium Risk': 1, 'Low Risk': 2, 'Not Assessed': 3}
        patients_list.sort(key=lambda x: risk_order.get(x['risk_level'], 4))

        return render_template('doctor_dashboard.html',
            user=user,
            patients=patients_list,
            now=datetime.now())

    elif role == 'Nurse':
        assigned_doctor = user.get('assigned_doctor', '')
        patients_list = []

        for pid, data in PATIENT_DB.items():
            if data.get('assigned_doctor') == assigned_doctor:
                latest = None
                for h in history:
                    if h['patient_id'] == pid:
                        latest = h
                        break

                if latest:
                    status = latest.get('status', 'Pending')
                    if status == 'Draft':
                        status = 'Not Assessed'
                else:
                    status = 'Not Assessed'

                risk_score = latest.get('risk_score', 0) if latest else 0
                risk_level = latest.get('risk_level', 'Not Assessed') if latest else 'Not Assessed'

                patients_list.append({
                    'id': pid,
                    'name': data['full_name'],
                    'risk_score': risk_score,
                    'risk_level': risk_level,
                    'status': status,
                    'assigned_by': latest.get('assigned_by', '') if latest else '',
                    'email_sent': latest.get('email_sent', False) if latest else False,
                    'sms_sent': latest.get('sms_sent', False) if latest else False
                })

        # ===== NEW: Calculate notification count (only unsent approved plans) =====
        notification_count = sum(
            1 for p in patients_list 
            if p['status'] == 'Approved' and not p['email_sent'] and not p['sms_sent']
        )

        risk_order = {'High Risk': 0, 'Medium Risk': 1, 'Low Risk': 2, 'Not Assessed': 3}
        patients_list.sort(key=lambda x: risk_order.get(x['risk_level'], 4))

        return render_template('nurse_dashboard.html',
            user=user,
            patients=patients_list,
            assigned_doctor=assigned_doctor,
            now=datetime.now(),
            notification_count=notification_count)  # <-- Pass to template

# --- 7. PATIENT MANAGEMENT (Receptionist/Admin) ---
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    if user['role'] not in ['Receptionist', 'Administrator']:
        flash('⛔ Access denied.', 'danger')
        return redirect(url_for('dashboard'))

    doctors = [s for s in STAFF_DB if s['role'] == 'Doctor']

    if request.method == 'POST':
        nic = request.form.get('nic')
        existing_patient = None
        for pid, data in PATIENT_DB.items():
            if data.get('nic') == nic:
                existing_patient = {'id': pid, **data}
                break

        if existing_patient:
            flash('✅ Patient found! Auto-filled.', 'info')
            return render_template('add_patient.html', user=user, doctors=doctors, patient=existing_patient, is_existing=True)

        existing_ids = list(PATIENT_DB.keys())
        if existing_ids:
            last_id = max([int(id.replace('P', '')) for id in existing_ids])
            new_id = f"P{last_id + 1}"
        else:
            new_id = "P2000"

        new_patient = {
            "full_name": request.form.get('full_name'),
            "age": int(request.form.get('age', 0)),
            "nic": nic,
            "gender": request.form.get('gender'),
            "address": request.form.get('address'),
            "phone": request.form.get('phone'),
            "email": request.form.get('email', ''),
            "diagnosis": request.form.get('diagnosis', ''),
            "secondary_diagnosis": request.form.get('secondary_diagnosis', ''),
            "existing_diseases": [d.strip() for d in request.form.get('existing_diseases', '').split(',') if d.strip()],
            "previous_admissions": int(request.form.get('previous_admissions', 0)),
            "current_medications": [m.strip() for m in request.form.get('current_medications', '').split(',') if m.strip()],
            "allergies": [a.strip() for a in request.form.get('allergies', '').split(',') if a.strip()],
            "admission_date": datetime.now().strftime('%Y-%m-%d'),
            "discharge_date": "",
            "length_of_stay": 0,
            "assigned_doctor": request.form.get('assigned_doctor'),
            "assigned_department": request.form.get('assigned_department'),
            "status": "Admitted"
        }

        PATIENT_DB[new_id] = new_patient
        save_patients()
        save_activity(f"🆕 New patient {new_patient['full_name']} (ID: {new_id}) registered by {user['name']}")
        flash(f'✅ Patient {new_patient["full_name"]} (ID: {new_id}) added!', 'success')
        return redirect(url_for('profile', patient_id=new_id))

    return render_template('add_patient.html', user=user, doctors=doctors, patient=None, is_existing=False)

# --- 8. ADMIN STAFF MANAGEMENT ---
@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['user']['role'] != 'Administrator':
        flash('⛔ Access denied.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        existing_ids = [s['id'] for s in STAFF_DB if s['id'].startswith('D')]
        if existing_ids:
            nums = [int(id.replace('D', '')) for id in existing_ids]
            new_id = f"D{max(nums) + 1:03d}"
        else:
            new_id = "D006"

        new_doctor = {
            'id': new_id,
            'name': request.form.get('name'),
            'role': 'Doctor',
            'specialization': request.form.get('specialization'),
            'username': request.form.get('username'),
            'password': request.form.get('password'),
            'department': request.form.get('department')
        }
        STAFF_DB.append(new_doctor)
        save_staff()
        save_activity(f"👨‍⚕️ New doctor {new_doctor['name']} added by {session['user']['name']}")
        flash(f'✅ Doctor {new_doctor["name"]} added!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_doctor.html', user=session['user'])

@app.route('/add_nurse', methods=['GET', 'POST'])
def add_nurse():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['user']['role'] != 'Administrator':
        flash('⛔ Access denied.', 'danger')
        return redirect(url_for('dashboard'))

    doctors = [s for s in STAFF_DB if s['role'] == 'Doctor']

    if request.method == 'POST':
        existing_ids = [s['id'] for s in STAFF_DB if s['id'].startswith('N')]
        if existing_ids:
            nums = [int(id.replace('N', '')) for id in existing_ids]
            new_id = f"N{max(nums) + 1:03d}"
        else:
            new_id = "N006"

        new_nurse = {
            'id': new_id,
            'name': request.form.get('name'),
            'role': 'Nurse',
            'assigned_doctor': request.form.get('assigned_doctor'),
            'username': request.form.get('username'),
            'password': request.form.get('password')
        }
        STAFF_DB.append(new_nurse)
        save_staff()
        save_activity(f"👩‍⚕️ New nurse {new_nurse['name']} added by {session['user']['name']}")
        flash(f'✅ Nurse {new_nurse["name"]} added!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_nurse.html', user=session['user'], doctors=doctors)

@app.route('/assign_nurse', methods=['GET', 'POST'])
def assign_nurse():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['user']['role'] != 'Administrator':
        flash('⛔ Access denied.', 'danger')
        return redirect(url_for('dashboard'))

    nurses = [s for s in STAFF_DB if s['role'] == 'Nurse']
    doctors = [s for s in STAFF_DB if s['role'] == 'Doctor']

    if request.method == 'POST':
        nurse_id = request.form.get('nurse_id')
        doctor_name = request.form.get('doctor_name')

        for s in STAFF_DB:
            if s['role'] == 'Nurse' and s['assigned_doctor'] == doctor_name and s['id'] != nurse_id:
                s['assigned_doctor'] = None
            if s['id'] == nurse_id:
                s['assigned_doctor'] = doctor_name

        save_staff()
        nurse_name = next((s['name'] for s in STAFF_DB if s['id'] == nurse_id), 'Unknown')
        save_activity(f"🔄 {nurse_name} assigned to {doctor_name} by {session['user']['name']}")
        flash(f'✅ Nurse assigned to {doctor_name}!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('assign_nurse.html', user=session['user'], nurses=nurses, doctors=doctors)

@app.route('/edit_staff/<staff_id>', methods=['GET', 'POST'])
def edit_staff(staff_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['user']['role'] != 'Administrator':
        flash('⛔ Access denied.', 'danger')
        return redirect(url_for('dashboard'))

    staff_member = next((s for s in STAFF_DB if s['id'] == staff_id), None)
    if not staff_member:
        flash('❌ Staff member not found.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        staff_member['name'] = request.form.get('name')
        staff_member['username'] = request.form.get('username')
        if request.form.get('password'):
            staff_member['password'] = request.form.get('password')

        if staff_member['role'] == 'Doctor':
            staff_member['specialization'] = request.form.get('specialization')
            staff_member['department'] = request.form.get('department')

        save_staff()
        save_activity(f"✏️ {staff_member['name']}'s details updated by {session['user']['name']}")
        flash(f'✅ Staff updated!', 'success')
        return redirect(url_for('dashboard'))

    doctors = [s for s in STAFF_DB if s['role'] == 'Doctor'] if staff_member['role'] == 'Nurse' else []
    return render_template('edit_staff.html', user=session['user'], staff=staff_member, doctors=doctors)

# --- 9. SEARCH ---
@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']

    results = {'patients': [], 'doctors': [], 'nurses': []}
    query = ''

    if request.method == 'POST':
        query = request.form.get('search_query', '').strip().lower()

        for pid, data in PATIENT_DB.items():
            if query in pid.lower() or query in data.get('full_name', '').lower():
                results['patients'].append({'id': pid, **data})

        for s in STAFF_DB:
            if query in s.get('name', '').lower() or query in s.get('id', '').lower():
                if s['role'] == 'Doctor':
                    results['doctors'].append(s)
                elif s['role'] == 'Nurse':
                    results['nurses'].append(s)

        if not any(results.values()):
            flash('❌ No results found.', 'danger')

    return render_template('search.html', results=results, query=query, user=user)

# --- 10. PROFILE ---
@app.route('/profile/<patient_id>')
def profile(patient_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    data = PATIENT_DB.get(patient_id)
    if not data:
        return "Patient not found", 404

    latest = None
    for h in history:
        if h['patient_id'] == patient_id:
            latest = h
            break

    if latest:
        risk = {
            'risk_score': latest.get('risk_score', 0),
            'risk_level': latest.get('risk_level', 'Not Assessed'),
            'risk_color': '#EF4444' if latest.get('risk_level') == 'High Risk' else '#F59E0B' if latest.get('risk_level') == 'Medium Risk' else '#10B981',
            'risk_factors': latest.get('risk_factors', '').split(', ') if latest.get('risk_factors') else ['No risk factors'],
            'priority': 'Critical' if latest.get('risk_level') == 'High Risk' else 'Medium' if latest.get('risk_level') == 'Medium Risk' else 'Low',
            'status': latest.get('status', 'Draft')
        }
    else:
        risk = {
            'risk_score': 0,
            'risk_level': 'Not Assessed',
            'risk_color': 'gray',
            'risk_factors': ['No assessment yet'],
            'priority': 'Unknown',
            'status': 'Not Assessed'
        }

    return render_template('profile.html', patient={'id': patient_id, **data}, risk=risk, user=user)

# --- 11. ASSESSMENT (Nurse) ---
@app.route('/assess/<patient_id>', methods=['GET', 'POST'])
def assess(patient_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    if user['role'] != 'Nurse':
        flash('⛔ Only nurses can perform assessments.', 'danger')
        return redirect(url_for('dashboard'))

    data = PATIENT_DB.get(patient_id)
    if not data:
        return "Patient not found", 404

    if data.get('admission_date'):
        try:
            admit = datetime.strptime(data['admission_date'], '%Y-%m-%d')
            discharge = datetime.now()
            length = (discharge - admit).days
            if length > 0:
                data['length_of_stay'] = length
                data['discharge_date'] = datetime.now().strftime('%Y-%m-%d')
                data['status'] = 'Discharged'
                save_patients()
        except:
            pass

    if request.method == 'POST':
        # 1. SAVE MEDICAL INFO TO PATIENT RECORD
        data['diagnosis'] = request.form.get('diagnosis', '')
        data['secondary_diagnosis'] = request.form.get('secondary_diagnosis', '')
        data['existing_diseases'] = [d.strip() for d in request.form.get('existing_diseases', '').split(',') if d.strip()]
        data['current_medications'] = [m.strip() for m in request.form.get('current_medications', '').split(',') if m.strip()]
        data['allergies'] = [a.strip() for a in request.form.get('allergies', '').split(',') if a.strip()]
        data['previous_admissions'] = int(request.form.get('previous_admissions', 0))
        save_patients()

        # 2. Assessment data
        assessment_data = {
            'recovery_status': request.form.get('recovery_status'),
            'mobility_status': request.form.get('mobility_status'),
            'medication_compliance_risk': request.form.get('medication_compliance_risk'),
            'family_support': request.form.get('family_support'),
            'lives_alone': request.form.get('lives_alone') == 'Yes',
            'transportation_access': request.form.get('transportation_access') == 'Yes',
            'additional_notes': request.form.get('additional_notes', '')
        }

        data['mobility_status'] = assessment_data['mobility_status']
        data['family_support'] = assessment_data['family_support']
        data['lives_alone'] = assessment_data['lives_alone']
        data['recovery_status'] = assessment_data['recovery_status']
        save_patients()

        # 3. AI Prediction
        patient_for_ai = {
            'Patient_ID': patient_id,
            'Age': data['age'],
            'Gender': data['gender'],
            'Diagnosis': data.get('diagnosis', ''),
            'Previous_Admissions': data.get('previous_admissions', 0),
            'Length_of_Stay': data.get('length_of_stay', 0),
            'Medications_Count': len(data.get('current_medications', [])),
            'Has_Diabetes': 1 if 'Diabetes' in data.get('existing_diseases', []) else 0,
            'Has_Heart_Disease': 1 if 'Heart Disease' in data.get('existing_diseases', []) else 0,
            'Has_Hypertension': 1 if 'Hypertension' in data.get('existing_diseases', []) else 0,
            'Has_COPD': 1 if 'COPD' in data.get('existing_diseases', []) else 0,
            'recovery_status': assessment_data['recovery_status'],
            'family_support': assessment_data['family_support'],
            'mobility_status': assessment_data['mobility_status'],
            'lives_alone': assessment_data['lives_alone'],
            'existing_diseases': data.get('existing_diseases', [])
        }

        risk_result = predict_readmission(patient_for_ai)
        care_plan = generate_medical_care_plan(patient_for_ai, risk_result)

        # 4. Save to History
        existing = next((h for h in history if h['patient_id'] == patient_id and h['status'] in ['Draft', 'Pending']), None)

        if existing:
            existing['risk_score'] = risk_result['risk_score']
            existing['risk_level'] = risk_result['risk_level']
            existing['risk_factors'] = ', '.join(risk_result['risk_factors'])
            existing['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            existing['assigned_by'] = user['name']
            existing['status'] = 'Pending'
            existing['care_plan_summary'] = ', '.join(care_plan['follow_up'][:2])
            existing['medical_care_plan'] = care_plan
        else:
            history_entry = {
                'patient_id': patient_id,
                'patient_name': data['full_name'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'risk_score': risk_result['risk_score'],
                'risk_level': risk_result['risk_level'],
                'risk_factors': ', '.join(risk_result['risk_factors']),
                'care_plan_summary': ', '.join(care_plan['follow_up'][:2]),
                'doctor': data.get('assigned_doctor', 'Unassigned'),
                'assigned_by': user['name'],
                'status': 'Pending',
                'doctor_notes': '',
                'follow_up_days': 7 if risk_result['risk_level'] == 'High Risk' else 14 if risk_result['risk_level'] == 'Medium Risk' else 30,
                'medical_care_plan': care_plan
            }
            history.append(history_entry)

        save_history()

        # 5. Create Alert if High Risk
        if risk_result['risk_level'] == 'High Risk':
            current_alerts = load_alerts()
            current_alerts.append({
                'patient_id': patient_id,
                'patient_name': data['full_name'],
                'risk_score': risk_result['risk_score'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'assigned_doctor': data.get('assigned_doctor', 'Unassigned'),
                'status': 'unread',
                'message': f"🚨 HIGH RISK: {data['full_name']} ({risk_result['risk_score']}%)"
            })
            save_alerts(current_alerts)
            save_activity(f"🚨 High-risk alert for {data['full_name']} sent to {data.get('assigned_doctor', 'doctor')}")

        save_activity(f"🤖 Assessment completed for {data['full_name']} by {user['name']}. Risk: {risk_result['risk_level']} ({risk_result['risk_score']}%)")
        flash(f'✅ Assessment sent to {data.get("assigned_doctor", "doctor")} for approval.', 'success')
        return redirect(url_for('care_plan', patient_id=patient_id))

    existing = next((h for h in history if h['patient_id'] == patient_id), None)
    return render_template('assess.html', patient={'id': patient_id, **data}, user=user, existing=existing)

# --- 12. CARE PLAN (Enhanced Medical Document) ---
@app.route('/care_plan/<patient_id>')
def care_plan(patient_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    data = PATIENT_DB.get(patient_id)
    if not data:
        return "Patient not found", 404

    latest = None
    for h in history:
        if h['patient_id'] == patient_id:
            latest = h
            break

    if not latest:
        flash('❌ No assessment found for this patient.', 'danger')
        return redirect(url_for('profile', patient_id=patient_id))

    risk_result = {
        'risk_score': latest.get('risk_score', 0),
        'risk_level': latest.get('risk_level', 'Not Assessed'),
        'risk_color': '#EF4444' if latest.get('risk_level') == 'High Risk' else '#F59E0B' if latest.get('risk_level') == 'Medium Risk' else '#10B981',
        'risk_factors': latest.get('risk_factors', '').split(', ') if latest.get('risk_factors') else ['No risk factors'],
        'priority': 'Critical' if latest.get('risk_level') == 'High Risk' else 'Medium' if latest.get('risk_level') == 'Medium Risk' else 'Low',
        'status': latest.get('status', 'Draft'),
        'doctor_notes': latest.get('doctor_notes', ''),
        'follow_up_days': latest.get('follow_up_days', 7)
    }

    care_plan_data = latest.get('medical_care_plan', None)
    if not care_plan_data:
        patient_for_ai = {
            'Patient_ID': patient_id,
            'Age': data['age'],
            'Gender': data['gender'],
            'Diagnosis': data.get('diagnosis', ''),
            'Previous_Admissions': data.get('previous_admissions', 0),
            'Length_of_Stay': data.get('length_of_stay', 0),
            'Medications_Count': len(data.get('current_medications', [])),
            'Has_Diabetes': 1 if 'Diabetes' in data.get('existing_diseases', []) else 0,
            'Has_Heart_Disease': 1 if 'Heart Disease' in data.get('existing_diseases', []) else 0,
            'Has_Hypertension': 1 if 'Hypertension' in data.get('existing_diseases', []) else 0,
            'Has_COPD': 1 if 'COPD' in data.get('existing_diseases', []) else 0,
            'existing_diseases': data.get('existing_diseases', []),
            'current_medications': data.get('current_medications', []),
            'mobility_status': data.get('mobility_status', ''),
            'family_support': data.get('family_support', ''),
            'lives_alone': data.get('lives_alone', '')
        }
        care_plan_data = generate_medical_care_plan(patient_for_ai, risk_result)

    patient_data = {
        'id': patient_id,
        'full_name': data.get('full_name', ''),
        'age': data.get('age', ''),
        'gender': data.get('gender', ''),
        'diagnosis': data.get('diagnosis', ''),
        'secondary_diagnosis': data.get('secondary_diagnosis', ''),
        'existing_diseases': data.get('existing_diseases', []),
        'current_medications': data.get('current_medications', []),
        'admission_date': data.get('admission_date', ''),
        'discharge_date': data.get('discharge_date', ''),
        'assigned_doctor': data.get('assigned_doctor', ''),
        'assigned_department': data.get('assigned_department', ''),
        'mobility_status': data.get('mobility_status', ''),
        'family_support': data.get('family_support', ''),
        'lives_alone': data.get('lives_alone', ''),
        'email': data.get('email', ''),
        'phone': data.get('phone', '')
    }

    return render_template('care_plan.html',
        patient=patient_data,
        risk=risk_result,
        care_plan=care_plan_data,
        history_entry=latest,
        user=user,
        now=datetime.now())

# --- 13. REVIEW PLAN (Doctor) ---
@app.route('/review_plan/<patient_id>', methods=['POST'])
def review_plan(patient_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    if user['role'] not in ['Doctor', 'Administrator']:
        flash('⛔ Only doctors can review plans.', 'danger')
        return redirect(url_for('dashboard'))

    entries = [h for h in history if h['patient_id'] == patient_id]
    if not entries:
        flash('❌ No plan found.', 'danger')
        return redirect(url_for('dashboard'))

    action = request.form.get('action')
    doctor_notes = request.form.get('doctor_notes', '')
    follow_up_days = int(request.form.get('follow_up_days', 7))
    doctor_signature = request.form.get('doctor_signature', user['name'])

    for h in history:
        if h['patient_id'] == patient_id:
            h['status'] = 'Approved' if action == 'approve' else 'Rejected'
            h['doctor_notes'] = doctor_notes
            h['follow_up_days'] = follow_up_days
            h['doctor_signature'] = doctor_signature
            break

    save_history()
    patient_name = PATIENT_DB.get(patient_id, {}).get('full_name', patient_id)
    if action == 'approve':
        save_activity(f"✅ Care plan approved for {patient_name} by {user['name']}")
        flash(f'✅ Plan approved! Signed by Dr. {doctor_signature}', 'success')
    else:
        save_activity(f"❌ Care plan rejected for {patient_name} by {user['name']}")
        flash('❌ Plan rejected.', 'danger')

    return redirect(url_for('care_plan', patient_id=patient_id))

@app.route('/edit_plan/<patient_id>', methods=['POST'])
def edit_plan(patient_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    if user['role'] not in ['Doctor', 'Administrator']:
        flash('⛔ Only doctors can edit plans.', 'danger')
        return redirect(url_for('dashboard'))

    entries = [h for h in history if h['patient_id'] == patient_id]
    if not entries:
        flash('❌ No plan found.', 'danger')
        return redirect(url_for('dashboard'))

    latest = entries[0]

    follow_up  = [f for f in request.form.get('follow_up',  '').split('\n') if f.strip()]
    medication = [m for m in request.form.get('medication', '').split('\n') if m.strip()]
    monitoring = [m for m in request.form.get('monitoring', '').split('\n') if m.strip()]
    dietary    = [d for d in request.form.get('dietary',    '').split('\n') if d.strip()]
    exercise   = [e for e in request.form.get('exercise',   '').split('\n') if e.strip()]
    lifestyle  = [l for l in request.form.get('lifestyle',  '').split('\n') if l.strip()]
    support    = [s for s in request.form.get('support',    '').split('\n') if s.strip()]
    emergency  = [e for e in request.form.get('emergency',  '').split('\n') if e.strip()]

    edited_plan = {
        'follow_up':  follow_up,
        'medication': medication,
        'monitoring': monitoring,
        'dietary':    dietary,
        'exercise':   exercise,
        'lifestyle':  lifestyle,
        'support':    support,
        'emergency':  emergency
    }

    for h in history:
        if h['patient_id'] == patient_id:
            h['medical_care_plan'] = edited_plan
            h['edited_by'] = user['name']
            h['edited_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break

    save_history()
    save_activity(f"✏️ Care plan edited for {latest['patient_name']} by {user['name']}")
    flash('✅ Plan updated successfully!', 'success')

    return redirect(url_for('care_plan', patient_id=patient_id))

# --- 14. FOLLOW-UP ---
@app.route('/follow_up/<patient_id>', methods=['GET', 'POST'])
def follow_up(patient_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    data = PATIENT_DB.get(patient_id)
    if not data:
        return "Patient not found", 404

    if request.method == 'POST':
        follow_data = {
            'patient_id': patient_id,
            'patient_name': data['full_name'],
            'doctor': user['name'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'attended': request.form.get('attended') == 'Yes',
            'condition_improved': request.form.get('condition_improved') == 'Yes',
            'readmitted': request.form.get('readmitted') == 'Yes',
            'notes': request.form.get('notes', '')
        }
        save_followup(follow_data)
        save_activity(f"📋 Follow-up recorded for {data['full_name']} by {user['name']}")
        flash('✅ Follow-up recorded!', 'success')
        return redirect(url_for('profile', patient_id=patient_id))

    return render_template('follow_up.html', patient={'id': patient_id, **data}, user=user)

# --- 15. HISTORY ---
@app.route('/history')
def history_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']

    if user['role'] == 'Doctor':
        filtered = [h for h in history if h.get('doctor') == user['name']]
    elif user['role'] == 'Nurse':
        assigned_doctor = user.get('assigned_doctor', '')
        filtered = [h for h in history if h.get('doctor') == assigned_doctor]
    else:
        filtered = history

    return render_template('history.html', history=filtered, user=user)

# --- 16. REPORTS ---
@app.route('/reports')
def reports():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['user']['role'] != 'Administrator':
        flash('⛔ Access denied. Admin only.', 'danger')
        return redirect(url_for('dashboard'))

    total_patients = len(PATIENT_DB)
    high_risk = sum(1 for h in history if h.get('risk_level') == 'High Risk')
    medium_risk = sum(1 for h in history if h.get('risk_level') == 'Medium Risk')
    low_risk = sum(1 for h in history if h.get('risk_level') == 'Low Risk')

    dept_counts = {}
    for pid, data in PATIENT_DB.items():
        dept = data.get('assigned_department', 'Unassigned')
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

    monthly_data = {}
    for h in history:
        date = h.get('timestamp', '')
        if date:
            month = date[:7]
            monthly_data[month] = monthly_data.get(month, 0) + 1

    doctor_patients = {}
    for pid, data in PATIENT_DB.items():
        doc = data.get('assigned_doctor', 'Unassigned')
        doctor_patients[doc] = doctor_patients.get(doc, 0) + 1

    recent_actions = []
    for h in history[:20]:
        if h.get('status') in ['Approved', 'Rejected']:
            recent_actions.append({
                'patient': h.get('patient_name'),
                'status': h.get('status'),
                'doctor': h.get('doctor'),
                'timestamp': h.get('timestamp')
            })

    return render_template('reports.html',
        user=session['user'],
        total_patients=total_patients,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk,
        dept_counts=dept_counts,
        monthly_data=monthly_data,
        doctor_patients=doctor_patients,
        recent_actions=recent_actions,
        now=datetime.now())

# --- 17. DOWNLOAD PDF ---
@app.route('/download_pdf/<patient_id>')
def download_pdf(patient_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    patient = PATIENT_DB.get(patient_id)
    if not patient:
        return "Patient not found", 404

    latest = None
    for h in history:
        if h['patient_id'] == patient_id:
            latest = h
            break

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()

    title_style      = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1E3A8A'), spaceAfter=30)
    heading_style    = ParagraphStyle('Heading',     parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#1E3A8A'), spaceAfter=12)
    subheading_style = ParagraphStyle('SubHeading',  parent=styles['Heading3'], fontSize=14, textColor=colors.HexColor('#1E3A8A'), spaceAfter=8)
    normal_style     = styles['Normal']

    story = []

    story.append(Paragraph("Suwa Setha Hospital", title_style))
    story.append(Paragraph("No. 25, Hospital Road, Colombo 02, Sri Lanka", normal_style))
    story.append(Paragraph("Tel: +94 11 234 5678 | Email: info@suwasetha.lk", normal_style))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("Patient Discharge After-Care Plan", heading_style))
    story.append(Paragraph(f"Document ID: CP-{patient_id}-{datetime.now().strftime('%Y%m%d')}", normal_style))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("PATIENT INFORMATION", subheading_style))
    patient_info_rows = [
        [f"Patient Name: {patient['full_name']}",             f"Patient ID: {patient_id}"],
        [f"Age: {patient['age']}",                            f"Gender: {patient['gender']}"],
        [f"Diagnosis: {patient.get('diagnosis', '')}",        f"Assigned Doctor: {patient.get('assigned_doctor', '')}"],
    ]
    if latest:
        patient_info_rows.append([
            f"Risk Level: {latest.get('risk_level', 'Not Assessed')}",
            f"Risk Score: {latest.get('risk_score', 0)}%"
        ])
    for row in patient_info_rows:
        story.append(Paragraph(f"{row[0]}     {row[1]}", normal_style))
    story.append(Spacer(1, 0.2 * inch))

    if latest:
        care_plan_data = latest.get('medical_care_plan', None)
        if not care_plan_data:
            patient_for_ai = {
                'Patient_ID': patient_id,
                'Age': patient['age'],
                'Gender': patient['gender'],
                'Diagnosis': patient.get('diagnosis', ''),
                'Previous_Admissions': patient.get('previous_admissions', 0),
                'Length_of_Stay': patient.get('length_of_stay', 0),
                'Medications_Count': len(patient.get('current_medications', [])),
                'Has_Diabetes': 1 if 'Diabetes' in patient.get('existing_diseases', []) else 0,
                'Has_Heart_Disease': 1 if 'Heart Disease' in patient.get('existing_diseases', []) else 0,
                'Has_Hypertension': 1 if 'Hypertension' in patient.get('existing_diseases', []) else 0,
                'Has_COPD': 1 if 'COPD' in patient.get('existing_diseases', []) else 0,
                'existing_diseases': patient.get('existing_diseases', []),
                'current_medications': patient.get('current_medications', []),
                'mobility_status': patient.get('mobility_status', ''),
                'family_support': patient.get('family_support', ''),
                'lives_alone': patient.get('lives_alone', '')
            }
            risk_result = {
                'risk_level': latest.get('risk_level', 'Low Risk'),
                'risk_score': latest.get('risk_score', 0)
            }
            care_plan_data = generate_medical_care_plan(patient_for_ai, risk_result)

        section_titles = {
            'follow_up':  '1. Follow-Up Schedule',
            'medication': '2. Medication Plan',
            'monitoring': '3. Monitoring Instructions',
            'dietary':    '4. Dietary Advice',
            'exercise':   '5. Physical Activity',
            'lifestyle':  '6. Lifestyle Recommendations',
            'support':    '7. Support System',
            'emergency':  '8. Emergency Advice'
        }

        for key, title in section_titles.items():
            if key in care_plan_data and care_plan_data[key]:
                story.append(Paragraph(title, subheading_style))
                for item in care_plan_data[key]:
                    story.append(Paragraph(f"• {item}", normal_style))
                story.append(Spacer(1, 0.1 * inch))

        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("DOCTOR SIGNATURE", subheading_style))
        story.append(Paragraph(f"Responsible Doctor: {patient.get('assigned_doctor', 'Dr. D. Samarasinghe')}", normal_style))
        story.append(Paragraph(f"Department: {patient.get('assigned_department', 'General Medicine')}", normal_style))
        story.append(Paragraph("Date: " + datetime.now().strftime('%B %d, %Y'), normal_style))
        story.append(Paragraph("_____________________________", normal_style))
        story.append(Paragraph("Doctor's Signature", normal_style))

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
    story.append(Paragraph("© Suwa Setha Hospital. All rights reserved.", normal_style))

    doc.build(story)
    buffer.seek(0)

    save_activity(f"📄 PDF downloaded for {patient['full_name']} by {session['user']['name']}")
    flash('✅ PDF downloaded!', 'success')
    return send_file(buffer, as_attachment=True, download_name=f'Care_Plan_{patient_id}.pdf', mimetype='application/pdf')

# --- 18. API ENDPOINTS ---
@app.route('/api/patients')
def api_patients():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(PATIENT_DB)

@app.route('/api/history')
def api_history():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(history)

@app.route('/mark_email_sent/<patient_id>', methods=['POST'])
def mark_email_sent(patient_id):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    for h in history:
        if h['patient_id'] == patient_id:
            h['email_sent'] = True
            break
    save_history()
    return jsonify({'success': True})

@app.route('/mark_sms_sent/<patient_id>', methods=['POST'])
def mark_sms_sent(patient_id):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    for h in history:
        if h['patient_id'] == patient_id:
            h['sms_sent'] = True
            break
    save_history()
    return jsonify({'success': True})

@app.route('/update_patient/<patient_id>', methods=['POST'])
def update_patient(patient_id):
    if 'user' not in session:
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))
    
    user = session['user']
    
    # Only Receptionist and Admin can edit patient info
    if user['role'] not in ['Receptionist', 'Administrator']:
        flash('⛔ Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    data = PATIENT_DB.get(patient_id)
    if not data:
        flash('❌ Patient not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Update personal information
    data['full_name'] = request.form.get('full_name', data['full_name'])
    data['age'] = int(request.form.get('age', data.get('age', 0)))
    data['gender'] = request.form.get('gender', data.get('gender', 'Male'))
    data['nic'] = request.form.get('nic', data.get('nic', ''))
    data['phone'] = request.form.get('phone', data.get('phone', ''))
    data['email'] = request.form.get('email', data.get('email', ''))
    data['address'] = request.form.get('address', data.get('address', ''))
    
    # Update hospital information
    data['admission_date'] = request.form.get('admission_date', data.get('admission_date', ''))
    data['discharge_date'] = request.form.get('discharge_date', data.get('discharge_date', ''))
    data['length_of_stay'] = int(request.form.get('length_of_stay', data.get('length_of_stay', 0)))
    data['assigned_doctor'] = request.form.get('assigned_doctor', data.get('assigned_doctor', ''))
    data['assigned_department'] = request.form.get('assigned_department', data.get('assigned_department', ''))
    data['status'] = request.form.get('status', data.get('status', 'Admitted'))
    
    save_patients()
    save_activity(f"✏️ Patient {data['full_name']} (ID: {patient_id}) updated by {user['name']}")
    
    flash(f'✅ Patient {data["full_name"]} updated successfully!', 'success')
    return redirect(url_for('profile', patient_id=patient_id))

# --- 19. RUN ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)