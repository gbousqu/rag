# Import necessary libraries
# import databutton as db
import streamlit as st

import os

from openai import OpenAI
from brain import get_index_for_file
from langchain.chains import RetrievalQA

# import pkg_resources
# openai_version = pkg_resources.get_distribution("openai").version
# st.write(f"OpenAI version: {openai_version}")


openai_api_key = st.text_input('Enter your OpenAI API key')
os.environ["OPENAI_API_KEY"] =openai_api_key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# Set the title for the Streamlit app
st.title("RAG enhanced Chatbot")


# Cached function to create a vectordb for the provided PDF files
@st.cache_resource 
def create_vectordb(files, filenames):
    # Show a spinner while creating the vectordb
    with st.spinner("Vector database"):
        vectordb = get_index_for_file(
            [file.getvalue() for file in files], filenames, os.environ["OPENAI_API_KEY"]
        )
    return vectordb


# Upload PDF files using Streamlit's file uploader
doc_files = st.file_uploader("", type="pdf,txt,docx,doc", accept_multiple_files=True)

# If PDF files are uploaded, create the vectordb and store it in the session state
if doc_files:
    doc_file_names = [file.name for file in doc_files]
    st.session_state["vectordb"] = create_vectordb(doc_files, doc_file_names)


prompt_template = """
    Vous êtes un assistant qui répond aux questions des utilisateurs sur la base de plusieurs contextes qui vous sont donnés.

    Votre réponse doit être courte et pertinente.
    
    Les preuves sont le contexte de l'extrait pdf avec les métadonnées. 
    
    Concentrez-vous soigneusement sur les métadonnées, en particulier le « nom de fichier » et la « page », lorsque vous répondez.
    
    Veillez à ajouter le nom du fichier et le numéro de la page à la fin de la phrase que vous citez.
        
    Répondez « Sans objet » si le texte n'est pas pertinent.
     
    Le contenu du PDF est le suivant :
    {pdf_extract}
"""


# Get the current prompt from the session state or set a default value
prompt = st.session_state.get("prompt", [{"role": "system", "content": "none"}])

# Display previous chat messages
for message in prompt:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Get the user's question using Streamlit's chat input
question = st.chat_input("Ask anything")

# Handle the user's question
if question:
    vectordb = st.session_state.get("vectordb", None)
    if not vectordb:
        with st.message("assistant"):
            st.write("You need to provide a PDF")
            st.stop()

    # Search the vectordb for similar content to the user's question
    search_results = vectordb.similarity_search(question, k=3)
    # search_results
    pdf_extract = "/n ".join([result.page_content for result in search_results])

    # Update the prompt with the pdf extract
    prompt[0] = {
        "role": "system",
        "content": prompt_template.format(pdf_extract=pdf_extract),
    }

    # Add the user's question to the prompt and display it
    prompt.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    # Display an empty assistant message while waiting for the response
    with st.chat_message("assistant"):
        botmsg = st.empty()

    # Call ChatGPT with streaming and display the response as it comes
    response = []
    result = ""
    for chunk in client.chat.completions.create(model="gpt-3.5-turbo", messages=prompt, stream=True):
        text = chunk.choices[0].delta.content

        if text is not None:
            response.append(text)
            result = "".join(response).strip()
            botmsg.write(result)

    # Add the assistant's response to the prompt
    prompt.append({"role": "assistant", "content": result})

    # Store the updated prompt in the session state
    st.session_state["prompt"] = prompt
    prompt.append({"role": "assistant", "content": result})

    # Store the updated prompt in the session state
    st.session_state["prompt"] = prompt
