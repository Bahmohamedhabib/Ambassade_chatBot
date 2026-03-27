import streamlit as st
from app.ui.components import UIComponents
from app.security.input_validation import InputValidator
from app.rag.vector_store import VectorStore
from app.rag.retriever import Retriever
from app.services.mistral_client import MistralChatClient
from app.utils.logger import setup_logger
from app.ui.admin_pages import render_admin_dashboard

logger = setup_logger("streamlit_app")

# Configuration de la page
st.set_page_config(
    page_title="Ambassade de Côte d'Ivoire",
    page_icon="🇨🇮",
    layout="centered"
)

# Initialisation des composants (simulée avec un cache pour éviter de recharger l'index)
@st.cache_resource
def init_services():
    store = VectorStore()
    retriever = Retriever(store)
    chat_client = MistralChatClient()
    return retriever, chat_client

def main():
    # Détection si on est sur la page d'administration via query params
    query_params = st.query_params
    if "admin" in query_params:
        render_admin_dashboard()
        return

    UIComponents.render_header()
    UIComponents.render_disclaimer()
    
    # Affichage de l'historique de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for message in st.session_state.messages:
        avatar_icon = "🏛️" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])
            # L'affichage des sources a été désactivé à la demande de l'utilisateur

    # Initialiser les services
    retriever, chat_client = init_services()

    # Saisie utilisateur
    if prompt := st.chat_input("Posez votre question (ex: Quels documents pour renouveler un passeport ?)"):
        # Afficher la question
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            
        # Validation de sécurité
        if not InputValidator.validate_query(prompt):
            error_msg = "Votre requête ne respecte pas les règles d'utilisation ou contient des éléments non autorisés."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant", avatar="🏛️"):
                st.error(error_msg)
            return
            
        sanitized_prompt = InputValidator.sanitize_query(prompt)
        
        # Traitement
        with st.chat_message("assistant", avatar="🏛️"):
            with st.spinner("Recherche dans les documents officiels..."):
                # 1. RAG Retrieval
                context, sources = retriever.retrieve_context(sanitized_prompt)
                sources_found = len(sources) > 0
                
                # 2. Génération conditionnée
                response = chat_client.generate_response(sanitized_prompt, context, sources_found)
                
                # 3. Affichage
                st.markdown(response)
                # L'affichage des sources a été désactivé
                    
                    
            # Sauvegarder dans l'historique
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response,
                "sources": sources if sources_found else None
            })

if __name__ == "__main__":
    main()
