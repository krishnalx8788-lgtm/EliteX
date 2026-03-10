# 🏥 AI-Based Emergency Triage Assistant

A complete production-style AI system that helps hospitals prioritize patients in emergency situations. The system analyzes patient symptoms, vital signs, and medical history to classify patients into urgency levels, assisting healthcare workers in making faster triage decisions.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30.0-red.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4.0-orange.svg)

## 🎯 Features

- **AI-Powered Triage**: Machine learning model classifies patients into 4 priority levels
- **OCR Integration**: Extract patient data from medical report images using Tesseract OCR
- **Real-time Predictions**: FastAPI backend for instant triage assessments
- **Patient Management**: Complete CRUD operations for patient records
- **Priority Queue**: Visual patient queue organized by urgency
- **Analytics Dashboard**: Charts and statistics for monitoring
- **Alert System**: Critical patient notifications
- **Web Interface**: Streamlit dashboard for easy interaction

## 📊 Priority Levels

| Priority | Color | Description | Response Time |
|----------|-------|-------------|---------------|
| 🔴 Critical | Red | Immediate treatment required | Immediate |
| 🟠 High | Orange | Very urgent | Within 15 min |
| 🟡 Medium | Yellow | Needs treatment soon | Within 1 hour |
| 🟢 Low | Green | Non-urgent | Routine care |

## 🏗️ Project Structure

```
ai-triage-system/
├── backend/                    # FastAPI Backend
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # SQLAlchemy database configuration
│   ├── models.py               # Database models
│   ├── schemas.py              # Pydantic request/response schemas
│   └── triage_router.py        # API routes and endpoints
├── ai_model/                   # Machine Learning
│   ├── train_model.py          # ML model training script
│   └── triage_model.pkl        # Trained model (generated)
├── dataset/                    # Data Generation
│   ├── generate_dataset.py     # Synthetic dataset generator
│   └── triage_dataset.csv      # Generated dataset
├── frontend/                   # Streamlit Dashboard
│   └── dashboard.py            # Interactive web interface
├── ocr_module/                 # OCR Module (NEW!)
│   ├── medical_report_ocr.py   # OCR processor for medical reports
│   ├── test_image_generator.py # Test image generator
│   ├── ocr_triage_integration.py # OCR + Triage integration
│   └── README.md               # OCR module documentation
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Dataset

```bash
python dataset/generate_dataset.py
```

This creates a synthetic dataset of 2000+ patient records with medically reasonable vital signs.

### 3. Train the ML Model

```bash
python ai_model/train_model.py
```

Trains a RandomForestClassifier and saves it to `ai_model/triage_model.pkl`.

**Expected Output:**
```
Accuracy: 1.0000 (100.00%)
Feature Importance:
  oxygen: 0.3912
  heart_rate: 0.2333
  respiratory_rate: 0.1379
  temperature: 0.1332
  systolic_bp: 0.0692
  age: 0.0211
  symptom: 0.0142
```

### 4. Start the Backend API

```bash
uvicorn backend.main:app --reload
```

The API will be available at: `http://localhost:8000`

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 5. Launch the Dashboard

In a new terminal:

```bash
streamlit run frontend/dashboard.py
```

The dashboard will open automatically at: `http://localhost:8501`

## 📄 OCR Module (NEW)

Extract patient data from medical report images automatically!

### Prerequisites

Install Tesseract OCR engine:

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:** Download from https://github.com/UB-Mannheim/tesseract/wiki

### Quick OCR Example

```python
from ocr_module import MedicalReportOCR

# Initialize OCR
ocr = MedicalReportOCR()

# Extract data from medical report image
result = ocr.process_image("medical_report.jpg")

print(result)
# {
#     "name": "John Smith",
#     "age": 65,
#     "heart_rate": 132,
#     "systolic_bp": 170,
#     "oxygen": 86,
#     "temperature": 38.2,
#     "respiratory_rate": 25,
#     "symptom": "Chest Pain"
# }
```

### OCR + Triage Integration

```bash
# Complete workflow: OCR → Triage Prediction → Save to DB
python ocr_module/ocr_triage_integration.py --image report.jpg --demo
```

### Generate Test Images

```bash
# Generate sample medical report images for testing
python ocr_module/test_image_generator.py --sample --output-dir test_images
```

For detailed OCR documentation, see [ocr_module/README.md](ocr_module/README.md).

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status and info |
| GET | `/api/health` | Health check |
| POST | `/api/predict-triage` | Get triage prediction |
| POST | `/api/patients` | Add new patient |
| GET | `/api/patients` | List all patients |
| GET | `/api/patients/queue` | Get priority queue |
| GET | `/api/patients/{id}` | Get specific patient |
| DELETE | `/api/patients/{id}` | Delete patient |
| GET | `/api/analytics/summary` | Get analytics |

