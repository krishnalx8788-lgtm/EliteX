"""
OCR Router for AI Triage System

This module provides API endpoints for extracting patient data from
medical report images using OCR.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
import tempfile
import os
import shutil
import pytesseract

from ocr_module import MedicalReportOCR

# Configure Tesseract path for Windows (auto-detect default install location)
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Create router
router = APIRouter(prefix="/api/ocr", tags=["ocr"])

# Initialize OCR processor once at module level
ocr_processor = None


def get_ocr_processor() -> MedicalReportOCR:
    """Get or initialize the OCR processor singleton."""
    global ocr_processor
    if ocr_processor is None:
        ocr_processor = MedicalReportOCR()
    return ocr_processor


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}


@router.post("/extract")
async def extract_from_image(file: UploadFile = File(...)):
    """
    Extract patient data from a medical report image using OCR.

    Accepts an uploaded image file, processes it through the OCR pipeline,
    and returns structured patient data ready for the triage system.

    Supported formats: JPG, JPEG, PNG, BMP, TIFF

    Returns:
        Dictionary with extracted patient data fields:
        - name, age, heart_rate, systolic_bp, oxygen,
          temperature, respiratory_rate, symptom, symptom_code
    """
    # Validate file extension
    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Save uploaded file to a temp location
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp_path = tmp.name
            shutil.copyfileobj(file.file, tmp)

        # Run OCR pipeline
        ocr = get_ocr_processor()
        result = ocr.process_image(tmp_path, return_raw_text=True)

        if not result.get("ocr_success"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"OCR extraction failed: {result.get('error', 'Unknown error')}"
            )

        # Convert to triage-ready format and merge with raw parsed data
        triage_data = ocr.to_triage_format(result)

        return {
            "success": True,
            "extracted": {
                "name": result.get("name"),
                "age": result.get("age"),
                "heart_rate": result.get("heart_rate"),
                "systolic_bp": result.get("systolic_bp"),
                "oxygen": result.get("oxygen"),
                "temperature": result.get("temperature"),
                "respiratory_rate": result.get("respiratory_rate"),
                "symptom_text": result.get("symptom"),
                "symptom_code": result.get("symptom_code"),
            },
            "triage_ready": triage_data,
            "fields_extracted": result.get("extracted_fields_count", 0),
            "raw_text": result.get("raw_text"),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing error: {str(e)}"
        )
    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
