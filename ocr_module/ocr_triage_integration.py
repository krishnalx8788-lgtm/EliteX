"""
OCR-Triage System Integration

This module demonstrates how to integrate the OCR module with the AI Triage System.
It provides a complete workflow:
1. Extract patient data from medical report image using OCR
2. Send extracted data to triage API for priority prediction
3. Display results

Usage:
    python ocr_triage_integration.py --image report.jpg
"""

import requests
import json
import argparse
from typing import Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ocr_module import MedicalReportOCR, process_medical_report


class OCRTriageIntegration:
    """
    Integration class connecting OCR module with Triage API.
    
    This class provides a seamless workflow for:
    - Extracting patient data from medical report images
    - Submitting data to the triage prediction API
    - Displaying triage results
    
    Example:
        >>> integration = OCRTriageIntegration()
        >>> result = integration.process_and_triage("report.jpg")
        >>> print(result['triage']['priority'])
        'Critical'
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000/api"):
        """
        Initialize the integration.
        
        Args:
            api_base_url: Base URL for the triage API
        """
        self.api_base_url = api_base_url
        self.ocr = MedicalReportOCR()
        
        # Verify API is accessible
        self._check_api_connection()
    
    def _check_api_connection(self) -> bool:
        """
        Check if the triage API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Triage API connection successful")
                return True
        except requests.exceptions.ConnectionError:
            print("⚠️  Warning: Triage API not accessible at", self.api_base_url)
            print("   Start the backend with: uvicorn backend.main:app --reload")
        except Exception as e:
            print(f"⚠️  Warning: Could not connect to Triage API: {e}")
        
        return False
    
    def extract_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        Extract patient data from medical report image.
        
        Args:
            image_path: Path to the medical report image
        
        Returns:
            Dictionary with extracted patient data
        """
        print("\n" + "=" * 60)
        print("STEP 1: OCR - Extracting Patient Data from Image")
        print("=" * 60)
        
        # Process image with OCR
        ocr_result = self.ocr.process_image(image_path)
        
        if not ocr_result.get('ocr_success'):
            raise Exception(f"OCR failed: {ocr_result.get('error', 'Unknown error')}")
        
        print("\n📄 Extracted Patient Data:")
        print("-" * 40)
        print(f"  Name:              {ocr_result.get('name', 'N/A')}")
        print(f"  Age:               {ocr_result.get('age', 'N/A')}")
        print(f"  Heart Rate:        {ocr_result.get('heart_rate', 'N/A')} bpm")
        print(f"  Blood Pressure:    {ocr_result.get('systolic_bp', 'N/A')} mmHg")
        print(f"  Oxygen Level:      {ocr_result.get('oxygen', 'N/A')}%")
        print(f"  Temperature:       {ocr_result.get('temperature', 'N/A')} °C")
        print(f"  Respiratory Rate:  {ocr_result.get('respiratory_rate', 'N/A')}/min")
        print(f"  Symptoms:          {ocr_result.get('symptom', 'N/A')}")
        print("-" * 40)
        
        return ocr_result
    
    def get_triage_prediction(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get triage prediction from API.
        
        Args:
            patient_data: Patient data dictionary
        
        Returns:
            Triage prediction result
        """
        print("\n" + "=" * 60)
        print("STEP 2: AI Triage - Getting Priority Prediction")
        print("=" * 60)
        
        # Convert to triage API format
        triage_input = self.ocr.to_triage_format(patient_data)
        
        print("\n📤 Sending to Triage API:")
        print(json.dumps(triage_input, indent=2))
        
        try:
            # Call triage prediction API
            response = requests.post(
                f"{self.api_base_url}/predict-triage",
                json=triage_input,
                timeout=10
            )
            
            if response.status_code == 200:
                triage_result = response.json()
                
                print("\n📥 Triage Prediction Result:")
                print("-" * 40)
                print(f"  Priority:           {triage_result.get('priority', 'N/A')}")
                print(f"  Recommended Action: {triage_result.get('recommended_action', 'N/A')}")
                print(f"  Confidence:         {triage_result.get('confidence', 'N/A')}")
                if triage_result.get('alert'):
                    print(f"  ⚠️  ALERT: {triage_result.get('alert')}")
                print("-" * 40)
                
                return triage_result
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            raise Exception("Could not connect to Triage API. Is the backend running?")
        except Exception as e:
            raise Exception(f"Triage prediction failed: {str(e)}")
    
    def save_patient_to_database(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save patient to database via API.
        
        Args:
            patient_data: Patient data dictionary
        
        Returns:
            Saved patient data with ID
        """
        print("\n" + "=" * 60)
        print("STEP 3: Database - Saving Patient Record")
        print("=" * 60)
        
        # Convert to triage API format
        triage_input = self.ocr.to_triage_format(patient_data)
        
        try:
            # Call create patient API
            response = requests.post(
                f"{self.api_base_url}/patients",
                json=triage_input,
                timeout=10
            )
            
            if response.status_code == 201:
                saved_patient = response.json()
                
                print(f"\n💾 Patient saved to database:")
                print(f"  Patient ID: {saved_patient.get('id')}")
                print(f"  Priority:   {saved_patient.get('priority')}")
                
                return saved_patient
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            raise Exception("Could not connect to Triage API. Is the backend running?")
        except Exception as e:
            raise Exception(f"Save patient failed: {str(e)}")
    
    def process_and_triage(self, 
                          image_path: str,
                          save_to_db: bool = True) -> Dict[str, Any]:
        """
        Complete workflow: OCR extraction + Triage prediction + Save to DB.
        
        Args:
            image_path: Path to medical report image
            save_to_db: Whether to save patient to database
        
        Returns:
            Complete result with OCR data, triage prediction, and patient ID
        """
        result = {
            'success': False,
            'ocr_data': None,
            'triage': None,
            'saved_patient': None,
            'error': None
        }
        
        try:
            # Step 1: Extract data from image
            ocr_data = self.extract_from_image(image_path)
            result['ocr_data'] = ocr_data
            
            # Step 2: Get triage prediction
            triage = self.get_triage_prediction(ocr_data)
            result['triage'] = triage
            
            # Step 3: Save to database (optional)
            if save_to_db:
                saved = self.save_patient_to_database(ocr_data)
                result['saved_patient'] = saved
            
            result['success'] = True
            
            # Print summary
            self._print_summary(result)
            
        except Exception as e:
            result['error'] = str(e)
            print(f"\n❌ Error: {str(e)}")
        
        return result
    
    def _print_summary(self, result: Dict[str, Any]):
        """
        Print a summary of the complete workflow.
        
        Args:
            result: Complete workflow result
        """
        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETE - SUMMARY")
        print("=" * 60)
        
        ocr = result.get('ocr_data', {})
        triage = result.get('triage', {})
        saved = result.get('saved_patient', {})
        
        priority = triage.get('priority', 'N/A')
        priority_emoji = {
            'Critical': '🔴',
            'High': '🟠',
            'Medium': '🟡',
            'Low': '🟢'
        }.get(priority, '⚪')
        
        print(f"\n  Patient: {ocr.get('name', 'N/A')} (Age: {ocr.get('age', 'N/A')})")
        print(f"  Priority: {priority_emoji} {priority}")
        print(f"  Confidence: {triage.get('confidence', 'N/A')}")
        
        if saved.get('id'):
            print(f"  Database ID: {saved.get('id')}")
        
        print("\n" + "=" * 60)


def demo_workflow(image_path: Optional[str] = None):
    """
    Run a complete demo of the OCR-Triage integration.
    
    If no image is provided, generates a sample image first.
    
    Args:
        image_path: Path to medical report image (optional)
    """
    print("=" * 60)
    print("AI Triage System - OCR Integration Demo")
    print("=" * 60)
    
    # Generate sample image if none provided
    if image_path is None:
        print("\nGenerating sample medical report image...")
        from ocr_module.test_image_generator import generate_sample_report
        
        image_path = "demo_medical_report.jpg"
        generate_sample_report(image_path)
    
    # Run integration workflow
    integration = OCRTriageIntegration()
    result = integration.process_and_triage(image_path, save_to_db=True)
    
    return result


def main():
    """
    Main entry point for OCR-Triage integration.
    """
    parser = argparse.ArgumentParser(
        description='Extract patient data from medical report image and get triage prediction'
    )
    parser.add_argument(
        '--image',
        help='Path to medical report image',
        default=None
    )
    parser.add_argument(
        '--api-url',
        help='Triage API base URL',
        default='http://localhost:8000/api'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save patient to database'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demo with sample image'
    )
    
    args = parser.parse_args()
    
    if args.demo or args.image is None:
        # Run demo mode
        demo_workflow(args.image)
    else:
        # Run with provided image
        integration = OCRTriageIntegration(api_base_url=args.api_url)
        integration.process_and_triage(args.image, save_to_db=not args.no_save)


if __name__ == "__main__":
    main()
