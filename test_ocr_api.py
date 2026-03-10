"""Test to see full OCR output."""
import requests
import json

API_URL = "http://localhost:8000/api/ocr/extract"
IMAGE_PATH = "test_sample_report.jpg"

with open(IMAGE_PATH, "rb") as f:
    files = {"file": ("test_sample_report.jpg", f, "image/jpeg")}
    response = requests.post(API_URL, files=files, timeout=30)

print(f"Status: {response.status_code}")
data = response.json()
print(json.dumps(data, indent=2))
