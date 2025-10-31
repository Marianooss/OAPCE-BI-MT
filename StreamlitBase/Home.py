import streamlit as st
import plotly.graph_objects as go
import sys
sys.path.append('.')
from db_utils import execute_query

st.set_page_config(page_title="BiOss – Data Driven Decisions", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    :root {
        --cian: #00F3FF;
        --magenta: #FF00F7;
        --bg: #0F0F15;
        --card-bg: #1E1E28;
    }
    .stApp { background-color: var(--bg); color: #E0E0FF; }
    .metric-card { background-color: var(--card-bg); padding: 1.2rem; border-radius: 8px; margin: 0.5rem 0; }
    .alert-critical { border-left: 4px solid var(--magenta); }
    .alert-info { border-left: 4px solid var(--cian); }
</style>
""", unsafe_allow_html=True)

st.title("🧠 BiOss – Data Driven Decisions")
st.markdown("Dashboard principal de inteligencia operativa")

latest_quality = execute_query("SELECT AVG(quality_score) as avg_score FROM quality_metrics WHERE metric_date >= CURRENT_DATE - INTERVAL '30 days'")
avg_score = round(latest_quality['avg_score'].iloc[0], 0) if len(latest_quality) > 0 else 92

active_alerts = execute_query("SELECT COUNT(*) as count FROM anomalies WHERE status = 'Abierta'")
alert_count = int(active_alerts['count'].iloc[0])

total_sales = execute_query("SELECT SUM(monto) as total FROM ventas_diarias WHERE fecha >= CURRENT_DATE - INTERVAL '90 days'")
sales_amount = total_sales['total'].iloc[0] if len(total_sales) > 0 and total_sales['total'].iloc[0] else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Calidad de Datos", f"{avg_score:.0f}%", "+2% vs mes")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card alert-critical">', unsafe_allow_html=True)
    st.metric("Alertas Activas", str(alert_count), "↑ 1 crítica")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Ventas Q4", f"${sales_amount/1000:.1f}K", "±4%")
    st.markdown('</div>', unsafe_allow_html=True)

st.subheader("Tendencia de Calidad de Datos")
quality_trend = execute_query("""
    SELECT metric_date, AVG(quality_score) as score 
    FROM quality_metrics 
    WHERE metric_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY metric_date 
    ORDER BY metric_date
""")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=quality_trend['metric_date'], 
    y=quality_trend['score'], 
    mode='lines', 
    line=dict(color="#00F3FF")
))
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="#E0E0FF",
    xaxis_showgrid=False,
    yaxis_showgrid=False
)
st.plotly_chart(fig, width='stretch')

st.subheader("Actividad Reciente")
recent_anomalies = execute_query("SELECT description FROM anomalies WHERE status = 'Abierta' ORDER BY detected_date DESC LIMIT 1")
if len(recent_anomalies) > 0:
    st.info(f"⚠️ {recent_anomalies['description'].iloc[0]} – [Ver detalle](#)")

recent_reports = execute_query("SELECT nombre FROM scheduled_reports WHERE activo = true ORDER BY ultima_ejecucion DESC LIMIT 1")
if len(recent_reports) > 0:
    st.success(f"✅ Reporte {recent_reports['nombre'].iloc[0]} generado y enviado")
