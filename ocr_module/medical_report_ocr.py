"""
Medical Report OCR Module for AI Triage System

This module extracts patient information from medical report images using OCR.
It preprocesses images, extracts text using Tesseract, and parses the data
into structured JSON format for integration with the triage system.

Dependencies:
    - pytesseract
    - opencv-python
    - Pillow
    - numpy

Author: AI Triage System
Version: 1.0.0
"""

import cv2
import pytesseract
import numpy as np
from PIL import Image
import re
import json
from typing import Dict, Optional, Tuple, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalReportOCR:
    """
    OCR processor for extracting patient data from medical report images.
    
    This class handles the complete OCR pipeline:
    1. Image loading and validation
    2. Image preprocessing (grayscale, thresholding, noise reduction)
    3. Text extraction using Tesseract OCR
    4. Data parsing using regex patterns
    5. Structured JSON output
    
    Example:
        >>> ocr = MedicalReportOCR()
        >>> result = ocr.process_image("patient_report.jpg")
        >>> print(result)
        {
            "name": "John Smith",
            "age": 65,
            "heart_rate": 132,
            "systolic_bp": 170,
            "oxygen": 86,
            "temperature": 38.2,
            "respiratory_rate": 25,
            "symptom": "Chest Pain"
        }
    """
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize the OCR processor.
        
        Args:
            tesseract_cmd: Path to Tesseract executable (optional).
                          If not provided, uses system default.
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # Compile regex patterns for better performance
        self.patterns = self._compile_patterns()
        
        logger.info("MedicalReportOCR initialized successfully")
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """
        Compile regex patterns for extracting patient data fields.
        
        Returns:
            Dictionary of compiled regex patterns for each field.
        """
        patterns = {
            # Patient name - captures text after "Patient Name:" or "Name:"
            'name': re.compile(
                r'(?:Patient\s*Name|Name)[:\s]+([A-Za-z\s\.\-]+?)(?=\n|$|Age:)',
                re.IGNORECASE
            ),
            
            # Age - captures numeric value
            'age': re.compile(
                r'Age[:\s]+(\d+)',
                re.IGNORECASE
            ),
            
            # Heart rate - captures numeric value (with optional bpm suffix)
            'heart_rate': re.compile(
                r'Heart\s*Rate[:\s]+(\d+)\s*(?:bpm)?',
                re.IGNORECASE
            ),
            
            # Blood pressure - captures systolic value (first number)
            'systolic_bp': re.compile(
                r'Blood\s*Pressure[:\s]+(\d+)(?:\s*/\s*\d+)?',
                re.IGNORECASE
            ),
            
            # Oxygen level - captures numeric value (with optional % suffix)
            'oxygen': re.compile(
                r'Oxygen[:\s]+(\d+)(?:\s*%)?',
                re.IGNORECASE
            ),
            
            # Temperature - captures numeric value (supports decimal)
            'temperature': re.compile(
                r'Temperature[:\s]+(\d+\.?\d*)',
                re.IGNORECASE
            ),
            
            # Respiratory rate - captures numeric value
            'respiratory_rate': re.compile(
                r'Respiratory\s*Rate[:\s]+(\d+)',
                re.IGNORECASE
            ),
            
            # Symptoms - captures text after symptoms label
            'symptom': re.compile(
                r'Symptoms?[:\s]+([A-Za-z\s\,\-]+?)(?=\n|$)',
                re.IGNORECASE
            )
        }
        
        return patterns
    
    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load an image from file path.
        
        Args:
            image_path: Path to the image file (jpg, png, etc.)
        
        Returns:
            Loaded image as numpy array (BGR format)
        
        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image cannot be loaded
        """
        logger.info(f"Loading image: {image_path}")
        
        # Check if file exists
        import os
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Load image using OpenCV
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"Could not load image: {image_path}. "
                           "Ensure it's a valid image file.")
        
        logger.info(f"Image loaded successfully. Shape: {image.shape}")
        return image
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image to improve OCR accuracy.
        
        Processing steps:
        1. Convert to grayscale
        2. Apply Gaussian blur to reduce noise
        3. Apply adaptive thresholding for binarization
        4. Optional: Denoise using morphological operations
        
        Args:
            image: Input image as numpy array (BGR format)
        
        Returns:
            Preprocessed binary image ready for OCR
        """
        logger.info("Preprocessing image for OCR...")
        
        # Step 1: Convert to grayscale
        # Grayscale reduces complexity and improves OCR accuracy
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        logger.debug("Converted to grayscale")
        
        # Step 2: Apply Gaussian blur to reduce noise
        # This helps remove small artifacts that might confuse OCR
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        logger.debug("Applied Gaussian blur")
        
        # Step 3: Apply adaptive thresholding
        # This creates a binary image where text is clearly separated from background
        # Adaptive thresholding handles varying lighting conditions better than global thresholding
        thresh = cv2.adaptiveThreshold(
            blurred,
            maxValue=255,
            adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            thresholdType=cv2.THRESH_BINARY,
            blockSize=11,  # Size of neighborhood for threshold calculation
            C=2            # Constant subtracted from mean
        )
        logger.debug("Applied adaptive thresholding")
        
        # Step 4: Optional denoising using morphological operations
        # This removes small noise pixels while preserving text structure
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        logger.debug("Applied morphological operations")
        
        logger.info("Image preprocessing complete")
        return processed
    
    def extract_text(self, image: np.ndarray) -> str:
        """
        Extract text from preprocessed image using Tesseract OCR.
        
        Args:
            image: Preprocessed image (grayscale or binary)
        
        Returns:
            Extracted text as string
        
        Raises:
            RuntimeError: If OCR extraction fails
        """
        logger.info("Extracting text using Tesseract OCR...")
        
        try:
            # Configure Tesseract OCR settings
            # --oem 3: Use LSTM neural net engine
            # --psm 6: Assume a single uniform block of text
            custom_config = r'--oem 3 --psm 6'
            
            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # Clean up extracted text
            text = self._clean_extracted_text(text)
            
            logger.info(f"Text extraction complete. Length: {len(text)} characters")
            logger.debug(f"Extracted text:\n{text}")
            
            return text
            
        except Exception as e:
            raise RuntimeError(f"OCR text extraction failed: {str(e)}")
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
        
        Returns:
            Cleaned text
        """
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Collapse multiple spaces within each line (but preserve newlines)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'[ \t]+', ' ', line).strip()
            if line:  # skip empty lines
                cleaned_lines.append(line)
        text = '\n'.join(cleaned_lines)
        
        return text.strip()
    
    def parse_patient_data(self, text: str) -> Dict[str, Any]:
        """
        Parse patient data from extracted text using regex patterns.
        
        Args:
            text: Extracted text from OCR
        
        Returns:
            Dictionary containing parsed patient data
        """
        logger.info("Parsing patient data from extracted text...")
        
        patient_data = {
            'name': None,
            'age': None,
            'heart_rate': None,
            'systolic_bp': None,
            'oxygen': None,
            'temperature': None,
            'respiratory_rate': None,
            'symptom': None
        }
        
        # Extract each field using compiled patterns
        for field, pattern in self.patterns.items():
            match = pattern.search(text)
            if match:
                value = match.group(1).strip()
                
                # Convert to appropriate type
                if field in ['age', 'heart_rate', 'systolic_bp', 'oxygen', 'respiratory_rate']:
                    try:
                        patient_data[field] = int(value)
                    except ValueError:
                        logger.warning(f"Could not convert {field} value to int: {value}")
                        patient_data[field] = value
                
                elif field == 'temperature':
                    try:
                        patient_data[field] = float(value)
                    except ValueError:
                        logger.warning(f"Could not convert {field} value to float: {value}")
                        patient_data[field] = value
                
                else:  # name, symptom (string fields)
                    patient_data[field] = value
                
                logger.debug(f"Extracted {field}: {patient_data[field]}")
            else:
                logger.warning(f"Could not extract {field} from text")
        
        # Map symptom string to symptom code for triage system integration
        patient_data['symptom_code'] = self._map_symptom_to_code(patient_data.get('symptom'))
        
        logger.info("Patient data parsing complete")
        return patient_data
    
    def _map_symptom_to_code(self, symptom_text: Optional[str]) -> Optional[int]:
        """
        Map symptom text to symptom code for triage system integration.
        
        Symptom codes:
            1: Chest Pain
            2: Breathing Difficulty
            3: Fever
            4: Headache
            5: Injury
            6: Vomiting
            7: Dizziness
        
        Args:
            symptom_text: Extracted symptom text
        
        Returns:
            Symptom code (1-7) or None if not recognized
        """
        if not symptom_text:
            return None
        
        symptom_lower = symptom_text.lower()
        
        symptom_mapping = {
            1: ['chest pain', 'chest', 'heart pain', 'angina'],
            2: ['breathing', 'shortness of breath', 'dyspnea', 'respiratory', 'breath'],
            3: ['fever', 'high temperature', 'pyrexia'],
            4: ['headache', 'head pain', 'migraine'],
            5: ['injury', 'trauma', 'wound', 'fracture', 'bleeding'],
            6: ['vomiting', 'nausea', 'throwing up', 'emesis'],
            7: ['dizziness', 'vertigo', 'lightheaded', 'faint']
        }
        
        for code, keywords in symptom_mapping.items():
            if any(keyword in symptom_lower for keyword in keywords):
                return code
        
        # Default to 1 (Chest Pain) if symptom contains "pain"
        if 'pain' in symptom_lower:
            return 1
        
        return None
    
    def process_image(self, image_path: str, return_raw_text: bool = False) -> Dict[str, Any]:
        """
        Complete OCR pipeline: load, preprocess, extract, and parse.
        
        This is the main entry point for processing medical report images.
        
        Args:
            image_path: Path to the medical report image
            return_raw_text: If True, include raw extracted text in output
        
        Returns:
            Dictionary containing parsed patient data
            
        Example:
            >>> ocr = MedicalReportOCR()
            >>> result = ocr.process_image("report.jpg")
            >>> print(json.dumps(result, indent=2))
            {
              "name": "John Smith",
              "age": 65,
              "heart_rate": 132,
              "systolic_bp": 170,
              "oxygen": 86,
              "temperature": 38.2,
              "respiratory_rate": 25,
              "symptom": "Chest Pain",
              "symptom_code": 1
            }
        """
        logger.info(f"Processing image: {image_path}")
        
        try:
            # Step 1: Load image
            image = self.load_image(image_path)
            
            # Step 2: Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Step 3: Extract text
            raw_text = self.extract_text(processed_image)
            
            # Step 4: Parse patient data
            patient_data = self.parse_patient_data(raw_text)
            
            # Add metadata
            patient_data['ocr_success'] = True
            patient_data['extracted_fields_count'] = sum(
                1 for v in patient_data.values() 
                if v is not None and not isinstance(v, bool)
            )
            
            if return_raw_text:
                patient_data['raw_text'] = raw_text
            
            logger.info(f"Image processing complete. "
                       f"Extracted {patient_data['extracted_fields_count']} fields")
            
            return patient_data
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return {
                'ocr_success': False,
                'error': str(e)
            }
    
    def to_triage_format(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert parsed patient data to triage system input format.
        
        Args:
            patient_data: Parsed patient data from OCR
        
        Returns:
            Dictionary formatted for triage prediction API
        """
        # Map OCR field names to triage API field names
        triage_data = {
            'name': patient_data.get('name', 'Unknown'),
            'age': patient_data.get('age', 45),
            'heart_rate': patient_data.get('heart_rate', 75),
            'systolic_bp': patient_data.get('systolic_bp', 120),
            'oxygen': patient_data.get('oxygen', 98),
            'temperature': patient_data.get('temperature', 37.0),
            'respiratory_rate': patient_data.get('respiratory_rate', 16),
            'symptom': patient_data.get('symptom_code', 1)
        }
        
        return triage_data


