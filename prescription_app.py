import streamlit as st
import requests
import datetime
from streamlit_searchbox import st_searchbox

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8001" # Assuming the backend runs on port 8001

st.set_page_config(page_title="MauEyeCare Prescription Writer", layout="wide")

# --- Helper Functions ---
def search_medicines(search_term: str) -> list[str]:
    """Callback to search for medicines via API."""
    if not search_term:
        return []
    try:
        res = requests.get(f"{API_BASE_URL}/api/inventory/medicines", params={"q": search_term})
        res.raise_for_status()
        data = res.json()
        return [f"{item['name']} ({item['strength']})" for item in data]
    except requests.RequestException as e:
        st.error(f"API Error: {e}")
        return []

def search_spectacles(search_term: str) -> list[str]:
    """Callback to search for spectacles via API."""
    if not search_term:
        return []
    try:
        res = requests.get(f"{API_BASE_URL}/api/inventory/spectacles", params={"q": search_term})
        res.raise_for_status()
        data = res.json()
        return [f"{item['brand']} {item['model_name']}" for item in data]
    except requests.RequestException as e:
        st.error(f"API Error: {e}")
        return []

def generate_ai_suggestions(notes: str) -> str:
    """Placeholder for a call to a LangChain agent."""
    if not notes:
        return ""
    # In a real implementation, this would call the LangChain agent.
    # For this example, we'll use simple keyword matching.
    suggestions = []
    if "dry eye" in notes.lower():
        suggestions.append("*   **Medicine**: Cyclosporine 0.05% Ophthalmic Emulsion, 1 drop in each eye twice daily.")
    if "conjunctivitis" in notes.lower():
        suggestions.append("*   **Medicine**: Moxifloxacin 0.5% Eye Drops, 1 drop in the affected eye 3 times a day for 7 days.")
    if "blurry vision" in notes.lower() or "new glasses" in notes.lower():
        suggestions.append("*   **Spectacles**: Consider new single-vision or progressive lenses based on refraction results.")
    
    if not suggestions:
        return "No specific suggestions found based on notes."
        
    return "### AI Suggestions\n" + "\n".join(suggestions)

def generate_pdf(prescription_data):
    """Placeholder for PDF generation. Returns bytes."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Header
    pdf.cell(0, 10, "MauEyeCare Clinic", 0, 1, "C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "123 Vision St, Optometry City | (555) 123-4567", 0, 1, "C")
    pdf.ln(10)

    # Patient Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Prescription for: {prescription_data['patient_name']}", 0, 1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Date: {prescription_data['date']}", 0, 1)
    pdf.ln(5)

    # Content
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Details:", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 5, prescription_data['markdown_text'])
    
    return pdf.output(dest='S').encode('latin1')

# --- Main UI ---
st.title("📝 Prescription Writer")

if 'prescription_text' not in st.session_state:
    st.session_state.prescription_text = ""

col1, col2 = st.columns(2)

with col1:
    st.header("Patient & Visit Details")
    patient_name = st.text_input("Patient Name", "John Doe")
    visit_date = st.date_input("Visit Date", datetime.date.today())

    st.header("Doctor's Notes")
    doctor_notes = st.text_area("Enter clinical notes here...", height=200, key="doctor_notes")

    if st.button("🤖 Generate AI Suggestions"):
        with st.spinner("Thinking..."):
            suggestions = generate_ai_suggestions(doctor_notes)
            st.session_state.prescription_text += "\n\n" + suggestions

with col2:
    st.header("Add to Prescription")
    
    # Medicine Selection
    with st.expander("💊 Add Medicine", expanded=True):
        selected_medicine = st_searchbox(search_medicines, key="medicine_search")
        med_dosage = st.text_input("Dosage/Frequency", "1 drop 3x daily")
        med_duration = st.text_input("Duration", "7 days")
        if st.button("Add Medicine", key="add_med"):
            if selected_medicine:
                st.session_state.prescription_text += f"\n*   **Medicine**: {selected_medicine}\n    *   **Instructions**: {med_dosage} for {med_duration}."

    # Spectacle Selection
    with st.expander("👓 Add Spectacles", expanded=True):
        selected_spectacle = st_searchbox(search_spectacles, key="spectacle_search")
        lens_details = st.text_input("Lens Details", "Single Vision, Anti-Glare Coating")
        if st.button("Add Spectacles", key="add_spec"):
            if selected_spectacle:
                st.session_state.prescription_text += f"\n*   **Spectacles**: {selected_spectacle}\n    *   **Lenses**: {lens_details}."

st.divider()

st.header("Final Prescription")
final_text = st.text_area("Edit prescription markdown here", value=st.session_state.prescription_text, height=400, key="final_text_area")

st.subheader("Preview")
st.markdown(final_text)

st.divider()

if st.button("Generate Final Prescription PDF", type="primary"):
    if not final_text:
        st.warning("Prescription is empty.")
    else:
        prescription_data = {
            "patient_name": patient_name,
            "date": visit_date.strftime("%Y-%m-%d"),
            "markdown_text": final_text
        }
        pdf_bytes = generate_pdf(prescription_data)
        st.success("PDF Generated!")
        
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"Prescription_{patient_name.replace(' ', '_')}_{visit_date}.pdf",
            mime="application/pdf"
        )