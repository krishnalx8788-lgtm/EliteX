"""
Streamlit Dashboard for AI Triage System

This module provides a web-based dashboard for the AI Triage System,
allowing healthcare workers to:
- Add patients and get AI triage predictions
- View the patient priority queue
- Monitor analytics and statistics
- Receive alerts for critical patients
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# API Configuration
API_BASE_URL = "http://localhost:8000/api"

# Page configuration
st.set_page_config(
    page_title="AI Triage System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .priority-critical {
        background-color: #ff4444;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .priority-high {
        background-color: #ff8800;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .priority-medium {
        background-color: #ffcc00;
        color: black;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .priority-low {
        background-color: #00cc66;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .alert-box {
        background-color: #ff4444;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Symptom mapping
SYMPTOMS = {
    1: "Chest Pain",
    2: "Breathing Difficulty",
    3: "Fever",
    4: "Headache",
    5: "Injury",
    6: "Vomiting",
    7: "Dizziness"
}


def get_priority_color(priority: str) -> str:
    """Get color code for priority level."""
    colors = {
        'Critical': '#ff4444',
        'High': '#ff8800',
        'Medium': '#ffcc00',
        'Low': '#00cc66'
    }
    return colors.get(priority, '#999999')


def get_priority_class(priority: str) -> str:
    """Get CSS class for priority level."""
    classes = {
        'Critical': 'priority-critical',
        'High': 'priority-high',
        'Medium': 'priority-medium',
        'Low': 'priority-low'
    }
    return classes.get(priority, '')


def check_api_status():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def add_patient(patient_data: dict) -> dict:
    """Add a patient to the system via API."""
    try:
        response = requests.post(f"{API_BASE_URL}/patients", json=patient_data, timeout=10)
        if response.status_code == 201:
            return response.json()
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Please ensure the backend is running.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def get_patients() -> list:
    """Get all patients from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/patients", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except:
        return []


def get_patient_queue() -> dict:
    """Get patient queue organized by priority."""
    try:
        response = requests.get(f"{API_BASE_URL}/patients/queue", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None


def get_analytics() -> dict:
    """Get analytics summary from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/summary", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None


def predict_triage(patient_data: dict) -> dict:
    """Get triage prediction without saving patient."""
    try:
        response = requests.post(f"{API_BASE_URL}/predict-triage", json=patient_data, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Please ensure the backend is running.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/hospital.png", width=80)
        st.title("AI Triage System")
        
        # Navigation
        st.markdown("---")
        page = st.radio(
            "Navigation",
            ["🏥 Patient Intake", "📷 Scan Report", "📋 Priority Queue", "📊 Analytics"],
            index=0
        )
        
        st.markdown("---")
        
        # API Status
        if check_api_status():
            st.success("🟢 API Connected")
        else:
            st.error("🔴 API Disconnected")
            st.info("Start backend: `uvicorn backend.main:app --reload`")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        AI-powered emergency triage system that helps hospitals 
        prioritize patients based on vital signs and symptoms.
        
        **Priority Levels:**
        - 🔴 Critical: Immediate treatment
        - 🟠 High: Very urgent
        - 🟡 Medium: Needs treatment soon
        - 🟢 Low: Non-urgent
        """)
        
        return page


