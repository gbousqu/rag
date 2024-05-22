import streamlit as st
from docx import Document as DocxDocument    
import re
from io import BytesIO

def parse(file):
    file_bytes = BytesIO(file.getvalue())
    doc = DocxDocument(file_bytes)
    output = []
    for para in doc.paragraphs:
        text = para.text
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
        text = re.sub(r"\n\s*\n", "\n\n", text)
        output.append(text)
    return output


doc_files = st.file_uploader("", type=["pdf", "txt", "docx", "doc"], accept_multiple_files=True)

if doc_files:
   for file in doc_files:
      st.write(file.name)
      output = parse(file)
      st.write(output)
   

