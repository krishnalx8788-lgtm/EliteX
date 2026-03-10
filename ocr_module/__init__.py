"""
OCR Module for AI Triage System

This module provides OCR capabilities for extracting patient data from
medical report images.

Usage:
    from ocr_module import MedicalReportOCR, process_medical_report
    
    # Method 1: Using the class
    ocr = MedicalReportOCR()
    result = ocr.process_image("report.jpg")
    
    # Method 2: Using the convenience function
    result = process_medical_report("report.jpg")
"""

from .medical_report_ocr import MedicalReportOCR, process_medical_report

__all__ = ['MedicalReportOCR', 'process_medical_report']
__version__ = '1.0.0'
