import streamlit as st
import pandas as pd
import sys
sys.path.append('.')
from db_utils import execute_query, execute_update

st.set_page_config(page_title="Programación de Reportes", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0F0F15; color: #E0E0FF; }
</style>
""", unsafe_allow_html=True)

st.title("📬 Programación de Reportes (ARD)")

with st.form("nuevo_reporte"):
    nombre = st.text_input("Nombre del reporte")
    frecuencia = st.selectbox("Frecuencia", ["Diaria", "Semanal", "Mensual"])
    formato = st.radio("Formato", ["PDF", "Excel", "Enlace"])
    destinatarios = st.text_input("Destinatarios (emails separados por coma)")
    submitted = st.form_submit_button("Guardar reporte")
    if submitted and nombre:
        execute_update("""
            INSERT INTO scheduled_reports (nombre, frecuencia, formato, destinatarios, activo)
            VALUES (%s, %s, %s, %s, true)
        """, (nombre, frecuencia, formato, destinatarios))
        st.success(f"✅ Reporte '{nombre}' programado ({frecuencia})")
        st.rerun()

st.subheader("Reportes Programados")
reportes = execute_query("""
    SELECT nombre, frecuencia, 
           TO_CHAR(ultima_ejecucion, 'YYYY-MM-DD') as ultima_ejecucion,
           CASE WHEN activo THEN 'Activo' ELSE 'Inactivo' END as estado,
           id
    FROM scheduled_reports
    ORDER BY created_at DESC
""")

if len(reportes) > 0:
    display_df = reportes[['nombre', 'frecuencia', 'ultima_ejecucion', 'estado']]
    display_df.columns = ['Nombre', 'Frecuencia', 'Última ejecución', 'Estado']
    st.dataframe(display_df, width='stretch')
else:
    st.info("No hay reportes programados")

