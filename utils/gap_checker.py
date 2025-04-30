import random
import pandas as pd

def run_compliance_check():
    gaps = [
        "Missing access logs", "Encryption undefined",
        "Backup policy outdated", "No risk evaluation",
        "No MFA enforcement", "Lack of breach policy"
    ]
    statuses = ["Conflicting Control", "Unlinked", "Full Compliance"]
    data = [(random.choice(gaps), random.choice(statuses), "[View](#)") for _ in range(10)]
    return pd.DataFrame(data, columns=["Compliance gap identified", "Status", "Link"])
