# 📁 app/utils/table_summarizer.py

from openai import OpenAI
import os
import json

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_table_data(tables):
    if not tables:
        return "### 📊 Table Summary\n\n_No tables detected in the uploaded documents._"

    table_strings = []
    for t in tables:
        headers = t[0]
        rows = t[1:]
        sample_rows = rows[:5]
        formatted = [dict(zip(headers, row)) for row in sample_rows if len(row) == len(headers)]
        table_strings.append(json.dumps(formatted, indent=2))

    prompt = (
        "You are a financial analyst. Convert the following financial tables into Markdown-formatted paragraph summaries. "
        "Use headings, bullets, and explain trends or risks. Be concise and professional.\n\n"
        + "\n\n".join(table_strings)
    )

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
