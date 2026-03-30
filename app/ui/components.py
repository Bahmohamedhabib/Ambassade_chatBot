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
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@400;500&display=swap');

            /* =========================================
               1. SURCHARGES & FOND MESH GRADIENT
               ========================================= */
            [data-testid="stHeader"] { display: none !important; height: 0 !important; }
            #MainMenu { visibility: hidden !important; display: none !important; }
            footer { visibility: hidden !important; display: none !important; }

            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 8rem !important;
                max-width: 850px !important;
            }

            .stApp {
                background-color: #fafbfc !important;
                background-image: 
                    radial-gradient(circle at 15% 50%, rgba(247, 127, 0, 0.04) 0%, transparent 50%),
                    radial-gradient(circle at 85% 30%, rgba(0, 128, 51, 0.04) 0%, transparent 50%) !important;
                background-attachment: fixed !important;
                font-family: 'Inter', sans-serif !important;
                color: #1e1e1e !important;
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
               3. CHAT BUBBLES (GLASSMORPHISM)
               ========================================= */
            div[data-testid="stChatMessage"] {
                background: rgba(255, 255, 255, 0.65) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.8) !important;
                border-radius: 24px !important;
                padding: 1.5rem 1.8rem !important;
                margin-bottom: 1.5rem !important;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.04) !important;
                transition: transform 0.3s ease, box-shadow 0.3s ease !important;
                animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
                color: #2d3748 !important;
            }
            div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] li {
                font-size: 1.05rem !important;
                line-height: 1.6 !important;
                color: #2d3748 !important;
                letter-spacing: -0.01em !important;
            }
            div[data-testid="stChatMessage"]:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 12px 40px rgba(31, 38, 135, 0.08) !important;
            }
            div[data-testid="stChatMessageAvatar"] {
                border-radius: 50% !important;
                background: linear-gradient(135deg, #ffffff, #f0f0f0) !important;
                box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
                border: 1px solid rgba(255,255,255,0.8) !important;
            }

            /* =========================================
               4. BARRE DE SAISIE (FLOATING INPUT)
               ========================================= */
            div[data-testid="stChatInput"] {
                padding-bottom: 2rem !important;
                background: transparent !important;
            }
            div[data-testid="stChatInput"] > div {
                background: rgba(255, 255, 255, 0.85) !important;
                backdrop-filter: blur(20px) !important;
                border-radius: 40px !important;
                border: 1px solid rgba(255, 255, 255, 0.6) !important;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08) !important;
                padding: 4px 10px !important;
                transition: all 0.3s ease !important;
            }
            div[data-testid="stChatInput"] > div:focus-within {
                border-color: rgba(247, 127, 0, 0.4) !important;
                box-shadow: 0 15px 50px rgba(247, 127, 0, 0.12) !important;
                transform: translateY(-2px) !important;
                animation: pulseGlow 3s infinite ease-in-out !important;
            }
            div[data-testid="stChatInput"] textarea {
                color: #1a202c !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 1.1rem !important;
            }
            div[data-testid="stChatInput"] textarea:focus {
                outline: none !important;
            }

            /* =========================================
               5. HEADER LUXURY (OUTFIT FONT)
               ========================================= */
            .insti-header-container {
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
                padding: 3.5rem 2rem !important;
                background: linear-gradient(135deg, #008033 0%, #005a22 100%) !important;
                border-radius: 32px !important;
                margin-top: 1.5rem !important;
                margin-bottom: 3.5rem !important;
                box-shadow: 0 20px 50px rgba(0, 128, 51, 0.25), inset 0 2px 0 rgba(255,255,255,0.2) !important;
                color: white !important;
                text-align: center !important;
                position: relative !important;
                overflow: hidden !important;
                width: 100% !important;
                box-sizing: border-box !important;
            }
            /* Lueur orange en haut à droite pour rappeler le drapeau */
            .insti-header-container::after {
                content: '' !important;
                position: absolute !important;
                top: -50px; right: -50px;
                width: 200px; height: 200px;
                background: radial-gradient(circle, rgba(247, 127, 0, 0.8) 0%, transparent 60%);
                filter: blur(40px);
                z-index: 0;
            }
            .insti-title {
                font-family: 'Outfit', sans-serif !important;
                font-size: clamp(2rem, 5vw, 3.2rem) !important;
                font-weight: 700 !important;
                margin: 0 !important;
                letter-spacing: -1px !important;
                line-height: 1.1 !important;
                z-index: 1 !important;
                color: #ffffff !important;
                text-shadow: 0 2px 10px rgba(0,0,0,0.2) !important;
            }
            .insti-subtitle {
                font-family: 'Outfit', sans-serif !important;
                font-size: clamp(1.1rem, 2vw, 1.4rem) !important;
                font-weight: 300 !important;
                margin-top: 1rem !important;
                color: rgba(255,255,255,0.9) !important;
                z-index: 1 !important;
                letter-spacing: 0.5px !important;
            }
            .insti-motto {
                font-family: 'Inter', sans-serif !important;
                font-size: 0.8rem !important;
                font-weight: 600 !important;
                margin-top: 2.5rem !important;
                color: #ffffff !important; 
                letter-spacing: 6px !important;
                text-transform: uppercase !important;
                background: rgba(255, 255, 255, 0.1) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                padding: 10px 30px !important;
                border-radius: 50px !important;
                backdrop-filter: blur(10px) !important;
                z-index: 1 !important;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
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
            div[data-testid="stAlert"] * {
                color: #1e1e1e !important;
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
                    padding: 2.5rem 1rem 2rem 1rem !important;
                    margin-top: 0.5rem !important;
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
