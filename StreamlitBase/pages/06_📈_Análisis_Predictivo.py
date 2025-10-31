import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Análisis Predictivo", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0F0F15; color: #E0E0FF; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Análisis Predictivo (PME)")

modelo = st.selectbox("Seleccionar modelo", ["Previsión de Ventas", "Riesgo de Morosidad"])

if modelo == "Previsión de Ventas":
    df = pd.DataFrame({
        "Fecha": pd.date_range("2025-07-01", periods=120),
        "Valor": [100 + i*0.5 + (i%10)*2 for i in range(120)]
    })
    df["Tipo"] = ["Histórico"] * 90 + ["Previsión"] * 30
    fig = px.line(df, x="Fecha", y="Valor", color="Tipo", color_discrete_map={"Histórico": "#555", "Previsión": "#00F3FF"})
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#E0E0FF"
    )
    st.plotly_chart(fig, width='stretch')
    
    st.metric("Ventas esperadas Q4", "$1.2M", delta="±4%")
    col1, col2 = st.columns(2)
    col1.metric("AUC", "0.92")
    col2.metric("MAPE", "4.1%")

else:
    clientes_df = pd.DataFrame({
        "Cliente": [f"Cliente {chr(65+i)}" for i in range(20)],
        "Probabilidad Morosidad": np.random.uniform(0.1, 0.95, 20),
        "Deuda Pendiente": np.random.uniform(5000, 50000, 20)
    })
    clientes_df = clientes_df.sort_values("Probabilidad Morosidad", ascending=False)
    
    fig = px.scatter(clientes_df, x="Deuda Pendiente", y="Probabilidad Morosidad", 
                     text="Cliente", color="Probabilidad Morosidad",
                     color_continuous_scale=["#00F3FF", "#FF00F7"])
    fig.update_traces(textposition='top center', marker=dict(size=12))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#E0E0FF"
    )
    st.plotly_chart(fig, width='stretch')
    
    st.metric("Clientes en riesgo alto (>60%)", "5", delta="+2")
    col1, col2 = st.columns(2)
    col1.metric("Precisión del modelo", "0.87")
    col2.metric("Recall", "0.82")
    
    st.subheader("Top 5 Clientes en Riesgo")
    st.dataframe(clientes_df.head(5), width='stretch')
