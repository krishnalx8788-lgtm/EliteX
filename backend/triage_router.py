"""
Triage Router for AI Triage System

This module defines the FastAPI routes for patient management,
triage predictions, and queue management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import joblib
import os
import numpy as np
import pandas as pd

from backend.database import get_db
from backend import models, schemas

# Create router
router = APIRouter(prefix="/api", tags=["triage"])

# Load ML model at module level
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'ai_model', 'triage_model.pkl')

# Global variable for model
triage_model = None
label_encoder = None
feature_names = None


def load_ml_model():
    """
    Load the ML model and associated objects.
    Called at startup to ensure model is loaded.
    """
    global triage_model, label_encoder, feature_names
    
    if os.path.exists(MODEL_PATH):
        model_data = joblib.load(MODEL_PATH)
        triage_model = model_data['model']
        label_encoder = model_data['label_encoder']
        feature_names = model_data['feature_names']
        print("ML model loaded successfully!")
    else:
        print(f"Warning: Model not found at {MODEL_PATH}")


def get_recommended_action(priority: str) -> str:
    """
    Get recommended medical action based on priority level.
    
    Args:
        priority: Priority level string
    
    Returns:
        Recommended action string
    """
    actions = {
        'Critical': 'Immediate ICU evaluation - Life-threatening condition',
        'High': 'Urgent care required within 15 minutes',
        'Medium': 'Treatment needed within 1 hour',
        'Low': 'Routine care - Can wait for standard appointment'
    }
    return actions.get(priority, 'Consult medical professional')


def predict_triage(patient_data: dict) -> dict:
    """
    Make triage prediction using the ML model.
    
    Args:
        patient_data: Dictionary containing patient vital signs
    
    Returns:
        Dictionary with priority, recommended action, and confidence
    """
    global triage_model, label_encoder, feature_names
    
    if triage_model is None:
        load_ml_model()
    
    if triage_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model not available. Please train the model first."
        )
    
    # Prepare features for prediction using DataFrame with proper feature names
    features_df = pd.DataFrame([{
        'age': patient_data['age'],
        'heart_rate': patient_data['heart_rate'],
        'systolic_bp': patient_data['systolic_bp'],
        'oxygen': patient_data['oxygen'],
        'temperature': patient_data['temperature'],
        'respiratory_rate': patient_data['respiratory_rate'],
        'symptom': patient_data['symptom']
    }])
    
    # Make prediction
    prediction_encoded = triage_model.predict(features_df)[0]
    priority = label_encoder.inverse_transform([prediction_encoded])[0]
    
    # Get prediction probabilities for confidence score
    probabilities = triage_model.predict_proba(features_df)[0]
    confidence = float(max(probabilities))
    
    # Generate alert for critical patients
    alert = None
    if priority == 'Critical':
        alert = "⚠️ CRITICAL ALERT: Immediate attention required!"
    
    return {
        'priority': priority,
        'recommended_action': get_recommended_action(priority),
        'confidence': round(confidence, 4),
        'alert': alert
    }


# API Endpoints

@router.get("/", response_model=schemas.APIStatus)
async def root():
    """
    Root endpoint - Returns API status.
    """
    return schemas.APIStatus(
        status="online",
        message="AI Triage System API is running"
    )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "model_loaded": triage_model is not None
    }


@router.post("/predict-triage", response_model=schemas.TriagePrediction)
async def predict_triage_endpoint(request: schemas.TriageRequest):
    """
    Predict triage priority for a patient based on vital signs.
    
    This endpoint analyzes patient symptoms and vital signs using the ML model
    to determine the appropriate urgency level.
    
    Returns:
        TriagePrediction with priority, recommended action, and confidence score
    """
    patient_data = request.model_dump()
    prediction = predict_triage(patient_data)
    
    return schemas.TriagePrediction(**prediction)


@router.post("/patients", response_model=schemas.PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    """
    Add a new patient to the system and run triage prediction.
    
    This endpoint:
    1. Creates a new patient record
    2. Runs ML prediction to determine priority
    3. Saves patient with priority to database
    4. Returns the created patient with prediction results
    
    Returns:
        PatientResponse with patient data and predicted priority
    """
    # Prepare data for prediction
    patient_dict = patient.model_dump()
    
    # Run triage prediction
    prediction = predict_triage(patient_dict)
    
    # Create patient record with prediction
    db_patient = models.Patient(
        name=patient.name,
        age=patient.age,
        heart_rate=patient.heart_rate,
        systolic_bp=patient.systolic_bp,
        oxygen=patient.oxygen,
        temperature=patient.temperature,
        respiratory_rate=patient.respiratory_rate,
        symptom=patient.symptom,
        priority=prediction['priority'],
        confidence=prediction['confidence']
    )
    
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_patient


@router.get("/patients", response_model=List[schemas.PatientResponse])
async def get_patients(
    priority: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all patients sorted by priority (Critical first).
    
    Optional query parameters:
    - priority: Filter by priority level
    - limit: Maximum number of results (default: 100)
    
    Returns:
        List of patients sorted by priority
    """
    query = db.query(models.Patient)
    
    # Filter by priority if specified
    if priority:
        query = query.filter(models.Patient.priority == priority)
    
    # Order by created_at (newest first) - priority sorting done in application layer
    patients = query.order_by(desc(models.Patient.created_at)).limit(limit).all()
    
    # Sort by priority: Critical > High > Medium > Low
    priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    patients.sort(key=lambda p: priority_order.get(p.priority, 4))
    
    return patients


