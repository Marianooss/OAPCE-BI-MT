import streamlit as st
import sys
sys.path.append('.')
from db_utils import execute_query

st.set_page_config(page_title="Catálogo de Datos", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0F0F15; color: #E0E0FF; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Catálogo de Datos (DCM)")

data = execute_query("SELECT nombre, descripcion, propietario, ultima_actualizacion, etiqueta FROM dataset_catalog ORDER BY nombre")
data.columns = ["Nombre", "Descripción", "Propietario", "Última actualización", "Etiquetas"]

etiqueta_filtro = st.selectbox("Filtrar por etiqueta", ["Todas", "público", "confidencial", "restringido"])
if etiqueta_filtro != "Todas":
    data = data[data["Etiquetas"] == etiqueta_filtro]

st.dataframe(data, width='stretch')

st.subheader("Vista de Detalle")
buscar = st.text_input("Buscar activo", placeholder="Ej: ventas_diarias")

if buscar:
    detalle = execute_query(
        "SELECT * FROM dataset_catalog WHERE nombre ILIKE %s", 
        (f"%{buscar}%",)
    )
    
    if len(detalle) > 0:
        row = detalle.iloc[0]
        st.markdown(f"""
**{row['nombre']}**  
- Descripción: {row['descripcion']}  
- Propietario: {row['propietario']}  
- SLA: {row['sla']}  
- Columnas: {row['columnas']}  
- Etiqueta: {row['etiqueta']} ✅
        """)
    else:
        st.warning("No se encontró ningún dataset con ese nombre")
else:
    st.markdown("""
**ventas_diarias**  
- Descripción: Ventas por día y tienda  
- Propietario: Equipo Finanzas  
- SLA: Actualización diaria antes de las 6 AM  
- Columnas: fecha, tienda_id, producto_id, monto, unidades  
- Etiqueta: público ✅
    """)
