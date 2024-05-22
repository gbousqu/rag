import streamlit as st
from docx import Document as DocxDocument

def read_docx(file):
    doc = DocxDocument(file)
    content = []
    for para in doc.paragraphs:
        content.append(para.text)
    return content

def split_into_pages(content, max_chars_per_page=1000):
    pages = []
    current_page = ""
    char_count = 0
    for para in content:
        if char_count + len(para) > max_chars_per_page:
            pages.append(current_page)
            current_page = ""
            char_count = 0
        current_page += para + "\n"
        char_count += len(para)
    if current_page:
        pages.append(current_page)
    return pages

st.title("Upload a DOCX file")
uploaded_file = st.file_uploader("Choose a DOCX file", type="docx")

if uploaded_file is not None:
    content = read_docx(uploaded_file)
    pages = split_into_pages(content)
    
    st.write(f"Document has {len(pages)} pages.")
    
    for i, page in enumerate(pages):
        st.subheader(f"Page {i+1}")
        st.text(page)
