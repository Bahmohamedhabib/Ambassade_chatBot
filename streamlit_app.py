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

@st.cache_resource
def init_services():
    # Suppression de init_db ici pour accélérer radicalement le démarrage du site public.
    # L'initialisation base de données ne doit se faire que pour le panneau d'admin.

    store = VectorStore()
    retriever = Retriever(store)
    chat_client = MistralChatClient()
    from app.rag.semantic_cache import SemanticCache
    semantic_cache = SemanticCache()
    return retriever, chat_client, store, semantic_cache

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

    # Le chargement des services (FAISS, Mistral) est retardé jusqu'au premier message (Lazy Loading)
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
        
        # Extraction de l'historique de conversation (sans la question actuelle)
        chat_history = st.session_state.messages[:-1]
        
        # Traitement
        with st.chat_message("assistant", avatar="🏛️"):
            # Initialisation (ou récupération du cache) des cerveaux de l'IA (Lazy Load ultra-rapide)
            retriever, chat_client, store, semantic_cache = init_services()
            
            # 1. ROUTING : Détection d'intention conversationnelle locale (sans API Mistral)
            if InputValidator.is_conversational(sanitized_prompt):
                local_response = InputValidator.get_conversational_response(sanitized_prompt)
                
                # Simulation esthétique du stream pour la continuité de l'expérience
                import time
                def stream_local():
                    for word in local_response.split():
                        yield word + " "
                        time.sleep(0.04)
                        
                full_response = st.write_stream(stream_local())
                sources_found = False
                sources = []
            
            # 2. RAG : Pipeline standard pour toutes les requêtes d'information
            else:
                # --- VÉRIFICATION DU CACHE SÉMANTIQUE ---
                cached_response = None
                query_emb = None
                
                # On n'utilise le cache que sur le premier message de la conversation
                if not chat_history:
                    query_emb = store.get_embedding(sanitized_prompt)
                    cached_response = semantic_cache.check_cache(query_emb, threshold=0.95)
                
                if cached_response:
                    # ⚡ CACHE HIT
                    import time
                    def stream_cache():
                        yield "⚡ *(Réponse optimisée : Cache Sémantique)*\n\n"
                        for word in cached_response.split():
                            yield word + " "
                            time.sleep(0.015)
                            
                    full_response = st.write_stream(stream_cache())
                    sources_found = False
                    sources = []
                    
                else:
                    # ❄️ CACHE MISS : Exécution Normale
                    with st.spinner("Recherche dans les documents officiels..."):
                        search_query = sanitized_prompt
                        if chat_history:
                            search_query = chat_client.rewrite_query(sanitized_prompt, chat_history)

                        context, sources = retriever.retrieve_context(search_query)
                        sources_found = len(sources) > 0
                        
                    response_stream = chat_client.generate_response_stream(sanitized_prompt, context, sources_found, history=chat_history)
                    full_response = st.write_stream(response_stream)
                    
                    # Ajout au cache sémantique si c'est une question indépendante et qu'on a trouvé des sources
                    if not chat_history and sources_found and query_emb is not None:
                        semantic_cache.add_to_cache(query_emb, sanitized_prompt, full_response)
                    
            # Sauvegarder dans l'historique
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response,
                "sources": sources if sources_found else None
            })

if __name__ == "__main__":
    main()
