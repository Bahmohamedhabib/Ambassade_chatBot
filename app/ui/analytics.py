import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.db.database import SessionLocal
from app.db.models import InteractionLog

class AnalyticsDashboard:
    """Dashboard Ultra-Moderne de l'activité du Chatbot."""

    @staticmethod
    def _fetch_logs() -> pd.DataFrame:
        db = SessionLocal()
        try:
            logs = db.query(InteractionLog).all()
            if not logs:
                return pd.DataFrame()
                
            data = [{
                "id": log.id,
                "timestamp": log.timestamp,
                "query": log.query,
                "response": log.response_text or "",
                "status": log.response_status,
                "is_malicious": log.is_malicious,
                "token_used": log.token_used or 0
            } for log in logs]
            
            df = pd.DataFrame(data)
            df['date'] = df['timestamp'].dt.date
            return df
        finally:
            db.close()

    @staticmethod
    def _render_kpi_cards(total, success, no_sources, malicious, cost):
        """Affiche des cartes KPI stylisées avec Glassmorphism et CSS personnalisé."""
        st.markdown("""
        <style>
        .kpi-container {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        .kpi-card {
            background: rgba(255, 255, 255, 0.05); /* Pour Dark Mode/Light Mode fluidité */
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 128, 0, 0.3);
            border-radius: 15px;
            padding: 1.5rem;
            flex: 1 1 18%;
            box-shadow: 0 8px 32px 0 rgba(0, 128, 0, 0.1);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(0, 128, 0, 0.2);
        }
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 5px;
            background: linear-gradient(90deg, #008000, #f77f00);
        }
        .kpi-card.alert::before {
            background: linear-gradient(90deg, #d90429, #ef233c);
        }
        .kpi-title {
            font-size: 0.95rem;
            font-weight: 600;
            color: #888;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .kpi-value {
            font-size: 2.2rem;
            font-weight: 800;
            color: #008000;
            margin: 0;
        }
        .kpi-value.alert { color: #d90429; }
        .kpi-value.neutral { color: #f77f00; }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-title">Flux Global</div>
                <div class="kpi-value">{total}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Succès</div>
                <div class="kpi-value">{success}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Inconnues</div>
                <div class="kpi-value neutral">{no_sources}</div>
            </div>
            <div class="kpi-card alert">
                <div class="kpi-title">Menaces Bloquées</div>
                <div class="kpi-value alert">{malicious}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Coût Estimé ($)</div>
                <div class="kpi-value" style="color: #457b9d;">{cost:.4f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_dashboard():
        st.markdown("<h2 style='text-align: center; font-weight: 800; color: #008000; margin-bottom: 2rem; letter-spacing: -1px;'>Intelligence & Surveillance Console</h2>", unsafe_allow_html=True)
        
        df = AnalyticsDashboard._fetch_logs()
        
        if df.empty:
            st.info("L'IA est en attente de sa première interaction. Aucune donnée à analyser.")
            return

        # KPIs
        total_queries = len(df)
        malicious = df['is_malicious'].sum()
        no_sources = len(df[df['status'] == 'NO_SOURCES'])
        success = len(df[df['status'] == 'SUCCESS'])
        total_tokens = df['token_used'].sum()
        estimated_cost = total_tokens * 0.000004
        
        AnalyticsDashboard._render_kpi_cards(total_queries, success, no_sources, malicious, estimated_cost)
        
        # Ligne de graphiques supérieure
        col_flux, col_gauge = st.columns([2.5, 1])
        
        with col_flux:
            st.markdown("### 📈 Pulsation de l'Activité")
            daily_counts = df.groupby('date').size().reset_index(name='count')
            fig_area = px.area(daily_counts, x='date', y='count', 
                               color_discrete_sequence=['#008000'],
                               labels={'date': '', 'count': 'Requêtes'})
            fig_area.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=(dict(showgrid=False)),
                yaxis=(dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')),
                font=dict(family="Inter")
            )
            # Remplissage dégradé
            fig_area.data[0].fill = 'tozeroy'
            fig_area.data[0].fillcolor = 'rgba(0, 128, 0, 0.2)'
            fig_area.data[0].line.width = 3
            
            st.plotly_chart(fig_area, use_container_width=True)
            
        with col_gauge:
            st.markdown("### 🛡️ Niveau de Menace")
            threat_level = (malicious / total_queries * 100) if total_queries > 0 else 0
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = threat_level,
                number = {"suffix": "%", "font": {"size": 40}},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1},
                    'bar': {'color': "rgba(217, 4, 41, 0.8)" if threat_level > 10 else "rgba(0, 128, 0, 0.8)"},
                    'bgcolor': "rgba(0,0,0,0.05)",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 5], 'color': "rgba(0, 128, 0, 0.1)"},
                        {'range': [5, 15], 'color': "rgba(247, 127, 0, 0.2)"},
                        {'range': [15, 100], 'color': "rgba(217, 4, 41, 0.2)"}],
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter"))
            st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown("---")
        
        # Bloc inférieur : Statut et Alertes
        col_pie, col_alert = st.columns([1, 1.5])
        
        with col_pie:
            st.markdown("### 🎯 Typologie des Retours")
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            
            # Palette moderne
            colors = {'SUCCESS': '#008000', 'NO_SOURCES': '#f77f00', 'PROMPT_INJECTION': '#d90429', 'API_ERROR': '#333333'}
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=status_counts['status'], 
                values=status_counts['count'], 
                hole=.6,
                marker=dict(colors=[colors.get(s, '#7f8c8d') for s in status_counts['status']]),
                textinfo='percent+label'
            )])
            fig_pie.update_layout(
                showlegend=False,
                annotations=[dict(text='Distribution', x=0.5, y=0.5, font_size=16, showarrow=False)],
                margin=dict(l=0, r=0, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_alert:
            st.markdown("### 🚨 Radar des Menaces (Récents)")
            df_malicious = df[(df['is_malicious'] == True) | (df['status'] == 'NO_SOURCES')].copy()
            if not df_malicious.empty:
                df_malicious = df_malicious.sort_values(by='timestamp', ascending=False).head(5)
                # Affichage stylisé dataframe
                st.dataframe(
                    df_malicious[['timestamp', 'query', 'status']], 
                    use_container_width=True, 
                    hide_index=True,
                    height=250
                )
            else:
                st.info("✅ Le système RAG est sécurisé. Aucune tentative d'intrusion détectée.")
                
        st.markdown("---")
        st.markdown("### 🧠 Mémoire des Intéractions (Data Log)")
        df_history = df.sort_values(by='timestamp', ascending=False)[['timestamp', 'query', 'response', 'status', 'token_used']]
        st.dataframe(df_history, use_container_width=True, hide_index=True, height=400)