def render_patient_intake():
    """Render the patient intake form."""
    st.markdown('<div class="main-header">🏥 Patient Intake</div>', unsafe_allow_html=True)
    
    # Check for OCR auto-fill data
    ocr_data = st.session_state.get('ocr_autofill', {})
    if ocr_data:
        st.success("✅ Form pre-filled from scanned medical report. Review and submit.")
        if st.button("Clear OCR Data"):
            del st.session_state['ocr_autofill']
            st.rerun()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="sub-header">Patient Information</div>', unsafe_allow_html=True)
        
        with st.form("patient_form"):
            name = st.text_input("Patient Name", value=ocr_data.get('name', ''), placeholder="Enter patient name")
            
            col_age, col_symptom = st.columns(2)
            with col_age:
                default_age = ocr_data.get('age', 45)
                default_age = max(18, min(90, default_age)) if isinstance(default_age, int) else 45
                age = st.number_input("Age", min_value=18, max_value=90, value=default_age)
            with col_symptom:
                # Determine default symptom index from OCR data
                default_symptom_idx = 0
                ocr_symptom_code = ocr_data.get('symptom_code')
                if ocr_symptom_code and ocr_symptom_code in SYMPTOMS:
                    symptom_values = list(SYMPTOMS.values())
                    default_symptom_idx = symptom_values.index(SYMPTOMS[ocr_symptom_code])
                symptom_name = st.selectbox(
                    "Symptom",
                    options=list(SYMPTOMS.values()),
                    index=default_symptom_idx
                )
                symptom = [k for k, v in SYMPTOMS.items() if v == symptom_name][0]
            
            st.markdown("---")
            st.markdown("**Vital Signs**")
            
            col_hr, col_bp = st.columns(2)
            with col_hr:
                default_hr = ocr_data.get('heart_rate', 75)
                default_hr = max(60, min(150, default_hr)) if isinstance(default_hr, int) else 75
                heart_rate = st.number_input("Heart Rate (bpm)", min_value=60, max_value=150, value=default_hr)
            with col_bp:
                default_bp = ocr_data.get('systolic_bp', 120)
                default_bp = max(90, min(180, default_bp)) if isinstance(default_bp, int) else 120
                systolic_bp = st.number_input("Systolic BP", min_value=90, max_value=180, value=default_bp)
            
            col_o2, col_temp = st.columns(2)
            with col_o2:
                default_o2 = ocr_data.get('oxygen', 98)
                default_o2 = max(80, min(100, default_o2)) if isinstance(default_o2, int) else 98
                oxygen = st.number_input("Oxygen Saturation (%)", min_value=80, max_value=100, value=default_o2)
            with col_temp:
                default_temp = ocr_data.get('temperature', 37.0)
                default_temp = max(36.0, min(40.0, float(default_temp))) if default_temp else 37.0
                temperature = st.number_input("Temperature (°C)", min_value=36.0, max_value=40.0, value=default_temp, step=0.1)
            
            default_rr = ocr_data.get('respiratory_rate', 16)
            default_rr = max(12, min(30, default_rr)) if isinstance(default_rr, int) else 16
            respiratory_rate = st.number_input("Respiratory Rate", min_value=12, max_value=30, value=default_rr)
            
            st.markdown("---")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                analyze_only = st.form_submit_button("🔍 Analyze Only", type="secondary")
            with col_btn2:
                submit_add = st.form_submit_button("➕ Add Patient", type="primary")
        
        # Handle form submission
        if analyze_only or submit_add:
            if not name:
                st.error("Please enter patient name")
                return
            
            # Clear OCR data after submitting
            if 'ocr_autofill' in st.session_state:
                del st.session_state['ocr_autofill']
            
            patient_data = {
                "name": name,
                "age": age,
                "heart_rate": heart_rate,
                "systolic_bp": systolic_bp,
                "oxygen": oxygen,
                "temperature": temperature,
                "respiratory_rate": respiratory_rate,
                "symptom": symptom
            }
            
            if analyze_only:
                result = predict_triage(patient_data)
                if result:
                    st.session_state['last_prediction'] = result
                    st.session_state['last_patient'] = patient_data
            else:
                result = add_patient(patient_data)
                if result:
                    st.success(f"✅ Patient '{name}' added successfully!")
                    st.session_state['last_prediction'] = {
                        'priority': result['priority'],
                        'recommended_action': result['priority'],  # Will be mapped below
                        'confidence': result.get('confidence'),
                        'alert': None
                    }
                    # Get full prediction details
                    pred = predict_triage(patient_data)
                    if pred:
                        st.session_state['last_prediction'] = pred
    
    # Display prediction results
    with col2:
        st.markdown('<div class="sub-header">AI Triage Result</div>', unsafe_allow_html=True)
        
        if 'last_prediction' in st.session_state:
            result = st.session_state['last_prediction']
            priority = result['priority']
            
            # Priority display
            priority_colors = {
                'Critical': '🔴',
                'High': '🟠',
                'Medium': '🟡',
                'Low': '🟢'
            }
            
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem; background-color: #f8f9fa; border-radius: 1rem;">
                <h3>Priority Level</h3>
                <div class="{get_priority_class(priority)}">
                    {priority_colors.get(priority, '⚪')} {priority.upper()}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Alert for critical patients
            if result.get('alert'):
                st.markdown(f'<div class="alert-box">{result["alert"]}</div>', unsafe_allow_html=True)
            
            # Recommended action
            actions = {
                'Critical': 'Immediate ICU evaluation - Life-threatening condition',
                'High': 'Urgent care required within 15 minutes',
                'Medium': 'Treatment needed within 1 hour',
                'Low': 'Routine care - Can wait for standard appointment'
            }
            
            st.markdown("**Recommended Action:**")
            st.info(actions.get(priority, 'Consult medical professional'))
            
            # Confidence score
            if result.get('confidence'):
                st.markdown("**AI Confidence:**")
                st.progress(result['confidence'], text=f"{result['confidence']*100:.1f}%")
            
            # Vital signs summary
            if 'last_patient' in st.session_state:
                patient = st.session_state['last_patient']
                st.markdown("---")
                st.markdown("**Patient Vital Signs Summary:**")
                
                # Create gauge charts for vital signs
                fig = go.Figure()
                
                # Add gauges for key vitals
                fig.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=patient['oxygen'],
                    title={'text': "Oxygen %"},
                    domain={'row': 0, 'column': 0},
                    gauge={'axis': {'range': [80, 100]},
                           'bar': {'color': "darkblue"},
                           'steps': [
                               {'range': [80, 88], 'color': "red"},
                               {'range': [88, 92], 'color': "orange"},
                               {'range': [92, 100], 'color': "green"}]
                           }
                ))
                
                fig.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=patient['heart_rate'],
                    title={'text': "Heart Rate"},
                    domain={'row': 0, 'column': 1},
                    gauge={'axis': {'range': [60, 150]},
                           'bar': {'color': "darkblue"},
                           'steps': [
                               {'range': [60, 110], 'color': "green"},
                               {'range': [110, 130], 'color': "orange"},
                               {'range': [130, 150], 'color': "red"}]
                           }
                ))
                
                fig.update_layout(grid={'rows': 1, 'columns': 2}, height=250)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Enter patient information and click 'Analyze' or 'Add Patient' to see AI triage results.")


