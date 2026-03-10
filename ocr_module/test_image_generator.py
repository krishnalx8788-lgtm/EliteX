"""
Test Image Generator for OCR Module

This module generates synthetic medical report images for testing
the OCR functionality. Useful for demo purposes when real medical
reports are not available.

Dependencies:
    - Pillow (PIL)
"""

from PIL import Image, ImageDraw, ImageFont
import random
import os
from typing import Dict, Any, Optional


class MedicalReportImageGenerator:
    """
    Generator for synthetic medical report images.
    
    Creates realistic-looking medical report images with patient data
    for testing OCR functionality.
    
    Example:
        >>> generator = MedicalReportImageGenerator()
        >>> patient_data = generator.generate_random_patient()
        >>> generator.create_report_image(patient_data, "test_report.jpg")
    """
    
    def __init__(self):
        """Initialize the image generator."""
        self.first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily',
            'Robert', 'Lisa', 'William', 'Jennifer', 'James', 'Maria',
            'Thomas', 'Patricia', 'Charles', 'Linda', 'Daniel', 'Barbara'
        ]
        
        self.last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
            'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez',
            'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore'
        ]
        
        self.symptoms = [
            'Chest Pain', 'Breathing Difficulty', 'Fever', 'Headache',
            'Injury', 'Vomiting', 'Dizziness', 'Abdominal Pain',
            'Back Pain', 'Cough', 'Fatigue', 'Nausea'
        ]
    
    def generate_random_patient(self) -> Dict[str, Any]:
        """
        Generate random patient data for testing.
        
        Returns:
            Dictionary with random patient data
        """
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        
        # Generate vitals with some critical values for variety
        is_critical = random.random() < 0.3  # 30% chance of critical
        
        if is_critical:
            # Generate critical values
            heart_rate = random.randint(120, 150)
            systolic_bp = random.randint(160, 180)
            oxygen = random.randint(80, 90)
            temperature = round(random.uniform(38.5, 40.0), 1)
            respiratory_rate = random.randint(24, 30)
        else:
            # Generate normal values
            heart_rate = random.randint(60, 100)
            systolic_bp = random.randint(100, 140)
            oxygen = random.randint(95, 100)
            temperature = round(random.uniform(36.5, 37.5), 1)
            respiratory_rate = random.randint(12, 20)
        
        return {
            'name': f"{first_name} {last_name}",
            'age': random.randint(18, 90),
            'heart_rate': heart_rate,
            'systolic_bp': systolic_bp,
            'oxygen': oxygen,
            'temperature': temperature,
            'respiratory_rate': respiratory_rate,
            'symptom': random.choice(self.symptoms)
        }
    
    def create_report_image(self, 
                           patient_data: Dict[str, Any],
                           output_path: str,
                           add_noise: bool = False) -> str:
        """
        Create a medical report image from patient data.
        
        Args:
            patient_data: Dictionary with patient information
            output_path: Path to save the generated image
            add_noise: If True, add some visual noise for realism
        
        Returns:
            Path to the generated image
        """
        # Create image with white background (larger for better OCR)
        width, height = 800, 700
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Try to load a readable font (Windows → Linux → default)
        font_large = None
        font_medium = None
        font_normal = None
        
        font_paths = [
            # Windows fonts
            ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arial.ttf"),
            # Linux fonts
            ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
        
        for bold_path, medium_path, normal_path in font_paths:
            try:
                font_large = ImageFont.truetype(bold_path, 32)
                font_medium = ImageFont.truetype(medium_path, 24)
                font_normal = ImageFont.truetype(normal_path, 22)
                break
            except (OSError, IOError):
                continue
        
        if font_large is None:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_normal = ImageFont.load_default()
        
        # Draw header
        header_y = 30
        draw.text((width//2 - 150, header_y), 
                 "MEDICAL REPORT", 
                 fill='black', 
                 font=font_large)
        
        # Draw separator line
        draw.line([(50, 80), (width-50, 80)], fill='black', width=2)
        
        # Draw patient data with generous spacing
        y_position = 110
        line_height = 50
        
        fields = [
            ("Patient Name:", patient_data['name']),
            ("Age:", str(patient_data['age'])),
            ("Heart Rate:", f"{patient_data['heart_rate']} bpm"),
            ("Blood Pressure:", str(patient_data['systolic_bp'])),
            ("Oxygen:", f"{patient_data['oxygen']}%"),
            ("Temperature:", str(patient_data['temperature'])),
            ("Respiratory Rate:", str(patient_data['respiratory_rate'])),
            ("Symptoms:", patient_data['symptom'])
        ]
        
        for label, value in fields:
            # Draw label
            draw.text((80, y_position), label, fill='black', font=font_medium)
            
            # Draw value with spacing
            label_width = draw.textlength(label, font=font_medium)
            draw.text((80 + label_width + 20, y_position), value, fill='black', font=font_normal)
            
            y_position += line_height
        
        # Draw footer
        draw.line([(50, height-60), (width-50, height-60)], fill='black', width=1)
        draw.text((width//2 - 100, height-40), 
                 "Hospital Triage System", 
                 fill='gray', 
                 font=font_normal)
        
        # Add some noise if requested (simulates scan artifacts)
        if add_noise:
            pixels = image.load()
            for i in range(width):
                for j in range(height):
                    if random.random() < 0.001:  # 0.1% noise
                        r, g, b = pixels[i, j]
                        noise = random.randint(-10, 10)
                        pixels[i, j] = (
                            max(0, min(255, r + noise)),
                            max(0, min(255, g + noise)),
                            max(0, min(255, b + noise))
                        )
        
        # Save image
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        image.save(output_path, 'JPEG', quality=95)
        
        return output_path
    
    def generate_test_dataset(self, 
                             output_dir: str, 
                             num_images: int = 5) -> list:
        """
        Generate multiple test images.
        
        Args:
            output_dir: Directory to save images
            num_images: Number of images to generate
        
        Returns:
            List of tuples (image_path, patient_data)
        """
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        for i in range(num_images):
            patient_data = self.generate_random_patient()
            image_path = os.path.join(output_dir, f"test_report_{i+1}.jpg")
            self.create_report_image(patient_data, image_path)
            results.append((image_path, patient_data))
        
        return results


def generate_sample_report(output_path: str = "sample_medical_report.jpg") -> str:
    """
    Generate a sample medical report image with known values.
    
    This is useful for testing the OCR module with predictable data.
    
    Args:
        output_path: Path to save the sample image
    
    Returns:
        Path to the generated image
    """
    generator = MedicalReportImageGenerator()
    
    # Sample patient data (known values for testing)
    sample_patient = {
        'name': 'John Smith',
        'age': 65,
        'heart_rate': 132,
        'systolic_bp': 170,
        'oxygen': 86,
        'temperature': 38.2,
        'respiratory_rate': 25,
        'symptom': 'Chest Pain'
    }
    
    generator.create_report_image(sample_patient, output_path)
    print(f"Sample medical report generated: {output_path}")
    print("\nExpected values:")
    for key, value in sample_patient.items():
        print(f"  {key}: {value}")
    
    return output_path


def main():
    """
    Generate test images for OCR module testing.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate test medical report images for OCR testing'
    )
    parser.add_argument(
        '--output-dir',
        default='test_images',
        help='Directory to save generated images'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='Number of test images to generate'
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Generate a single sample report with known values'
    )
    
    args = parser.parse_args()
    
    generator = MedicalReportImageGenerator()
    
    if args.sample:
        # Generate single sample report
        print("=" * 60)
        print("Generating Sample Medical Report")
        print("=" * 60)
        output_path = os.path.join(args.output_dir, "sample_report.jpg")
        generate_sample_report(output_path)
    else:
        # Generate multiple test images
        print("=" * 60)
        print(f"Generating {args.count} Test Medical Reports")
        print("=" * 60)
        
        results = generator.generate_test_dataset(args.output_dir, args.count)
        
        print(f"\nGenerated {len(results)} test images in: {args.output_dir}")
        for image_path, patient_data in results:
            print(f"\n  {image_path}")
            print(f"    Patient: {patient_data['name']}, Age: {patient_data['age']}")


if __name__ == "__main__":
    main()
