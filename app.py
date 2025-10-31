import streamlit as st
from auth import check_authentication, login_page, logout, get_current_user
from page_direccion import show_management_dashboard
from page_comercial import show_commercial_dashboard
from page_finanzas import show_finance_dashboard
from page_forms import show_data_forms
from agents_ui import show_data_catalog_page, show_data_pipeline_page, show_predictive_models_page, show_prescriptive_advisor_page, show_data_quality_page, show_anomaly_detector_page, show_ssbf_page, show_generative_assistant_page, show_system_health_page, show_data_import_page
from database import init_db
import os

# Performance optimization: Cache expensive operations
# ZERO-BUDGET OPTIMIZATIONS FOR FREE TIERS
@st.cache_data(ttl=7200)  # Cache for 2 hours (maximizar cache gratis)
def get_app_config():
    """Get application configuration with extended caching"""
    return {
        "title": "OAPCE BI Pro - IA para Pymes Chilenas",
        "icon": "🚀",
        "layout": "wide",
        "sidebar_state": "expanded"
    }

@st.cache_data(ttl=3600)  # Cache for 1 hour (check less frequently)
def check_database_exists():
    """Check if database exists with caching"""
    return os.path.exists("oapce_multitrans.db")

@st.cache_data(ttl=7200)  # Cache for 2 hours (navigation rarely changes)
def get_navigation_modules():
    """Get navigation modules with caching"""
    return [
        "📈 Dirección General",
        "📊 Comercial",
        "💰 Finanzas",
        "📝 Gestión de Datos",
        "📤 Importación de Datos",
        "🤖 Agentes IA (9 Agentes Disponibles)",
        "🆘 Ayuda & Guía"
    ]

# AGENTS MODULAR LOADING FOR FREE TIERS
@st.cache_data(ttl=3600)
def load_agents_lightweight():
    """Load only essential agents on startup for faster loading"""
    return {
        "catalog_ready": True,
        "pipeline_ready": True,
        "ai_agents_ready_count": 7
    }

st.set_page_config(
    page_title=get_app_config()["title"],
    page_icon=get_app_config()["icon"],
    layout=get_app_config()["layout"],
    initial_sidebar_state=get_app_config()["sidebar_state"],
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': 'OAPCE Multitrans v1.0 - Grupo OM © 2024'
    }
)

def initialize_app():
    if not check_database_exists():
        init_db()
        st.info("Inicializando base de datos... Por favor ejecute `python init_db.py` para cargar datos de ejemplo.")
    else:
        st.success("Base de datos cargada correctamente")

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_sidebar_info(user):
    """Get sidebar information with caching"""
    return {
        "title": "🏢 OAPCE Multitrans",
        "subtitle": "### Sistema de Control y Gestión",
        "user_info": f"**Usuario:** {user['nombre']}",
        "role_info": f"**Rol:** {user['rol'].capitalize()}",
        "version": "Versión 1.0",
        "copyright": "Grupo OM © 2024"
    }

def main():
    # Optimize performance by reducing unnecessary re-renders
    st.markdown("""
        <style>
        /* Use system fonts for better performance - no @import needed */
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }

        /* Performance optimizations */
        .stButton button {
            width: 100%;
        }
        /* Reduce layout shifts */
        .main .block-container {
            padding-top: 2rem;
        }
        /* Improve font rendering */
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        </style>
    """, unsafe_allow_html=True)

    initialize_app()

    if not check_authentication():
        login_page()
        return

    user = get_current_user()

    # Use cached sidebar information
    sidebar_info = get_sidebar_info(user)

    with st.sidebar:
        st.image("Bioss logo.png", use_container_width=True)
        st.title(sidebar_info["title"])
        st.markdown(sidebar_info["subtitle"])

        st.markdown("---")

        st.markdown(sidebar_info["user_info"])
        st.markdown(sidebar_info["role_info"])

        st.markdown("---")

        st.markdown("### Módulos")

        # Use cached navigation modules
        modules = get_navigation_modules()
        page = st.radio(
            "Seleccione un módulo:",
            modules,
            label_visibility="collapsed"
        )

        st.markdown("---")

        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()

        st.markdown("---")
        st.markdown("##### Información del Sistema")
        st.caption(sidebar_info["version"])
        st.caption(sidebar_info["copyright"])

    # Route to appropriate dashboard with performance optimization
    if page == "📈 Dirección General":
        show_management_dashboard()
    elif page == "📊 Comercial":
        show_commercial_dashboard()
    elif page == "💰 Finanzas":
        show_finance_dashboard()
    elif page == "📝 Gestión de Datos":
        show_data_forms()
    elif page == "📤 Importación de Datos":
        show_data_import_page()
    elif page == "🤖 Agentes IA":
        st.title("🤖 Agentes IA - Plataforma de BI Autónoma")
        st.markdown("**Selecciona el agente que deseas usar:**")

        # Agentes disponibles en tabs
        tab_pme, tab_pa, tab_ad, tab_dqg, tab_dpo, tab_dcm, tab_ssbf, tab_gda, tab_si = st.tabs([
            "🎯 PME - Modelos Predictivos",
            "💡 PA - Asesor Prescriptivo",
            "🚨 AD - Detector Anomalías",
            "🔍 DQG - Calidad Datos",
            "🔄 DPO - Pipeline Datos",
            "📚 DCM - Catálogo Datos",
            "📊 SSBF - BI Autoservicio",
            "🤖 GDA - Asistente IA",
            "🏥 SI - Estado Sistema"
        ])

        with tab_pme:
            st.subheader("🔮 Modelos Predictivos Inteligentes")
            st.info("🎯 **Agente funcional y listo para uso en tiempo real.**")
            show_predictive_models_page()

        with tab_pa:
            show_prescriptive_advisor_page()

        with tab_ad:
            show_anomaly_detector_page()

        with tab_dqg:
            show_data_quality_page()

        with tab_dpo:
            show_data_pipeline_page()

        with tab_dcm:
            show_data_catalog_page()

        with tab_ssbf:
            show_ssbf_page()

        with tab_gda:
            show_generative_assistant_page()

        with tab_si:
            show_system_health_page()
    elif page == "🆘 Ayuda & Guía":
        show_help_and_guide_page()

