# data_generator.py
import pandas as pd
import numpy as np
import random

def generate_patient_data(n_patients=10000):
    np.random.seed(42)
    random.seed(42)

    # Age distribution
    age = np.concatenate([
        np.random.normal(25, 10, int(n_patients*0.3)),
        np.random.normal(45, 10, int(n_patients*0.3)),
        np.random.normal(70, 10, int(n_patients*0.4))
    ])
    age = np.clip(age, 0, 100).astype(int)
    np.random.shuffle(age)

    # Vital signs
    heart_rate = np.clip(np.random.normal(85, 20, n_patients), 40, 200).astype(int)
    systolic_bp = np.clip(np.random.normal(130, 25, n_patients), 70, 220).astype(int)
    diastolic_bp = np.clip(systolic_bp*0.6 + np.random.normal(0,5,n_patients), 40, 130).astype(int)
    oxygen_sat = np.clip(np.random.normal(95, 5, n_patients), 70, 100).astype(int)
    temperature = np.clip(np.random.normal(37.2, 1.2, n_patients), 34, 41).round(1)
    respiratory_rate = np.clip(np.random.normal(18, 5, n_patients), 8, 40).astype(int)
    consciousness = np.random.choice([0,1,2], n_patients, p=[0.8,0.15,0.05])

    # Symptoms
    symptoms_list = ['chest_pain','shortness_of_breath','fever','headache','abdominal_pain',
                     'bleeding','vomiting','dizziness','weakness','palpitations','seizure','stroke_symptoms']
    symptoms = []
    for _ in range(n_patients):
        n_symptoms = np.random.poisson(1.5)
        n_symptoms = min(n_symptoms, 4)
        patient_symptoms = random.sample(symptoms_list, n_symptoms) if n_symptoms>0 else []
        symptoms.append(','.join(patient_symptoms))

    # Medical history
    conditions = ['hypertension','diabetes','heart_disease','asthma','none']
    history_weights = [0.3,0.2,0.15,0.1,0.25]
    medical_history = np.random.choice(conditions, n_patients, p=history_weights)

    # MEWS score (simplified)
    mews = np.zeros(n_patients)
    # Heart rate
    mews += np.where(heart_rate<40,3,0)
    mews += np.where((heart_rate>=40)&(heart_rate<=50),2,0)
    mews += np.where((heart_rate>=101)&(heart_rate<=110),1,0)
    mews += np.where((heart_rate>=111)&(heart_rate<=129),2,0)
    mews += np.where(heart_rate>=130,3,0)
    # Systolic BP
    mews += np.where(systolic_bp<70,3,0)
    mews += np.where((systolic_bp>=71)&(systolic_bp<=80),2,0)
    mews += np.where((systolic_bp>=81)&(systolic_bp<=100),1,0)
    mews += np.where(systolic_bp>200,2,0)
    # Temperature
    mews += np.where(temperature<35,2,0)
    mews += np.where(temperature>38.5,2,0)
    # Oxygen
    mews += np.where(oxygen_sat<85,3,0)
    mews += np.where((oxygen_sat>=85)&(oxygen_sat<=89),2,0)
    mews += np.where((oxygen_sat>=90)&(oxygen_sat<=94),1,0)
    # Consciousness
    mews += consciousness*2
    # Respiratory rate
    mews += np.where(respiratory_rate<9,2,0)
    mews += np.where((respiratory_rate>=15)&(respiratory_rate<=20),1,0)
    mews += np.where((respiratory_rate>=21)&(respiratory_rate<=29),2,0)
    mews += np.where(respiratory_rate>=30,3,0)

    # Priority (1=critical, 5=non-urgent)
    priority = np.where(mews>=7,1,
               np.where(mews>=5,2,
               np.where(mews>=3,3,
               np.where(mews>=1,4,5))))

    df = pd.DataFrame({
        'age': age,
        'heart_rate': heart_rate,
        'systolic_bp': systolic_bp,
        'diastolic_bp': diastolic_bp,
        'oxygen_sat': oxygen_sat,
        'temperature': temperature,
        'respiratory_rate': respiratory_rate,
        'consciousness': consciousness,
        'symptoms': symptoms,
        'medical_history': medical_history,
        'mews_score': mews.astype(int),
        'priority': priority.astype(int)
    })
    return df

if __name__ == "__main__":
    df = generate_patient_data(10000)
    df.to_csv('data/triage_data.csv', index=False)
    print("✅ Data saved to data/triage_data.csv")
    print(df['priority'].value_counts().sort_index())