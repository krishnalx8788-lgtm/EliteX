"""
SQLAlchemy Models for AI Triage System

This module defines the database models for storing patient information
and triage predictions.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, func
from backend.database import Base


class Patient(Base):
    """
    Patient model for storing patient information and triage predictions.
    
    Attributes:
        id: Primary key (auto-increment)
        name: Patient name
        age: Patient age (18-90)
        heart_rate: Heart rate in bpm (60-150)
        systolic_bp: Systolic blood pressure (90-180)
        oxygen: Oxygen saturation level (80-100%)
        temperature: Body temperature in Celsius (36-40)
        respiratory_rate: Breaths per minute (12-30)
        symptom: Symptom category (1-7)
        priority: Predicted priority level (Critical/High/Medium/Low)
        confidence: Prediction confidence score (0-1)
        created_at: Timestamp when record was created
    """
    
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    heart_rate = Column(Integer, nullable=False)
    systolic_bp = Column(Integer, nullable=False)
    oxygen = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    respiratory_rate = Column(Integer, nullable=False)
    symptom = Column(Integer, nullable=False)
    priority = Column(String(20), nullable=False, index=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}', priority='{self.priority}')>"
    
    def to_dict(self):
        """
        Convert patient object to dictionary.
        
        Returns:
            Dictionary representation of the patient
        """
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'heart_rate': self.heart_rate,
            'systolic_bp': self.systolic_bp,
            'oxygen': self.oxygen,
            'temperature': self.temperature,
            'respiratory_rate': self.respiratory_rate,
            'symptom': self.symptom,
            'priority': self.priority,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
