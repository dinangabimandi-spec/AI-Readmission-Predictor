import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

N = 800

DIAGNOSES = ["Heart Disease", "Diabetes", "Pneumonia", "Asthma", "Hypertension",
             "COPD", "Stroke", "Kidney Disease", "Liver Disease", "Cancer",
             "Arthritis", "Depression"]

RECOVERY = ["Good", "Fair", "Poor"]
MOBILITY = ["Independent", "Assisted", "Bedridden"]
COMPLIANCE = ["Low", "Medium", "High"]
SUPPORT = ["Strong", "Moderate", "Weak"]

rows = []
for i in range(N):
    age = random.randint(18, 90)
    gender = random.choice(["Male", "Female"])
    diagnosis = random.choice(DIAGNOSES)
    previous_admissions = random.randint(0, 6)
    length_of_stay = random.randint(1, 30)
    medications_count = random.randint(0, 10)
    has_diabetes = random.choice([0, 1])
    has_heart_disease = random.choice([0, 1])
    has_hypertension = random.choice([0, 1])
    has_copd = random.choice([0, 1])

    recovery_status = random.choice(RECOVERY)
    mobility_status = random.choice(MOBILITY)
    medication_compliance_risk = random.choice(COMPLIANCE)
    family_support = random.choice(SUPPORT)
    lives_alone = random.choice([0, 1])
    has_transportation_access = random.choice([0, 1])

    # Clinically-logical risk score (log-odds), not random
    score = -3.2
    score += 0.025 * max(age - 50, 0)
    score += 0.9 * has_diabetes
    score += 0.9 * has_heart_disease
    score += 0.7 * has_hypertension
    score += 0.8 * has_copd
    score += 0.45 * min(previous_admissions, 5)
    score += 0.06 * length_of_stay
    score += 0.12 * medications_count
    score += {"Good": 0, "Fair": 0.6, "Poor": 1.5}[recovery_status]
    score += {"Independent": 0, "Assisted": 0.5, "Bedridden": 1.3}[mobility_status]
    score += {"Low": 0, "Medium": 0.6, "High": 1.4}[medication_compliance_risk]
    score += {"Strong": 0, "Moderate": 0.4, "Weak": 1.0}[family_support]
    score += 0.6 * lives_alone
    score += 0.6 * (1 - has_transportation_access)
    score += np.random.normal(0, 0.5)

    probability = 1 / (1 + np.exp(-score))
    readmitted = np.random.binomial(1, probability)

    rows.append({
        "Patient_ID": f"P{1000+i}", "Age": age, "Gender": gender, "Diagnosis": diagnosis,
        "Previous_Admissions": previous_admissions, "Length_of_Stay": length_of_stay,
        "Medications_Count": medications_count, "Has_Diabetes": has_diabetes,
        "Has_Heart_Disease": has_heart_disease, "Has_Hypertension": has_hypertension,
        "Has_COPD": has_copd, "Recovery_Status": recovery_status,
        "Mobility_Status": mobility_status,
        "Medication_Compliance_Risk": medication_compliance_risk,
        "Family_Support": family_support, "Lives_Alone": lives_alone,
        "Has_Transportation_Access": has_transportation_access,
        "Readmitted_30days": readmitted
    })

df = pd.DataFrame(rows)
df.to_csv("patient_data.csv", index=False)
print(f"✅ Generated {N} rows -> patient_data.csv")
print(df["Readmitted_30days"].value_counts())