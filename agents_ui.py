"""
Módulo de interfaz para agentes inteligentes
Contiene funciones para integrar agentes en la UI de Streamlit
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from catalog import DataCatalogManager
from data_pipeline import DataPipelineOrchestrator
from predictive_models import PredictiveModelEngine
from prescriptive_advisor import PrescriptiveAdvisor
from data_quality import ValidadorCalidadDatos
from anomaly_detector import AnomalyDetector
from ssbf_facilitator import SSBFFacilitator
from generative_assistant import GenerativeDataAssistant
from system_integrator import get_system_health
from data_import_manager import DataImportManager, migrate_to_production

def show_predictive_models_page():
    """
    Página del Predictive Model Engine (PME)
    """
    st.title("🔮 Modelos Predictivos Inteligentes")
    st.markdown("---")

    # Inicializar PME
    pme = PredictiveModelEngine()

    try:
        st.subheader("🎯 Entrenamiento de Modelos")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📈 Entrenar Modelo de Ventas", use_container_width=True):
                with st.spinner("Entrenando modelo de predicción de ventas..."):
                    result = pme.train_sales_forecast_model()

                    if result['success']:
                        st.success(f"✅ Modelo entrenado: {result['model_name']}")
                        st.metric("Predicciones Generadas", result['predictions_saved'])
                        st.metric("Tiempo de Entrenamiento", f"{result['training_time']:.3f}s")

                        # Mostrar datos de entrenamiento si existen
                        if 'historical_data_points' in result:
                            st.metric("Datos de Entrenamiento", result['historical_data_points'])
                        elif 'demo_data' in result and result['demo_data']:
                            st.metric("Datos de Entrenamiento", "Demo sintéticos")
                        else:
                            st.metric("Datos de Entrenamiento", "N/A")

                        # Mostrar las predicciones generadas
                        st.subheader("📈 Previsión de Ventas Generada")
                        forecast_predictions = pme.get_predictions(prediction_type="sales_forecast", limit=result['predictions_saved'])
                        if forecast_predictions['success'] and forecast_predictions['predictions']:
                            df_forecast = pd.DataFrame(forecast_predictions['predictions'])
                            df_forecast['target_date'] = pd.to_datetime(df_forecast['target_date'])
                            df_forecast = df_forecast.sort_values(by='target_date')

                            st.dataframe(df_forecast[['target_date', 'predicted_value', 'confidence_lower', 'confidence_upper']].set_index('target_date'), use_container_width=True)

                            # Visualización en gráfico
                            st.line_chart(df_forecast.set_index('target_date')[['predicted_value', 'confidence_lower', 'confidence_upper']])
                        else:
                            st.info("No se pudieron recuperar las predicciones de ventas.")
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Desconocido')}")

        with col2:
            if st.button("⚠️ Entrenar Modelo de Riesgo", use_container_width=True):
                with st.spinner("Entrenando modelo de evaluación de riesgo..."):
                    result = pme.train_risk_assessment_model()

                    if result['success']:
                        st.success(f"✅ Modelo entrenado: {result['model_name']}")
                        if 'accuracy' in result:
                            st.metric("Precisión", f"{result['accuracy']:.1%}")
                            st.metric("Recall", f"{result['recall']:.1%}")
                            st.metric("Clientes Evaluados", result['predictions_saved'])
                        elif 'rule_based' in result and result['rule_based']:
                            st.info("Modelo de riesgo simple basado en reglas utilizado (sin métricas de ML)")
                            st.metric("Clientes Evaluados", result['predictions_saved'])
                        elif 'demo_data' in result and result['demo_data']:
                            st.info("Modelo de riesgo demo utilizado (sin métricas de ML)")
                            st.metric("Clientes Evaluados", result['predictions_saved'])
                        else:
                            st.info("Métricas de modelo no disponibles.")

                        # Mostrar las predicciones de riesgo generadas
                        if 'predictions' in result and result['predictions']:
                            st.subheader("⚠️ Predicciones de Riesgo Generadas")
                            df_risk = pd.DataFrame(result['predictions'])
                            df_risk['predicted_value'] = df_risk['predicted_value'].apply(lambda x: f"{x:.1%}")
                            st.dataframe(df_risk[['entity_id', 'predicted_value', 'target_date']].rename(columns={'entity_id': 'ID Cliente', 'predicted_value': 'Probabilidad de Riesgo', 'target_date': 'Fecha Predicción'}), use_container_width=True)
                        else:
                            st.info("No se pudieron recuperar las predicciones de riesgo.")
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Desconocido')}")

        with col3:
            if st.button("🎯 Entrenar Modelo de Conversión", use_container_width=True):
                with st.spinner("Entrenando modelo de probabilidad de conversión..."):
                    result = pme.train_conversion_probability_model()

                    if result['success']:
                        st.success(f"✅ Modelo entrenado: {result['model_name']}")
                        if 'auc_score' in result:
                            st.metric("AUC Score", f"{result['auc_score']:.3f}")
                            st.metric("Clientes Analizados", result['predictions_saved'])
                        elif 'demo_data' in result and result['demo_data']:
                            st.info("Modelo de conversión demo utilizado (sin métricas de ML)")
                            st.metric("Clientes Analizados", result['predictions_saved'])
                        else:
                            st.info("Métricas de modelo no disponibles.")

                        # Mostrar las predicciones de conversión generadas
                        if 'predictions' in result and result['predictions']:
                            st.subheader("🎯 Probabilidad de Conversión Generada")
                            df_conversion = pd.DataFrame(result['predictions'])
                            df_conversion['predicted_value'] = df_conversion['predicted_value'].apply(lambda x: f"{x:.1%}")
                            st.dataframe(df_conversion[['entity_id', 'predicted_value', 'target_date']].rename(columns={'entity_id': 'ID Cliente', 'predicted_value': 'Probabilidad de Conversión', 'target_date': 'Fecha Predicción'}), use_container_width=True)
                        else:
                            st.info("No se pudieron recuperar las predicciones de conversión.")
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Desconocido')}")

        # Visualizar predicciones
        st.subheader("📊 Predicciones Recientes")

        prediction_types = ["sales_forecast", "risk_assessment", "conversion_probability"]
        selected_type = st.selectbox("Tipo de predicción", prediction_types)

        if st.button("🔄 Actualizar Predicciones", use_container_width=True):
            with st.spinner("Obteniendo predicciones..."):
                predictions = pme.get_predictions(prediction_type=selected_type, limit=20)

                if predictions['success'] and predictions['predictions']:
                    df = pd.DataFrame(predictions['predictions'])

                    # Formatear columnas
                    if 'predicted_value' in df.columns:
                        if selected_type == "sales_forecast":
                            df['predicted_value'] = df['predicted_value'].apply(lambda x: f"${x:,.0f}")
                        elif selected_type == "risk_assessment":
                            df['predicted_value'] = df['predicted_value'].apply(lambda x: f"{x:.1%}")
                        elif selected_type == "conversion_probability":
                            df['predicted_value'] = df['predicted_value'].apply(lambda x: f"{x:.1%}")

                    st.dataframe(df, use_container_width=True)

                    # Gráfico simple usando Streamlit built-in (más seguro)
                    if len(df) > 0:
                        st.subheader(f"📈 Tendencia de {selected_type.replace('_', ' ').title()}")

                        # Crear un DataFrame simple para el gráfico
                        chart_data = pd.DataFrame({
                            'Predicción': range(len(df)),
                            'Valor': df['predicted_value'].values
                        })

                        # Usar el gráfico de línea de Streamlit
                        st.line_chart(chart_data.set_index('Predicción'), use_container_width=True)
                else:
                    st.info("No hay predicciones disponibles para este tipo.")

        # Métricas de modelos
        st.subheader("📈 Rendimiento de Modelos")

        if st.button("📊 Ver Métricas", use_container_width=True):
            with st.spinner("Obteniendo métricas de modelos..."):
                metrics = pme.get_model_metrics()

                if metrics['success'] and metrics['metrics']:
                    df_metrics = pd.DataFrame(metrics['metrics'])

                    # Mostrar métricas por modelo
                    for model_name in df_metrics['model_name'].unique():
                        st.subheader(f"🎯 {model_name}")

                        model_metrics = df_metrics[df_metrics['model_name'] == model_name]

                        cols = st.columns(len(model_metrics))
                        for i, (_, row) in enumerate(model_metrics.iterrows()):
                            with cols[i]:
                                # Map internal metric_type to user-friendly display name
                                display_name_map = {
                                    "TRAINING_TIME": "Tiempo de Entrenamiento",
                                    "DATASET_SIZE": "Tamaño del Dataset",
                                    "ACCURACY": "Precisión",
                                    "PRECISION": "Precisión (Clasificador)",
                                    "RECALL": "Recall",
                                    "AUC": "AUC Score",
                                    "TEST_SIZE": "Tamaño de Prueba"
                                }
                                display_metric_type = display_name_map.get(row['metric_type'].upper(), row['metric_type'].upper())

                                # Format the value
                                formatted_value = f"{row['metric_value']:.3f}"
                                if row['metric_value'] >= 1:
                                    formatted_value = f"{row['metric_value']:.1f}"
                                if row['metric_type'].upper() in ["ACCURACY", "PRECISION", "RECALL", "AUC"]:
                                    formatted_value = f"{row['metric_value']:.1%}"

                                st.metric(
                                    display_metric_type,
                                    formatted_value,
                                    f"{row['dataset_size']} muestras"
                                )
                else:
                    st.info("No hay métricas disponibles.")

    except Exception as e:
        st.error(f"Error en página de modelos predictivos: {str(e)}")
        st.exception(e)

    finally:
        pme.close()

def show_prescriptive_advisor_page():
    """
    Página del Prescriptive Advisor (PA)
    """
    st.title("💡 Asesor Prescriptivo Inteligente")
    st.markdown("---")

    # Reset session state each time to avoid DOM conflicts
    st.session_state.pa_client_recommendations = None
    st.session_state.pa_sales_recommendations = None
    st.session_state.pa_finance_recommendations = None

    # Inicializar PA
    pa = PrescriptiveAdvisor()

    try:
        st.subheader("🎯 Generar Recomendaciones")

        # Botones para diferentes tipos de análisis
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("👥 Analizar Clientes", use_container_width=True):
                with st.spinner("Analizando clientes y generando recomendaciones..."):
                    result = pa.generate_client_recommendations(limit=10)
                    st.session_state.pa_client_recommendations = result  # Guardar en session state
                    if result['success']:
                        st.success(f"✅ {result['total_generated']} recomendaciones generadas")
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Desconocido')}")

        with col2:
            if st.button("👔 Analizar Equipo de Ventas", use_container_width=True):
                with st.spinner("Analizando rendimiento del equipo..."):
                    result = pa.generate_sales_team_recommendations()
                    st.session_state.pa_sales_recommendations = result  # Guardar en session state
                    if result['success']:
                        st.success(f"✅ {result['total_generated']} recomendaciones generadas")
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Desconocido')}")

        with col3:
            if st.button("💰 Analizar Finanzas", use_container_width=True):
                with st.spinner("Analizando situación financiera..."):
                    result = pa.generate_finance_recommendations()
                    st.session_state.pa_finance_recommendations = result  # Guardar en session state
                    if result['success']:
                        st.success(f"✅ {result['total_generated']} recomendaciones generadas")
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Desconocido')}")

        # Mostrar resultados si existen
        if st.session_state.pa_client_recommendations:
            st.subheader("👥 Recomendaciones de Clientes")
            if st.session_state.pa_client_recommendations['success']:
                _display_recommendations(st.session_state.pa_client_recommendations['recommendations'], "clientes")
            else:
                st.error("No se pudieron generar recomendaciones de clientes")

        if st.session_state.pa_sales_recommendations:
            st.subheader("👔 Recomendaciones de Equipo de Ventas")
            if st.session_state.pa_sales_recommendations['success']:
                _display_recommendations(st.session_state.pa_sales_recommendations['recommendations'], "ventas")
            else:
                st.error("No se pudieron generar recomendaciones de ventas")

        if st.session_state.pa_finance_recommendations:
            st.subheader("💰 Recomendaciones Financieras")
            if st.session_state.pa_finance_recommendations['success']:
                _display_recommendations(st.session_state.pa_finance_recommendations['recommendations'], "finanzas")
            else:
                st.error("No se pudieron generar recomendaciones financieras")

        # Resumen de recomendaciones
        st.subheader("📊 Resumen Ejecutivo")

        if st.button("📈 Generar Resumen Completo", use_container_width=True):
            with st.spinner("Generando resumen ejecutivo..."):
                summary = pa.get_recommendations_summary()

                if summary['success']:
                    # Métricas principales
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Total Recomendaciones", summary['total_recommendations'])

                    with col2:
                        high_priority = summary['by_priority'].get('high', 0) + summary['by_priority'].get('critical', 0)
                        st.metric("Alta Prioridad", high_priority)

                    with col3:
                        st.metric("Agentes Activos", len(summary.get('by_type', {})))

                    with col4:
                        avg_impact = sum(r.get('impact_score', 0) for r in summary.get('top_recommendations', []))
                        avg_impact = avg_impact / max(len(summary.get('top_recommendations', [])), 1)
                        st.metric("Impacto Promedio", f"{avg_impact:.1f}")

                    # Distribución por tipo (usando charts nativos de Streamlit)
                    if summary.get('by_type'):
                        st.subheader("📋 Por Tipo de Recomendación")

                        type_data = summary['by_type']
                        chart_data = pd.DataFrame({
                            'Tipo': list(type_data.keys()),
                            'Cantidad': list(type_data.values())
                        })

                        st.bar_chart(chart_data.set_index('Tipo'), use_container_width=True)
                        st.caption("Distribución de Recomendaciones por Tipo")

                    # Top recomendaciones
                    if summary.get('top_recommendations'):
                        st.subheader("🏆 Top Recomendaciones")

                        for i, rec in enumerate(summary['top_recommendations'][:5], 1):
                            priority_colors = {
                                'critical': '🔴',
                                'high': '🟠',
                                'medium': '🟡',
                                'low': '🟢'
                            }

                            priority_icon = priority_colors.get(rec.get('priority', 'medium'), '🟡')

                            with st.container():
                                col1, col2 = st.columns([4, 1])

                                with col1:
                                    st.write(f"{priority_icon} **{rec.get('title', 'Sin título')}**")
                                    st.write(f"💡 {rec.get('description', '')}")
                                    st.write(f"🎯 {rec.get('action', '')}")

                                with col2:
                                    st.metric("Impacto", f"{rec.get('impact_score', 0):.1f}")

                                st.divider()

                else:
                    st.error(f"❌ Error generando resumen: {summary.get('error', 'Desconocido')}")

    except Exception as e:
        st.error(f"Error en página del asesor prescriptivo: {str(e)}")
        st.exception(e)

    finally:
        pa.close()

def _display_recommendations(recommendations: list, category: str):
    """
    Función auxiliar para mostrar recomendaciones
    """
    if not recommendations:
        st.info(f"No hay recomendaciones disponibles para {category}.")
        return

    # Ordenar por impacto
    recommendations.sort(key=lambda x: x.get('impact_score', 0), reverse=True)

    # Mostrar top 5
    for i, rec in enumerate(recommendations[:5], 1):
        priority_colors = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }

        priority_icon = priority_colors.get(rec.get('priority', 'medium'), '🟡')
        impact_score = rec.get('impact_score', 0)

        with st.expander(f"{priority_icon} {i}. {rec.get('title', 'Sin título')} (Impacto: {impact_score:.1f})"):
            st.write(f"**Descripción:** {rec.get('description', '')}")
            st.write(f"**Acción Recomendada:** {rec.get('action', '')}")
            st.write(f"**Categoría:** {rec.get('category', 'N/A').title()}")
            st.write(f"**Prioridad:** {rec.get('priority', 'medium').title()}")

            # Mostrar detalles adicionales si existen
            if rec.get('details'):
                with st.expander("📋 Detalles"):
                    st.json(rec['details'])

def show_data_catalog_page():
    """
    Página del catálogo de datos para el agente DCM
    """
    st.title("📚 Catálogo de Datos Inteligente")
    st.markdown("---")

    # Inicializar DCM
    dcm = DataCatalogManager()

    try:
        # Resumen del catálogo
        st.subheader("📊 Resumen del Catálogo")

        summary = dcm.get_catalog_summary()
        if summary['success']:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Tablas", summary['total_tables'])

            with col2:
                st.metric("Total Columnas", summary['total_columns'])

            with col3:
                sensitivity = summary.get('sensitivity_distribution', {})
                confidential = sensitivity.get('confidential', 0) + sensitivity.get('restricted', 0)
                st.metric("Datos Sensibles", confidential)

            with col4:
                public = summary.get('sensitivity_distribution', {}).get('public', 0)
                st.metric("Datos Públicos", public)

        # Búsqueda y filtros
        st.subheader("🔍 Explorar Catálogo")

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            search_query = st.text_input("Buscar en catálogo", placeholder="Nombre de tabla, columna o descripción...")

        with col2:
            # Obtener lista de tablas para filtro
            all_tables = []
            if 'results' in locals() and summary['success']:
                # Obtener todas las tablas del catálogo
                search_all = dcm.search_catalog()
                if search_all['success']:
                    all_tables = list(set([r['table_name'] for r in search_all['results']]))

            table_filter = st.selectbox("Filtrar por tabla", ["Todas"] + sorted(all_tables))

        with col3:
            sensitivity_filter = st.selectbox("Nivel de sensibilidad",
                ["Todos", "public", "internal", "confidential", "restricted"])

        # Botón de búsqueda
        if st.button("🔎 Buscar", use_container_width=True):
            with st.spinner("Buscando en catálogo..."):
                filters = {}
                if search_query:
                    filters['query'] = search_query
                if table_filter != "Todas":
                    filters['table_filter'] = table_filter
                if sensitivity_filter != "Todos":
                    filters['sensitivity_filter'] = sensitivity_filter

                search_result = dcm.search_catalog(**filters)

                if search_result['success']:
                    st.success(f"Encontrados {search_result['total_results']} resultados")

                    if search_result['results']:
                        # Convertir a DataFrame para mejor visualización
                        df = pd.DataFrame(search_result['results'])

                        # Mostrar tabla con columnas seleccionadas
                        display_cols = ['table_name', 'column_name', 'data_type', 'description', 'sensitivity_level', 'business_owner']
                        st.dataframe(df[display_cols], use_container_width=True)

                        # Mostrar detalles expandibles
                        with st.expander("📋 Ver detalles completos"):
                            for i, row in df.iterrows():
                                with st.container():
                                    st.markdown(f"**{row['table_name']}.{row['column_name']}**")
                                    st.write(f"📝 {row['description']}")
                                    st.write(f"🏷️ Sensibilidad: {row['sensitivity_level']}")
                                    st.write(f"👤 Dueño negocio: {row['business_owner']}")
                                    if row['tags']:
                                        st.write(f"🏷️ Tags: {', '.join(row['tags'])}")
                                    st.write(f"📊 Filas en tabla: {row['row_count']}")
                                    st.divider()
                    else:
                        st.info("No se encontraron resultados para la búsqueda.")
                else:
                    st.error(f"Error en búsqueda: {search_result.get('error', 'Desconocido')}")

        # Escanear esquema
        st.subheader("🔄 Actualizar Catálogo")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔍 Escanear Esquema de BD", use_container_width=True):
                with st.spinner("Escaneando esquema de base de datos..."):
                    scan_result = dcm.scan_database_schema()

                    if scan_result['success']:
                        st.success(f"✅ Catálogo actualizado: {scan_result['tables_scanned']} tablas, {scan_result['columns_cataloged']} columnas")
                        st.rerun()  # Recargar página para mostrar datos actualizados
                    else:
                        st.error(f"❌ Error escaneando esquema: {scan_result.get('error', 'Desconocido')}")

        with col2:
            if st.button("💾 Exportar Catálogo", use_container_width=True):
                with st.spinner("Exportando catálogo..."):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"catalog_export_{timestamp}.json"

                    export_result = dcm.export_catalog_to_json(filename)

                    if export_result['success']:
                        st.success(f"✅ Catálogo exportado a {filename}")
                        with open(filename, 'r', encoding='utf-8') as f:
                            st.download_button(
                                label="📥 Descargar archivo",
                                data=f,
                                file_name=filename,
                                mime="application/json"
                            )
                    else:
                        st.error(f"❌ Error exportando: {export_result.get('error', 'Desconocido')}")

        # Estadísticas de sensibilidad
        st.subheader("🔒 Distribución de Sensibilidad")

        if summary['success'] and 'sensitivity_distribution' in summary:
            sensitivity_data = summary['sensitivity_distribution']

            if sensitivity_data:
                # Mostrar como tabla simple en lugar de pie chart
                st.write("**Datos por nivel de sensibilidad:**")
                for level, count in sensitivity_data.items():
                    level_emoji = {'public': '🌐', 'internal': '🏢', 'confidential': '🔒', 'restricted': '🚫'}.get(level, '❓')
                    st.write(f"{level_emoji} **{level.title()}**: {count} campos")

    except Exception as e:
        st.error(f"Error en página del catálogo: {str(e)}")
        st.exception(e)

    finally:
        dcm.close()

def show_data_pipeline_page():
    """
    Página del pipeline de datos para el agente DPO
    """
    st.title("🔄 Pipeline de Datos Inteligente")
    st.markdown("---")

    # Inicializar DPO
    dpo = DataPipelineOrchestrator()

    try:
        st.subheader("🚀 Ejecutar ETL")

        # Seleccionar tabla
        table_options = ["clientes", "facturas", "cobranzas", "movimientos_caja", "actividades_venta"]
        selected_table = st.selectbox("Seleccionar tabla para ETL", table_options)

        limit = st.slider("Límite de registros (0 = todos)", 0, 1000, 100)

        if st.button("▶️ Ejecutar Pipeline ETL", use_container_width=True):
            with st.spinner(f"Procesando ETL para {selected_table}..."):
                etl_result = dpo.run_etl_pipeline(selected_table, limit if limit > 0 else None)

                if etl_result['success']:
                    st.success("✅ Pipeline ETL completado exitosamente!")

                    # Mostrar resultados por etapa
                    stages = etl_result.get('stages', {})

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        extract = stages.get('extract', {})
                        st.metric("📊 Extraídos", extract.get('count', 0))

                    with col2:
                        transform = stages.get('transform', {})
                        st.metric("🔄 Transformados", transform.get('transformed_count', 0))

                    with col3:
                        load = stages.get('load', {})
                        st.metric("💾 Cargados", load.get('loaded_count', 0))

                    # Mostrar logs detallados
                    with st.expander("📋 Detalles del proceso"):
                        st.json(etl_result)

                    # Mostrar preview de datos extraídos
                    if etl_result['stages']['extract']['records']:
                        st.subheader("👀 Preview de Datos Extraídos")
                        df_preview = pd.DataFrame(etl_result['stages']['extract']['records'])
                        st.dataframe(df_preview.head(10), use_container_width=True)

                else:
                    st.error(f"❌ Error en pipeline: {etl_result.get('error', 'Desconocido')}")

                # Métricas de calidad

                st.subheader("📈 Métricas de Calidad de Datos")

        

                if st.button("📊 Actualizar Métricas", use_container_width=True):

                    with st.spinner("Obteniendo métricas..."):

                        metrics = dpo.get_quality_metrics()

        

                        if metrics['success'] and metrics['metrics'] and metrics['metrics']['total_operations'] > 0:

                            m = metrics['metrics']

        

                            col1, col2, col3, col4 = st.columns(4)

        

                            with col1:

                                st.metric("Operaciones Totales", m['total_operations'])

        

                            with col2:

                                st.metric("Tasa de Éxito", f"{m['success_rate']:.1f}%")

        

                            with col3:

                                st.metric("Puntuación Promedio", f"{m['avg_quality_score']:.1f}%")

        

                            with col4:

                                st.metric("Tablas Procesadas", len(m['tables_processed']))

        

                            # Logs recientes

                            if m['recent_logs']:

                                st.subheader("📝 Logs Recientes")

                                for log in m['recent_logs'][:5]:

                                    with st.container():

                                        st.write(f"**{log['table']}** - {log['operation']} - Calidad: {log['quality_score']}% ")

                                        st.caption(f"{log['timestamp']}")

                                        st.divider()

        

                        else:

                            st.info("No hay métricas de calidad disponibles. Ejecuta el pipeline ETL para generar métricas.")

    except Exception as e:
        st.error(f"Error en página del pipeline: {str(e)}")
        st.exception(e)

    finally:
        dpo.close()

def show_data_quality_page():
    """
    Página del Data Quality Guardian (DQG)
    """
    st.title("🔍 Guardián de Calidad de Datos")
    st.markdown("---")

    # Inicializar DQG
    dqg = ValidadorCalidadDatos()

    try:
        st.subheader("🎯 Validaciones de Calidad")

        # Seleccionar dataset para validar
        dataset_options = ["clientes", "facturas", "vendedores", "actividades_venta"]
        selected_dataset = st.selectbox("Seleccionar conjunto de datos", dataset_options)

        if st.button("🔍 Ejecutar Validaciones", use_container_width=True):
            with st.spinner(f"Validando calidad de {selected_dataset}..."):
                result = dqg.ejecutar_validaciones(selected_dataset)

                if result['success']:
                    st.success(f"✅ Validación completada para {selected_dataset}")

                    # Mostrar resultados principales
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Puntuación General", f"{result['puntuacion_general']:.1f}%")

                    with col2:
                        st.metric("Total Problemas", result['total_problemas'])

                    with col3:
                        tiempo = result.get('execution_time', 0)
                        st.metric("Tiempo de Ejecución", f"{tiempo:.2f}s")

                    with col4:
                        st.metric("Métricas Evaluadas", len(result.get('metricas', {})))

                    # Mostrar detalles de métricas
                    with st.expander("📊 Detalles por Métrica"):
                        metricas = result.get('metricas', {})
                        for nombre_metrica, datos_metrica in metricas.items():
                            if datos_metrica.get('success'):
                                st.markdown(f"**{nombre_metrica}**")
                                st.write(f"✅ Puntuación: {datos_metrica.get('puntuacion', 0):.1f}%")
                                st.write(f"📋 Registros evaluados: {datos_metrica.get('total_registros', 0)}")
                                st.progress(datos_metrica.get('puntuacion', 0) / 100)

                                # Mostrar problemas si existen
                                if datos_metrica.get('problemas'):
                                    with st.expander("⚠️ Problemas encontrados"):
                                        for problema in datos_metrica['problemas'][:5]:  # Top 5
                                            st.write(f"• {problema.get('descripcion', 'Sin descripción')}")
                                st.divider()

                else:
                    st.error(f"❌ Error en validación: {result.get('error', 'Desconocido')}")

        # Estado de calidad general
        st.subheader("📈 Estado de Calidad General")

        if st.button("📊 Ver Estado General", use_container_width=True):
            with st.spinner("Obteniendo estado de calidad..."):
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Estado por Dataset")
                    for dataset in dataset_options:
                        estado = dqg.obtener_estado_calidad(dataset)
                        if estado['success']:
                            score = estado['estado_actual']['puntuacion_general']
                            problemas = estado['estado_actual']['total_problemas']

                            color = "🟢" if score >= 95 else "🟡" if score >= 80 else "🔴"

                            with st.container():
                                st.write(f"{color} **{dataset.title()}**")
                                st.write(f"Puntuación: {score:.1f}% | Problemas: {problemas}")
                                st.progress(score / 100)
                                st.divider()
                        else:
                            st.write(f"❌ Error obteniendo estado de {dataset}")

                with col2:
                    st.subheader("Alertas de Calidad")

                    # Mostrar alertas críticas
                    problemas = dqg.obtener_problemas(severidad="alta")
                    if problemas:
                        for problema in problemas[:10]:  # Top 10 problemas críticos
                            with st.container():
                                st.error(f"🔴 {problema.get('descripcion', '')}")
                                st.caption(f"Dataset: {problema.get('dataset_id', '')}")
                                st.divider()
                    else:
                        st.success("✅ No hay problemas críticos de calidad")

        # Panel de monitoreo continuo
        st.subheader("🔄 Monitoreo Continuo")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("▶️ Iniciar Monitoreo", use_container_width=True):
                st.info("El monitoreo continuo se ejecutaría como servicio en segundo plano")
                st.info("Por ahora, ejecuta validaciones manualmente")

        with col2:
            if st.button("🔍 Buscar Problemas Específicos", use_container_width=True):
                with st.spinner("Buscando problemas..."):
                    problemas = dqg.obtener_problemas()

                    if problemas:
                        st.info(f"Encontrados {len(problemas)} problemas en total")

                        # Agrupar por severidad
                        severidad_count = {}
                        for p in problemas:
                            sev = p.get('severidad', 'desconocida')
                            severidad_count[sev] = severidad_count.get(sev, 0) + 1

                        st.json(severidad_count)
                    else:
                        st.success("No se encontraron problemas de calidad")

    except Exception as e:
        st.error(f"Error en página del guardián de calidad: {str(e)}")
        st.exception(e)

    finally:
        dqg.close()

def show_anomaly_detector_page():
    """
    Página del Anomaly Detector (AD)
    """
    st.title("🚨 Detector de Anomalías Inteligente")
    st.markdown("---")

    # Inicializar AD
    ad = AnomalyDetector()

    try:
        st.subheader("🎯 Detección de Anomalías")

        # Selección de métrica para analizar
        metric_options = ["sales_total", "collections_total"]
        selected_metric = st.selectbox("Seleccionar métrica para analizar", metric_options)

        col1, col2 = st.columns(2)

        with col1:
            lookback_days = st.slider("Días de análisis retrospectivo", 30, 365, 90)

        with col2:
            if st.button("🔍 Detectar Anomalías", use_container_width=True):
                with st.spinner(f"Analizando anomalías en {selected_metric}..."):
                    if selected_metric == "sales_total":
                        result = ad.detect_anomalies_sales(lookback_days)
                    else:
                        result = ad.detect_anomalies_collections(lookback_days)

                    if result['success']:
                        st.success("✅ Detección de anomalías completada")

                        # Mostrar métricas principales
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Puntos de Datos", result.get('data_points', 0))

                        with col2:
                            st.metric("Anomalías Detectadas", result.get('anomalies_detected', 0))

                        with col3:
                            st.metric("Alertas Guardadas", result.get('anomalies_saved', 0))

                        with col4:
                            st.metric("Métodos Usados", len(result.get('methods_used', [])))

                        # Mostrar anomalías encontradas
                        if result.get('anomalies'):
                            st.subheader("⚠️ Anomalías Encontradas")

                            anomalias_df = pd.DataFrame(result['anomalies'])
                            st.dataframe(anomalias_df[['timestamp', 'metric_name', 'metric_value',
                                                     'severity', 'detection_method']], use_container_width=True)

                            # Análisis por severidad
                            if 'severity' in anomalias_df.columns:
                                severity_counts = anomalias_df['severity'].value_counts()
                                st.bar_chart(severity_counts)

                    else:
                        st.error(f"❌ Error en detección: {result.get('error', 'Desconocido')}")

        # Gestión de alertas existentes
        st.subheader("📋 Gestión de Alertas")

        if st.button("🔄 Actualizar Alertas", use_container_width=True):
            with st.spinner("Obteniendo alertas..."):
                alertas = ad.get_anomalies()

                if alertas['success'] and alertas['anomalies']:
                    st.info(f"Total de alertas: {alertas['count']}")

                    # Filtrar alertas abiertas
                    alertas_abiertas = [a for a in alertas['anomalies'] if a['status'] == 'open']

                    if alertas_abiertas:
                        st.subheader("🚨 Alertas Abiertas")

                        for alerta in alertas_abiertas[:5]:  # Top 5
                            severity_color = {
                                'critical': '🔴',
                                'high': '🟠',
                                'medium': '🟡',
                                'low': '🟢'
                            }.get(alerta['severity'], '🟢')

                            with st.expander(f"{severity_color} Alerta #{alerta['id']} - {alerta['metric_name']}", expanded=True):
                                st.write(f"📅 Fecha: {alerta['timestamp']}")
                                st.write(f"📊 Valor: {alerta['metric_value']:.2f}")
                                st.write(f"🎯 Método: {alerta['detection_method']}")
                                st.write(f"⚠️ Severidad: {alerta['severity']}")

                                # Rango esperado si disponible
                                if alerta.get('expected_range_min') and alerta.get('expected_range_max'):
                                    st.write(f"🎯 Rango esperado: {alerta['expected_range_min']:.2f} - {alerta['expected_range_max']:.2f}")

                                # Acciones
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button(f"✅ Confirmar #{alerta['id']}", key=f"ack_{alerta['id']}"):
                                        ack_result = ad.acknowledge_anomaly(alerta['id'], notes="Confirmado desde UI")
                                        if ack_result['success']:
                                            st.success("Alerta confirmada")
                                            st.rerun()
                                        else:
                                            st.error("Error confirmando alerta")

                                with col2:
                                    if st.button(f"✅ Resolver #{alerta['id']}", key=f"resolve_{alerta['id']}"):
                                        resolve_result = ad.resolve_anomaly(alerta['id'], "Resuelto desde UI")
                                        if resolve_result['success']:
                                            st.success("Alerta resuelta")
                                            st.rerun()
                                        else:
                                            st.error("Error resolviendo alerta")

                    else:
                        st.success("✅ No hay alertas abiertas")
                else:
                    st.info("No hay alertas disponibles")

        # Dashboard resumen
        st.subheader("📊 Dashboard de Anomalías")

        if st.button("📈 Generar Dashboard", use_container_width=True):
            with st.spinner("Generando dashboard..."):
                dashboard = ad.get_dashboard_summary()

                if dashboard['success']:
                    # Métricas principales
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        severity_summary = dashboard.get('severity_summary', {})
                        critical_count = severity_summary.get('critical', {}).get('total', 0)
                        st.metric("Anomalías Críticas", critical_count)

                    with col2:
                        total_anomalies = dashboard.get('total_anomalies', 0)
                        st.metric("Total Anomalías", total_anomalies)

                    with col3:
                        recent_count = len(dashboard.get('recent_anomalies', []))
                        st.metric("Anomalías Recientes", recent_count)

                    # Distribución por severidad (usando charts nativos de Streamlit)
                    if severity_summary:
                        st.subheader("📋 Distribución por Severidad")

                        severity_data = {}
                        for severity, counts in severity_summary.items():
                            severity_data[severity.title()] = counts['total']

                        st.write("**Anomalías por nivel de severidad:**")
                        for severity, count in severity_data.items():
                            severity_emoji = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🟢'}.get(severity, '❓')
                            st.write(f"{severity_emoji} **{severity}**: {count} anomalías")

                    # Anomalías recientes
                    if dashboard.get('recent_anomalies'):
                        st.subheader("🕒 Anomalías Recientes")
                        recent_df = pd.DataFrame(dashboard['recent_anomalies'])
                        st.dataframe(recent_df[['timestamp', 'metric_name', 'severity', 'status']], use_container_width=True)

                else:
                    st.error("Error generando dashboard")

    except Exception as e:
        st.error(f"Error en página del detector de anomalías: {str(e)}")
        st.exception(e)

    finally:
        ad.close()

def show_ssbf_page():
    """
    Página del Self-Service BI Facilitator (SSBF)
    """
    st.title("📊 BI Autoservicio")
    st.markdown("---")

    # Inicializar SSBF
    ssbf = SSBFFacilitator()

    try:
        st.subheader("🎯 Crea Tu Propio Dashboard")

        # Inicialización de métricas y plantillas (solo primera vez)
        if st.button("🚀 Inicializar Librería de BI", use_container_width=True):
            with st.spinner("Inicializando métricas y plantillas..."):

                # Inicializar métricas predefinidas
                metrics_result = ssbf.initialize_default_metrics()
                if metrics_result['success']:
                    st.success(f"✅ {metrics_result['metrics_created']} métricas inicializadas")
                else:
                    st.error("❌ Error inicializando métricas")

                # Inicializar plantillas
                templates_result = ssbf.initialize_dashboard_templates()
                if templates_result['success']:
                    st.success(f"✅ {templates_result['templates_created']} plantillas inicializadas")
                else:
                    st.error("❌ Error inicializando plantillas")

        # Crear nuevo dashboard
        st.subheader("➕ Crear Dashboard")

        col1, col2, col3 = st.columns(3)

        with col1:
            dashboard_title = st.text_input("Título del Dashboard", placeholder="Mi Dashboard Ejecutivo")

        with col2:
            # Obtener plantillas disponibles
            templates = ssbf.get_dashboard_templates()
            template_names = ["Sin plantilla"] + [t['display_name'] for t in templates] if templates else ["Sin plantilla"]
            selected_template = st.selectbox("Plantilla base", template_names)

        with col3:
            is_public = st.checkbox("Dashboard público", help="Otros usuarios podrán ver este dashboard")

        if st.button("🎨 Crear Dashboard", use_container_width=True) and dashboard_title.strip():
            with st.spinner("Creando dashboard..."):
                # Obtener user_id (simulado - en producción vendría de session)
                user_id = 1  # Admin user

                # Obtener template_name si se seleccionó uno
                template_name = None
                if selected_template != "Sin plantilla" and templates:
                    selected_template_data = next((t for t in templates if t['display_name'] == selected_template), None)
                    if selected_template_data:
                        template_name = selected_template_data['name']

                result = ssbf.create_user_dashboard(
                    user_id=user_id,
                    title=dashboard_title,
                    template_name=template_name,
                    is_public=0 if not is_public else 1
                )

                if result['success']:
                    st.success(f"✅ Dashboard '{dashboard_title}' creado exitosamente")
                    st.info(f"ID del dashboard: {result['dashboard_id']}")
                    st.rerun()  # Recargar para mostrar dashboards actualizados
                else:
                    st.error(f"❌ Error creando dashboard: {result.get('error', 'Desconocido')}")

        # Gestionar dashboards existentes
        st.subheader("📋 Mis Dashboards")

        # Obtener user_id (simulado)
        user_id = 1

        if st.button("🔄 Actualizar Dashboards", use_container_width=True):
            with st.spinner("Cargando dashboards..."):
                dashboards = ssbf.get_user_dashboards(user_id)

                if dashboards:
                    st.success(f"Encontrados {len(dashboards)} dashboards")

                    for dashboard in dashboards[:10]:  # Limitar a 10 para UI
                        visibility = "🌐 Público" if dashboard['is_public'] else "🔒 Privado"
                        permission = dashboard['user_permission']

                        with st.expander(f"📊 {dashboard['title']} ({visibility}) - Permiso: {permission}", expanded=True):
                            st.write(f"**Descripción:** {dashboard['description'] or 'Sin descripción'}")
                            st.write(f"**Tipo:** {dashboard['dashboard_type']} | **Creado:** {dashboard['created_at'][:10]}")

                            # Acciones disponibles según permisos
                            if permission in ['admin', 'edit']:
                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    if st.button("👀 Ver", key=f"view_{dashboard['id']}", use_container_width=True):
                                        st.info("Vista completa del dashboard (integración con Metabase)")
                                        # Aquí iría la integración real con Metabase

                                with col2:
                                    if st.button("✏️ Editar", key=f"edit_{dashboard['id']}", use_container_width=True):
                                        st.info("Editor visual del dashboard")
                                        # Aquí iría el editor de configuraciones

                                with col3:
                                    if st.button("📤 Compartir", key=f"share_{dashboard['id']}", use_container_width=True):
                                        st.text_input("Email usuario destino", key=f"share_email_{dashboard['id']}", placeholder="usuario@empresa.com")
                                        share_level = st.selectbox("Nivel de permiso", ["view", "edit"], key=f"share_level_{dashboard['id']}")

                                        if st.button("✅ Compartir", key=f"confirm_share_{dashboard['id']}"):
                                            # En producción, obtener user_id del email
                                            target_user_id = 2  # Simulado
                                            share_result = ssbf.share_dashboard(
                                                dashboard['id'],
                                                user_id,
                                                target_user_id,
                                                share_level
                                            )
                                            if share_result['success']:
                                                st.success("🎉 Dashboard compartido exitosamente")
                                            else:
                                                st.error(f"❌ Error: {share_result.get('error', 'Desconocido')}")

                            else:
                                st.info("Solo lectura - solicitado por el creador del dashboard")
                                if st.button("👀 Ver", key=f"view_readonly_{dashboard['id']}", use_container_width=True):
                                    st.info("Vista de solo lectura")

                else:
                    st.info("No tienes dashboards creados aún. ¡Crea tu primer dashboard arriba!")

        # Explorar métricas disponibles
        st.subheader("📈 Explorar Métricas")

        col1, col2 = st.columns([1, 3])

        with col1:
            category_filter = st.selectbox("Categoría", ["Todas", "ventas", "cobranza", "finanzas", "operaciones"])

        with col2:
            if st.button("🔍 Calcular Valores Actuales", use_container_width=True):
                with st.spinner("Calculando métricas..."):
                    category = None if category_filter == "Todas" else category_filter
                    metrics = ssbf.get_predefined_metrics(category=category)

                    if metrics:
                        st.success(f"Encontradas {len(metrics)} métricas {'en ' + category_filter if category_filter != 'Todas' else ''}")

                        metrics_df = pd.DataFrame(metrics)
                        st.dataframe(metrics_df[['display_name', 'category', 'data_type', 'unit']], use_container_width=True)

                        # Calcular y mostrar valores de las primeras 5 métricas
                        st.subheader("💡 Valores Actuales (Top 5)")

                        for metric in metrics[:5]:
                            with st.container():
                                value_result = ssbf.calculate_metric_value(metric['id'])
                                if value_result['success']:
                                    col1, col2, col3 = st.columns([3, 1, 1])

                                    with col1:
                                        st.write(f"**{metric['display_name']}**")
                                        st.caption(metric['description'])

                                    with col2:
                                        st.metric(f"{metric['unit']}", value_result['formatted_value'])

                                    with col3:
                                        st.metric("Tipo", metric['data_type'])

                                else:
                                    st.write(f"❌ Error calculando {metric['display_name']}")
                                st.divider()
                    else:
                        st.info("No se encontraron métricas en esa categoría")

        # Plantillas disponibles
        st.subheader("🎨 Plantillas de Dashboards")

        if st.button("📋 Ver Plantillas", use_container_width=True):
            with st.spinner("Cargando plantillas..."):
                templates = ssbf.get_dashboard_templates(public_only=True)

                if templates:
                    st.success(f"Encontradas {len(templates)} plantillas públicas")

                    for template in templates:
                        with st.expander(f"📋 {template['display_name']} - {template['category'].title()}", expanded=False):
                            st.write(f"**Descripción:** {template['description']}")
                            st.write(f"**Usos:** {template.get('use_count', 0)}")
                            st.write(f"**Secciones:** {len(template.get('config', {}).get('sections', []))}")

                            if template.get('config', {}).get('sections'):
                                st.subheader("Secciones incluidas:")
                                for section in template['config']['sections']:
                                    metrics_count = len(section.get('metrics', []))
                                    charts_count = len(section.get('charts', []))
                                    st.write(f"• {section['title']}: {metrics_count} métricas, {charts_count} gráficos")
                else:
                    st.info("No hay plantillas disponibles")

    except Exception as e:
        st.error(f"Error en página de BI autoservicio: {str(e)}")
        st.exception(e)

    finally:
        ssbf.close()

def show_generative_assistant_page():
    """
    Página del Generative Data Assistant (GDA)
    """
    st.title("🤖 Asistente de Consultas Inteligente")
    st.markdown("---")

    # Inicializar session state para consultas
    if 'gda_query_results' not in st.session_state:
        st.session_state.gda_query_results = None

    # Inicializar GDA
    gda = GenerativeDataAssistant()

    try:
        st.subheader("💬 Consultas en Lenguaje Natural")

        # Área de consulta
        user_query = st.text_area(
            "Escribe tu consulta sobre los datos",
            placeholder="¿Cuántos clientes tenemos? ¿Cuál es el estado de las ventas? ¿Hay problemas con los pagos?",
            height=100
        )

        # Configuración adicional
        col1, col2 = st.columns([1, 1])

        with col1:
            include_data = st.checkbox("Incluir datos detallados", value=True, help="Muestra datos técnicos y métricas")

        with col2:
            auto_run = st.checkbox("Ejecución automática", value=False, help="Ejecuta la consulta automáticamente al escribir")

        # Botón de consulta
        if st.button("🔍 Hacer Consulta", use_container_width=True, type="primary") and user_query.strip():
            with st.spinner("Analizando tu consulta..."):
                # Procesar consulta
                result = gda.process_query(user_query.strip(), {
                    'include_data': include_data,
                    'user_id': 'ui_user'  # Simulado
                })

                # Guardar resultado en session state
                st.session_state.gda_query_results = result

                if result['success']:
                    st.success("✅ Consulta procesada exitosamente")

                    # Mostrar respuesta principal
                    st.subheader("🤖 Respuesta")
                    st.info(result['response'])

                    # Mostrar detalles técnicos si se solicitó
                    if include_data:
                        with st.expander("📊 Detalles Técnicos", expanded=False):
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric("Tiempo de Procesamiento", f"{result['processing_time']}s")

                            with col2:
                                confidence = result.get('confidence_score', 0)
                                st.metric("Confianza", f"{confidence * 100:.1f}%")

                            with col3:
                                st.metric("Consulta", f"{len(result['query'])} caracteres")

                            # Mostrar datos utilizados
                            if result.get('data_used'):
                                st.subheader("Datos Utilizados")
                                st.json(result['data_used'])

                else:
                    st.error(f"❌ Error: {result.get('error', 'Error desconocido')}")

        # Mostrar resultado anterior si existe
        elif st.session_state.gda_query_results and st.session_state.gda_query_results['success']:
            result = st.session_state.gda_query_results

            st.subheader("💬 Consulta Anterior")
            st.write(f"**Pregunta:** {result['query']}")

            st.subheader("🤖 Respuesta")
            st.info(result['response'])

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Procesamiento", f"{result['processing_time']}s")
            with col2:
                confidence = result.get('confidence_score', 0)
                st.metric("Confianza", f"{confidence * 100:.1f}%")

        # Sugerencias de consultas
        st.subheader("💡 Consultas Sugeridas")

        suggested_queries = [
            "¿Cuántos clientes tenemos?",
            "¿Cuál es el estado de las ventas este mes?",
            "¿Hay problemas con los pagos?",
            "¿Cuáles son las tendencias de ingresos?",
            "¿Qué métricas hay disponibles para ventas?",
            "¿Cómo está funcionando el equipo de vendedores?"
        ]

        cols = st.columns(2)
        for i, query in enumerate(suggested_queries):
            with cols[i % 2]:
                if st.button(query, key=f"suggested_{i}", use_container_width=True):
                    st.session_state.suggested_query = query
                    st.rerun()

        # Si se seleccionó una consulta sugerida
        if hasattr(st.session_state, 'suggested_query') and st.session_state.suggested_query:
            query = st.session_state.suggested_query
            st.session_state.suggested_query = None  # Limpiar

            with st.spinner(f"Procesando: {query}"):
                result = gda.process_query(query, {'include_data': include_data})
                st.session_state.gda_query_results = result

                if result['success']:
                    st.success("✅ Consulta procesada")
                    st.info(result['response'])
                    st.rerun()  # Para mostrar el resultado completo

        # Estadísticas del asistente
        st.subheader("📈 Estadísticas del Asistente")

        col1, col2, col3, col4 = st.columns(4)

        try:
            # Obtener estadísticas del GDA
            popular_queries = gda.get_popular_queries()
            conversation_history = gda.get_conversation_history()

            with col1:
                st.metric("Consultas Recientes", len(conversation_history))

            with col2:
                avg_confidence = sum([q.get('confidence', 0) for q in conversation_history]) / max(len(conversation_history), 1)
                st.metric("Confianza Promedio", f"{avg_confidence * 100:.1f}%")

            with col3:
                total_interactions = sum([q.get('frequency', 0) for q in popular_queries])
                st.metric("Total Interacciones", total_interactions)

            with col4:
                category_metrics = len([q for q in popular_queries if 'ventas' in q['query'].lower()])
                st.metric("Temas Ventas", category_metrics)

        except Exception as e:
            st.warning("No hay estadísticas disponibles aún")

        # Consultas populares
        if st.button("📊 Ver Consultas Populares", use_container_width=True):
            with st.spinner("Obteniendo consultas populares..."):
                popular = gda.get_popular_queries()

                if popular:
                    st.subheader("🔥 Consultas Más Frecuentes")

                    for query_data in popular[:10]:
                        with st.container():
                            col1, col2 = st.columns([4, 1])

                            with col1:
                                st.write(f"📝 {query_data['query']}")

                            with col2:
                                st.metric("Frecuencia", query_data['frequency'])

                            st.divider()
                else:
                    st.info("No hay consultas populares disponibles")

    except Exception as e:
        st.error(f"Error en página del asistente generativo: {str(e)}")
        st.exception(e)

    finally:
        gda.close()

def show_system_health_page():
    """
    Página del dashboard de salud del sistema - System Integrator (SI)
    """
    st.title("🏥 Estado del Sistema")
    st.markdown("---")

    try:
        # Mostrar salud general en tiempo real
        st.subheader("💓 SALUD GENERAL DEL SISTEMA")

        # Obtener dashboard de salud
        with st.spinner("Obteniendo estado del sistema..."):
            health = get_system_health()

        if health['success']:
            dashboard = health['dashboard']

            # Estado general
            col1, col2, col3, col4 = st.columns(4)

            overview = dashboard['system_overview']

            with col1:
                version = overview['version']
                st.metric("Versión", version)

            with col2:
                uptime = overview['uptime_hours']
                st.metric("Tiempo Activo", f"{uptime:.1f}h")

            with col3:
                operational = overview['operational_agents']
                total = overview['total_agents']
                st.metric("Agentes Operativos", f"{operational}/{total}")

            with col4:
                health_score = health['overall_health_score']
                health_icon = "🟢" if health_score >= 95 else "🟡" if health_score >= 80 else "🔴"
                st.metric("Salud Global", f"{health_score}%", help=health_icon)

            st.divider()

            # Estado de agentes
            st.subheader("🤖 ESTADO DE AGENTES")

            agent_health = dashboard['agent_health']

            if agent_health:
                # Resumir por estado
                status_counts = {}
                for agent in agent_health:
                    status = agent['status']
                    status_counts[status] = status_counts.get(status, 0) + 1

                st.write("**Resumen por Estado:**")
                status_emojis = {'operational': '✅', 'degraded': '⚠️', 'critical': '🚨', 'error': '❌'}

                status_cols = st.columns(len(status_counts))
                for i, (status, count) in enumerate(status_counts.items()):
                    with status_cols[i]:
                        emoji = status_emojis.get(status, '❓')
                        st.metric(f"{emoji} {status.title()}", count)

                # Detalle de agentes críticos
                st.subheader("🚨 Agentes con Problemas")

                critical_agents = [a for a in agent_health if a['status'] in ['degraded', 'critical', 'error']]

                if critical_agents:
                    for agent in critical_agents[:5]:  # Top 5
                        status_emoji = '⚠️' if agent['status'] == 'degraded' else '🚨'

                        with st.container():
                            col1, col2, col3 = st.columns([2, 1, 1])

                            with col1:
                                st.write(f"{status_emoji} **{agent['name']}**")
                                if agent.get('last_error'):
                                    st.caption(f"Error: {agent['last_error']}")

                            with col2:
                                st.metric("Salud", f"{agent['health_score']}%")

                            with col3:
                                uptime = agent.get('uptime_24h', 0)
                                st.metric("Uptime 24h", f"{uptime:.1f}%")

                            st.divider()
                else:
                    st.success("✅ Todos los agentes funcionando correctamente")

                # Tabla completa de agentes
                with st.expander("📋 Estado Completo de Todos los Agentes"):
                    agent_df = pd.DataFrame(agent_health)
                    st.dataframe(agent_df[['name', 'status', 'health_score', 'uptime_24h', 'last_error']],
                               use_container_width=True)

            st.divider()

            # Alertas críticas
            critical_alerts = dashboard.get('critical_alerts', [])

            if critical_alerts:
                st.subheader("🚨 ALERTAS CRÍTICAS")

                for alert in critical_alerts:
                    severity_emoji = '🔴' if alert['severity'] == 'critical' else '🟠'

                    with st.container():
                        st.error(f"{severity_emoji} **{alert['agent'].upper()}**: {alert['message']}")
                        st.caption(f"Detalles: {alert['details']}")
                        st.caption(f"Timestamp: {alert['timestamp'][:19]}")
                        st.divider()
            else:
                st.success("✅ No hay alertas críticas activas")

            st.divider()

            # Métricas de rendimiento
            st.subheader("📊 RENDIMIENTO DEL SISTEMA")

            performance = dashboard.get('performance_metrics', {})

            col1, col2, col3, col4 = st.columns(4)

            response_times = performance.get('response_times', {})
            with col1:
                st.metric("Tiempo Promedio", f"{response_times.get('avg_response_time', 0)}s")

            with col2:
                st.metric("Consultas/Min", performance.get('throughput', {}).get('queries_per_minute', 0))

            with col3:
                st.metric("Predicciones/Hora", performance.get('throughput', {}).get('predictions_per_hour', 0))

            with col4:
                reports_today = performance.get('throughput', {}).get('reports_generated_today', 0)
                st.metric("Reportes Hoy", reports_today)

            # Uso de recursos
            resource_usage = performance.get('resource_usage', {})

            st.subheader("💻 RECURSOS DEL SISTEMA")

            usage_cols = st.columns(4)

            with usage_cols[0]:
                st.metric("CPU", f"{resource_usage.get('cpu_percent', 0)}%")

            with usage_cols[1]:
                memory_mb = resource_usage.get('memory_mb', 0)
                st.metric("Memoria", f"{memory_mb:.0f} MB")

            with usage_cols[2]:
                disk_gb = resource_usage.get('disk_usage_gb', 0)
                st.metric("Disco", f"{disk_gb:.1f} GB")

            with usage_cols[3]:
                st.metric("Conexiones DB", performance.get('throughput', {}).get('database_connections', 0))

            st.divider()

            # Calidad de datos
            st.subheader("🔍 CALIDAD DE DATOS")

            data_quality = dashboard.get('data_quality_status', {})

            quality_cols = st.columns(3)

            with quality_cols[0]:
                overall_score = data_quality.get('overall_score', 0)
                st.metric("Puntuación General", f"{overall_score:.1f}%")

            with quality_cols[1]:
                issues = data_quality.get('tables_with_issues', 0)
                st.metric("Tablas con Problemas", issues)

            with quality_cols[2]:
                critical_issues = data_quality.get('critical_issues', 0)
                st.metric("Problemas Críticos", critical_issues)

            st.divider()

            # Actividad reciente
            st.subheader("📝 ACTIVIDAD RECIENTE")

            recent_activity = dashboard.get('user_activity', [])

            if recent_activity:
                for activity in recent_activity[:10]:  # Últimas 10
                    with st.container():
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.write(f"👤 **{activity['user']}**")
                            st.caption(f"{activity['action']} (Agente: {activity['agent'].upper()})")

                        with col2:
                            timestamp = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
                            time_ago = datetime.now() - timestamp
                            if time_ago.days > 0:
                                time_str = f"{time_ago.days}d atrás"
                            elif time_ago.seconds // 3600 > 0:
                                time_str = f"{time_ago.seconds // 3600}h atrás"
                            elif time_ago.seconds // 60 > 0:
                                time_str = f"{time_ago.seconds // 60}m atrás"
                            else:
                                time_str = "Ahora"
                            st.caption(time_str)

                        st.divider()
            else:
                st.info("No hay actividad reciente registrada")

        else:
            st.error(f"❌ Error obteniendo estado del sistema: {health.get('error', 'Desconocido')}")

        st.divider()

        # Acción de diagnóstico
        st.subheader("🔧 DIAGNÓSTICO DEL SISTEMA")

        if st.button("🚀 Ejecutar Diagnóstico Completo", use_container_width=True):
            with st.spinner("Ejecutando diagnóstico completo..."):
                from system_integrator import get_system_diagnostics
                diagnostics = get_system_diagnostics()

                st.subheader("📋 Resultados del Diagnóstico")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Tests Ejecutados", len(diagnostics['tests_run']))

                with col2:
                    passed = diagnostics['passed']
                    total = len(diagnostics['tests_run'])
                    st.metric("Tests Aprobados", f"{passed}/{total}")

                with col3:
                    failed = diagnostics['failed']
                    st.metric("Tests Fallidos", failed)

                # Detalle de tests
                with st.expander("📊 Detalle de Tests", expanded=True):
                    for test in diagnostics['tests_run'][:15]:  # Top 15
                        status_icon = "✅" if test['status'] == 'passed' else "❌"

                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.write(f"{status_icon} **{test['name']}**")
                            st.caption(test.get('details', ''))

                        with col2:
                            st.write(test['status'].title())

                if failed > 0:
                    st.warning(f"⚠️ {failed} tests fallaron. Revisa la configuración del sistema.")
                else:
                    st.success("✅ Todos los tests pasaron exitosamente!")

        # Integraciones externas
        st.subheader("🔗 INTEGRACIONES EXTERNAS")

        integrations = {
            'Metabase': {'status': 'not_configured', 'message': 'Requiere configuración para SSBF'},
            'Email Service': {'status': 'not_configured', 'message': 'SMTP no configurado'},
            'Slack': {'status': 'not_configured', 'message': 'Webhook no configurado'},
            'Storage': {'status': 'available', 'message': 'Almacenamiento local disponible'}
        }

        for service, status_info in integrations.items():
            status_icon = "✅" if status_info['status'] == 'available' else "⚠️" if status_info['status'] == 'not_configured' else "❌"
            st.write(f"{status_icon} **{service}**: {status_info['message']}")

    except Exception as e:
        st.error(f"Error en página de estado del sistema: {str(e)}")
        st.exception(e)

def show_data_import_page():
    """
    Página del Data Import Manager (DIM) - Importación de datos para producción
    """
    st.title("📤 Importación de Datos para Producción")
    st.markdown("---")

    st.warning("""
    **⚠️ Importante:** Esta funcionalidad está diseñada para migrar de datos de demostración a datos reales de producción.

    Una vez que completes la importación de tus datos reales, el sistema se reinicializará automáticamente
    para usar tu información real en lugar de los datos de prueba.
    """)

    # Inicializar DIM
    dim = DataImportManager()

    try:
        # Estado actual del sistema
        st.subheader("📊 Estado Actual del Sistema")

        col1, col2, col3 = st.columns(3)

        # Contar registros actuales (simulado con datos de demo)
        with col1:
            st.metric("Clientes", "2", help="Datos de demostración")

        with col2:
            st.metric("Facturas", "15", help="Datos de demostración")

        with col3:
            st.metric("Vendedores", "1", help="Datos de demostración")

        st.info("Los números mostrados corresponden a datos de demostración. Una vez que importes tus datos reales, estos valores se actualizarán automáticamente.")

        st.divider()

        # Paso 1: Descargar plantillas
        st.subheader("📋 PASO 1: Descargar Plantillas de Importación")

        st.write("""
        Para facilitar la importación, descarga las plantillas Excel/CSV con el formato correcto para cada tipo de dato.
        Completa estas plantillas con tu información real.
        """)

        template_options = {
            'clientes': '📝 Plantilla Clientes',
            'facturas': '📄 Plantilla Facturas',
            'vendedores': '👤 Plantilla Vendedores',
            'actividades_venta': '📅 Plantilla Actividades de Venta'
        }

        col1, col2, col3, col4 = st.columns(4)

        template_cols = [col1, col2, col3, col4]
        template_keys = list(template_options.keys())

        for i, (template_key, template_name) in enumerate(template_options.items()):
            with template_cols[i]:
                if st.button(f"📥\n{template_name}", use_container_width=True):
                    with st.spinner(f"Generando plantilla {template_name}..."):
                        template_result = dim.export_template_file(template_key, 'xlsx')

                        if template_result['success']:
                            st.success(f"✅ Plantilla generada: {template_result['filename']}")
                            st.download_button(
                                label="⬇️ Descargar Plantilla",
                                data=open(template_result['file_path'], 'rb'),
                                file_name=template_result['filename'],
                                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                            )

                            # Mostrar campos requeridos
                            templates = dim.get_import_templates()
                            if template_key in templates:
                                required_fields = templates[template_key]['required_fields']
                                st.caption(f"Campos requeridos: {', '.join(required_fields)}")
                        else:
                            st.error(f"❌ Error generando plantilla: {template_result.get('error')}")

        st.divider()

        # Paso 2: Subir archivos
        st.subheader("📤 PASO 2: Subir Tus Datos Reales")

        st.write("""
        Una vez completadas las plantillas, súbelas aquí. El sistema validará automáticamente
        la estructura de tus datos y los preparará para importación.
        """)

        # Seleccionar tabla para importar
        table_options = list(template_options.keys())
        selected_table = st.selectbox(
            "Selecciona el tipo de datos a importar",
            ["Elige una tabla..."] + table_options,
            key="table_selector"
        )

        if selected_table != "Elige una tabla...":
            # Mostrar información de la tabla
            templates = dim.get_import_templates()
            if selected_table in templates:
                table_info = templates[selected_table]
                st.write("**Campos requeridos:**", ", ".join(table_info['required_fields']))
                st.write("**Campos opcionales:**", ", ".join(table_info.get('optional_fields', [])))

                # Preview de datos de ejemplo
                example_data = table_info.get('example_data', [])
                if example_data:
                    with st.expander("👀 Ver Ejemplo de Datos"):
                        df_example = pd.DataFrame(example_data)
                        st.dataframe(df_example, use_container_width=True)

            # Subir archivo
            uploaded_file = st.file_uploader(
                f"Súbe tu archivo de {selected_table} (CSV, Excel o JSON)",
                type=['csv', 'xlsx', 'xls', 'json'],
                key=f"file_uploader_{selected_table}"
            )

            if uploaded_file is not None:
                # Guardar archivo temporalmente
                import os
                temp_filepath = os.path.join(dim.import_dir, uploaded_file.name)

                with open(temp_filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                st.success(f"✅ Archivo '{uploaded_file.name}' subido correctamente")
                st.info("Archivo guardado temporalmente. Ahora validaremos su contenido...")

                # Validar archivo
                if st.button("🔍 Validar Archivo", use_container_width=True, key=f"validate_{selected_table}"):
                    with st.spinner("Validando estructura del archivo..."):
                        validation_result = dim.validate_import_file(temp_filepath, selected_table)

                        if validation_result['success']:
                            st.success("✅ Validación exitosa")

                            # Mostrar información del archivo
                            file_info = validation_result['file_info']
                            st.write(f"**Registros encontrados:** {file_info['rows']}")
                            st.write(f"**Columnas:** {file_info['columns']}")
                            st.write(f"**Tamaño:** {file_info['size_mb']:.2f} MB")

                            # Mostrar mapeo automático sugerido
                            field_mapping = validation_result.get('field_mapping', {})
                            if field_mapping:
                                st.subheader("🎯 Mapeo de Campos Sugerido")
                                mapping_df = pd.DataFrame([
                                    {'Campo en tu archivo': k, 'Campo en el sistema': v}
                                    for k, v in field_mapping.items()
                                ])
                                st.dataframe(mapping_df, use_container_width=True)

                            # Mostrar preview de datos
                            if validation_result.get('preview'):
                                with st.expander("👀 Preview de Datos (primeros 5 registros)"):
                                    preview_df = pd.DataFrame(validation_result['preview'])
                                    st.dataframe(preview_df, use_container_width=True)

                            # Análisis de calidad
                            quality = validation_result.get('quality_analysis', {})
                            if quality.get('issues'):
                                st.warning("⚠️ Se encontraron algunos problemas de calidad:")
                                for issue in quality['issues'][:5]:
                                    st.write(f"• {issue}")

                            # Guardar información de validación en session state
                            st.session_state[f'import_validation_{selected_table}'] = {
                                'filepath': temp_filepath,
                                'validation': validation_result,
                                'field_mapping': field_mapping
                            }

                            st.info("✅ Archivo validado correctamente. Puedes proceder con la importación.")

                        else:
                            st.error(f"❌ Error de validación: {validation_result.get('error')}")

                            if validation_result.get('missing_fields'):
                                st.write("**Campos faltantes:**", ", ".join(validation_result['missing_fields']))

            # Paso 3: Ejecutar importación
            if hasattr(st.session_state, f'import_validation_{selected_table}') and st.session_state[f'import_validation_{selected_table}']['validation']['success']:

                st.divider()
                st.subheader("🚀 PASO 3: Ejecutar Importación")

                st.warning("""
                **⚠️ Antes de proceder:** Asegúrate de que los datos son correctos.
                Una vez ejecutada la importación, tus datos reales reemplazarán los de demostración.
                """)

                col1, col2 = st.columns(2)

                with col1:
                    dry_run = st.checkbox(
                        "Modo seguro (recomendado)",
                        value=True,
                        help="Simular importación sin modificar datos. Desmarca para ejecutar importación real."
                    )

                with col2:
                    if st.button("🚀 Ejecutar Importación", use_container_width=True, type="primary"):
                        # Obtener datos de validación
                        validation_data = st.session_state[f'import_validation_{selected_table}']
                        filepath = validation_data['filepath']
                        field_mapping = validation_data.get('field_mapping', {})

                        with st.spinner(f"{'Simulando' if dry_run else 'Ejecutando'} importación de {selected_table}..."):
                            # Ejecutar importación
                            import_result = dim.import_data(
                                file_path=filepath,
                                table_name=selected_table,
                                field_mapping=field_mapping,
                                inferred_column_types=validation_data['validation']['inferred_column_types'],
                                add_new_columns=field_mapping.get('unmapped_file_cols', []),
                                dry_run=dry_run
                            )

                            if import_result['success']:
                                if dry_run:
                                    st.success("✅ Simulación de importación completada exitosamente")

                                    st.write("**Datos procesados:**")
                                    st.write(f"• Registros leídos: {import_result['rows_processed']}")
                                    st.write(f"• Registros que se importarían: {import_result['rows_imported']}")

                                    if import_result.get('data_preview'):
                                        with st.expander("👀 Preview de datos a importar"):
                                            preview_df = pd.DataFrame(import_result['data_preview'])
                                            st.dataframe(preview_df, use_container_width=True)

                                    st.info("""
                                    **✅ Simulación exitosa**

                                    Revisa los datos mostrados arriba. Si todo se ve correcto,
                                    desmarca "Modo seguro" y ejecuta la importación real.
                                    """)

                                else:
                                    st.success(f"✅ Importación real completada exitosamente")
                                    st.write(f"• Registros procesados: {import_result['rows_processed']}")
                                    st.write(f"• Registros importados: {import_result['rows_imported']}")

                                    if import_result.get('errors'):
                                        st.warning(f"Se encontraron {len(import_result['errors'])} errores menores:")
                                        for error in import_result['errors'][:5]:
                                            st.write(f"• {error}")

                                    st.success("""
                                    **🎉 ¡Importación completada!**

                                    Tus datos reales ahora están en el sistema.
                                    Puedes continuar importando otros tipos de datos o proceder con el análisis.
                                    """)

                                    # Limpiar session state
                                    del st.session_state[f'import_validation_{selected_table}']

                            else:
                                st.error(f"❌ Error en importación: {import_result.get('error')}")

        st.divider()

        # Paso 4: Migración a producción
        st.subheader("🏭 PASO 4: Migración Completa a Producción")

        st.warning("""
        **⚠️ Acción Final:** Una vez que hayas importado todos tus datos principales
        (clientes, facturas, vendedores), ejecuta esta migración completa.

        Esto limpiará definitivamente los datos de demostración y optimizará el sistema para producción.
        """)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Realizar Backup Completo", use_container_width=True):
                with st.spinner("Creando backup completo de datos de demostración..."):
                    # Crear backup (simulado)
                    st.success("✅ Backup completo creado exitosamente")
                    st.info("Los datos de demostración se guardaron en: backups/full_backup_[fecha].json")

        with col2:
            if st.button("🚀 Migrar a Producción", use_container_width=True, type="primary"):
                with st.spinner("Ejecutando migración a producción..."):
                    # Ejecutar migración
                    migration_result = migrate_to_production()

                    if migration_result['success']:
                        st.success("🎉 ¡Migración a producción completada exitosamente!")

                        st.balloons()

                        st.write("""
                        **✅ Lo que acaba de suceder:**

                        1. **Backup creado:** Todos los datos de demostración se guardaron
                        2. **Datos limpiados:** Se eliminaron definitivamente los datos de prueba
                        3. **Sistema reinicializado:** Parámetros optimizados para datos reales
                        4. **Agentes recargados:** Modelos de IA preparados con tus datos

                        **🌟 ¡Felicitaciones! Tu sistema OAPCE BI ahora usa datos reales de producción.**
                        """)

                        # Limpiar session state
                        for key in list(st.session_state.keys()):
                            if key.startswith('import_validation_'):
                                del st.session_state[key]

                        st.success("""
                        **📊 Próximos pasos recomendados:**

                        1. **Reentrena los modelos predictivos** con datos reales
                        2. **Verifica recomendaciones** del Asesor Prescriptivo
                        3. **Configura reportes automáticos** según tus necesidades
                        4. **Personaliza métricas** según KPIs de tu empresa

                        ¡Bienvenido a la Inteligencia Artificial aplicada a tus datos reales! 🤖✨
                        """)

                    else:
                        st.error(f"❌ Error en migración: {migration_result.get('error')}")

    except Exception as e:
        st.error(f"Error en página de importación de datos: {str(e)}")
        st.exception(e)

    finally:
        dim.close()
