# OCR Module for AI Triage System

This module provides Optical Character Recognition (OCR) capabilities for extracting patient information from medical report images.

## 📋 Features

- **Image Preprocessing**: Grayscale conversion, thresholding, noise reduction
- **Text Extraction**: Using Tesseract OCR engine
- **Data Parsing**: Regex-based extraction of patient fields
- **Structured Output**: JSON format compatible with triage system
- **Integration Ready**: Seamless connection to triage prediction API

## 🔧 Prerequisites

### Install Tesseract OCR Engine

The OCR module requires Tesseract to be installed on your system:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer and note the installation path
3. Add Tesseract to your PATH or specify the path in code

### Python Dependencies

```bash
pip install pytesseract opencv-python Pillow numpy
```

## 📁 Module Structure

```
ocr_module/
├── __init__.py                  # Module exports
├── medical_report_ocr.py        # Main OCR processor class
├── test_image_generator.py      # Test image generator
└── ocr_triage_integration.py    # Integration with triage API
```

## 🚀 Usage

### Basic Usage

```python
from ocr_module import MedicalReportOCR

# Initialize OCR processor
ocr = MedicalReportOCR()

# Process a medical report image
result = ocr.process_image("medical_report.jpg")

# Print extracted data
print(result)
# {
#     "name": "John Smith",
#     "age": 65,
#     "heart_rate": 132,
#     "systolic_bp": 170,
#     "oxygen": 86,
#     "temperature": 38.2,
#     "respiratory_rate": 25,
#     "symptom": "Chest Pain",
#     "symptom_code": 1,
#     "ocr_success": True,
#     "extracted_fields_count": 8
# }
```

### Convenience Function

```python
from ocr_module import process_medical_report

# One-line processing
result = process_medical_report("medical_report.jpg")
print(result['name'])  # John Smith
```

### With Raw Text Output

```python
result = ocr.process_image("report.jpg", return_raw_text=True)
print(result['raw_text'])  # Raw OCR output
```

### Convert to Triage Format

```python
# Convert OCR output to triage system input format
triage_data = ocr.to_triage_format(result)
print(triage_data)
# {
#     "name": "John Smith",
#     "age": 65,
#     "heart_rate": 132,
#     "systolic_bp": 170,
#     "oxygen": 86,
#     "temperature": 38.2,
#     "respiratory_rate": 25,
#     "symptom": 1
# }
```

## 🔗 Integration with Triage System

### Complete Workflow

```python
from ocr_module.ocr_triage_integration import OCRTriageIntegration

# Initialize integration
integration = OCRTriageIntegration(api_base_url="http://localhost:8000/api")

# Process image and get triage prediction
result = integration.process_and_triage("medical_report.jpg")

# Access results
print(result['ocr_data']['name'])       # Patient name
print(result['triage']['priority'])     # Triage priority
print(result['saved_patient']['id'])    # Database ID
```

### Command Line

```bash
# Process image and get triage prediction
python ocr_module/ocr_triage_integration.py --image report.jpg

# Run demo with sample image
python ocr_module/ocr_triage_integration.py --demo

# Don't save to database
python ocr_module/ocr_triage_integration.py --image report.jpg --no-save
```

## 🧪 Testing

### Generate Test Images

```bash
# Generate a sample report with known values
python ocr_module/test_image_generator.py --sample --output-dir test_images

# Generate multiple test images
python ocr_module/test_image_generator.py --count 10 --output-dir test_images
```

### Test OCR Module

```bash
# Test with sample image
python ocr_module/medical_report_ocr.py test_images/sample_report.jpg

# Test with raw text output
python ocr_module/medical_report_ocr.py test_images/sample_report.jpg --raw-text

# Test with triage format output
python ocr_module/medical_report_ocr.py test_images/sample_report.jpg --triage-format
```

## 📊 Supported Fields

The OCR module extracts the following fields:

