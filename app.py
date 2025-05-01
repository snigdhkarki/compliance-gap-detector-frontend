import streamlit as st
import zipfile
import os
import pandas as pd
import tempfile
import random
from pathlib import Path
import re
from textwrap import dedent
import plotly.express as px
from collections import Counter

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
    

# --- Dummy Gap Generator ---
# def generate_dummy_gaps():
#     gap_examples = [
#         "Missing encryption at rest control",
#         "No incident response plan defined",
#         "Data retention policy incomplete",
#         "Unclear access control mechanisms",
#         "Inconsistent backup schedule",
#         "Unlinked audit log policies",
#         "Conflicting role-based access setup",
#         "No data breach notification plan",
#         "Third-party vendor risk not addressed",
#         "Monitoring policies lack clarity"
#     ]
    
#     statuses = ["Conflicting Control", "Unlinked", "Full Compliance"]
#     data = []
    
#     for _ in range(10):
#         gap = random.choice(gap_examples)
#         status = random.choices(statuses, weights=(0.4, 0.4, 0.2))[0]
#         link = f"[View]({'#'})"
#         data.append((gap, status, link))
        
#     return pd.DataFrame(data, columns=["Compliance gap identified", "Status", "Link"])

def parse_report(text):
    """
    Parse a text report of the form:
    
    *Requirement*:
    ...
    *Status*: ...
    *Reason*:
    ...
    *Target Policy*: ...
    
    into a list of dicts:
    [
      {
        "Requirement": "...",
        "Status": "...",
        "Reason": "...",
        "Target Policy": "..."
      },
      ...
    ]
    """
    entries = []
    
    # Split on each "*Requirement*:" (skip any leading text)
    blocks = re.split(r'\*Requirement\*:', text)[1:]
    
    for blk in blocks:
        # Requirement: up to *Status*:
        req, rest = re.split(r'\*Status\*:', blk, maxsplit=1)
        
        # Status: up to *Reason*:
        status, rest = re.split(r'\*Reason\*:', rest, maxsplit=1)
        
        # # Reason: up to *Target Policy*:
        # reason, rest = re.split(r'\*Target Policy\*[:]? ', rest, maxsplit=1)
        if '*Target Policy*' in rest:
            reason_text, target_text = re.split(r'\*Target Policy\*[:]? ?', rest, maxsplit=1)
        else:
            reason_text, target_text = rest, '' 
        # Target Policy: up to end of block (or next *Requirement*, but split took care)
        # target = rest
        
        # Clean up whitespace and newlines
        clean = lambda s: dedent(s).strip().replace('\n', ' ').replace('  ', ' ')
        
        entries.append({
            "Requirement": clean(req),
            "Status": clean(status),
            "Reason": clean(reason_text),
            "Target Policy": clean(target_text)
        })
    
    return entries
def normalize_response(value):
    val = value.strip('*').strip().lower()
    if val == 'satisfied':
        return 'Yes'
    elif val == 'not satisfied':
        return 'No'
    elif val == 'missing':
        return 'Miss'
    else:
        return 'Unknown'  # fallback if unexpected input

# --- Display Results ---
if uploaded_file and selected_frameworks:
    print(selected_frameworks)
    #USE THE CODE THAT TAKES LIST OF FRAMEWORK NAMES AND OUTPUTS CONSISE REPORT HERE
    #consise_report=main_code(selected_frameworks)
    consise_report = """
    *Requirement*:
    A business that collects a consumer's personal information shall implement reasonable security procedures and practices appropriate to the nature of the personal information to protect the personal information from unauthorized or illegal access, destruction, use, modification, or disclosure in accordance with Section 1798.81.5.

    *Status*: Not Satisfied

    *Reason*:
    The requirement is not satisfied because the evidence only mentions that the organization has outlined security controls and practices designed to protect sensitive data, but it does not explicitly state that these procedures and practices are reasonable for the nature of the personal information being collected. Additionally, while the text mentions compliance with legal and regulatory obligations, it does not confirm that the business has implemented specific "reasonable" security measures as required by the statute.

    *Target Policy* : It outlines the security controls and 
    practices designed to protect sensitive data and ensure compliance with legal, 
    regulatory, and contractual obligations.


    *Requirement*: For purposes of subdivision (b) of Section 1798.115:
Identify by category or categories the personal information of the consumer that the business disclosed for a business purpose during the applicable period of time by reference to the enumerated category or categories in subdivision (c) that most closely describes the personal information, and provide the categories of persons to whom the consumer's personal information was disclosed for a business purpose during the applicable period of time by reference to the enumerated category or categories in subdivision (c) that most closely describes the personal information disclosed. The business shall disclose the information in a list that is separate from a list generated for the purposes of subparagraph (B). 
 *Status*: Missing 
 *Reason*: 
 The requirement is missing.

     *Requirement*:
    The organization shall provide:

    a) a process for a consumer to request that the business deletes any personal information about the consumer which the business has collected from the consumer;

    b) specific criteria or conditions under which such deletion will occur.

    *Status*: *Not Satisfied*

    *Reason*: 
    The requirement is not satisfied because, although there is a "Request deletion of your personal data" link on the website, it does not clearly outline specific criteria or conditions for when deletion will occur. The phrase "under certain conditions" is vague and does not provide sufficient information about the criteria that need to be met for deletion to take place.

    *Target Policy*: Request deletion of your personal data
    under certain conditions.

    """
    # gap_and_status = [{"gap":"snigdh","status":"lol"}, {"gap":"sussy", "status":"fuhrer"}]
    dict_report = parse_report(consise_report)
    Status_list = [d['Status'] for d in dict_report]
    print(Status_list)
    


    output_list = [normalize_response(val) for val in Status_list]
    print(output_list)
    counts = Counter(output_list)

    # Create DataFrame for plotly
    labels = list(counts.keys())
    values = list(counts.values())

    # Create pie chart
    fig = px.pie(
        names=labels,
        values=values,
        title='Response Distribution',
        color=labels,
        color_discrete_map={'Yes':'green', 'No':'red', 'Miss':'gray'}
    )

    # Display in Streamlit
    st.plotly_chart(fig)



    data = []
    for dic in dict_report:
        data.append((dic["Requirement"], dic["Status"], dic["Reason"], dic["Target Policy"]))


    
    # with tempfile.TemporaryDirectory() as tmp_dir:
    #     file_path = os.path.join(tmp_dir, uploaded_file.name)
    #     with open(file_path, "wb") as f:
    #         f.write(uploaded_file.getbuffer())

    #     with zipfile.ZipFile(file_path, 'r') as zip_ref:
    #         zip_ref.extractall(tmp_dir)

    #     st.success("ZIP uploaded and extracted successfully.")


    #     st.markdown(f"**Frameworks selected:** {', '.join(selected_frameworks)}")

    df = pd.DataFrame(data, columns=["Requirement","Status", "Reason", "Target Policy"])

    st.markdown("### Compliance Gap Results")
    st.dataframe(df, use_container_width=True)
elif not uploaded_file:
    st.info("Please upload a ZIP file.")
elif not selected_frameworks:
    st.warning("Please select at least one compliance framework.")