### Example API Usage

#### Predict Triage

```bash
curl -X POST "http://localhost:8000/api/predict-triage" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "age": 65,
    "heart_rate": 130,
    "systolic_bp": 170,
    "oxygen": 85,
    "temperature": 38.5,
    "respiratory_rate": 25,
    "symptom": 1
  }'
```

**Response:**
```json
{
  "priority": "Critical",
  "recommended_action": "Immediate ICU evaluation - Life-threatening condition",
  "confidence": 0.98,
  "alert": "⚠️ CRITICAL ALERT: Immediate attention required!"
}
```

#### Add Patient

```bash
curl -X POST "http://localhost:8000/api/patients" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "age": 45,
    "heart_rate": 85,
    "systolic_bp": 120,
    "oxygen": 98,
    "temperature": 37.0,
    "respiratory_rate": 16,
    "symptom": 3
  }'
```

## 🖥️ Dashboard Features

### 1. Patient Intake
- Input form for patient information
- Vital signs entry (heart rate, BP, oxygen, etc.)
- Symptom selection dropdown
- AI triage prediction with confidence score
- Visual gauge charts for vital signs
- Critical patient alerts

### 2. Priority Queue
- Patients organized by priority level
- Auto-refresh option
- Expandable patient details
- Color-coded priority badges
- Quick statistics summary

### 3. Analytics
- Priority distribution pie chart
- Patient count by priority bar chart
- Age distribution analysis
- Vital signs scatter plots
- Key metrics summary cards

## 🔬 ML Model Details

### Algorithm
- **Model**: RandomForestClassifier
- **Features**: 7 vital sign parameters
- **Classes**: 4 priority levels

### Features Used
| Feature | Range | Description |
|---------|-------|-------------|
| age | 18-90 | Patient age in years |
| heart_rate | 60-150 | Beats per minute |
| systolic_bp | 90-180 | Systolic blood pressure |
| oxygen | 80-100 | Oxygen saturation % |
| temperature | 36-40 | Body temperature °C |
| respiratory_rate | 12-30 | Breaths per minute |
| symptom | 1-7 | Symptom category |

### Training Rules
```python
Critical: oxygen < 88 OR heart_rate > 130 OR systolic_bp > 170
High:     oxygen 88-92 OR heart_rate 110-130
Medium:   temperature > 38 OR respiratory_rate > 22
Low:      otherwise
```

### Symptom Categories
| Code | Symptom |
|------|---------|
| 1 | Chest Pain |
| 2 | Breathing Difficulty |
| 3 | Fever |
| 4 | Headache |
| 5 | Injury |
| 6 | Vomiting |
| 7 | Dizziness |

## 🗄️ Database Schema

### Patients Table
```sql
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    heart_rate INTEGER NOT NULL,
    systolic_bp INTEGER NOT NULL,
    oxygen INTEGER NOT NULL,
    temperature FLOAT NOT NULL,
    respiratory_rate INTEGER NOT NULL,
    symptom INTEGER NOT NULL,
    priority VARCHAR(20) NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## ⚙️ Configuration

### Environment Variables
```bash
# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///./triage_database.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/triage_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## 🧪 Testing

### Test the API
```bash
# Health check
curl http://localhost:8000/api/health

# Get all patients
curl http://localhost:8000/api/patients

# Get patient queue
curl http://localhost:8000/api/patients/queue

# Get analytics
curl http://localhost:8000/api/analytics/summary
```

### Test Critical Patient Alert
```bash
curl -X POST "http://localhost:8000/api/predict-triage" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 70,
    "heart_rate": 140,
    "systolic_bp": 180,
    "oxygen": 82,
    "temperature": 39.0,
    "respiratory_rate": 28,
    "symptom": 2
  }'
```

## 📈 Future Enhancements

- [ ] Real-time patient monitoring with WebSockets
- [ ] SMS/email alerts for critical patients
- [ ] Integration with hospital EHR systems
- [ ] Multi-language support
- [ ] Advanced analytics with time-series data
- [ ] User authentication and role-based access
- [ ] Audit logging for compliance
- [ ] Model retraining pipeline
- [ ] Docker containerization
- [ ] Kubernetes deployment

## 📝 License

This project is for educational and demonstration purposes. Not intended for production medical use without proper validation and regulatory approval.

## 🤝 Contributing

This is a hackathon demo project. Feel free to fork and enhance!

## ⚠️ Disclaimer

**IMPORTANT**: This system is a prototype for demonstration purposes only. It should NOT be used for actual medical diagnosis or treatment decisions without proper clinical validation and regulatory approval. Always consult qualified healthcare professionals for medical decisions.

---

Built with ❤️ for hackathons and healthcare innovation.