def render_priority_queue():
    """Render the patient priority queue."""
    st.markdown('<div class="main-header">📋 Patient Priority Queue</div>', unsafe_allow_html=True)
    
    # Auto-refresh option
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=False)
    with col2:
        if st.button("🔄 Refresh Now"):
            st.rerun()
    with col3:
        if st.button("🗑️ Clear All Patients"):
            # This would need a delete all endpoint - for now just info
            st.info("Use API to delete patients individually")
    
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Fetch patient queue
    queue = get_patient_queue()
    
    if queue and queue.get('total', 0) > 0:
        # Summary metrics
        st.markdown("---")
        cols = st.columns(4)
        
        metrics = [
            ("🔴 Critical", queue.get('critical', []), '#ff4444'),
            ("🟠 High", queue.get('high', []), '#ff8800'),
            ("🟡 Medium", queue.get('medium', []), '#ffcc00'),
            ("🟢 Low", queue.get('low', []), '#00cc66')
        ]
        
        for col, (label, patients, color) in zip(cols, metrics):
            with col:
                count = len(patients)
                st.markdown(f"""
                <div style="background-color: {color}; padding: 1rem; border-radius: 0.5rem; text-align: center; color: white;">
                    <h3>{label}</h3>
                    <h2>{count}</h2>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Display patients by priority
        priority_order = [
            ('critical', '🔴 CRITICAL - Immediate Attention', '#ffebee'),
            ('high', '🟠 HIGH - Urgent', '#fff3e0'),
            ('medium', '🟡 MEDIUM - Soon', '#fffde7'),
            ('low', '🟢 LOW - Routine', '#e8f5e9')
        ]
        
        for key, title, bg_color in priority_order:
            patients = queue.get(key, [])
            if patients:
                st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                    <h3>{title}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                for i, patient in enumerate(patients, 1):
                    with st.expander(f"{i}. {patient['name']} (Age: {patient['age']})"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Vital Signs:**")
                            st.write(f"- Heart Rate: {patient['heart_rate']} bpm")
                            st.write(f"- BP: {patient['systolic_bp']} mmHg")
                            st.write(f"- Oxygen: {patient['oxygen']}%")
                        with col2:
                            st.write(f"- Temperature: {patient['temperature']}°C")
                            st.write(f"- Respiratory: {patient['respiratory_rate']}/min")
                            st.write(f"- Symptom: {SYMPTOMS.get(patient['symptom'], 'Unknown')}")
                        
                        if patient.get('confidence'):
                            st.progress(patient['confidence'], text=f"AI Confidence: {patient['confidence']*100:.1f}%")
                        
                        st.caption(f"Added: {patient.get('created_at', 'N/A')}")
    else:
        st.info("No patients in queue. Add patients from the Patient Intake page.")


def render_analytics():
    """Render the analytics dashboard."""
    st.markdown('<div class="main-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Fetch analytics
    analytics = get_analytics()
    patients = get_patients()
    
    if analytics and analytics.get('total_patients', 0) > 0:
        # Summary cards
        st.markdown("---")
        cols = st.columns(4)
        
        with cols[0]:
            st.metric("Total Patients", analytics['total_patients'])
        with cols[1]:
            st.metric("Critical Patients", analytics['critical_count'], 
                     delta=f"{analytics['critical_percentage']:.1f}%")
        with cols[2]:
            st.metric("Average Age", f"{analytics['average_age']:.1f}")
        with cols[3]:
            non_critical = analytics['total_patients'] - analytics['critical_count']
            st.metric("Non-Critical", non_critical)
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Priority Distribution")
            
            # Pie chart for priority distribution
            priority_data = {
                'Priority': ['Critical', 'High', 'Medium', 'Low'],
                'Count': [
                    analytics['critical_count'],
                    analytics['high_count'],
                    analytics['medium_count'],
                    analytics['low_count']
                ]
            }
            df_priority = pd.DataFrame(priority_data)
            
            fig_pie = px.pie(
                df_priority, 
                values='Count', 
                names='Priority',
                color='Priority',
                color_discrete_map={
                    'Critical': '#ff4444',
                    'High': '#ff8800',
                    'Medium': '#ffcc00',
                    'Low': '#00cc66'
                }
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown("### Priority Breakdown")
            
            # Bar chart
            fig_bar = px.bar(
                df_priority,
                x='Priority',
                y='Count',
                color='Priority',
                color_discrete_map={
                    'Critical': '#ff4444',
                    'High': '#ff8800',
                    'Medium': '#ffcc00',
                    'Low': '#00cc66'
                }
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Age distribution
        if patients:
            st.markdown("---")
            st.markdown("### Age Distribution by Priority")
            
            df_patients = pd.DataFrame(patients)
            
            fig_age = px.box(
                df_patients,
                x='priority',
                y='age',
                color='priority',
                color_discrete_map={
                    'Critical': '#ff4444',
                    'High': '#ff8800',
                    'Medium': '#ffcc00',
                    'Low': '#00cc66'
                }
            )
            fig_age.update_layout(showlegend=False)
            st.plotly_chart(fig_age, use_container_width=True)
            
            # Vital signs analysis
            st.markdown("---")
            st.markdown("### Vital Signs Analysis")
            
            col_v1, col_v2 = st.columns(2)
            
            with col_v1:
                # Oxygen levels by priority
                fig_o2 = px.scatter(
                    df_patients,
                    x='age',
                    y='oxygen',
                    color='priority',
                    color_discrete_map={
                        'Critical': '#ff4444',
                        'High': '#ff8800',
                        'Medium': '#ffcc00',
                        'Low': '#00cc66'
                    },
                    title='Oxygen Saturation by Age and Priority',
                    size='heart_rate',
                    hover_data=['name']
                )
                st.plotly_chart(fig_o2, use_container_width=True)
            
            with col_v2:
                # Heart rate distribution
                fig_hr = px.histogram(
                    df_patients,
                    x='heart_rate',
                    color='priority',
                    color_discrete_map={
                        'Critical': '#ff4444',
                        'High': '#ff8800',
                        'Medium': '#ffcc00',
                        'Low': '#00cc66'
                    },
                    title='Heart Rate Distribution',
                    nbins=20
                )
                st.plotly_chart(fig_hr, use_container_width=True)
    else:
        st.info("No data available for analytics. Add patients to see statistics.")


def render_ocr_upload():
    """Render the OCR report scanning page."""
    st.markdown('<div class="main-header">📷 Scan Medical Report</div>', unsafe_allow_html=True)
    st.markdown(
        "Upload a medical report image to automatically extract patient data "
        "and pre-fill the intake form."
    )
    
    st.markdown("---")
    
    uploaded_file = st.file_uploader(
        "Upload Medical Report Image",
        type=["jpg", "jpeg", "png", "bmp", "tiff"],
        help="Supported formats: JPG, JPEG, PNG, BMP, TIFF"
    )
    
    if uploaded_file is not None:
        # Show the uploaded image
        col_img, col_result = st.columns([1, 1])
        
        with col_img:
            st.markdown('<div class="sub-header">Uploaded Image</div>', unsafe_allow_html=True)
            st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)
        
        with col_result:
            st.markdown('<div class="sub-header">Extracted Data</div>', unsafe_allow_html=True)
            
            # Process button
            if st.button("🔍 Extract Patient Data", type="primary", use_container_width=True):
                with st.spinner("Processing image with OCR..."):
                    try:
                        # Send image to backend OCR endpoint
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        response = requests.post(
                            f"{API_BASE_URL}/ocr/extract",
                            files=files,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state['ocr_result'] = data
                            st.success(f"✅ Extracted {data.get('fields_extracted', 0)} fields successfully!")
                        else:
                            error_detail = response.json().get('detail', 'Unknown error')
                            st.error(f"❌ OCR failed: {error_detail}")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to API. Please ensure the backend is running.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            # Display extracted results
            if 'ocr_result' in st.session_state:
                result = st.session_state['ocr_result']
                extracted = result.get('extracted', {})
                
                st.markdown("---")
                
                # Show extracted fields in a clean format
                fields = [
                    ("👤 Name", extracted.get('name', 'Not detected')),
                    ("📅 Age", extracted.get('age', 'Not detected')),
                    ("❤️ Heart Rate", f"{extracted.get('heart_rate', 'N/A')} bpm"),
                    ("🩸 Systolic BP", f"{extracted.get('systolic_bp', 'N/A')} mmHg"),
                    ("💨 Oxygen", f"{extracted.get('oxygen', 'N/A')}%"),
                    ("🌡️ Temperature", f"{extracted.get('temperature', 'N/A')} °C"),
                    ("🫁 Respiratory Rate", f"{extracted.get('respiratory_rate', 'N/A')}/min"),
                    ("🩺 Symptom", extracted.get('symptom_text', 'Not detected')),
                ]
                
                for label, value in fields:
                    st.markdown(f"**{label}:** {value}")
                
                # Show raw text in an expander
                if result.get('raw_text'):
                    with st.expander("📄 Raw OCR Text"):
                        st.text(result['raw_text'])
                
                st.markdown("---")
                
                # Button to auto-fill intake form
                if st.button("➡️ Use Data in Patient Intake", type="primary", use_container_width=True):
                    st.session_state['ocr_autofill'] = extracted
                    st.session_state['selected_page'] = '🏥 Patient Intake'
                    # Clear OCR result after transferring
                    if 'ocr_result' in st.session_state:
                        del st.session_state['ocr_result']
                    st.rerun()
    else:
        # Placeholder when no image is uploaded
        st.info("👆 Upload a medical report image to get started. The OCR system will extract patient data automatically.")


def main():
    """Main function to run the dashboard."""
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Override page if redirected from OCR
    if st.session_state.get('selected_page'):
        page = st.session_state.pop('selected_page')
    
    # Render appropriate page
    if "Patient Intake" in page:
        render_patient_intake()
    elif "Scan Report" in page:
        render_ocr_upload()
    elif "Priority Queue" in page:
        render_priority_queue()
    elif "Analytics" in page:
        render_analytics()


if __name__ == "__main__":
    main()