@router.get("/patients/queue", response_model=schemas.PatientQueueResponse)
async def get_patient_queue(db: Session = Depends(get_db)):
    """
    Get patients organized by priority queue.
    
    Returns patients grouped by priority level for easy visualization
    of the triage queue.
    
    Returns:
        PatientQueueResponse with patients grouped by priority
    """
    patients = db.query(models.Patient).all()
    
    # Group patients by priority
    queue = {
        'critical': [],
        'high': [],
        'medium': [],
        'low': []
    }
    
    for patient in patients:
        if patient.priority == 'Critical':
            queue['critical'].append(patient)
        elif patient.priority == 'High':
            queue['high'].append(patient)
        elif patient.priority == 'Medium':
            queue['medium'].append(patient)
        else:
            queue['low'].append(patient)
    
    return schemas.PatientQueueResponse(
        critical=queue['critical'],
        high=queue['high'],
        medium=queue['medium'],
        low=queue['low'],
        total=len(patients)
    )


@router.get("/patients/{patient_id}", response_model=schemas.PatientResponse)
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Get a specific patient by ID.
    
    Args:
        patient_id: Patient ID
    
    Returns:
        PatientResponse with patient details
    """
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    return patient


@router.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Delete a patient from the system.
    
    Args:
        patient_id: Patient ID to delete
    """
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    db.delete(patient)
    db.commit()
    
    return {"message": f"Patient {patient_id} deleted successfully"}


@router.get("/analytics/summary", response_model=schemas.AnalyticsSummary)
async def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Get analytics summary of patient queue.
    
    Returns statistics about current patients including:
    - Total patient count
    - Count by priority level
    - Average age
    - Critical patient percentage
    
    Returns:
        AnalyticsSummary with queue statistics
    """
    patients = db.query(models.Patient).all()
    total = len(patients)
    
    if total == 0:
        return schemas.AnalyticsSummary(
            total_patients=0,
            critical_count=0,
            high_count=0,
            medium_count=0,
            low_count=0,
            average_age=0.0,
            critical_percentage=0.0
        )
    
    critical_count = sum(1 for p in patients if p.priority == 'Critical')
    high_count = sum(1 for p in patients if p.priority == 'High')
    medium_count = sum(1 for p in patients if p.priority == 'Medium')
    low_count = sum(1 for p in patients if p.priority == 'Low')
    
    average_age = sum(p.age for p in patients) / total
    critical_percentage = (critical_count / total) * 100
    
    return schemas.AnalyticsSummary(
        total_patients=total,
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        average_age=round(average_age, 1),
        critical_percentage=round(critical_percentage, 2)
    )


# Load model when module is imported
load_ml_model()
