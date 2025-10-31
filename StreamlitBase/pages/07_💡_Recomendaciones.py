import streamlit as st

st.set_page_config(page_title="Recomendaciones", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0F0F15; color: #E0E0FF; }
</style>
""", unsafe_allow_html=True)

st.title("💡 Asesor Prescriptivo (PA)")

st.warning("⚠️ **Riesgo alto de morosidad**\n\nCliente ABC: probabilidad del 60%. Se recomienda contactar para negociar plan de pago.", icon="🚨")
st.button("📞 Contactar cliente", type="primary")

st.info("💡 **Oportunidad de venta cruzada**\n\nCliente XYZ: productos complementarios sugeridos. Impacto esperado: $5,000.", icon="✨")
st.button("🛒 Ver productos", type="secondary")

st.success("✅ **Campaña optimizada**\n\nROI proyectado aumenta un 18% con ajuste de segmento.", icon="📈")