| Field | Type | Example |
|-------|------|---------|
| name | string | "John Smith" |
| age | integer | 65 |
| heart_rate | integer | 132 |
| systolic_bp | integer | 170 |
| oxygen | integer | 86 |
| temperature | float | 38.2 |
| respiratory_rate | integer | 25 |
| symptom | string | "Chest Pain" |
| symptom_code | integer | 1 |

### Symptom Code Mapping

| Code | Symptom |
|------|---------|
| 1 | Chest Pain |
| 2 | Breathing Difficulty |
| 3 | Fever |
| 4 | Headache |
| 5 | Injury |
| 6 | Vomiting |
| 7 | Dizziness |

## 🔍 Image Preprocessing Pipeline

1. **Grayscale Conversion**: Reduces color complexity
2. **Gaussian Blur**: Reduces noise (5x5 kernel)
3. **Adaptive Thresholding**: Creates binary image (handles varying lighting)
4. **Morphological Operations**: Removes small artifacts

## 📝 Expected Text Format

The OCR module expects medical reports in this format:

```
Patient Name: John Smith
Age: 65
Heart Rate: 132 bpm
Blood Pressure: 170
Oxygen: 86%
Temperature: 38.2
Respiratory Rate: 25
Symptoms: Chest Pain
```

## ⚙️ Configuration

### Specify Tesseract Path

If Tesseract is not in your system PATH:

```python
# Windows
ocr = MedicalReportOCR(tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe')

# Linux/Mac (if installed in non-standard location)
ocr = MedicalReportOCR(tesseract_cmd='/usr/local/bin/tesseract')
```

### Custom Regex Patterns

You can extend the `MedicalReportOCR` class to customize parsing:

```python
class CustomOCR(MedicalReportOCR):
    def _compile_patterns(self):
        patterns = super()._compile_patterns()
        # Add custom pattern
        patterns['custom_field'] = re.compile(r'Custom:\s*(.+)', re.IGNORECASE)
        return patterns
```

## 🐛 Troubleshooting

### Tesseract Not Found

```
Error: tesseract is not installed or it's not in your PATH
```

**Solution**: Install Tesseract and ensure it's in your PATH, or specify the path:

```python
ocr = MedicalReportOCR(tesseract_cmd='/path/to/tesseract')
```

### Poor OCR Accuracy

**Solutions:**
1. Ensure image is high resolution (300+ DPI)
2. Check image is well-lit and not blurry
3. Try preprocessing the image manually
4. Adjust thresholding parameters in `preprocess_image()`

### Missing Fields in Output

**Solutions:**
1. Check text format matches expected pattern
2. Enable raw text output to see what OCR detected
3. Adjust regex patterns for your document format

## 📈 Performance Tips

1. **Image Quality**: Use high-resolution images (300+ DPI)
2. **Lighting**: Ensure even lighting, avoid shadows
3. **Contrast**: High contrast between text and background
4. **Preprocessing**: The module handles most preprocessing automatically

## 🔒 Security Note

Medical reports contain sensitive patient information. Ensure:
- Images are stored securely
- Data is transmitted over HTTPS in production
- Access is restricted to authorized personnel
- Follow HIPAA/GDPR compliance requirements

## 📄 License

This module is part of the AI Triage System for educational purposes.

## 🤝 Integration Example

```python
# Complete integration example
from ocr_module import MedicalReportOCR
import requests

# 1. Extract data from image
ocr = MedicalReportOCR()
patient_data = ocr.process_image("report.jpg")

# 2. Convert to triage format
triage_input = ocr.to_triage_format(patient_data)

# 3. Send to triage API
response = requests.post(
    "http://localhost:8000/api/predict-triage",
    json=triage_input
)

# 4. Get triage priority
triage_result = response.json()
print(f"Priority: {triage_result['priority']}")
```

---

**Ready to extract patient data from medical reports!** 📄➡️💻
