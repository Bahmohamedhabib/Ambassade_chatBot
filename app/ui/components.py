import streamlit as st
import base64
from typing import List, Dict, Any

class UIComponents:
    """Composants visuels pour l'interface Streamlit de l'Ambassade."""

    @staticmethod
    def apply_custom_css():
        """CSS Mobile-First premium — optimisé pour tous les écrans, clavier mobile inclus."""
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@400;500;600&display=swap');

            /* =============================================
               0. VARIABLES CSS GLOBALES
               ============================================= */
            :root {
                --green-dark:   #004d1a;
                --green-main:   #006e2a;
                --green-light:  #008a35;
                --orange-main:  #f77f00;
                --orange-soft:  #ffa640;
                --white-glass:  rgba(255,255,255,0.72);
                --border-glass: rgba(255,255,255,0.55);
                --shadow-sm:    0 2px 12px rgba(0,0,0,0.06);
                --shadow-md:    0 8px 32px rgba(0,0,0,0.09);
                --shadow-lg:    0 20px 60px rgba(0,0,0,0.13);
                --radius-sm:    12px;
                --radius-md:    20px;
                --radius-lg:    28px;
                --radius-pill:  999px;
                --font-body:    'Inter', system-ui, -apple-system, sans-serif;
                --font-head:    'Outfit', system-ui, sans-serif;
                --text-primary: #1a202c;
                --text-muted:   #4a5568;
                --bg-page:      #f0f4f8;
                --safe-bottom:  env(safe-area-inset-bottom, 0px);
                --safe-top:     env(safe-area-inset-top, 0px);
            }

            /* =============================================
               1. FOND & STRUCTURE PRINCIPALE
               ============================================= */
            [data-testid="stHeader"] { display: none !important; height: 0 !important; }
            #MainMenu, footer, [data-testid="stToolbar"] { display: none !important; visibility: hidden !important; }

            html {
                overscroll-behavior: none;
                -webkit-text-size-adjust: 100%;
            }

            .stApp {
                background-color: var(--bg-page) !important;
                background-image:
                    radial-gradient(ellipse at 10% 20%,  rgba(0,128,51,0.07)  0%, transparent 55%),
                    radial-gradient(ellipse at 90% 80%,  rgba(247,127,0,0.06) 0%, transparent 55%),
                    radial-gradient(ellipse at 50% 100%, rgba(0,78,26,0.04)   0%, transparent 50%) !important;
                background-attachment: fixed !important;
                font-family: var(--font-body) !important;
                color: var(--text-primary) !important;
                overflow-x: hidden !important;
            }

            .block-container {
                padding-top: 0.5rem !important;
                padding-bottom: calc(7rem + var(--safe-bottom)) !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                max-width: 820px !important;
                margin: 0 auto !important;
                box-sizing: border-box !important;
            }

            /* =============================================
               2. ANIMATIONS
               ============================================= */
            @keyframes fadeSlideUp {
                from { opacity: 0; transform: translateY(14px); }
                to   { opacity: 1; transform: translateY(0); }
            }
            @keyframes pulseGlow {
                0%, 100% { box-shadow: 0 8px 32px rgba(0,0,0,0.09), 0 0 0 0 rgba(0,128,51,0.10); }
                50%       { box-shadow: 0 8px 32px rgba(0,0,0,0.09), 0 0 0 5px rgba(0,128,51,0.15); }
            }

            ::-webkit-scrollbar { width: 5px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { background: rgba(0,128,51,0.22); border-radius: 10px; }

            /* =============================================
               3. EN-TÊTE INSTITUTIONNEL
               ============================================= */
            .insti-header-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 2.8rem 2rem 2.4rem;
                background: linear-gradient(145deg, var(--green-light) 0%, var(--green-dark) 100%);
                border-radius: var(--radius-lg);
                margin: 0.8rem 0 1.8rem;
                box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255,255,255,0.18);
                color: white;
                text-align: center;
                position: relative;
                overflow: hidden;
                width: 100%;
                box-sizing: border-box;
                -webkit-user-select: none;
                user-select: none;
            }
            .insti-header-container::before {
                content: '';
                position: absolute;
                top: -60px; right: -60px;
                width: 220px; height: 220px;
                background: radial-gradient(circle, rgba(247,127,0,0.85) 0%, transparent 65%);
                filter: blur(45px);
                pointer-events: none;
                z-index: 0;
            }
            .insti-header-container::after {
                content: '';
                position: absolute;
                bottom: -40px; left: -40px;
                width: 160px; height: 160px;
                background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
                filter: blur(30px);
                pointer-events: none;
                z-index: 0;
            }
            .insti-emblem-wrap {
                position: relative;
                z-index: 1;
                width: clamp(60px, 15vw, 88px);
                height: clamp(60px, 15vw, 88px);
                margin-bottom: 0.9rem;
            }
            .insti-emblem-wrap img {
                width: 100%;
                height: 100%;
                object-fit: contain;
                filter: drop-shadow(0 4px 14px rgba(0,0,0,0.3));
            }
            .insti-title {
                font-family: var(--font-head);
                font-size: clamp(1.5rem, 5.5vw, 2.7rem);
                font-weight: 700;
                margin: 0;
                letter-spacing: -0.5px;
                line-height: 1.15;
                z-index: 1;
                position: relative;
                color: #ffffff;
                text-shadow: 0 2px 12px rgba(0,0,0,0.25);
            }
            .insti-subtitle {
                font-family: var(--font-head);
                font-size: clamp(0.82rem, 3vw, 1.15rem);
                font-weight: 300;
                margin-top: 0.5rem;
                color: rgba(255,255,255,0.88);
                z-index: 1;
                position: relative;
                letter-spacing: 0.3px;
            }
            .insti-motto {
                font-family: var(--font-body);
                font-size: clamp(0.58rem, 1.8vw, 0.73rem);
                font-weight: 600;
                margin-top: 1.6rem;
                color: #ffffff;
                letter-spacing: clamp(2px, 1vw, 5px);
                text-transform: uppercase;
                background: rgba(255,255,255,0.12);
                border: 1px solid rgba(255,255,255,0.25);
                padding: 7px clamp(10px, 4vw, 26px);
                border-radius: var(--radius-pill);
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                z-index: 1;
                position: relative;
            }

            /* =============================================
               4. BULLES DE CHAT (GLASSMORPHISM)
               ============================================= */
            div[data-testid="stChatMessage"] {
                background: var(--white-glass) !important;
                backdrop-filter: blur(18px) saturate(160%) !important;
                -webkit-backdrop-filter: blur(18px) saturate(160%) !important;
                border: 1px solid var(--border-glass) !important;
                border-radius: var(--radius-md) !important;
                padding: 1.1rem 1.4rem !important;
                margin-bottom: 1rem !important;
                box-shadow: var(--shadow-sm) !important;
                animation: fadeSlideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
                color: var(--text-primary) !important;
                overflow-wrap: break-word !important;
                word-break: break-word !important;
            }
            div[data-testid="stChatMessage"] p,
            div[data-testid="stChatMessage"] li {
                font-size: clamp(0.9rem, 3.5vw, 1.04rem) !important;
                line-height: 1.65 !important;
                color: var(--text-primary) !important;
            }
            div[data-testid="stChatMessageAvatar"] {
                border-radius: 50% !important;
                background: linear-gradient(135deg, #f0faf4, #e8f5ec) !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.07) !important;
                border: 1.5px solid rgba(255,255,255,0.9) !important;
                min-width: 36px !important;
                min-height: 36px !important;
            }

            /* =============================================
               5. ZONE DE SAISIE — KEYBOARD-AWARE MOBILE
               ============================================= */
            div[data-testid="stChatInput"] {
                position: -webkit-sticky !important;
                position: sticky !important;
                bottom: 0 !important;
                padding-bottom: calc(0.6rem + var(--safe-bottom)) !important;
                padding-top: 0.5rem !important;
                background: linear-gradient(to top, var(--bg-page) 70%, transparent) !important;
                z-index: 100 !important;
            }
            div[data-testid="stChatInput"] > div {
                background: rgba(255,255,255,0.93) !important;
                backdrop-filter: blur(24px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
                border-radius: var(--radius-pill) !important;
                border: 1.5px solid rgba(255,255,255,0.75) !important;
                box-shadow: var(--shadow-md), 0 0 0 1px rgba(0,128,51,0.05) !important;
                padding: 3px 8px !important;
                transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
            }
            div[data-testid="stChatInput"] > div:focus-within {
                border-color: rgba(0,128,51,0.35) !important;
                box-shadow: var(--shadow-md), 0 0 0 3px rgba(0,128,51,0.10) !important;
                animation: pulseGlow 2.5s infinite ease-in-out !important;
            }
            div[data-testid="stChatInput"] textarea {
                color: var(--text-primary) !important;
                font-family: var(--font-body) !important;
                /* CRITIQUE : 16px minimum pour empêcher le zoom auto sur iOS & Android */
                font-size: max(16px, 1rem) !important;
                line-height: 1.5 !important;
                caret-color: var(--green-main) !important;
                background: transparent !important;
            }
            div[data-testid="stChatInput"] textarea::placeholder {
                color: #9daebf !important;
                font-size: max(16px, 0.95rem) !important;
            }
            div[data-testid="stChatInput"] textarea:focus {
                outline: none !important;
                box-shadow: none !important;
            }
            div[data-testid="stChatInput"] button {
                border-radius: 50% !important;
                background: linear-gradient(135deg, var(--green-light), var(--green-dark)) !important;
                border: none !important;
                min-width: 40px !important;
                min-height: 40px !important;
                box-shadow: 0 4px 14px rgba(0,110,42,0.35) !important;
                transition: transform 0.15s ease, box-shadow 0.15s ease !important;
                -webkit-tap-highlight-color: transparent !important;
            }
            div[data-testid="stChatInput"] button:active {
                transform: scale(0.92) !important;
            }
            div[data-testid="stChatInput"] button svg {
                fill: white !important;
            }

            /* =============================================
               6. ALERTES
               ============================================= */
            div[data-testid="stAlert"] {
                border-radius: var(--radius-sm) !important;
                border: 1px solid rgba(0,128,0,0.08) !important;
                border-left: 5px solid var(--orange-main) !important;
                background: linear-gradient(90deg, #ffffff 0%, #fffdfb 100%) !important;
                box-shadow: var(--shadow-sm) !important;
                padding: 0.9rem 1.2rem !important;
                font-size: clamp(0.82rem, 3vw, 0.95rem) !important;
            }
            div[data-testid="stAlert"] p { color: var(--text-primary) !important; }

            /* =============================================
               7. ÉCRAN D'ACCUEIL (VIDE)
               ============================================= */
            .welcome-hint {
                text-align: center;
                padding: 2rem 0.5rem 1rem;
                color: var(--text-muted);
                font-family: var(--font-body);
                animation: fadeSlideUp 0.7s ease forwards;
            }
            .welcome-hint .hint-icon {
                font-size: clamp(2.4rem, 9vw, 3.2rem);
                display: block;
                margin-bottom: 0.7rem;
                filter: drop-shadow(0 3px 8px rgba(0,128,51,0.22));
            }
            .welcome-hint p {
                font-size: clamp(0.88rem, 3.5vw, 1.02rem);
                margin: 0 0 1.2rem;
                line-height: 1.5;
            }
            .welcome-hint .hint-chips {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                justify-content: center;
            }
            .welcome-hint .chip {
                background: rgba(255,255,255,0.78);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(0,128,51,0.15);
                border-radius: var(--radius-pill);
                padding: 7px 15px;
                font-size: clamp(0.75rem, 2.8vw, 0.88rem);
                color: var(--green-dark);
                font-weight: 500;
                box-shadow: var(--shadow-sm);
                -webkit-tap-highlight-color: transparent;
            }

            /* =============================================
               8. OPTIMISATIONS TACTILES GLOBALES
               ============================================= */
            button, [role="button"], a {
                -webkit-tap-highlight-color: transparent !important;
                touch-action: manipulation !important;
            }

            /* =============================================
               9. RESPONSIVE — PETITS MOBILES (< 380px)
               ============================================= */
            @media screen and (max-width: 380px) {
                .block-container {
                    padding-left: 0.5rem !important;
                    padding-right: 0.5rem !important;
                    padding-bottom: calc(5.5rem + var(--safe-bottom)) !important;
                }
                .insti-header-container {
                    padding: 1.5rem 0.7rem 1.3rem !important;
                    border-radius: var(--radius-md) !important;
                    margin: 0.3rem 0 1rem !important;
                }
                .insti-motto { letter-spacing: 1.5px !important; }
                div[data-testid="stChatMessage"] {
                    padding: 0.75rem 0.9rem !important;
                    border-radius: var(--radius-sm) !important;
                    margin-bottom: 0.6rem !important;
                }
                div[data-testid="stChatMessageAvatar"] {
                    width: 28px !important; height: 28px !important;
                    min-width: 28px !important; min-height: 28px !important;
                }
            }

            /* =============================================
               10. RESPONSIVE — MOBILES STANDARDS (< 768px)
               ============================================= */
            @media screen and (max-width: 768px) {
                .block-container {
                    padding-left: 0.75rem !important;
                    padding-right: 0.75rem !important;
                    padding-bottom: calc(6rem + var(--safe-bottom)) !important;
                }
                .insti-header-container {
                    padding: 1.8rem 0.9rem 1.6rem !important;
                    border-radius: var(--radius-md) !important;
                    margin: 0.4rem 0 1.3rem !important;
                }
                div[data-testid="stChatMessage"] {
                    padding: 0.85rem 1rem !important;
                    border-radius: var(--radius-sm) !important;
                    margin-bottom: 0.7rem !important;
                    /* Hover désactivé sur tactile */
                    transform: none !important;
                    transition: none !important;
                }
                div[data-testid="stChatMessageAvatar"] {
                    width: 32px !important; height: 32px !important;
                    min-width: 32px !important; min-height: 32px !important;
                }
                div[data-testid="stChatInput"] > div {
                    border-radius: var(--radius-lg) !important;
                    padding: 4px 8px !important;
                }
                div[data-testid="stChatInput"] textarea,
                div[data-testid="stChatInput"] textarea::placeholder {
                    /* 16px STRICT pour éviter le zoom iOS/Android */
                    font-size: 16px !important;
                }
                div[data-testid="stChatInput"] button {
                    min-width: 36px !important;
                    min-height: 36px !important;
                }
                div[data-testid="stAlert"] {
                    padding: 0.7rem 0.9rem !important;
                    border-left-width: 4px !important;
                }
            }

            /* =============================================
               11. RESPONSIVE — TABLETTES (769px - 1024px)
               ============================================= */
            @media screen and (min-width: 769px) and (max-width: 1024px) {
                .block-container { max-width: 680px !important; }
                .insti-header-container { padding: 2.5rem 1.5rem !important; }
            }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    @st.cache_data(ttl=3600)
    def get_local_emblem_b64() -> str:
        """Charge l'emblème depuis un fichier local."""
        from pathlib import Path

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
        """Affiche l'en-tête institutionnel complet avec emblème dans le header ET watermark de fond."""
        UIComponents.apply_custom_css()

        b64_image = UIComponents.get_local_emblem_b64()

        # Watermark fixe en fond de page
        watermark_html = ""
        if b64_image:
            watermark_html = f"""
            <img
                src='{b64_image}'
                alt=''
                aria-hidden='true'
                style='
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: clamp(220px, 55vw, 420px);
                    height: auto;
                    opacity: 0.055;
                    z-index: 0;
                    pointer-events: none;
                    user-select: none;
                    -webkit-user-select: none;
                '
            />"""

        # Emblème dans l'en-tête
        emblem_html = ""
        if b64_image:
            emblem_html = f"""
            <div class='insti-emblem-wrap'>
                <img src='{b64_image}' alt="Emblème de la Côte d'Ivoire" />
            </div>"""

        st.markdown(
            f"""
            {watermark_html}
            <div class='insti-header-container'>
                {emblem_html}
                <h1 class='insti-title'>Ambassade de Côte d'Ivoire</h1>
                <p class='insti-subtitle'>Assistant Consulaire &amp; Administratif · France</p>
                <div class='insti-motto'>Union · Discipline · Travail</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def render_disclaimer():
        """Affiche le message d'avertissement formaté."""
        st.info("ℹ️ **Information :** Cet assistant officiel répond exclusivement à partir des directives consulaires validées. Il ne fournit pas de conseils juridiques personnalisés.")

    @staticmethod
    def render_welcome_screen():
        """Affiche l'écran de bienvenue avec des suggestions de questions rapides."""
        st.markdown("""
        <div class='welcome-hint'>
            <span class='hint-icon'>🏛️</span>
            <p>Posez votre question sur les démarches consulaires.<br>
            Je vous réponds à partir des documents officiels de l'Ambassade.</p>
            <div class='hint-chips'>
                <span class='chip'>📄 Documents passeport</span>
                <span class='chip'>🛂 Visa &amp; séjour</span>
                <span class='chip'>📝 Légalisation</span>
                <span class='chip'>⏰ Horaires d'ouverture</span>
                <span class='chip'>📞 Contact consulaire</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
