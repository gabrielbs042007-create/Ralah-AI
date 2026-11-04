import os
import streamlit as st
import ollama
from pypdf import PdfReader

st.set_page_config(page_title="RALAH - Assistant Local", page_icon="🛡️", layout="centered")

MODEL_NAME = "qwen2.5:0.5b"

st.title("🛡️ RALAH - Assistant Local (Jetson Orin Nano)")
st.markdown("Assistant IA 100% hors-ligne, privé et propulsé par Ollama.")

with st.sidebar:
    st.header("⚙️ Paramètres")
    st.info(f"Modèle actif :\n`{MODEL_NAME}`")
    
    st.markdown("---")
    st.header("📁 Document joint")
    uploaded_file = st.file_uploader("Importer un PDF ou TXT", type=["pdf", "txt", "py", "md"])
    
    file_context = ""
    if uploaded_file is not None:
        ext = uploaded_file.name.split('.')[-1].lower()
        if ext == 'pdf':
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                t = page.extract_text()
                if t: file_context += t + "\n"
        else:
            file_context = uploaded_file.read().decode("utf-8", errors="ignore")
        st.success(f"Fichier chargé : {uploaded_file.name}")

    if st.button("Effacer l'historique"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu es RALAH, un assistant technique intelligent et concis. Réponds toujours en français."}
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if user_prompt := st.chat_input("Écris ton message ici..."):
    full_prompt = user_prompt
    if file_context and not any(m["role"] == "user" and "[Fichier joint]" in m["content"] for m in st.session_state.messages):
        full_prompt = f"Voici un document de référence :\n{file_context[:4000]}\n\nQuestion / Demande : {user_prompt}"
        st.session_state.messages.append({"role": "user", "content": f"{user_prompt} *[Fichier joint chargé]*"})
    else:
        st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            stream = ollama.chat(
                model=MODEL_NAME, 
                messages=st.session_state.messages, 
                stream=True,
                options={'temperature': 0.3, 'num_predict': 400}
            )
            
            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                message_placeholder.markdown(full_response + "▌")
                
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Erreur de communication avec Ollama : {e}")
