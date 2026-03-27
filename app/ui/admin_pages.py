import streamlit as st
import pandas as pd
from app.admin.auth import AuthManager
from app.admin.document_manager import DocumentManager
from app.rag.indexer_from_db import reindex_all_documents
from app.ui.analytics import AnalyticsDashboard

def render_login_page():
    """Affiche la page de connexion sécurisée."""
    st.markdown("<h2 style='text-align: center; color: #008000;'>Connexion Administrateur</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div style='max-width: 400px; margin: auto;'>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submitted:
                # Protection de base (brute force etc. serait mieux gérée via rate limit API)
                if AuthManager.authenticate_admin(username, password):
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_username = username
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects. Accès refusé.")
        st.markdown("</div>", unsafe_allow_html=True)

def render_admin_dashboard():
    """Point d'entrée principal du dashboard admin."""
    if not st.session_state.get("admin_logged_in", False):
        render_login_page()
        st.stop()
        
    st.sidebar.title(f"Admin: {st.session_state.get('admin_username', 'User')}")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Se déconnecter", use_container_width=True):
        st.session_state.admin_logged_in = False
        st.rerun()

    menu = ["🏠 Vue d'ensemble", "📄 Gestion Documents", "📊 Statistiques & API", "⚠️ Sécurité & Logs"]
    choice = st.sidebar.radio("Navigation", menu)
    
    st.markdown(f"<h2 style='color: #008000;'>{choice}</h2>", unsafe_allow_html=True)
    
    if choice == "🏠 Vue d'ensemble":
        st.info("Bienvenue dans le centre de contrôle de l'Ambassade de Côte d'Ivoire.")
    elif choice == "📄 Gestion Documents":
        st.subheader("Documents enregistrés dans la base de données")
        docs = DocumentManager.get_all_documents()
        
        if docs:
            df = pd.DataFrame(docs)
            st.dataframe(df, use_container_width=True)
            
            # Formulaire de suppression rapide
            col1, col2 = st.columns([3, 1])
            with col1:
                doc_to_delete = st.selectbox("Sélectionner un document à supprimer", [d['id'] for d in docs], format_func=lambda x: next(d['filename'] for d in docs if d['id'] == x))
            with col2:
                st.write("") # espacement
                st.write("")
                if st.button("🗑️ Supprimer", type="primary"):
                    if DocumentManager.delete_document(doc_to_delete):
                        st.success("Document supprimé avec succès.")
                        # Réindexation après suppression
                        with st.spinner("Mise à jour de l'index IA..."):
                            reindex_all_documents()
                            st.cache_resource.clear() # Force le RAG à recharger le nouvel index
                        st.rerun()
        else:
            st.info("Aucun document actuellement dans la base de données.")
            
        st.markdown("---")
        st.subheader("Charger un nouveau document (PDF, TXT)")
        
        with st.form("upload_form", clear_on_submit=True):
            uploaded_file = st.file_uploader("Choisissez un fichier", type=['pdf', 'txt'])
            category = st.selectbox("Catégorie", ["Général", "Passeport", "Visa", "Légalisation", "État Civil"])
            submit_upload = st.form_submit_button("Sauvegarder et Indexer")
            
            if submit_upload and uploaded_file is not None:
                file_bytes = uploaded_file.read()
                DocumentManager.upload_document(uploaded_file.name, file_bytes, category)
                st.success(f"Fichier {uploaded_file.name} sauvegardé avec succès en base de données !")
                
                # Attente visuelle le temps d'indexer
                with st.spinner("Indexation du document dans l'Intelligence Artificielle..."):
                    reindex_all_documents()
                    st.cache_resource.clear() # Force le RAG à recharger le nouvel index
                    
                st.rerun()
    elif choice == "📊 Statistiques & API":
        AnalyticsDashboard.render_dashboard()
    elif choice == "⚠️ Sécurité & Logs":
        st.warning("Journal de sécurité fusionné dans le Dashboard Statistiques pour l'instant.")
