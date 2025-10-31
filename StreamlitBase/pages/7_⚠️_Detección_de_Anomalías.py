import streamlit as st
import pandas as pd
import plotly.express as px
import sys
sys.path.append('.')
from db_utils import execute_query, execute_update

st.set_page_config(page_title="Detección de Anomalías", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0F0F15; color: #E0E0FF; }
</style>
""", unsafe_allow_html=True)

st.title("⚠️ Detección de Anomalías (AD)")

anomalies = execute_query("""
    SELECT id, metric_name, detected_date, expected_value, actual_value, 
           deviation_percent, severity, status, description 
    FROM anomalies 
    ORDER BY detected_date DESC
""")

if len(anomalies) > 0:
    dates = pd.date_range("2025-10-01", periods=30)
    values = [20000] * 30
    
    for idx, row in anomalies.iterrows():
        date_idx = (pd.Timestamp(row['detected_date']) - pd.Timestamp("2025-10-01")).days
        if 0 <= date_idx < 30:
            values[date_idx] = row['actual_value']
    
    df = pd.DataFrame({
        "Fecha": dates,
        "Valor": values
    })
    
    anomalies['detected_date'] = pd.to_datetime(anomalies['detected_date'])
    anomaly_dates = anomalies[anomalies['detected_date'] >= pd.Timestamp("2025-10-01")]['detected_date']
    anomaly_values = anomalies[anomalies['detected_date'] >= pd.Timestamp("2025-10-01")]['actual_value']
    
    fig = px.line(df, x="Fecha", y="Valor", markers=True)
    if len(anomaly_dates) > 0:
        fig.add_scatter(x=anomaly_dates, y=anomaly_values,
                        mode='markers', marker=dict(color='#FF00F7', size=12), name='Anomalía')
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#E0E0FF"
    )
    st.plotly_chart(fig, width='stretch')

st.subheader("Alertas")

for idx, row in anomalies.iterrows():
    severity_icon = "🔴" if row['severity'] == "Crítica" else "🟡" if row['severity'] == "Alta" else "🟢"
    
    with st.expander(f"{severity_icon} {row['metric_name']} - {row['detected_date'].strftime('%Y-%m-%d')}"):
        st.write(f"**Descripción:** {row['description']}")
        st.write(f"**Valor esperado:** ${row['expected_value']:,.2f}")
        st.write(f"**Valor actual:** ${row['actual_value']:,.2f}")
        st.write(f"**Desviación:** {row['deviation_percent']:.1f}%")
        
        new_status = st.selectbox(
            "Estado", 
            ["Abierta", "En revisión", "Resuelta"],
            index=["Abierta", "En revisión", "Resuelta"].index(row['status']),
            key=f"status_{row['id']}"
        )
        
        if st.button("Actualizar Estado", key=f"update_{row['id']}"):
            execute_update("UPDATE anomalies SET status = %s WHERE id = %s", (new_status, row['id']))
            st.success("Estado actualizado")
            st.rerun()
