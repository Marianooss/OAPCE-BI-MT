import streamlit as st
import pandas as pd

st.set_page_config(page_title="Centro de Métricas", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0F0F15; color: #E0E0FF; }
</style>
""", unsafe_allow_html=True)

st.title("📘 Centro de Métricas (MDH)")

metrics = pd.DataFrame({
    "Métrica": ["Tasa de Conversión", "LTV", "CAC"],
    "Fórmula": [
        "(Oportunidades Cerradas / Oportunidades Creadas) * 100",
        "Valor promedio de compra × Frecuencia × Tiempo",
        "Costo total de adquisición / Nuevos clientes"
    ],
    "Dimensiones": ["Canal, Región", "Segmento, Cohorte", "Campaña, Canal"]
})

st.dataframe(metrics, width='stretch')

st.subheader("Definición detallada")
st.markdown("""
**Tasa de Conversión**  
Mide la eficiencia del funnel de ventas.  
- **Fórmula**: `(Oportunidades Cerradas / Oportunidades Creadas) * 100`  
- **Ejemplo**: 250 cerradas / 1000 creadas = **25%**  
- **Dashboards relacionados**: [Funnel de Ventas](#)
""")
