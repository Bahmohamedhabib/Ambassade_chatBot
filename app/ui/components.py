import streamlit as st
import base64
import urllib.request
from typing import List, Dict, Any

class UIComponents:
    """Composants visuels pour l'interface Streamlit de l'Ambassade."""
    
    @staticmethod
    def apply_custom_css():
        """Injecte du CSS personnalisé pour un rendu institutionnel et premium."""
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

            /* Animations de base */
            @keyframes fadeSlideUp {
                0% { opacity: 0; transform: translateY(20px); }
                100% { opacity: 1; transform: translateY(0); }
            }

            @keyframes pulseGlow {
                0% { box-shadow: 0 4px 15px rgba(247, 127, 0, 0.1); }
                50% { box-shadow: 0 4px 25px rgba(247, 127, 0, 0.3); }
                100% { box-shadow: 0 4px 15px rgba(247, 127, 0, 0.1); }
            }

            /* Cacher les menus Streamlit */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}

            /* Typographie et fond global */
            .stApp {
                background-color: #f4f7fb;
                font-family: 'Inter', sans-serif;
            }

            /* Custom Webkit Scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            ::-webkit-scrollbar-track {
                background: rgba(0,0,0,0.02); 
            }
            ::-webkit-scrollbar-thumb {
                background: rgba(0, 128, 0, 0.2); 
                border-radius: 10px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(0, 128, 0, 0.5); 
            }

            /* Zone de Chat : bulles avec animation et glassmorphism */
            div[data-testid="stChatMessage"] {
                background: rgba(255, 255, 255, 0.85);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.4);
                border-radius: 20px;
                padding: 1.5rem;
                margin-bottom: 24px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
                transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s ease;
                animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            }
            div[data-testid="stChatMessage"]:hover {
                transform: translateY(-3px) scale(1.01);
                box-shadow: 0 15px 35px rgba(0, 128, 0, 0.07);
            }

            /* Avatar du Chat */
            div[data-testid="stChatMessageAvatar"] {
                border-radius: 50%;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            }

            /* Champ de saisie utilisateur */
            div[data-testid="stChatInput"] {
                padding-bottom: 2rem;
            }
            div[data-testid="stChatInput"] textarea {
                border-radius: 30px !important;
                border: 2px solid transparent !important;
                background-color: #ffffff;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06) !important;
                transition: all 0.4s ease !important;
                padding-left: 20px !important;
                font-size: 1.05rem;
            }
            div[data-testid="stChatInput"] textarea:focus {
                border-color: #f77f00 !important;
                background-color: #fffbf5 !important;
                animation: pulseGlow 3s infinite ease-in-out;
                outline: none !important;
            }

            /* Conteneur d'en-tête (Header) */
            .insti-header-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 4.5rem 2rem 3rem 2rem;
                background: linear-gradient(135deg, #006600 0%, #008033 50%, #f77f00 100%);
                border-radius: 0 0 50px 50px;
                margin-top: -80px; 
                margin-bottom: 4rem;
                box-shadow: 0 20px 50px rgba(0, 102, 0, 0.2);
                color: white;
                text-align: center;
                position: relative;
                overflow: hidden;
            }

            /* Overlay élégant type mesh gradient */
            .insti-header-container::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: radial-gradient(circle at 20% 150%, rgba(255,255,255,0.1) 0%, transparent 50%),
                            radial-gradient(circle at 80% -50%, rgba(0,0,0,0.2) 0%, transparent 50%);
                pointer-events: none;
                z-index: 0;
            }

            .insti-title {
                font-family: 'Inter', sans-serif;
                font-size: 2.6rem;
                font-weight: 800;
                margin: 0;
                text-transform: uppercase;
                letter-spacing: 2px;
                color: #ffffff;
                text-shadow: 0 4px 15px rgba(0,0,0,0.3);
                line-height: 1.2;
                z-index: 1;
            }

            .insti-subtitle {
                font-family: 'Inter', sans-serif;
                font-size: 1.2rem;
                font-weight: 400;
                margin-top: 1rem;
                color: #ffffff;
                opacity: 0.9;
                letter-spacing: 0.5px;
                z-index: 1;
            }

            /* La devise ivoirienne encapsulée façon Glassmorphism */
            .insti-motto {
                font-family: 'Inter', sans-serif;
                font-size: 0.85rem;
                font-weight: 700;
                margin-top: 2rem;
                color: #ffffff; 
                letter-spacing: 5px;
                text-transform: uppercase;
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 8px 24px;
                border-radius: 40px;
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
                z-index: 1;
                transition: background 0.3s, transform 0.3s;
            }
            .insti-motto:hover {
                background: rgba(255, 255, 255, 0.25);
                transform: translateY(-2px);
            }
            
            /* Message d'info (Disclaimer) */
            div[data-testid="stAlert"] {
                border-radius: 16px;
                border: 1px solid rgba(0, 128, 0, 0.1);
                border-left: 6px solid #f77f00;
                background: linear-gradient(90deg, #ffffff 0%, #fefcfb 100%);
                box-shadow: 0 4px 20px rgba(0,0,0,0.03);
                padding: 1rem 1.5rem;
                font-weight: 500;
            }

            /* 📱 RESPONSIVE DESIGN (Mobile & Android) */
            @media screen and (max-width: 768px) {
                /* Header / En-tête */
                .insti-header-container {
                    padding: 4rem 1rem 1.5rem 1rem;
                    margin-top: -60px;
                    margin-bottom: 2rem;
                    border-radius: 0 0 30px 30px;
                }
                .insti-title {
                    font-size: 1.6rem;
                    letter-spacing: 1px;
                }
                .insti-subtitle {
                    font-size: 0.95rem;
                    margin-top: 0.6rem;
                }
                .insti-motto {
                    font-size: 0.65rem;
                    padding: 6px 16px;
                    margin-top: 1.5rem;
                    letter-spacing: 3px;
                }

                /* Chat Bubbles */
                div[data-testid="stChatMessage"] {
                    padding: 1rem;
                    margin-bottom: 16px;
                    border-radius: 14px;
                }
                div[data-testid="stChatMessage"] p {
                    font-size: 0.95rem;
                }

                /* Chat Input (évite le zoom auto sur iOS et s'adapte à l'écran) */
                div[data-testid="stChatInput"] {
                    padding-bottom: 0.5rem;
                }
                div[data-testid="stChatInput"] textarea {
                    font-size: 16px !important; /* Empêche le zoom Safari iOS */
                    padding-left: 15px !important;
                }

                /* Alertes */
                div[data-testid="stAlert"] {
                    padding: 0.8rem 1rem;
                    font-size: 0.9rem;
                }
            }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    @st.cache_data(ttl=3600)
    def get_local_emblem_b64() -> str:
        """Charge l'emblème depuis un fichier local."""
        from pathlib import Path
        import base64
        
        possible_paths = [
            Path("app/ui/emblem.png"),
            Path("data/raw/emblem.png"),
            Path("emblem.png")
        ]
        
        for path in possible_paths:
            if path.exists():
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                    return f"data:image/png;base64,{b64}"
        return ""

    @staticmethod
    def render_header():
        """Affiche l'en-tête institutionnel complet avec l'emblème."""
        UIComponents.apply_custom_css()
        
        b64_image = UIComponents.get_local_emblem_b64()
        
        # Le watermark est injecté directement avec Base64 s'il a été trouvé
        img_html = ""
        if b64_image:
            img_html = f"<img src='{b64_image}' style='position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 50vw; height: auto; opacity: 0.08; z-index: 999999; pointer-events: none;' alt='' />"
        else:
            st.error("💡 Emblème introuvable ! Placez le fichier emblem.png dans le dossier app/ui/")
        
        st.markdown(
            f"""
            {img_html}
            <div class='insti-header-container'>
                <h1 class='insti-title'>Ambassade de Côte d'Ivoire</h1>
                <h3 class='insti-subtitle'>Assistant Consulaire & Administratif en France</h3>
                <div class='insti-motto'>Union - Discipline - Travail</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def render_disclaimer():
        """Affiche le message d'avertissement formaté."""
        st.info("ℹ️ **Information :** Cet assistant officiel répond exclusivement à partir des directives consulaires validées. Il ne fournit pas de conseils juridiques personnalisés.")
