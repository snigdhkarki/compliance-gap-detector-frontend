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
import altair as alt

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
    blocks = re.split(r'\*{2}Requirement\*{2}:', text)[1:]
    
    for blk in blocks:
        # Requirement: up to *Status*:
        # req, rest = re.split(r'\**Status\**:', blk, maxsplit=1)
        split_result = re.split(r'\*{2}Status\*{2}:', blk, maxsplit=1)
        if len(split_result) == 2:
            req, rest = split_result
        else:
            req = blk  # fallback if pattern not found
            rest = ''
        
        # Status: up to *Reason*:
        # status, rest = re.split(r'\**Reason\**:', rest, maxsplit=1)
        split_result = re.split(r'\*{2}Reason\*{2}:', rest, maxsplit=1)
        if len(split_result) == 2:
            status, rest = split_result
        else:
            status = rest  # or some fallback
            rest = ''
        
        # # Reason: up to *Target Policy*:
        # reason, rest = re.split(r'\*Target Policy\*[:]? ', rest, maxsplit=1)
        if '*Target Policy*' in rest:
            reason_text, target_text = re.split(r'\*{2}Target Policy\*{2}[:]? ?', rest, maxsplit=1)
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

    consise_report_gdpr = '''

    **Requirement**:
The organization shall provide the data subject prior to further processing of their personal data with information on that other purpose and with any relevant further information as referred to in paragraph 2.

**Status**: **Not Satisfied**

**Reason**: 
The requirement is not satisfied because although the evidence shows a request for personal data to be provided in a structured, commonly used, machine-readable format for transfer to another controller (which implies providing data for further processing), it does not explicitly mention informing the data subject about the other purpose of further processing and any relevant additional information.

**Target Policy**: Request your personal data in a
structured, commonly used,
machine-readable format for transfer to
another data controller.


**Requirement**:
The organization shall provide data subjects with information on purposes of further processing of their personal data prior to that further processing.

**Status**: **Not Satisfied**

**Reason**:

* The requirement is not satisfied because the provided evidence does not mention the provision of information on purposes of further processing, as required by the regulation. Instead, it only mentions providing personal data in a structured format for transfer to another data controller.
* The requested format (structured, commonly used, machine-readable) can be seen as related to this requirement, but it does not address the issue of informing the data subject about purposes of further processing.

**Target Policy**: Request your personal data in a
structured, commonly used,
machine-readable format for transfer to
another data controller.


**Requirement**:

 The right to obtain a copy referred to in paragraph 3 shall not adversely affect the rights and freedoms of others. 

 **Status**: **Missing **

**Reason**: 

The requirement is missing.


**Requirement**:

 A data subject who has obtained restriction of processing pursuant to paragraph 1 shall be informed by the controller before the restriction of processing is lifted. 

 **Status**: **Missing **

**Reason**: 

The requirement is missing.



**Requirement**:
The organization shall ensure that workforce members are trained to:

a) recognize a potential incident;
b) report such an incident.

**Status**: **Satisfied**

**Reason**:

* The requirement is satisfied because the evidence states that "Regular training will be conducted for employees, contractors, and partners to recognize potential incidents and respond appropriately." This suggests that the organization has taken concrete steps to train its workforce members on incident recognition and reporting.
* Although the text does not explicitly mention reporting incidents to a specific person or entity, it implies that training is being provided to equip workforce members with the necessary skills to take action in case of an incident.

**Target Policy**:  Training and Awareness: Regular training will be conducted for employees, contractors, and partners to recognize potential incidents and respond appropriately.


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

 Nothing in this section shall require a business to disclose trade secrets, as specified in regulations adopted pursuant to paragraph (3) of subdivision (a) of Section 1798.185. 

 **Status**: **Missing **

**Reason**: 

The requirement is missing.


**Requirement**:
A business that collects a consumer's personal information shall implement reasonable security procedures and practices appropriate to the nature of the personal information to protect the personal information from unauthorized or illegal access, destruction, use, modification, or disclosure in accordance with Section 1798.81.5.

**Status**: 
Not Satisfied

**Reason**: 
The requirement is not satisfied because, although the evidence mentions "security controls and practices designed to protect sensitive data", it does not explicitly state that these measures are reasonable given the nature of the personal information being collected. The language used in the regulation emphasizes the need for "reasonable" security procedures, which implies a level of proportionality and adequacy to the type of personal information being handled.

**Target Policy**: It outlines the security controls and 
practices designed to protect sensitive data and ensure compliance with legal, 
regulatory, and contractual obligations.


'''
    consise_report_hippa = '''
**Requirement**:

 General requirements. Covered entities and business associates must do the following:
(1) Ensure the confidentiality, integrity, and availability of all electronic protected health information the covered entity or business associate creates, receives, maintains, or transmits.
(2) Protect against any reasonably anticipated threats or hazards to the security or integrity of such information.
(3) Protect against any reasonably anticipated uses or disclosures of such information that are not permitted or required under subpart E of this part.
(4) Ensure compliance with this subpart by its workforce. 

 **Status**: **Missing** 

**Reason**: 

The requirement is missing.


**Requirement**:

The organization shall implement policies and procedures to limit physical access to its electronic information systems and the facility or facilities in which they are housed, while ensuring that properly authorized access is allowed.

**Status**:
**Satisfied**

**Reason**:
The requirement is satisfied because the evidence mentions "Facility Access: Physical entry to critical infrastructure (such as data centers) is restricted to authorized personnel".

**Target Policy**: Physical Access Control 
●​ Facility Access: Physical entry to critical infrastructure (such as data centers) is restricted to authorized personnel.


**Requirement**:

The organization shall implement policies and procedures that specify the proper functions, manner, and physical attributes of workstations accessing electronic protected health information.

**Status**: Not Satisfied

**Reason**:

* Although the requirement mentions securing devices used to access sensitive information, it does not explicitly state that policies and procedures are in place for workstations.
* The evidence only mentions "Workstation Security: Devices used to access sensitive information must be secured", which is a partial compliance with the requirement. It does not provide information on the implementation of specific policies and procedures for workstations.

Note: The current status is "Not Satisfied" because the evidence only partially addresses part of the requirement, specifically workstation security, but lacks detail on implementing policies and procedures.

**Target Policy**: ●​ Workstation Security: Devices used to access ensitive information must be secured.


**Requirement**:

 Standard: Device and media controls. Implement policies and procedures that govern the receipt and removal of hardware and electronic media that contain electronic protected health information into and out of a facility, and the movement of these items within the facility. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

 Implementation specifications:
Accountability (Addressable). Maintain a record of the movements of hardware and electronic media and any person responsible therefore. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:
The organization shall implement technical policies and procedures for electronic information systems that maintain electronic protected health information, allowing access only to those persons or software programs that have been granted access rights as specified in §164.308(a)(4).

**Status**:
**Not Satisfied**

**Reason**: The requirement is not satisfied because the evidence shows that users are permitted to access "only those systems and data for which they are authorized", but it does not explicitly state that this permission is granted based on the specific access rights specified in §164.308(a)(4). The text only mentions authorization, but does not link it directly to the specified access rights requirement.

**Target Policy**: ●​ Access Control: Users are permitted to access only those systems and data for 
which they are authorized.


**Requirement**:

 Implementation specifications:
Unique user identification (Required). Assign a unique name and/or number for identifying and tracking user identity. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

 Implementation specifications:
Emergency access procedure (Required). Establish (and implement as needed) procedures for obtaining necessary electronic protected health information during an emergency. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.



**Requirement**:
The organization shall implement:

a) a mechanism for encryption;
b) a mechanism for decryption;
c) mechanisms for encrypting and decrypting electronic protected health information.

**Status**: Not Satisfied

**Reason**:
The requirement is not satisfied because the evidence provided only mentions an "Encryption Key", which is a data element used in the encryption process, but does not describe a complete mechanism for implementation.

**Target Policy**: ●​ Encryption Key: A string of data used by an algorithm to perform encryption or decryption.


**Requirement**:

 General requirements. Covered entities and business associates must do the following:
(1) Ensure the confidentiality, integrity, and availability of all electronic protected health information the covered entity or business associate creates, receives, maintains, or transmits.
(2) Protect against any reasonably anticipated threats or hazards to the security or integrity of such information.
(3) Protect against any reasonably anticipated uses or disclosures of such information that are not permitted or required under subpart E of this part.
(4) Ensure compliance with this subpart by its workforce. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.
'''

    consise_report_cis = '''

**Requirement**:
Establish and maintain a secure network architecture. A secure network architecture must address segmentation, least privilege, and availability, at a minimum.

**Status**: Satisfied

**Reason**:

* The requirement is satisfied because the organization has implemented a network segmentation approach that limits access between systems based on role and function.
* This approach inherently addresses one of the required elements (segmentation) and contributes to achieving another element (least privilege), as restricted access reduces the potential for unauthorized actions.

**Target Policy**: ●​ Segmentation: The network is segmented to limit access between systems 
based on role and function, thereby reducing the potential impact of any security breach.



**Requirement**:
Operate processes and tooling to establish and maintain comprehensive network monitoring and defense against security threats across the enterprise's network infrastructure and user base.

**Status**: Not Satisfied

**Reason**:

* The requirement mentions operating processes and tooling for comprehensive network monitoring, but it does not explicitly mention the deployment of intrusion detection systems (IDS) or other tools to detect security threats in real-time.
* While the evidence mentions "intrusion detection systems", it is unclear if this is a separate control from regular security audits, and whether it covers all aspects of comprehensive network monitoring and defense.

**Target Policy**: These controls include network 
segmentation, deployment of firewalls and intrusion detection systems, and regular security audits.


**Requirement**:

 Actively manage (inventory, track, and correct) all enterprise assets (end-user devices, including portable and mobile; network devices; non-computing/Internet of Things (IoT) devices; and servers) connected to the infrastructure physically, virtually, remotely, and those within cloud environments, to accurately know the totality of assets that need to be monitored and protected within the enterprise. This will also support identifying unauthorized and unmanaged assets to remove or remediate. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

 Establish and maintain an accurate, detailed, and up-to-date inventory of all enterprise assets with the potential to store or process data, to include: end-user devices (including portable and mobile), network devices, non-computing/IoT devices, and servers. Ensure the inventory records the network address (if static), hardware address, machine name, data asset owner, department for each asset, and whether the asset has been approved to connect to the network. For mobile end-user devices, MDM type tools can support this process, where appropriate. This inventory includes assets connected to the infrastructure physically, virtually, remotely, and those within cloud environments. Additionally, it includes assets that are regularly connected to the enterprise's network infrastructure, even if they are not under control of the enterprise. Review and update the inventory of all enterprise assets bi-annually, or more frequently. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

 Prevent or control the installation, spread, and execution of malicious applications, code, or scripts on enterprise assets. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

 Deploy and maintain anti-malware software on all enterprise assets. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:
The organization shall establish and maintain data recovery practices sufficient to restore in-scope enterprise assets to a pre-incident and trusted state.

**Status**: Satisfied

**Reason**: The requirement is satisfied because the evidence mentions robust backup strategies, redundant storage solutions, and clearly defined recovery point objectives. The language used focuses on preserving data integrity and ensuring availability with minimal data loss as well as restoration of the assets to their original state.

**Target Policy**: Data protection forms another crucial objective, as we 
commit to preserving data integrity and ensuring availability with minimal data loss through robust backup strategies, redundant storage solutions, and clearly defined recovery point objectives that balance business needs with technical capabilities.


**Requirement**:
Establish and maintain a data recovery process. In the process, address the scope of data recovery activities, recovery prioritization, and the security of backup data. Review and update documentation annually, or when significant enterprise changes occur that could impact this Safeguard.

**Status**: Not Satisfied

**Reason**:

* Although the organization mentions having "robust backup strategies" and "redundant storage solutions", which suggests an attempt to establish a data recovery process.
* However, the evidence does not explicitly mention addressing the scope of data recovery activities, recovery prioritization, or the security of backup data. The requirement specifically states that these aspects must be addressed in the process.
* Furthermore, the requirement specifies that documentation should be reviewed and updated annually, but the evidence only mentions updating documentation when "significant enterprise changes occur". This does not guarantee an annual review as required by the policy.

**Target Policy**: Data protection forms another crucial objective, as we 
commit to preserving data integrity and ensuring availability with minimal data loss through robust backup strategies, redundant storage solutions, and clearly defined recovery point objectives that balance business needs with technical capabilities.

'''

    consise_report_scf = '''

**Requirement**:
Mechanisms exist to establish, maintain and disseminate cybersecurity & data protection policies, standards and procedures.

**Status**: Satisfied

**Reason**:

* The requirement is satisfied because the evidence mentions that a systematic approach exists for identifying, assessing, and mitigating risks associated with information security. This implies the existence of mechanisms to establish, maintain, and disseminate cybersecurity policies, standards, and procedures.
* Although the text does not explicitly mention dissemination, it can be inferred that this aspect is covered as part of the regular evaluations and implementation of controls mentioned in the evidence.

**Target Policy**: Additionally, the policy establishes a systematic approach to identifying, assessing, and mitigating risks associated with information security through regular evaluations and implementation of controls commensurate with risk levels.


**Requirement**:

 Mechanisms exist to prohibit exceptions to standards, except when the exception has been formally assessed for risk impact, approved and recorded. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:
Mechanisms exist to review the cybersecurity & data privacy program, including policies, standards and procedures, at planned intervals or if significant changes occur to ensure their continuing suitability, adequacy and effectiveness.

**Status**: Not Satisfied

**Reason**:

* Although the organization mentions updating security measures based on findings from reviews, it does not explicitly state that these updates are made at "planned intervals" as required by the requirement.
* The text only mentions reviewing policies, incident response procedures, and controls in response to significant changes, but does not provide assurance that reviews will occur at planned intervals regardless of changes.

**Target Policy**: ●​ Updating Security Measures: Findings from the review will be used to update security policies, incident response procedures, and controls to prevent future incidents.



**Requirement**:

Mechanisms exist to assign one or more qualified individuals with the mission and resources to centrally-manage, coordinate, develop, implement and maintain an enterprise-wide cybersecurity & data protection program.

**Status**: Not Satisfied

**Reason**:
The requirement is not satisfied because while the organization mentions having "sophisticated access control mechanisms" that limit data access, it does not explicitly mention the existence of a central management team or individuals with the mission and resources to manage this program. The text only discusses access controls and permission reviews, which are components of an enterprise-wide cybersecurity & data protection program, but do not provide evidence of a centralized management structure.

**Target Policy**: Our security infrastructure includes sophisticated access control mechanisms that strictly limit data access to authorized personnel based on job responsibilities and the principle of least privilege, with regular permission reviews and updates as roles change.


**Requirement**:

 Mechanisms exist to establish an authoritative chain of command with clear lines of communication to remove ambiguity from individuals and teams related to managing data and technology-related risks. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

 Mechanisms exist to develop, report and monitor cybersecurity & data privacy program measures of performance. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.

**Requirement**:

 Mechanisms exist to establish contact with selected groups and associations within the cybersecurity & data privacy communities to: 
 (1) Facilitate ongoing cybersecurity & data privacy education and training for organizational personnel;
 (2) Maintain currency with recommended cybersecurity & data privacy practices, techniques and technologies; and
 (3) Share current cybersecurity and/or data privacy-related information including threats, vulnerabilities and incidents. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

 Mechanisms exist to define the context of its business model and document the mission of the organization. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:
Mechanisms exist to compel data and/or process owners to operationalize cybersecurity & data privacy practices for each system, application and/or service under their control.

**Status**: Not Satisfied

**Reason**:

* Although the organization mentions having "sophisticated access control mechanisms" that limit data access to authorized personnel, this does not directly address the requirement of compelling data and/or process owners to operationalize cybersecurity and data privacy practices.
* The mention of regular permission reviews and updates as roles change is a positive step, but it is unclear if these processes are sufficient to ensure that cybersecurity and data privacy practices are consistently applied across all systems, applications, and services.

**Target Policy**: Our security infrastructure includes sophisticated access control mechanisms that strictly limit data access to authorized personnel based on job responsibilities and the principle of least privilege, with regular permission reviews and updates as roles change.



'''
    consise_report_pci_dss = '''

**Requirement**:
The organization shall ensure that all audit log files are protected from unauthorized modifications by individuals.

**Status**:
Satisfied

**Reason**:

* The requirement is satisfied because the evidence shows that "Restricted Access" is implemented, which restricts access to logging systems and log data only to authorized personnel based on job responsibilities and security clearance. This suggests that audit log files are protected from unauthorized modifications by individuals.
* Although the text does not explicitly mention protection of audit log files, it implies that measures are in place to prevent unauthorized modifications to logging systems and log data. It can be inferred that similar protection would apply to audit log files as well.

**Target Policy**: Access Controls for Logs Access to logging systems and log data represents a sensitive security control point that requires appropriate restrictions: Restricted Access: Only authorized personnel may access system logs based on job responsibilities and security clearance.


**Requirement**:
The organization shall review the following audit logs at least once daily:

a) All security events.
b) Logs of all system components that store, process, or transmit CHD and/or SAD.
c) Logs of all critical system components.
d) Logs of all servers and system components that perform security functions.

**Status**: Not Satisfied

**Reason**:
The requirement is not satisfied because the provided evidence only mentions reviewing audit logs for "system access, user activity, and communication traffic", which does not explicitly include all the specified types of logs (a, b, c, d). While it does mention reviewing logs periodically, there is no guarantee that these specific logs are being reviewed daily.

**Target Policy**: ●​ Audit Logs: Audit logs of system access, user activity, and communication traffic will be maintained and periodically reviewed to detect and investigate suspicious behavior.


**Requirement**:
The organization shall implement:

a) file integrity monitoring or change-detection mechanisms on audit logs to prevent alteration of existing log data;

b) measures to ensure that changes to audit logs generate alerts, indicating potential tampering or unauthorized activity.

**Status**: Not Satisfied

**Reason**:

* The requirement specifies the use of "file integrity monitoring or change-detection mechanisms" which is not explicitly mentioned in the evidence.
* Although the evidence requires transaction logging and audit trails for data integrity, it does not mention the specific use of file integrity monitoring or change-detection mechanisms on audit logs.

**Target Policy**: Require transaction logging and audit trails to maintain data integrity and track sensitive information access.


**Requirement**:

Audit logs shall be protected from destruction and unauthorized modifications.

**Status**: Not Satisfied

**Reason**:

The requirement is not satisfied because the evidence provided only shows that all access events are logged to maintain an audit trail, which meets the logging part of the requirement. However, it does not explicitly state whether these log entries are protected from destruction or unauthorized modifications.

**Target Policy**: Monitoring and Logging 
6.1 Audit Logging 
●​ Logging of Access Events: All access events—including login attempts, role changes, and privilege escalations—are logged to maintain an audit trail.


**Requirement**:

 Audit logs capture all creation and deletion of system-level objects. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

 Configuration standards for NSC rulesets are:
a) Defined.
b) Implemented.
c) Maintained. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

 All changes to network connections and to configurations of NSCs are approved and managed in accordance with the change control process defined at Requirement 6.5.1. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

 An accurate network diagram(s) is maintained that shows all connections between the CDE and other networks, including any wireless networks. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

 An accurate data-flow diagram(s) is maintained that meets the following:
a) Shows all account data flows across systems and networks.
b) Updated as needed upon changes to the environment. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


'''
    consise_report_nist_csf = '''
**Requirement**:

The organization shall detect anomalous activity and understand the potential impact of events.

**Status**: Not Satisfied

**Reason**:

* The requirement is not satisfied because, although the organization investigates any anomalies promptly, there is no information available to suggest that they are actively detecting anomalous activity in the first place.

**Target Policy**: Any anomalies are promptly investigated.


**Requirement**:

 A baseline of network operations and expected data flows for users and systems is established and managed 

 **Status**: Missing 

**Reason**: 

The requirement is missing.



**Requirement**:
The organization shall understand:

a) policies, procedures, and processes related to managing and monitoring regulatory, legal, risk, environmental, and operational requirements;
b) how these policies, procedures, and processes inform the management of cybersecurity risk;

**Status**: **Satisfied**

**Reason**:

* The requirement is satisfied because the policy establishes a systematic approach to identifying, assessing, and mitigating risks associated with information security. This implies that the organization understands its regulatory, legal, and operational requirements.
* Additionally, the text mentions "cybersecurity risk", which suggests that the organization's policies, procedures, and processes inform the management of cybersecurity risk specifically.

**Target Policy**: Additionally, the policy establishes a systematic approach to identifying, assessing, and mitigating risks associated with information security through regular evaluations and implementation of controls commensurate with risk levels.



**Requirement**:

 Organizational cybersecurity policy is established and communicated 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:
The organization shall ensure that cybersecurity roles and responsibilities are coordinated and aligned with internal roles and external partners.

**Status**: Not Satisfied

**Reason**:

* The evidence provided only mentions the "IT Security Team" having specific responsibilities for maintaining network security, which does not explicitly indicate alignment or coordination with other internal roles or external partners.
* Although it is mentioned that the IT Security Team monitors for threats and enforces compliance, this information alone does not suggest coordination or alignment with other stakeholders.

**Target Policy**: Roles and Responsibilities The following roles have specific responsibilities for maintaining network security: ●​ IT Security Team: Oversees network security, monitors for threats, and enforces 
compliance.

**Requirement**:
The organization shall have risk management processes that address cybersecurity risks.

**Status**:
**Satisfied**

**Reason**:

* The requirement is satisfied because, there is a Security Team that conducts risk assessments related to cybersecurity threats.

**Target Policy**: Security Team Conducts risk assessments related to cybersecurity threats.


**Requirement**:

 Organizational cybersecurity policy is established and communicated 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:
The organization shall ensure that monitoring of authorized users and systems is performed on a continuous basis.

**Status**:
**Not Satisfied**

**Reason**: 

* The requirement specifically mentions monitoring for "unauthorized personnel", but the evidence only provides information about monitoring remote access sessions, which does not explicitly cover unauthorized personnel.
* While it can be inferred that monitoring of authorized users may also be necessary, the provided evidence is insufficient to confirm this.

**Target Policy**: ●​ Monitoring: Remote access sessions are continuously monitored, with unauthorized attempts logged and investigated.

'''
    consise_report_nist_80053 = '''

**Requirement**:

 Notify account managers and organization-defined personnel or roles within organization-defined time period when accounts are no longer required, when users are terminated or transferred, and when system usage or need-to-know changes for an individual 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:
The organization shall setup monitoring processes and tools for the system for any unauthorized access attempts.

**Status**:
Satisfied

**Reason**:

* The requirement is satisfied because the evidence states that "all access attempts are logged and monitored through automated systems", which implies the presence of a robust monitoring process.

**Target Policy**: All access 
attempts are logged and monitored through automated systems that can detect and alert security personnel to unusual or potentially malicious activities.


**Requirement**:
The organization shall Regularly review access control policies and update them as needed.

**Status**: **Satisfied**

**Reason**:

* The requirement is satisfied because the evidence states that "access rights are reviewed regularly to ensure they remain appropriate", which implies a regular review process in place. This suggests that the organization is actively monitoring its access control policies and making updates as necessary.
* Although the text does not explicitly state that all reviews result in updates, the fact that reviews are conducted at all indicates a commitment to maintaining up-to-date policies.

**Target Policy**: Access rights are reviewed regularly to ensure they remain appropriate.


**Requirement**:
Implement security measures to protect against unauthorized access.

**Status**: Satisfied

**Reason**:

* The requirement is satisfied because the evidence describes a comprehensive approach that includes "advanced technical measures" and "robust organizational safeguards". This suggests that the organization has implemented multiple layers of protection to prevent unauthorized access, which aligns with the requirement.

**Target Policy**: Our approach combines advanced technical measures with robust organizational safeguards to prevent unauthorized access, disclosure, alteration, and destruction of sensitive information.



**Requirement**:
The organization shall implement access control mechanisms to restrict access to authorized users.

**Status**:
**Not Satisfied**

**Reason**:

* Although the text mentions that "Users are permitted to access only those systems and data for which they are authorized", this statement appears to describe a permission-based approach rather than implementing access control mechanisms. 
* Access control mechanisms typically involve limiting or managing user access based on roles, privileges, or other factors, but the provided evidence does not explicitly state how this is achieved.

**Target Policy**: ●​ Access Control: Users are permitted to access only those systems and data for which they are authorized.


**Requirement**:
Establish access control policies that define the rules and regulations for access to information and system resources.

**Status**:
Satisfied

**Reason**:

* The requirement is satisfied because the evidence states "Users are permitted to access only those systems and data for which they are authorized." This implies that there are clear rules and regulations in place for controlling access, aligning with the requirement of establishing access control policies.

**Target Policy**: ●​ Access Control: Users are permitted to access only those systems and data for which they are authorized.



**Requirement**:

 Review accounts for compliance with account management requirements organization-defined frequency 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

 Establish and implement a process for changing shared or group account authenticators (if deployed) when individuals are removed from the group. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

 Align account management processes with personnel termination and transfer processes 

 **Status**: Missing 

**Reason**: 

The requirement is missing.
'''
    consise_report_hitrust = '''

**Requirement**:
The organization shall have a formal information protection program based on an accepted industry framework that is reviewed and updated as needed.

**Status**:
**Not Satisfied**

**Reason**:

* The requirement is not satisfied because the provided evidence only mentions "advanced technical measures" and "robust organizational safeguards" without explicitly stating that this approach is based on an accepted industry framework. While the text does imply a structured approach, it lacks direct confirmation of the use of an accepted industry framework.
* There is no mention of reviewing and updating the information protection program as needed, which is another key aspect of the requirement.

**Target Policy**: Our approach combines advanced technical measures with robust organizational safeguards to prevent unauthorized access, disclosure, alteration, and destruction of sensitive information.


**Requirement**:
The organization shall formally document and actively monitor, review, and update the information protection program to ensure it continues to meet its objectives.

**Status**: Satisfied

**Reason**:

* The requirement is satisfied because the policy mentions formal documentation, systematic approach to risk identification, evaluation, and mitigation.

**Target Policy**: Additionally, the policy establishes a systematic approach to identifying, assessing, and mitigating risks associated with information security through regular evaluations and implementation of controls commensurate with risk levels.


**Requirement**:
The organization shall define user security roles and responsibilities clearly.

**Status**: Not Satisfied

**Reason**:

* The evidence mentions specific "roles" with "responsibilities".

**Target Policy**: Roles and Responsibilities 
The following roles have specific responsibilities for maintaining network security: 
●​ IT Security Team: Oversees network security, monitors for threats, and enforces compliance.


**Requirement**:

 The organization has an information security workforce improvement program. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:
The organization ensures plans for security testing, training, and monitoring activities are developed, implemented, maintained, and reviewed for consistency with the risk management strategy and response priorities.

**Status**: Not Satisfied

**Reason**:
The requirement is not satisfied because while it mentions that the "Security Team" conducts security reviews, risk assessments, and ensures compliance with security requirements, there is no direct evidence that plans for security testing, training, and monitoring activities are specifically developed, implemented, maintained, and reviewed in line with the risk management strategy and response priorities.

**Target Policy**: Security Team Conducts security reviews, risk assessments, and ensures compliance with security requirements.


**Requirement**:

 The organization employs a formal sanctions process for personnel failing to comply with established information security policies and procedures, and notifies defined personnel (e.g., supervisors) within a defined time frame (e.g., 24 hours) when a formal sanction process is initiated, identifying the individual sanctioned and the reason for the sanction. Further, the organization includes specific procedures for license, registration, and certification denial or revocation and other disciplinary action. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:
The organization shall regularly review and update its security policies to reflect leading practices and communicate them throughout the organization.

**Status**: Not Satisfied

**Reason**:

* The requirement is not satisfied because while the policy review and updates are scheduled annually or upon significant changes, it does not meet the condition of "regularly" as stated in the requirement. 
* Although the organization has established a formal process for reviewing policies, this may not be sufficient to ensure that security policies remain up-to-date and reflect leading practices on an ongoing basis.

**Target Policy**: Policy Review and Updates 
This policy shall be reviewed annually or upon significant changes to software development practices, regulatory requirements, or the security landscape.



**Requirement**:
The organization shall determine:

a) a senior-level information security official who is responsible for ensuring security processes are in place, communicated to all stakeholders, and consider and address organizational requirements.

b) the specific responsibilities of this role.

**Status**: **Not Satisfied**

**Reason**: 

* The requirement states that the organization must appoint a senior-level information security official with specific responsibilities, but it does not explicitly state that such an official exists.
* Although the evidence mentions a "Roles and Responsibilities" section, it only lists one team ("IT Security Team") with specific roles, without mentioning a senior-level information security official or their responsibilities.

**Target Policy**: Roles and Responsibilities 
The following roles have specific responsibilities for maintaining network security: 
●​ IT Security Team: Oversees network security, monitors for threats, and enforces 
compliance.
'''
    consise_report_iso = '''
**Requirement**:

 The organization shall determine external and internal issues that are relevant to its purpose and that affect its ability to achieve the intended outcome(s) of its information security management system. 

 **Status**: **Missing** 

**Reason**: 

The requirement is missing.


**Requirement**:
The organization shall determine:

a) interested parties that are relevant to the information security management system;
b) the relevant requirements of these interested parties;
c) which of these requirements will be addressed through the information security management system.

**Status**: **Not Satisfied**

**Reason**:

* The requirement is not satisfied because, although an "Information Security Committee" has been established, it is unclear if all identified interested parties and their respective requirements have been considered.
* The text only mentions key stakeholders from various departments participating in the committee, but does not provide information on other potentially relevant parties.
* There is no evidence to suggest that the organization has conducted a thorough analysis of its internal and external environments to identify all relevant requirements.

**Target Policy**: ●​ Information Security Committee: A dedicated committee comprising key 
stakeholders from various departments will oversee the implementation and 
ongoing management of the information security program.


**Requirement**:
The organization shall determine:

a) issues referred to in 4.1 that need to be addressed;
b) requirements referred to in 4.2 that need to be met;

c) risks and opportunities that need to be addressed to ensure the information security management system can achieve its intended outcome(s), prevent undesired effects, and achieve continual improvement.

**Status**: **Not Satisfied**

**Reason**:
The requirement is not satisfied because the evidence provided does not indicate that the organization has identified and assessed issues referred to in 4.1 or requirements referred to in 4.2. The policy only mentions establishing a systematic approach to identifying, assessing, and mitigating risks associated with information security through regular evaluations and implementation of controls commensurate with risk levels, which is related but not identical to the requirement.

**Target Policy**: Additionally, the policy establishes a systematic approach to identifying, 
assessing, and mitigating risks associated with information security through regular 
evaluations and implementation of controls commensurate with risk levels.


**Requirement**:

 When the organization determines the need for changes to the information security management system, the changes shall be carried out in a planned manner. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:
The organization shall determine and provide the resources needed for the establishment, implementation, maintenance and continual improvement of the information security management system.

**Status**: Not Satisfied

**Reason**:

* The requirement is not satisfied because while there is an Information Security Committee in place, there is no explicit mention of determining and providing the necessary resources.
* The committee's focus on "oversight" rather than direct resource allocation suggests that other parties may be responsible for providing necessary resources.

**Target Policy**: ●​ Information Security Committee: A dedicated committee comprising key 
stakeholders from various departments will oversee the implementation and 
ongoing management of the information security program.


**Requirement**:

 The organization shall determine the need for internal and external communications relevant to the information security management system including:
a) on what to communicate;
b) when to communicate;
c) with whom to communicate;
d) how to communicate. 

 **Status**: Missing 

**Reason**: 

The requirement is missing.


**Requirement**:

The organization shall control documented information to ensure it is available and suitable for use, where and when it is needed; and adequately protected from loss of confidentiality, improper use, or loss of integrity.

**Status**: Not Satisfied

**Reason**:

* The requirement is not satisfied because the evidence only outlines security controls and practices designed to protect sensitive data and ensure compliance with legal, regulatory, and contractual obligations. However, it does not explicitly state how documented information will be controlled to meet the specific requirements mentioned in the control of documented information standard (e.g., availability, protection).
* The evidence lacks detail on how the organization ensures that documented information is available and suitable for use when needed, or how it protects against loss of confidentiality, improper use, or loss of integrity.
* Although the requirement mentions distribution, access, retrieval, and use; storage and preservation, including preservation of legibility; control of changes (e.g., version control); and retention and disposition as part of the control of documented information, these activities are not explicitly mentioned in the evidence.

**Target Policy**: It outlines the security controls and 
practices designed to protect sensitive data and ensure compliance with legal, 
regulatory, and contractual obligations.


**Requirement**:

The organization shall determine:
a) what needs to be monitored and measured, including information security processes and controls;
b) the methods for monitoring, measurement, analysis and evaluation, as applicable, to ensure valid results. The methods selected should produce comparable and reproducible results to be considered valid;
c) when the monitoring and measuring shall be performed;
d) who shall monitor and measure;
e) when the results from monitoring and measurement shall be analysed and evaluated;
f) who shall analyse and evaluate these results.

**Status**: **Not Satisfied**

**Reason**:

* The requirement is not satisfied because while the evidence mentions regular audits, it does not explicitly cover all aspects required by the standard. For example, there is no mention of methods for monitoring, measurement, analysis, and evaluation or who will perform these tasks.
* Although continuous monitoring of information systems is mentioned, this alone does not address all the requirements listed in a) and b).
* The evidence only provides information on auditing and monitoring being conducted to ensure compliance with policy but does not explicitly mention when results from monitoring and measurement shall be analysed and evaluated or who will perform this task.

**Target Policy**: Regular audits and continuous monitoring of information systems will Auditing and Monitoring be conducted to ensure compliance with this policy and detect any security gaps.

'''
    consise_report_group = []
    consise_report = ""
    for framework in selected_frameworks:
        if 'CCPA' == framework:
            consise_report_group.append({"name":"CCPA", "report":consise_report_ccpa})
            consise_report += consise_report_ccpa
        if 'GDPR' == framework:
            consise_report_group.append({"name":"GDPR", "report":consise_report_gdpr})
            consise_report += consise_report_gdpr
        if 'HIPAA' == framework:
            consise_report_group.append({"name":"HIPAA", "report":consise_report_hippa})
            consise_report += consise_report_hippa
        if 'NIST 800-53' == framework:
            consise_report_group.append({"name":"NIST 800-53", "report":consise_report_nist_80053})
            consise_report += consise_report_nist_80053
        if 'ISO' == framework:
            consise_report_group.append({"name":"ISO", "report":consise_report_iso})
            consise_report += consise_report_iso
        if 'PCI-DSS' == framework:
            consise_report_group.append({"name":"PCI-DSS", "report":consise_report_pci_dss})
            consise_report += consise_report_pci_dss
        if 'CIS' == framework:
            consise_report_group.append({"name":"CIS", "report":consise_report_cis})
            consise_report += consise_report_cis
        if 'HITRUST' == framework:
            consise_report_group.append({"name":"HITRUST", "report":consise_report_hitrust})
            consise_report += consise_report_hitrust
        if 'NIST CSF' == framework:
            consise_report_group.append({"name":"NIST CSF", "report":consise_report_nist_csf})
            consise_report += consise_report_nist_csf
        if 'SCF' == framework:
            consise_report_group.append({"name":"SCF", "report":consise_report_scf})
            consise_report += consise_report_scf





    # gap_and_status = [{"gap":"snigdh","status":"lol"}, {"gap":"sussy", "status":"fuhrer"}]
    dict_report = parse_report(consise_report)
    Status_list = [d['Status'] for d in dict_report]