def process_medical_report(image_path: str, 
                          tesseract_cmd: Optional[str] = None,
                          return_raw_text: bool = False) -> Dict[str, Any]:
    """
    Convenience function to process a medical report image.
    
    This is a simplified interface for one-off OCR processing.
    
    Args:
        image_path: Path to the medical report image
        tesseract_cmd: Path to Tesseract executable (optional)
        return_raw_text: Include raw extracted text in output
    
    Returns:
        Dictionary containing parsed patient data
    
    Example:
        >>> result = process_medical_report("patient_report.jpg")
        >>> print(result['name'])
        'John Smith'
    """
    ocr = MedicalReportOCR(tesseract_cmd=tesseract_cmd)
    return ocr.process_image(image_path, return_raw_text=return_raw_text)


def main():
    """
    Example usage of the Medical Report OCR module.
    
    This demonstrates how to use the OCR module to extract patient data
    from a medical report image and convert it to triage system format.
    """
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Extract patient data from medical report images using OCR'
    )
    parser.add_argument(
        'image_path',
        help='Path to the medical report image (jpg, png)'
    )
    parser.add_argument(
        '--tesseract',
        help='Path to Tesseract executable (if not in PATH)',
        default=None
    )
    parser.add_argument(
        '--raw-text',
        action='store_true',
        help='Include raw extracted text in output'
    )
    parser.add_argument(
        '--triage-format',
        action='store_true',
        help='Output in triage system format'
    )
    
    args = parser.parse_args()
    
    # Process the image
    print("=" * 60)
    print("Medical Report OCR - Patient Data Extraction")
    print("=" * 60)
    print()
    
    try:
        # Initialize OCR processor
        ocr = MedicalReportOCR(tesseract_cmd=args.tesseract)
        
        # Process image
        result = ocr.process_image(
            args.image_path,
            return_raw_text=args.raw_text
        )
        
        if result.get('ocr_success'):
            print("✅ OCR Processing Successful!")
            print()
            
            # Convert to triage format if requested
            if args.triage_format:
                result = ocr.to_triage_format(result)
                print("Triage System Format:")
            else:
                print("Extracted Patient Data:")
            
            print("-" * 40)
            print(json.dumps(result, indent=2))
            print("-" * 40)
            
            # Show extraction summary
            if 'extracted_fields_count' in result:
                print(f"\nFields extracted: {result['extracted_fields_count']}/8")
            
        else:
            print("❌ OCR Processing Failed")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
