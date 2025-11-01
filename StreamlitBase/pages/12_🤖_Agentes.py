import streamlit as st
from datetime import datetime, timedelta
from agents import (
    DataQualityGuardian,
    PredictiveModelEngine,
    PrescriptiveAdvisor,
    AnomalyDetector
)
from agents.scheduler import AgentScheduler
from db_utils import get_agent_logs

def initialize_agents():
    """Inicializa los agentes si no existen en session_state"""
    if 'agents_initialized' not in st.session_state:
        st.session_state.dq_agent = DataQualityGuardian()
        st.session_state.pm_agent = PredictiveModelEngine()
        st.session_state.pa_agent = PrescriptiveAdvisor()
        st.session_state.ad_agent = AnomalyDetector()
        st.session_state.scheduler = AgentScheduler()
        st.session_state.agents_initialized = True

def render_agent_dashboard():
    st.title("🤖 Centro de Control de Agentes")
    
    # Status general de agentes
    st.subheader("Estado del Sistema")
    cols = st.columns(4)
    
    agents = {
        "Data Quality": st.session_state.dq_agent,
        "Predictive": st.session_state.pm_agent,
        "Prescriptive": st.session_state.pa_agent,
        "Anomaly": st.session_state.ad_agent
    }
    
    for col, (name, agent) in zip(cols, agents.items()):
        with col:
            health = agent.health_check()
            st.metric(
                f"Agente {name}",
                "Activo" if health else "Inactivo",
                delta="OK" if health else "Error",
                delta_color="normal" if health else "inverse"
            )
    
    # Logs recientes
    st.subheader("Actividad Reciente")
    logs = get_agent_logs(limit=10)
    
    if not logs.empty:
        for _, log in logs.iterrows():
            severity = log['status']
            if severity == 'error':
                st.error(f"🚨 {log['agent_name']}: {log['message']}")
            elif severity == 'warning':
                st.warning(f"⚠️ {log['agent_name']}: {log['message']}")
            else:
                st.info(f"ℹ️ {log['agent_name']}: {log['message']}")
    
    # Controles de ejecución
    st.subheader("Control Manual")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Iniciar Todos"):
            st.session_state.scheduler.start()
            st.success("Scheduler iniciado correctamente")
            
    with col2:
        if st.button("⏹️ Detener Todos"):
            st.session_state.scheduler.stop()
            st.warning("Scheduler detenido")

def main():
    initialize_agents()
    render_agent_dashboard()

if __name__ == "__main__":
    main()
