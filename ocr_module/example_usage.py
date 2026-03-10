"""
OCR Module - Example Usage

This script demonstrates how to use the Medical Report OCR module
to extract patient information from medical report images.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ocr_module import MedicalReportOCR, process_medical_report
from ocr_module.test_image_generator import generate_sample_report
import json


def example_1_basic_usage():
    """
    Example 1: Basic OCR usage with the MedicalReportOCR class.
    """
    print("=" * 70)
    print("EXAMPLE 1: Basic OCR Usage")
    print("=" * 70)
    
    # Generate a sample medical report image
    print("\n1. Generating sample medical report image...")
    image_path = "example_medical_report.jpg"
    generate_sample_report(image_path)
    
    # Initialize OCR processor
    print("\n2. Initializing OCR processor...")
    ocr = MedicalReportOCR()
    
    # Process the image
    print("\n3. Processing image with OCR...")
    result = ocr.process_image(image_path)
    
    # Display results
    print("\n4. Extracted Patient Data:")
    print("-" * 50)
    print(json.dumps(result, indent=2))
    print("-" * 50)
    
    # Clean up
    if os.path.exists(image_path):
        os.remove(image_path)
    
    return result


def example_2_convenience_function():
    """
    Example 2: Using the convenience function for one-off processing.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Convenience Function")
    print("=" * 70)
    
    # Generate sample image
    image_path = "example_report_2.jpg"
    generate_sample_report(image_path)
    
    # Use convenience function
    print("\nProcessing with convenience function...")
    result = process_medical_report(image_path)
    
    print("\nExtracted Data:")
    print(f"  Name: {result.get('name')}")
    print(f"  Age: {result.get('age')}")
    print(f"  Heart Rate: {result.get('heart_rate')}")
    print(f"  Priority Symptom: {result.get('symptom')}")
    
    # Clean up
    if os.path.exists(image_path):
        os.remove(image_path)
    
    return result


def example_3_with_raw_text():
    """
    Example 3: Getting raw OCR text for debugging.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Raw Text Output (for debugging)")
    print("=" * 70)
    
    # Generate sample image
    image_path = "example_report_3.jpg"
    generate_sample_report(image_path)
    
    # Initialize OCR
    ocr = MedicalReportOCR()
    
    # Process with raw text
    print("\nProcessing with raw text output...")
    result = ocr.process_image(image_path, return_raw_text=True)
    
    print("\nRaw OCR Text:")
    print("-" * 50)
    print(result.get('raw_text', 'N/A'))
    print("-" * 50)
    
    print("\nParsed Data:")
    print(f"  Extracted fields: {result.get('extracted_fields_count')}/8")
    
    # Clean up
    if os.path.exists(image_path):
        os.remove(image_path)
    
    return result


def example_4_triage_format():
    """
    Example 4: Converting to triage system format.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Triage System Format Conversion")
    print("=" * 70)
    
    # Generate sample image
    image_path = "example_report_4.jpg"
    generate_sample_report(image_path)
    
    # Initialize OCR
    ocr = MedicalReportOCR()
    
    # Process image
    print("\nProcessing image...")
    ocr_result = ocr.process_image(image_path)
    
    # Convert to triage format
    print("\nConverting to triage format...")
    triage_data = ocr.to_triage_format(ocr_result)
    
    print("\nTriage System Input:")
    print("-" * 50)
    print(json.dumps(triage_data, indent=2))
    print("-" * 50)
    
    print("\nThis data can be sent to the triage prediction API:")
    print("  POST /api/predict-triage")
    print("  Body:", json.dumps(triage_data))
    
    # Clean up
    if os.path.exists(image_path):
        os.remove(image_path)
    
    return triage_data


def example_5_individual_steps():
    """
    Example 5: Using individual processing steps.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Individual Processing Steps")
    print("=" * 70)
    
    # Generate sample image
    image_path = "example_report_5.jpg"
    generate_sample_report(image_path)
    
    # Initialize OCR
    ocr = MedicalReportOCR()
    
    # Step 1: Load image
    print("\nStep 1: Loading image...")
    image = ocr.load_image(image_path)
    print(f"  Image shape: {image.shape}")
    
    # Step 2: Preprocess image
    print("\nStep 2: Preprocessing image...")
    processed = ocr.preprocess_image(image)
    print(f"  Processed shape: {processed.shape}")
    
    # Step 3: Extract text
    print("\nStep 3: Extracting text...")
    text = ocr.extract_text(processed)
    print(f"  Extracted {len(text)} characters")
    
    # Step 4: Parse data
    print("\nStep 4: Parsing patient data...")
    data = ocr.parse_patient_data(text)
    print(f"  Parsed {data.get('extracted_fields_count', 0)} fields")
    
    print("\nFinal Result:")
    print("-" * 50)
    print(json.dumps(data, indent=2))
    print("-" * 50)
    
    # Clean up
    if os.path.exists(image_path):
        os.remove(image_path)
    
    return data


def example_6_error_handling():
    """
    Example 6: Error handling.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Error Handling")
    print("=" * 70)
    
    ocr = MedicalReportOCR()
    
    # Try to process non-existent file
    print("\nTrying to process non-existent file...")
    try:
        result = ocr.process_image("non_existent_file.jpg")
    except FileNotFoundError as e:
        print(f"  Caught FileNotFoundError: {e}")
    
    # Try to process invalid file
    print("\nTrying to process invalid file...")
    try:
        # Create an empty file
        with open("invalid_file.jpg", "w") as f:
            f.write("not an image")
        result = ocr.process_image("invalid_file.jpg")
    except ValueError as e:
        print(f"  Caught ValueError: {e}")
    finally:
        if os.path.exists("invalid_file.jpg"):
            os.remove("invalid_file.jpg")
    
    print("\n✅ Error handling works correctly!")


def main():
    """
    Run all examples.
    """
    print("\n" + "=" * 70)
    print("OCR MODULE - EXAMPLE USAGE")
    print("=" * 70)
    print("\nThis script demonstrates various ways to use the OCR module.")
    print("Each example is self-contained and can be run independently.")
    
    # Run examples
    example_1_basic_usage()
    example_2_convenience_function()
    example_3_with_raw_text()
    example_4_triage_format()
    example_5_individual_steps()
    example_6_error_handling()
    
    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nFor more information, see:")
    print("  - ocr_module/README.md")
    print("  - ocr_module/medical_report_ocr.py")
    print("  - ocr_module/ocr_triage_integration.py")


if __name__ == "__main__":
    main()