#    print(Status_list)
    


    output_list = [normalize_response(val) for val in Status_list]
#    print(output_list)
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
    st.plotly_chart(fig, key = "main")

    data = []
    for dic in dict_report:
        data.append((dic["Requirement"], dic["Status"], dic["Reason"], dic["Target Policy"]))
    df = pd.DataFrame(data, columns=["Requirement","Status", "Reason", "Target Policy"])


    i = 0
    bar_data = []
    for report in consise_report_group:
        i+= 1
        st.markdown("### PIE CHART OF " + report["name"]) 
        consise_report = report["report"]
        dict_report = parse_report(consise_report)
        Status_list = [d['Status'] for d in dict_report]
    #    print(Status_list)
        


        output_list = [normalize_response(val) for val in Status_list]
    #    print(output_list)
        counts = Counter(output_list)
        bar_data.append(counts)
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
        st.plotly_chart(fig, key=f"plotly_chart_{i}")



   
    
    # with tempfile.TemporaryDirectory() as tmp_dir:
    #     file_path = os.path.join(tmp_dir, uploaded_file.name)
    #     with open(file_path, "wb") as f:
    #         f.write(uploaded_file.getbuffer())

    #     with zipfile.ZipFile(file_path, 'r') as zip_ref:
    #         zip_ref.extractall(tmp_dir)

    #     st.success("ZIP uploaded and extracted successfully.")


    #     st.markdown(f"**Frameworks selected:** {', '.join(selected_frameworks)}")

    st.title("Stacked Bar Chart from Nested Lists")

    # Your data
    # bar_data = [[2, 3, 2],
    #         [0, 3, 2],
    #         [1, 2, 0]]

    # Turn it into a DataFrame
    df_bar = pd.DataFrame(bar_data, columns=["Miss", "No", "Yes"])
    df_bar["Bar #"] = selected_frameworks

    # Melt to long form for Altair
    df_long = df_bar.melt(id_vars="Bar #", var_name="Block", value_name="Value")

    # Build the chart
    chart = (
        alt.Chart(df_long)
        .mark_bar()
        .encode(
            x=alt.X("Bar #:N", title="Bar Index"),
            y=alt.Y("Value:Q", title="Value"),
            color=alt.Color("Block:N", 
                            scale=alt.Scale(
                                domain=["Miss", "No", "Yes"],
                                range=["#1f77b4", "#ff7f0e", "#2ca02c"]
                            ),
                            title="Block"
            )
        )
        .properties(width=600, height=400)
    )

    # Render
    st.altair_chart(chart, use_container_width=True)

    st.markdown("### Compliance Gap Results")
    st.dataframe(df, use_container_width=True)
elif not uploaded_file:
    st.info("Please upload a ZIP file.")
elif not selected_frameworks:
    st.warning("Please select at least one compliance framework.")
