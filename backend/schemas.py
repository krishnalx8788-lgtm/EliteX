"""
Pydantic Schemas for AI Triage System

This module defines the request and response models for API validation.
Uses Pydantic for data validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class SymptomType(int, Enum):
    """
    Enum for symptom categories.
    
    Values:
        1: Chest Pain
        2: Breathing Difficulty
        3: Fever
        4: Headache
        5: Injury
        6: Vomiting
        7: Dizziness
    """
    CHEST_PAIN = 1
    BREATHING_DIFFICULTY = 2
    FEVER = 3
    HEADACHE = 4
    INJURY = 5
    VOMITING = 6
    DIZZINESS = 7


class PriorityLevel(str, Enum):
    """
    Enum for patient priority levels.
    
    Values:
        Critical: Immediate treatment required
        High: Very urgent
        Medium: Needs treatment soon
        Low: Non-urgent
    """
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class PatientBase(BaseModel):
    """
    Base schema for patient data with common attributes.
    """
    name: str = Field(..., min_length=1, max_length=100, description="Patient name")
    age: int = Field(..., ge=18, le=90, description="Patient age (18-90)")
    heart_rate: int = Field(..., ge=60, le=150, description="Heart rate in bpm (60-150)")
    systolic_bp: int = Field(..., ge=90, le=180, description="Systolic blood pressure (90-180)")
    oxygen: int = Field(..., ge=80, le=100, description="Oxygen saturation level (80-100%)")
    temperature: float = Field(..., ge=36.0, le=40.0, description="Body temperature in Celsius (36-40)")
    respiratory_rate: int = Field(..., ge=12, le=30, description="Respiratory rate (12-30)")
    symptom: SymptomType = Field(..., description="Symptom category (1-7)")


class PatientCreate(PatientBase):
    """
    Schema for creating a new patient.
    Inherits all fields from PatientBase.
    """
    pass


class PatientResponse(PatientBase):
    """
    Schema for patient response with additional fields.
    
    Attributes:
        id: Patient ID
        priority: Predicted priority level
        confidence: Prediction confidence score
        created_at: Timestamp when record was created
    """
    id: int
    priority: PriorityLevel
    confidence: Optional[float] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TriagePrediction(BaseModel):
    """
    Schema for triage prediction response.
    
    Attributes:
        priority: Predicted priority level
        recommended_action: Recommended medical action
        confidence: Prediction confidence score
        alert: Alert message if critical
    """
    priority: PriorityLevel
    recommended_action: str
    confidence: Optional[float] = None
    alert: Optional[str] = None


class TriageRequest(BaseModel):
    """
    Schema for triage prediction request.
    
    Contains all vital signs and symptoms needed for prediction.
    """
    name: Optional[str] = Field(None, description="Patient name (optional for prediction)")
    age: int = Field(..., ge=18, le=90, description="Patient age (18-90)")
    heart_rate: int = Field(..., ge=60, le=150, description="Heart rate in bpm (60-150)")
    systolic_bp: int = Field(..., ge=90, le=180, description="Systolic blood pressure (90-180)")
    oxygen: int = Field(..., ge=80, le=100, description="Oxygen saturation level (80-100%)")
    temperature: float = Field(..., ge=36.0, le=40.0, description="Body temperature in Celsius (36-40)")
    respiratory_rate: int = Field(..., ge=12, le=30, description="Respiratory rate (12-30)")
    symptom: SymptomType = Field(..., description="Symptom category (1-7)")


class PatientQueueResponse(BaseModel):
    """
    Schema for patient queue response.
    
    Groups patients by priority level.
    """
    critical: list[PatientResponse]
    high: list[PatientResponse]
    medium: list[PatientResponse]
    low: list[PatientResponse]
    total: int


class APIStatus(BaseModel):
    """
    Schema for API status response.
    """
    status: str
    message: str
    version: str = "1.0.0"


class AnalyticsSummary(BaseModel):
    """
    Schema for analytics summary response.
    
    Provides statistics about patient queue.
    """
    total_patients: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    average_age: float
    critical_percentage: float
