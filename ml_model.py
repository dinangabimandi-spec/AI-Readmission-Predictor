import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import warnings
warnings.filterwarnings('ignore')

class ReadmissionPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.encoders = {}
        self.feature_columns = []
        
    def prepare_data(self, df):
        feature_cols = [
            'Age', 'Previous_Admissions', 'Length_of_Stay', 
            'Medications_Count', 'Has_Diabetes', 'Has_Heart_Disease',
            'Has_Hypertension', 'Has_COPD'
        ]
        
        df_encoded = df.copy()
        
        le = LabelEncoder()
        df_encoded['Diagnosis_Encoded'] = le.fit_transform(df_encoded['Diagnosis'])
        self.encoders['Diagnosis'] = le
        feature_cols.append('Diagnosis_Encoded')
        
        le_gender = LabelEncoder()
        df_encoded['Gender_Encoded'] = le_gender.fit_transform(df_encoded['Gender'])
        self.encoders['Gender'] = le_gender
        feature_cols.append('Gender_Encoded')
        
        self.feature_columns = feature_cols
        X = df_encoded[feature_cols]
        y = df_encoded['Readmitted_30days']
        return X, y
    
    def train(self, df):
        X, y = self.prepare_data(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model Accuracy: {accuracy:.2%}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        return accuracy
    
    def predict(self, patient_data):
        df = pd.DataFrame([patient_data])
        df['Diagnosis_Encoded'] = self.encoders['Diagnosis'].transform(df['Diagnosis'])
        df['Gender_Encoded'] = self.encoders['Gender'].transform(df['Gender'])
        X = df[self.feature_columns]
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
        probability = self.model.predict_proba(X_scaled)[0][1]
        
        risk_level = 'Low Risk'
        risk_color = 'green'
        if probability > 0.7:
            risk_level = 'High Risk'
            risk_color = 'red'
        elif probability > 0.4:
            risk_level = 'Medium Risk'
            risk_color = 'orange'
            
        return {
            'readmission_prediction': bool(prediction),
            'risk_score': round(probability * 100, 1),
            'risk_level': risk_level,
            'risk_color': risk_color
        }
    
    def save_model(self, filename='readmission_model.pkl'):
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'encoders': self.encoders,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_data, filename)
        print(f"Model saved to {filename}")
    
    def load_model(self, filename='readmission_model.pkl'):
        model_data = joblib.load(filename)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.encoders = model_data['encoders']
        self.feature_columns = model_data['feature_columns']
        print("Model loaded successfully!")

if __name__ == "__main__":
    df = pd.read_csv('patient_data.csv')
    predictor = ReadmissionPredictor()
    predictor.train(df)
    predictor.save_model()
    
    test_patient = {
        'Age': 65,
        'Gender': 'Male',
        'Diagnosis': 'Heart Disease',
        'Previous_Admissions': 3,
        'Length_of_Stay': 10,
        'Medications_Count': 5,
        'Has_Diabetes': 1,
        'Has_Heart_Disease': 1,
        'Has_Hypertension': 1,
        'Has_COPD': 0
    }
    result = predictor.predict(test_patient)
    print("\nTest Prediction:", result)