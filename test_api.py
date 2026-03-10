"""
Test script for AI Triage System API
"""

import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    print("✅ Root endpoint test passed")
    return data


def test_health():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health check test passed")
    return data


def test_predict_triage_critical():
    """Test triage prediction for critical patient."""
    patient_data = {
        "name": "Critical Patient",
        "age": 70,
        "heart_rate": 140,
        "systolic_bp": 180,
        "oxygen": 82,
        "temperature": 39.0,
        "respiratory_rate": 28,
        "symptom": 2
    }
    
    response = client.post("/api/predict-triage", json=patient_data)
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "Critical"
    assert data["alert"] is not None
    assert "confidence" in data
    print(f"✅ Critical prediction test passed: {data['priority']} (confidence: {data['confidence']})")
    return data


def test_predict_triage_low():
    """Test triage prediction for low priority patient."""
    patient_data = {
        "name": "Low Priority Patient",
        "age": 30,
        "heart_rate": 70,
        "systolic_bp": 110,
        "oxygen": 98,
        "temperature": 36.5,
        "respiratory_rate": 14,
        "symptom": 4
    }
    
    response = client.post("/api/predict-triage", json=patient_data)
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "Low"
    print(f"✅ Low priority prediction test passed: {data['priority']} (confidence: {data['confidence']})")
    return data


def test_create_patient():
    """Test creating a patient."""
    patient_data = {
        "name": "Test Patient",
        "age": 45,
        "heart_rate": 85,
        "systolic_bp": 120,
        "oxygen": 98,
        "temperature": 37.0,
        "respiratory_rate": 16,
        "symptom": 3
    }
    
    response = client.post("/api/patients", json=patient_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Patient"
    assert "id" in data
    assert "priority" in data
    print(f"✅ Create patient test passed: ID={data['id']}, Priority={data['priority']}")
    return data


def test_get_patients():
    """Test getting all patients."""
    response = client.get("/api/patients")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ Get patients test passed: {len(data)} patients found")
    return data


def test_get_queue():
    """Test getting patient queue."""
    response = client.get("/api/patients/queue")
    assert response.status_code == 200
    data = response.json()
    assert "critical" in data
    assert "high" in data
    assert "medium" in data
    assert "low" in data
    assert "total" in data
    print(f"✅ Get queue test passed: {data['total']} total patients")
    return data


def test_analytics():
    """Test analytics endpoint."""
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_patients" in data
    print(f"✅ Analytics test passed: {data['total_patients']} patients")
    return data


def run_all_tests():
    """Run all API tests."""
    print("=" * 60)
    print("AI Triage System - API Tests")
    print("=" * 60)
    
    try:
        test_root()
        test_health()
        test_predict_triage_critical()
        test_predict_triage_low()
        test_create_patient()
        test_get_patients()
        test_get_queue()
        test_analytics()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    run_all_tests()
