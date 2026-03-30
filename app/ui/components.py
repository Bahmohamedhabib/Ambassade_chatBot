import streamlit as st
import base64
import urllib.request
from typing import List, Dict, Any

class UIComponents:
    """Composants visuels pour l'interface Streamlit de l'Ambassade."""
    
    @staticmethod
    def apply_custom_css():
        """Injecte du CSS personnalisé et hyper-robuste (!important) pour forcer le responsive sur Streamlit."""
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

            /* =========================================
               1. SURCHARGES STRUCTURELLES STREAMLIT 
               ========================================= */
            [data-testid="stHeader"] { display: none !important; height: 0 !important; }
            #MainMenu { visibility: hidden !important; display: none !important; }
            footer { visibility: hidden !important; display: none !important; }

            /* Le conteneur maître : on garde les marges verticales mais on laisse Streamlit gérer max-width */
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 6rem !important;
            }

            .stApp {
                background-color: #f4f7fb !important;
                font-family: 'Inter', sans-serif !important;
            }

            /* =========================================
               2. ANIMATIONS & SCROLLBAR
               ========================================= */
            @keyframes fadeSlideUp {
                0% { opacity: 0; transform: translateY(15px); }
                100% { opacity: 1; transform: translateY(0); }
            }
            @keyframes pulseGlow {
                0% { box-shadow: 0 4px 15px rgba(247, 127, 0, 0.1); }
                50% { box-shadow: 0 4px 25px rgba(247, 127, 0, 0.3); }
                100% { box-shadow: 0 4px 15px rgba(247, 127, 0, 0.1); }
            }

            ::-webkit-scrollbar { width: 6px; height: 6px; }
            ::-webkit-scrollbar-track { background: rgba(0,0,0,0.02); }
            ::-webkit-scrollbar-thumb { background: rgba(0, 128, 0, 0.2); border-radius: 10px; }
            ::-webkit-scrollbar-thumb:hover { background: rgba(0, 128, 0, 0.5); }

            /* =========================================
               3. DESIGN DES BULLES (DESKTOP)
               ========================================= */
            div[data-testid="stChatMessage"] {
                background: rgba(255, 255, 255, 0.85) !important;
                backdrop-filter: blur(10px) !important;
                -webkit-backdrop-filter: blur(10px) !important;
                border: 1px solid rgba(255,255,255,0.4) !important;
                border-radius: 20px !important;
                padding: 1.5rem !important;
                margin-bottom: 24px !important;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04) !important;
                transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s ease !important;
                animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
            }
            div[data-testid="stChatMessage"]:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 15px 35px rgba(0, 128, 0, 0.07) !important;
            }
            div[data-testid="stChatMessageAvatar"] {
                border-radius: 50% !important;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
            }

            /* Champ de saisie utilisateur mis à jour */
            div[data-testid="stChatInput"] {
                padding-bottom: 2rem !important;
            }
            /* Cibler le wrapper au lieu du textarea pour ne pas casser le layout flex du bouton d'envoi */
            div[data-testid="stChatInput"] > div {
                border-radius: 30px !important;
                border: 2px solid transparent !important;
                background-color: #ffffff !important;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06) !important;
                transition: all 0.4s ease !important;
                padding-left: 10px !important;
            }
            div[data-testid="stChatInput"] > div:focus-within {
                border-color: #f77f00 !important;
                animation: pulseGlow 3s infinite ease-in-out !important;
            }
            div[data-testid="stChatInput"] textarea {
                color: #333333 !important;
                font-size: 1.05rem !important;
            }
            div[data-testid="stChatInput"] textarea:focus {
                outline: none !important;
            }

            /* =========================================
               4. HEADER & TYPOGRAPHIE
               ========================================= */
            .insti-header-container {
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
                padding: 3rem 2rem !important;
                background: linear-gradient(135deg, #006600 0%, #008033 50%, #f77f00 100%) !important;
                border-radius: 20px !important;
                margin-top: 0 !important;
                margin-bottom: 3.5rem !important;
                box-shadow: 0 20px 50px rgba(0, 102, 0, 0.2) !important;
                color: white !important;
                text-align: center !important;
                position: relative !important;
                overflow: hidden !important;
                width: 100% !important;
                box-sizing: border-box !important;
            }
            .insti-header-container::before {
                content: '' !important;
                position: absolute !important;
                top: 0; left: 0; right: 0; bottom: 0 !important;
                background: radial-gradient(circle at 20% 150%, rgba(255,255,255,0.1) 0%, transparent 50%),
                            radial-gradient(circle at 80% -50%, rgba(0,0,0,0.2) 0%, transparent 50%) !important;
                pointer-events: none !important;
                z-index: 0 !important;
            }
            .insti-title {
                font-family: 'Inter', sans-serif !important;
                font-size: clamp(1.8rem, 4vw, 2.6rem) !important;
                font-weight: 800 !important;
                margin: 0 !important;
                text-transform: uppercase !important;
                letter-spacing: 2px !important;
                text-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
                line-height: 1.2 !important;
                z-index: 1 !important;
                color: #ffffff !important;
            }
            .insti-subtitle {
                font-family: 'Inter', sans-serif !important;
                font-size: clamp(1rem, 2vw, 1.2rem) !important;
                font-weight: 400 !important;
                margin-top: 1rem !important;
                color: #ffffff !important;
                opacity: 0.9 !important;
                z-index: 1 !important;
            }
            .insti-motto {
                font-family: 'Inter', sans-serif !important;
                font-size: clamp(0.7rem, 1.5vw, 0.85rem) !important;
                font-weight: 700 !important;
                margin-top: 2rem !important;
                color: #ffffff !important; 
                letter-spacing: 5px !important;
                text-transform: uppercase !important;
                background: rgba(255, 255, 255, 0.15) !important;
                border: 1px solid rgba(255, 255, 255, 0.3) !important;
                padding: 8px 24px !important;
                border-radius: 40px !important;
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
                box-shadow: 0 8px 20px rgba(0,0,0,0.15) !important;
                z-index: 1 !important;
            }

            div[data-testid="stAlert"] {
                border-radius: 16px !important;
                border: 1px solid rgba(0, 128, 0, 0.1) !important;
                border-left: 6px solid #f77f00 !important;
                background: linear-gradient(90deg, #ffffff 0%, #fefcfb 100%) !important;
                box-shadow: 0 4px 20px rgba(0,0,0,0.03) !important;
                padding: 1rem 1.5rem !important;
                font-weight: 500 !important;
            }

            /* =========================================
               5. 📱 FIX RESPONSIVE ABSOLU (MOBILE)
               ========================================= */
            @media screen and (max-width: 768px) {
                .block-container {
                    padding-left: 1rem !important;
                    padding-right: 1rem !important;
                    padding-top: 1rem !important;
                    padding-bottom: 5rem !important;
                }

                .insti-header-container {
                    padding: 2rem 1rem !important;
                    margin-bottom: 1.5rem !important;
                    border-radius: 16px !important;
                }
                .insti-title {
                    text-shadow: none !important;
                }
                .insti-motto {
                    padding: 5px 12px !important;
                    margin-top: 1.2rem !important;
                    letter-spacing: 2px !important;
                }

                div[data-testid="stChatMessage"] {
                    padding: 1.2rem !important;
                    margin-bottom: 12px !important;
                    border-radius: 12px !important;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
                }
                div[data-testid="stChatMessage"] p {
                    font-size: 0.95rem !important;
                }

                div[data-testid="stChatMessageAvatar"] {
                    width: 32px !important;
                    height: 32px !important;
                }

                /* Zone de texte mobile - Optimisée */
                div[data-testid="stChatInput"] {
                    padding-bottom: 1rem !important;
                }
                div[data-testid="stChatInput"] > div {
                    border-radius: 24px !important;
                    padding: 5px !important;
                }
                div[data-testid="stChatInput"] textarea {
                    font-size: 16px !important; /* CRITIQUE: Empêche le zoom auto sur iOS et Android */
                }

                div[data-testid="stAlert"] {
                    padding: 0.8rem !important;
                    font-size: 0.85rem !important;
                    border-radius: 12px !important;
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
