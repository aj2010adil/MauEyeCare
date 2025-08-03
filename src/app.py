import streamlit as st
from agent.doctor_agent import DoctorAgent
import pandas as pd
from PIL import Image
import pytesseract
import io

st.title("MauEyeCare - Agentic AI")

st.header("Doctor's Notes")

uploaded_file = st.file_uploader("Upload handwritten note (image):", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Note", use_column_width=True)
    doctor_notes = pytesseract.image_to_string(image)
    st.info("Extracted text from handwriting:")
    st.write(doctor_notes)
else:
    doctor_notes = st.text_area("Or enter doctor's notes here:")

if "inventory_data" not in st.session_state:
    st.session_state["inventory_data"] = pd.DataFrame({
        "Item": ["Eye Drops", "Ointment"],
        "Quantity": [10, 5]
    })

st.subheader("Inventory Table (Editable)")
edited_df = st.data_editor(
    st.session_state["inventory_data"],
    num_rows="dynamic",
    key="inventory_editor"
)
st.session_state["inventory_data"] = edited_df

if st.button("Analyze Notes"):
    agent = DoctorAgent()
    inventory, prescription = agent.analyze_notes(doctor_notes)

    st.success("Agent analyzed the notes.")
    st.subheader("Inventory Management Suggestion")
    st.write(", ".join(inventory))

    st.subheader("Prescription for Patient")
    st.write("\n".join(prescription))