def show_help_and_guide_page():
    """Página completa de ayuda y guía de uso interactiva"""
    st.title("🆘 Ayuda & Guía - OAPCE BI Pro")
    st.markdown("**Sistema Inteligente de BI Empresarial - Guía completa de uso**")

    # Pestañas principales
    tab1, tab2 = st.tabs(["📋 Guía por Módulo", "🤖 Guía por Agente IA"])

    # TAB 1: GUÍA POR MÓDULO
    with tab1:
        st.markdown("### 🎯 UTILIDAD DE AGENTES POR MÓDULO")

        # DIRECCIÓN GENERAL
        with st.expander("📈 DIRECCIÓN GENERAL - Toma de decisiones estratégicas", expanded=True):
            st.markdown("**Dashboard ejecutivo para CEOs y directores**")

            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("""
                **🔮 PME (Modelos Predictivos):**
                - Predice tendencias del negocio
                - Anticipa escenarios futuros
                - Base para decisiones estratégicas

                **💡 PA (Asesor Prescriptivo):**
                - Recomendaciones estratégicas automáticas
                - Acciones con máximo impacto
                - Guía para crecimiento sostenible
                """)
            with col2:
                st.markdown("""
                **📊 SSBF (BI Autoservicio):**
                - Dashboards personalizados ejecutivos
                - Visualizaciones estratégicas perfectas
                - Comunicación efectiva con stakeholders

                **🚨 AD (Detector de Anomalías):**
                - Alertas de irregularidades críticas
                - Monitoreo continuo de KPIs estratégicos
                - Riesgo reducido por acción preventiva
                """)

        # COMERCIAL
        with st.expander("📊 COMERCIAL - Gestión inteligente de ventas"):
            st.markdown("**Optimización del equipo comercial y forecasting de ventas**")

            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("""
                **🔮 PME (Forecasting Ventas):**
                - Predicción exacta de cierres en pipeline
                - Planning de cuotas por IA
                - 85% accuracy en forecasting

                **📚 DCM (Datos de Clientes):**
                - Insights instantáneos de comportamiento
                - Preparación meetings de ventas
                - Segmentación automática
                """)
            with col2:
                st.markdown("""
                **💡 PA (Coaching Automático):**
                - Acciones específicas para conversión
                - Mejora productividad del equipo
                - Recomendaciones personalizadas

                **🚨 AD (Monitor de Ventas):**
                - Alertas de caídas anormales
                - Intervención inmediata en problemas
                - Tendencias negativas detected
                """)

        # FINANZAS
        with st.expander("💰 FINANZAS - Control inteligente del cash flow"):
            st.markdown("**Gestión financiera proactiva con forecasting preciso**")

            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("""
                **🔮 PME (Forecasting Financiero):**
                - Predicción flujo de caja futuro
                - Budgeting automático
                - Decisiones financieras acertadas

                **🔄 DPO (Consolidación Data):**
                - ETL automático de datos contables
                - Estados financieros actualizados
                - Eliminación errores manuales
                """)
            with col2:
                st.markdown("""
                **🚨 AD (Detección Fraudes):**
                - Alertas transacciones inusuales
                - Prevención de irregularidades
                - Compliance financiero automático

                **💡 PA (Optimización Financiera):**
                - Mejora automática de ratios
                - Optimización cuentas por cobrar/pagar
                - Recomendaciones de inversión
                """)

        # GESTIÓN DE DATOS
        with st.expander("📝 GESTIÓN DE DATOS - Calidad y accesibilidad"):
            st.markdown("**Mantenimiento de la calidad fundamental de datos**")

            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("""
                **🔄 DPO (ETL Automatizado):**
                - Integración automática de fuentes
                - Escalabilidad infinita de data
                - Procesamiento sin intervención

                **🔍 DQG (Calidad 24/7):**
                - Monitoreo continuo calidad data
                - Alertas cuando baja de estándares
                - decision-making confiable
                """)
            with col2:
                st.markdown("""
                **📚 DCM (Catálogo Inteligente):**
                - Inventario automático datasets
                 - Descubrimiento fácil para usuarios
                  - Democratización del acceso data

                **🚨 AD (Problemas en Pipelines):**
                - Alertas cuando data deja de actualizarse
                - Monitoreo integridad pipelines
                - Sistemas siempre operativos

                **💡 PA (Arquitectura Data):**
                - Optimización automática warehouse
                - Sugerencias de índices particionado
                - Mejor performance y menores costos
                """)

    # TAB 2: GUÍA POR AGENTE IA
    with tab2:
        st.markdown("### 🤖 UTILIDAD INDIVIDUAL DE CADA AGENTE IA")
        st.markdown("**Qué hace exactamente cada agente y cómo usarlo**")

        # DCM
        with st.expander("📚 DCM - CATÁLOGO DE DATOS INTELIGENTE"):
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("""
                **¿Qué hace?**
                Explora automáticamente todo el ecosistema data

                **Para Empresa:**
                Inventario inteligente de 170 columnas y 17 tablas

                **Caso típico:**
                "Necesito datos clientes con actividad últimos 6 meses"
                """)
            with col2:
                st.markdown("""
                **Cómo usar:**
                - Busca por nombre, descripción, tipo o etiquetas
                - Resultados automatico de segundos

                **Valor:**
                Ahorro 2+ horas diarias en búsquedas manuales
                """)

        # DPO
        with st.expander("🔄 DPO - PIPELINE DE DATOS"):
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("""
                **¿Qué hace?**
                ETL automatizado con calidad integrada

                **Para Empresa:**
                Procesamiento automático de 1000+ registros

                **Caso típico:**
                "Actualizar datos facturas desde producción a warehouse"
                """)
            with col2:
                st.markdown("""
                **Cómo usar:**
                - Selecciona tabla origen
                - Sistema procesa automáticamente

                **Valor:**
                Eliminación completa de procesos ETL manuales
                """)

        # PME
        with st.expander("🔮 PME - MODELOS PREDICTIVOS"):
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("""
                **¿Qué hace?**
                Forecasting inteligente con IA

                **Para Empresa:**
                Predicciones con 85%+ accuracy

                **Caso típico:**
                "Pronosticar ventas próximo trimestre"
                """)
            with col2:
                st.markdown("""
                **Cómo usar:**
                - Ejecuta modelos entrenados automáticamente
                - Forecasting futuro del negocio

                **Valor:**
                Decisiones más acertadas y rentables
                """)

        # PA
        with st.expander("💡 PA - ASESOR PRESCRIPTIVO"):
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("""
                **¿Qué hace?**
                Recomendaciones inteligentes ejecutables

                **Para Empresa:**
                Mejores prácticas con acciones contextuales

                **Caso típico:**
                "Recomendaciones para mejorar conversión clientes"
                """)
            with col2:
                st.markdown("""
                **Cómo usar:**
                - Sistema analiza data
                - Sugiere acciones específicas

                **Valor:**
                Mejora automática de KPIs críticos
                """)

        # DQG
        with st.expander("🔍 DQG - GUARDIÁN DE CALIDAD"):
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("""
                **¿Qué hace?**
                Vigilancia 24/7 calidad de datos

                **Para Empresa:**
                Validación data integrity en tiempo real

                **Caso típico:**
                "Auditar calidad base datos clientes"
                """)
            with col2:
                st.markdown("""
                **Cómo usar:**
                - Ejecuta diagnóstico completo
                - Scorecard calidad automático

                **Valor:**
                40% reducción problemas por data inconsistente
                """)

        # AD
        with st.expander("🚨 AD - DETECTOR DE ANOMALÍAS"):
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("""
                **¿Qué hace?**
                Alertas inteligentes de problemas/oportunidades

                **Para Empresa:**
                Detección automática patrones inusuales

                **Caso típico:**
                "Detectar si ventas inusuales esta semana"
                """)
            with col2:
                st.markdown("""
                **Cómo usar:**
                - Selecciona métrica (ventas, flujo caja)
                - Sistema detecta anomalías automáticamente

                **Valor:**
                Riesgos reducidos, oportunidades maximizadas
                """)

        # SSBF
        with st.expander("📊 SSBF - BI AUTOSERVICIO"):
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("""
                **¿Qué hace?**
                Dashboards personalizados sin conocimientos técnicos

                **Para Empresa:**
                BI personalizado para cada rol/usuario

                **Caso típico:**
                "Crear dashboard ejecutivo con KPIs personalizados"
                """)
            with col2:
                st.markdown("""
                **Cómo usar:**
                - Define métricas personalizadas
                - Sistema construye dashboards automáticamente

                **Valor:**
                Cada usuario tiene vista perfecta de empresa
                """)

if __name__ == "__main__":
    main()
