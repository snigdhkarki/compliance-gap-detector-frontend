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
    blocks = re.split(r'\**Requirement\**:', text)[1:]
    
    for blk in blocks:
        # Requirement: up to *Status*:
        req, rest = re.split(r'\**Status\**:', blk, maxsplit=1)
        
        # Status: up to *Reason*:
        status, rest = re.split(r'\**Reason\**:', rest, maxsplit=1)
        
        # # Reason: up to *Target Policy*:
        # reason, rest = re.split(r'\*Target Policy\*[:]? ', rest, maxsplit=1)
        if '*Target Policy*' in rest:
            reason_text, target_text = re.split(r'\**Target Policy\**[:]? ?', rest, maxsplit=1)
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
    consise_report_ccpa = """
**Requirement**:

 A business that controls the collection of a consumer's personal information shall, at or before the point of collection, inform consumers of the following:
(1) The categories of personal information to be collected and the purposes for which the categories of personal information are collected or used and whether that information is sold or shared. A business shall not collect additional categories of personal information or use personal information collected for additional purposes that are incompatible with the disclosed purpose for which the personal information was collected without providing the consumer with notice consistent with this section.
(2) If the business collects sensitive personal information, the categories of sensitive personal information to be collected and the purposes for which the categories of sensitive personal information are collected or used, and whether that information is sold or shared. A business shall not collect additional categories of sensitive personal information or use sensitive personal information collected for additional purposes that are incompatible with the disclosed purpose for which the sensitive personal information was collected without providing the consumer with notice consistent with this section.
(3) The length of time the business intends to retain each category of personal information, including sensitive personal information, or if that is not possible, the criteria used to determine that period provided that a business shall not retain a consumer's personal information or sensitive personal information for each disclosed purpose for which the personal information was collected for longer than is reasonably necessary for that disclosed purpose. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

 A business that, acting as a third party, controls the collection of personal information about a consumer may satisfy its obligation under subdivision (a) by providing the required information prominently and conspicuously on the homepage of its internet website. In addition, if a business acting as a third party controls the collection of personal information about a consumer on its premises, including in a vehicle, then the business shall, at or before the point of collection, inform consumers as to the categories of personal information to be collected and the purposes for which the categories of personal information are used, and whether that personal information is sold, in a clear and conspicuous manner at the location. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

 A business' collection, use, retention, and sharing of a consumer's personal information shall be reasonably necessary and proportionate to achieve the purposes for which the personal information was collected or processed, or for another disclosed purpose that is compatible with the context in which the personal information was collected, and not further processed in a manner that is incompatible with those purposes. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

A business that collects a consumer's personal information and that sells that personal information to, or shares it with, a third party or that discloses it to a service provider or contractor for a business purpose shall enter into an agreement with the third party, service provider, or contractor, that:

(1) Specifies that the personal information is sold or disclosed by the business only for limited and specified purposes.
(2) Obligates the third party, service provider, or contractor to comply with applicable obligations under this title and obligate those persons to provide the same level of privacy protection as is required by this title.
(3) Grants the business rights to take reasonable and appropriate steps to help ensure that the third party, service provider, or contractor uses the personal information transferred in a manner consistent with the business' obligations under this title.
(4) Requires the third party, service provider, or contractor to notify the business if it makes a determination that it can no longer meet its obligations under this title.
(5) Grants the business the right, upon notice, including under paragraph (4), to take reasonable and appropriate steps to stop and remediate unauthorized use of personal information.

**Status**: Not Satisfied

**Reason**:

* The evidence only shows that contracts with third-party service providers include provisions for encryption and data protection in alignment with a policy. This does not necessarily mean that the agreements specify that the personal information is sold or disclosed by the business only for limited and specified purposes (requirement 1).
* While the presence of privacy protection requirements (requirements 2-5) is noted, it is unclear if these requirements are comprehensive enough to ensure compliance with applicable obligations under this title.
* The evidence does not explicitly confirm that all identified requirements will be addressed through the information security management system.

**Target Policy**: ●​ Contracts with third-party service providers must include provisions for encryption 
and data protection in alignment with this policy.




**Requirement**:
A business that collects a consumer's personal information shall implement reasonable security procedures and practices appropriate to the nature of the personal information to protect the personal information from unauthorized or illegal access, destruction, use, modification, or disclosure in accordance with Section 1798.81.5.

**Status**: 
Not Satisfied

**Reason**: 
The requirement is not satisfied because, although the evidence mentions "security controls and practices designed to protect sensitive data", it does not explicitly state that these measures are reasonable given the nature of the personal information being collected. The language used in the regulation emphasizes the need for "reasonable" security procedures, which implies a level of proportionality and adequacy to the type of personal information being handled.

**Target Policy**: It outlines the security controls and 
practices designed to protect sensitive data and ensure compliance with legal, 
regulatory, and contractual obligations.




**Requirement**:

 Nothing in this section shall require a business to disclose trade secrets, as specified in regulations adopted pursuant to paragraph (3) of subdivision (a) of Section 1798.185. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:
The organization shall provide:

a) a process for a consumer to request that the business deletes any personal information about the consumer which the business has collected from the consumer;

b) specific criteria or conditions under which such deletion will occur.

**Status**: **Not Satisfied**

**Reason**: 
The requirement is not satisfied because, although there is a "Request deletion of your personal data" link on the website, it does not clearly outline specific criteria or conditions for when deletion will occur. The phrase "under certain conditions" is vague and does not provide sufficient information about the criteria that need to be met for deletion to take place.

**Target Policy**: Request deletion of your personal data
under certain conditions.

**Requirement**:
The organization shall ensure that workforce members are trained to:

a) recognize a potential incident;
b) report such an incident.

**Status**: **Satisfied**

**Reason**:

* The requirement is satisfied because the evidence states that "Regular training will be conducted for employees, contractors, and partners to recognize potential incidents and respond appropriately." This suggests that the organization has taken concrete steps to train its workforce members on incident recognition and reporting.
* Although the text does not explicitly mention reporting incidents to a specific person or entity, it implies that training is being provided to equip workforce members with the necessary skills to take action in case of an incident.

**Target Policy**: ●​ Training and Awareness: Regular training will be conducted for employees, 
contractors, and partners to recognize potential incidents and respond 
appropriately.





    """

    consise_report_gdrp = '''

    **Requirement**:

 Processing of personal data relating to criminal convictions and offences or related security measures based on Article 6(1) shall be carried out only under the control of official authority or when the processing is authorised by Union or Member State law providing for appropriate safeguards for the rights and freedoms of data subjects. Any comprehensive register of criminal convictions shall be kept only under the control of official authority. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

 If the purposes for which a controller processes personal data do not or do no longer require the identification of a data subject by the controller, the controller shall not be obliged to maintain, acquire or process additional information in order to identify the data subject for the sole purpose of complying with this Regulation. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

 Where, in cases referred to in paragraph 1 of this Article, the controller is able to demonstrate that it is not in a position to identify the data subject, the controller shall inform the data subject accordingly, if possible. In such cases, Articles 15 to 20 shall not apply except where the data subject, for the purpose of exercising his or her rights under those articles, provides additional information enabling his or her identification. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

 The controller shall take appropriate measures to provide any information referred to in Articles 13 and 14 and any communication under Articles 15 to 22 and 34 relating to processing to the data subject in a concise, transparent, intelligible and easily accessible form, using clear and plain language, in particular for any information addressed specifically to a child. The information shall be provided in writing, or by other means, including, where appropriate, by electronic means. When requested by the data subject, the information may be provided orally, provided that the identity of the data subject is proven by other means. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

 The controller shall facilitate the exercise of data subject rights under Articles 15 to 22. In the cases referred to in Article 11(2), the controller shall not refuse to act on the request of the data subject for exercising his or her rights under Articles 15 to 22, unless the controller demonstrates that it is not in a position to identify the data subject. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

 The controller shall provide information on action taken on a request under Articles 15 to 22 to the data subject without undue delay and in any event within one month of receipt of the request. That period may be extended by two further months where necessary, taking into account the complexity and number of the requests. The controller shall inform the data subject of any such extension within one month of receipt of the request, together with the reasons for the delay. Where the data subject makes the request by electronic form means, the information shall be provided by electronic means where possible, unless otherwise requested by the data subject. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

 If the controller does not take action on the request of the data subject, the controller shall inform the data subject without delay and at the latest within one month of receipt of the request of the reasons for not taking action and on the possibility of lodging a complaint with a supervisory authority and seeking a judicial remedy. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

 Information provided under Articles 13 and 14 and any communication and any actions taken under Articles 15 to 22 and 34 shall be provided free of charge. Where requests from a data subject are manifestly unfounded or excessive, in particular because of their repetitive character, the controller may either:
(a) charge a reasonable fee taking into account the administrative costs of providing the information or communication or taking the action requested; or
(b) refuse to act on the request.
The controller shall bear the burden of demonstrating the manifestly unfounded or excessive character of the request. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.

    '''
    consise_report_hippa = '''

**Requirement**:

 General requirements. Covered entities and business associates must do the following:
(1) Ensure the confidentiality, integrity, and availability of all electronic protected health information the covered entity or business associate creates, receives, maintains, or transmits.
(2) Protect against any reasonably anticipated threats or hazards to the security or integrity of such information.
(3) Protect against any reasonably anticipated uses or disclosures of such information that are not permitted or required under subpart E of this part.
(4) Ensure compliance with this subpart by its workforce. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

 Flexibility of approach.
(1) Covered entities and business associates may use any security measures that allow the covered entity or business associate to reasonably and appropriately implement the standards and implementation specifications as specified in this subpart.
(2) In deciding which security measures to use, a covered entity or business associate must take into account the following factors:
(2)(i) The size, complexity, and capabilities of the covered entity or business associate.
(2)(ii) The covered entity's or the business associate's technical infrastructure, hardware, and software security capabilities.
(2)(iii) The costs of security measures.
(2)(iv) The probability and criticality of potential risks to electronic protected health information. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

 Standards. A covered entity or business associate must comply with the applicable standards as provided in this section and in §§164.308, 164.310, 164.312, 164.314 and 164.316 with respect to all electronic protected health information. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

 Implementation specifications. In this subpart:
(1) Implementation specifications are required or addressable. If an implementation specification is required, the word "Required" appears in parentheses after the title of the implementation specification. If an implementation specification is addressable, the word "Addressable" appears in parentheses after the title of the implementation specification.
(2) When a standard adopted in §164.308, §164.310, §164.312, §164.314, or §164.316 includes required implementation specifications, a covered entity or business associate must implement the implementation specifications.
(3) When a standard adopted in §164.308, §164.310, §164.312, §164.314, or §164.316 includes addressable implementation specifications, a covered entity or business associate must—
(3)(i) Assess whether each implementation specification is a reasonable and appropriate safeguard in its environment, when analyzed with reference to the likely contribution to protecting electronic protected health information; and
(3)(ii) As applicable to the covered entity or business associate—
(3)(ii)(A) Implement the implementation specification if reasonable and appropriate; or
(3)(ii)(B) If implementing the implementation specification is not reasonable and appropriate—
(3)(ii)(B) Document why it would not be reasonable and appropriate to implement the implementation specification; and
(3)(ii)(B) Implement an equivalent alternative measure if reasonable and appropriate. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.




**Requirement**:

 Maintenance. A covered entity or business associate must review and modify the security measures implemented under this subpart as needed to continue provision of reasonable and appropriate protection of electronic protected health information, and update documentation of such security measures in accordance with §164.316(b)(2)(iii). 

 **Status**: Missing 

**Reason**: 

The requirement is missing.
    '''

    consise_report = ""
    for framework in selected_frameworks:
        if 'CCPA' in selected_frameworks:
            consise_report += consise_report_ccpa
        if 'GDPR' in selected_frameworks:
            consise_report += consise_report_gdrp
        if 'HIPPA' in selected_frameworks:
            consise_report += consise_report_hippa


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
