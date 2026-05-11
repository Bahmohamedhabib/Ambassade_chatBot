import streamlit as st
import time
from app.ui.components import UIComponents
from app.security.input_validation import InputValidator
from app.utils.logger import setup_logger

logger = setup_logger("streamlit_app")

# Configuration de la page
st.set_page_config(
    page_title="Ambassade de Côte d'Ivoire",
    page_icon="🇨🇮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Injection des balises meta pour mobile (viewport, themeColor, etc.)
# Ceci est injecté avant tout autre composant pour garantir le bon rendu mobile.
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#006e2a">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="mobile-web-app-capable" content="yes">
""", unsafe_allow_html=True)

@st.cache_resource
def init_services():
    # Suppression de init_db ici pour accélérer radicalement le démarrage du site public.
    # Imports paresseux pour éviter de bloquer l'initialisation du site public :
    from app.rag.vector_store import VectorStore
    from app.rag.retriever import Retriever
    from app.services.mistral_client import MistralChatClient
    from app.rag.semantic_cache import SemanticCache
    from app.rag.graph import EmbassyGraph

    store = VectorStore()
    retriever = Retriever(store)
    chat_client = MistralChatClient()
    semantic_cache = SemanticCache()
    
    # Initialisation du graphe LangGraph
    graph = EmbassyGraph(retriever, chat_client, semantic_cache, store)
    
    return retriever, chat_client, store, semantic_cache, graph

# ---------------------------------------------------------------------------
# Rate limiting — 15 requêtes max par fenêtre de 5 minutes (par session)
# ---------------------------------------------------------------------------
_RATE_LIMIT_MAX = 15
_RATE_LIMIT_WINDOW = 300  # secondes

def _check_rate_limit():
    """Retourne (True, 0) si autorisé, (False, secondes_restantes) si bloqué."""
    now = time.time()
    if "rl_count" not in st.session_state:
        st.session_state.rl_count = 0
        st.session_state.rl_reset = now + _RATE_LIMIT_WINDOW

    # Réinitialisation automatique de la fenêtre si expirée
    if now > st.session_state.rl_reset:
        st.session_state.rl_count = 0
        st.session_state.rl_reset = now + _RATE_LIMIT_WINDOW

    if st.session_state.rl_count >= _RATE_LIMIT_MAX:
        remaining = int(st.session_state.rl_reset - now)
        logger.warning(f"Rate limit atteint ({_RATE_LIMIT_MAX} req/5min).")
        return False, remaining

    st.session_state.rl_count += 1
    return True, 0

def main():
    # Détection si on est sur la page d'administration via query params
    query_params = st.query_params
    if "admin" in query_params:
        # Import retardé très ciblé (Pandas, Plotly, SQLAlchemy)
        from app.ui.admin_pages import render_admin_dashboard
        render_admin_dashboard()
        return

    UIComponents.render_header()
    UIComponents.render_disclaimer()
    
    # Affichage de l'historique de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Ecran d'accueil si aucun message
    if not st.session_state.messages:
        UIComponents.render_welcome_screen()
        
    for message in st.session_state.messages:
        avatar_icon = "🏛️" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])

    # Le chargement des services (FAISS, Mistral) est retardé jusqu'au premier message (Lazy Loading)
    # Saisie utilisateur
    if prompt := st.chat_input("Posez votre question (ex: Quels documents pour renouveler un passeport ?)"):
        # Afficher la question
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            
        # Rate limiting
        allowed, wait_sec = _check_rate_limit()
        if not allowed:
            minutes = wait_sec // 60
            secondes = wait_sec % 60
            rate_msg = f"Vous avez atteint la limite de {_RATE_LIMIT_MAX} questions par 5 minutes. Merci de patienter encore {minutes}m{secondes:02d}s."
            st.session_state.messages.append({"role": "assistant", "content": rate_msg})
            with st.chat_message("assistant", avatar="🏗️"):
                st.warning(rate_msg)
            return

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
            # Initialisation des services et du graphe
            retriever, chat_client, store, semantic_cache, graph = init_services()
            
            # Exécution du graphe LangGraph
            with st.spinner("Réflexion en cours..."):
                result = graph.run(sanitized_prompt, chat_history)
                
            full_response = result.get("response", "Désolé, je n'ai pas pu générer de réponse.")
            sources = result.get("sources", [])
            sources_found = len(sources) > 0

            # Simulation esthétique du stream — sans PyArrow (st.write_stream en dépend)
            import time
            placeholder = st.empty()
            displayed = ""
            for word in full_response.split():
                displayed += word + " "
                placeholder.markdown(displayed)
                time.sleep(0.01)
                    
            # Sauvegarder dans l'historique
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response,
                "sources": sources if sources_found else None
            })

if __name__ == "__main__":
    main()
