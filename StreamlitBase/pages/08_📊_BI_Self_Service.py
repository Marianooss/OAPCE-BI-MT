import streamlit as st

st.set_page_config(page_title="BI Self-Service", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0F0F15; color: #E0E0FF; }
</style>
""", unsafe_allow_html=True)

st.title("📊 BI Self-Service (SSBF)")

st.markdown("### Construye y comparte tus propios dashboards")

st.info("📊 Aquí podrás integrar herramientas como Metabase, Superset o Power BI para crear dashboards personalizados.")

st.markdown("""
### Ejemplo de integración:

Para integrar un dashboard externo, puedes usar:
```python
st.components.v1.iframe(
    src="https://tu-dashboard-url.com",
    height=600,
    scrolling=True
)
```
""")

st.sidebar.header("Biblioteca de Métricas")
st.sidebar.markdown("""
- Tasa de Conversión  
- CAC  
- LTV  
- Margen Bruto  
- Retención Mensual
""")
