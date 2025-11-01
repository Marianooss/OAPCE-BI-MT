import streamlit as st
from agents import (
    DataQualityGuardian, 
    PredictiveModelEngine,
    AnomalyDetector
)
from agents.scheduler import AgentScheduler

def initialize_agents():
    """Inicializa los agentes en la sesión de Streamlit"""
    if 'agents_initialized' not in st.session_state:
        st.session_state.dq_agent = DataQualityGuardian()
        st.session_state.pm_agent = PredictiveModelEngine()
        st.session_state.ad_agent = AnomalyDetector()
        st.session_state.scheduler = AgentScheduler()
        st.session_state.scheduler.start()
        st.session_state.agents_initialized = True

# Inicializar agentes al arrancar la aplicación
initialize_agents()

# ... resto del código de la aplicación ...
