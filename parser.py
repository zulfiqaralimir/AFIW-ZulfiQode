# 📁 app/utils/parser.py

import pdfplumber
import pandas as pd
import io

def extract_text_and_tables(file_obj, file_type="pdf"):
    text = ""
    tables = []

    if file_type == "pdf":
        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
                for table in page.extract_tables():
                    tables.append(table)

    elif file_type == "csv":
        df = pd.read_csv(file_obj)
        text = df.to_string()
        tables.append([df.columns.tolist()] + df.values.tolist())

    return text, tables
