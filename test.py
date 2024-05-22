import streamlit as st


doc_files = st.file_uploader("", type=["pdf", "txt", "docx", "doc"], accept_multiple_files=True)


