import streamlit as st
from auth import check_authentication, login_page, logout, get_current_user
from page_direccion import show_management_dashboard
from page_comercial import show_commercial_dashboard
from page_finanzas import show_finance_dashboard
from page_forms import show_data_forms
from database import init_db
import os

st.set_page_config(
    page_title="OAPCE Multitrans",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_app():
    if not os.path.exists("oapce_multitrans.db"):
        init_db()
        st.info("Inicializando base de datos... Por favor ejecute `python init_db.py` para cargar datos de ejemplo.")

def main():
    initialize_app()
    
    if not check_authentication():
        login_page()
        return
    
    user = get_current_user()
    
    with st.sidebar:
        st.title("🏢 OAPCE Multitrans")
        st.markdown("### Sistema de Control y Gestión")
        
        st.markdown("---")
        
        st.markdown(f"**Usuario:** {user['nombre']}")
        st.markdown(f"**Rol:** {user['rol'].capitalize()}")
        
        st.markdown("---")
        
        st.markdown("### Módulos")
        
        page = st.radio(
            "Seleccione un módulo:",
            [
                "📈 Dirección General",
                "📊 Comercial",
                "💰 Finanzas",
                "📝 Gestión de Datos"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
        
        st.markdown("---")
        st.markdown("##### Información del Sistema")
        st.caption("Versión 1.0")
        st.caption("Grupo OM © 2024")
    
    if page == "📈 Dirección General":
        show_management_dashboard()
    elif page == "📊 Comercial":
        show_commercial_dashboard()
    elif page == "💰 Finanzas":
        show_finance_dashboard()
    elif page == "📝 Gestión de Datos":
        show_data_forms()

if __name__ == "__main__":
    main()
