import streamlit as st
import zipfile
import os
import pandas as pd
import tempfile
import random
from pathlib import Path

# --- UI CONFIG ---
st.set_page_config(page_title="Compliance Gap Detector", layout="wide")

# --- Title & Description ---
st.markdown("""
<h1 style='text-align: center; color: #00CFFD;'>CyberPulse Compliance Gap Dashboard</h1>
<p style='text-align: center; color: #EDEDED;'>Select frameworks and upload your policy documents to identify gaps.</p>
""", unsafe_allow_html=True)

# --- Select Frameworks First ---
st.markdown("### Select Compliance Framework(s):")

frameworks = [
    "ISO", "NIST 800-53", "HIPAA", "GDPR", "CCPA",
    "PCI-DSS", "CIS", "HITRUST", "NIST CSF", "SCF"
]

col1, col2, col3 = st.columns(3)
selected_frameworks = []

for i, fw in enumerate(frameworks):
    if i % 3 == 0:
        if col1.checkbox(fw): selected_frameworks.append(fw)
    elif i % 3 == 1:
        if col2.checkbox(fw): selected_frameworks.append(fw)
    else:
        if col3.checkbox(fw): selected_frameworks.append(fw)
# --- Upload ZIP File ---
st.markdown("### Upload Your ZIP File")

uploaded_file = st.file_uploader("Upload ZIP File Containing Policy Documents (.zip)", type="zip")

if uploaded_file is not None:

    # Define the target directory
    output_dir = Path("internal_policy")
    output_dir.mkdir(exist_ok=True)

    # Save the uploaded file temporarily
    zip_path = output_dir / "temp_upload.zip"
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())

    # Unzip the file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    zip_path.unlink()
    
    #USE THE CODE THAT TAKES LIST OF FRAMEWORK NAMES AND OUTPUTS CONSISE REPORT HERE
    #consise_report=main_code(selected_frameworks)

# --- Dummy Gap Generator ---
def generate_dummy_gaps():
    gap_examples = [
        "Missing encryption at rest control",
        "No incident response plan defined",
        "Data retention policy incomplete",
        "Unclear access control mechanisms",
        "Inconsistent backup schedule",
        "Unlinked audit log policies",
        "Conflicting role-based access setup",
        "No data breach notification plan",
        "Third-party vendor risk not addressed",
        "Monitoring policies lack clarity"
    ]
    
    statuses = ["Conflicting Control", "Unlinked", "Full Compliance"]
    data = []
    
    for _ in range(10):
        gap = random.choice(gap_examples)
        status = random.choices(statuses, weights=(0.4, 0.4, 0.2))[0]
        link = f"[View]({'#'})"
        data.append((gap, status, link))
        
    return pd.DataFrame(data, columns=["Compliance gap identified", "Status", "Link"])

# --- Display Results ---
if uploaded_file and selected_frameworks:
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)

        st.success("ZIP uploaded and extracted successfully.")


        st.markdown(f"**Frameworks selected:** {', '.join(selected_frameworks)}")

        df = generate_dummy_gaps()
        st.markdown("### Compliance Gap Results")
        st.dataframe(df, use_container_width=True)
elif not uploaded_file:
    st.info("Please upload a ZIP file.")
elif not selected_frameworks:
    st.warning("Please select at least one compliance framework.")
