import zipfile
import os

def extract_zip(file_bytes, extract_to):
    with open(os.path.join(extract_to, "temp.zip"), "wb") as f:
        f.write(file_bytes)
    with zipfile.ZipFile(os.path.join(extract_to, "temp.zip"), 'r') as zip_ref:
        zip_ref.extractall(extract_to)
