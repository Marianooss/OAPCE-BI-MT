import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import get_db
from models import Cliente, Vendedor, ActividadVenta, Factura, EstadoFunnelEnum
from sqlalchemy import func
from datetime import datetime, timedelta

def show_commercial_dashboard():
    st.title("📊 Módulo Comercial")
    
    db = get_db()
    
    try:
        tab1, tab2, tab3 = st.tabs(["Cartera de Clientes", "Funnel de Ventas", "Performance Vendedores"])
        
        with tab1:
            show_client_portfolio(db)
        
        with tab2:
            show_sales_funnel(db)
        
        with tab3:
            show_vendor_performance(db)
    
    finally:
        db.close()

def show_client_portfolio(db):
    st.subheader("Cartera de Clientes")
    
    clientes = db.query(Cliente).all()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Clientes", len(clientes))
    
    with col2:
        clientes_activos = len([c for c in clientes if c.estado_funnel != EstadoFunnelEnum.perdido])
        st.metric("Clientes Activos", clientes_activos)
    
    with col3:
        valor_total = sum(c.valor_estimado for c in clientes)
        st.metric("Valor Total Cartera", f"${valor_total:,.0f}")
    
    with col4:
        nuevos_mes = len([c for c in clientes if c.fecha_ingreso >= (datetime.now().date() - timedelta(days=30))])
        st.metric("Nuevos este mes", nuevos_mes)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Clientes por Estado")
        estado_counts = {}
        for cliente in clientes:
            estado = cliente.estado_funnel.value
            estado_counts[estado] = estado_counts.get(estado, 0) + 1
        
        if estado_counts:
            df_estados = pd.DataFrame(list(estado_counts.items()), columns=['Estado', 'Cantidad'])
            fig = px.pie(df_estados, values='Cantidad', names='Estado', 
                        title='Distribución por Estado del Funnel')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Clientes por Vendedor")
        vendedor_counts = db.query(
            Vendedor.nombre,
            func.count(Cliente.id).label('cantidad')
        ).join(Cliente).group_by(Vendedor.nombre).all()
        
        if vendedor_counts:
            df_vendedores = pd.DataFrame(vendedor_counts, columns=['Vendedor', 'Cantidad'])
            fig = px.bar(df_vendedores, x='Vendedor', y='Cantidad',
                        title='Clientes por Vendedor')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### Lista de Clientes")
    
    df_clientes = pd.DataFrame([{
        'Nombre': c.nombre,
        'RUT': c.rut,
        'Vendedor': c.vendedor.nombre if c.vendedor else 'N/A',
        'Estado': c.estado_funnel.value,
        'Valor Estimado': f"${c.valor_estimado:,.0f}",
        'Email': c.email
    } for c in clientes])
    
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True, hide_index=True)

def show_sales_funnel(db):
    st.subheader("Funnel de Ventas")
    
    clientes = db.query(Cliente).all()
    
    funnel_data = {}
    funnel_values = {}
    
    for estado in EstadoFunnelEnum:
        clientes_estado = [c for c in clientes if c.estado_funnel == estado]
        funnel_data[estado.value] = len(clientes_estado)
        funnel_values[estado.value] = sum(c.valor_estimado for c in clientes_estado)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Funnel por Cantidad")
        if funnel_data:
            fig = go.Figure(go.Funnel(
                y=list(funnel_data.keys()),
                x=list(funnel_data.values()),
                textinfo="value+percent initial"
            ))
            fig.update_layout(title='Cantidad de Clientes por Etapa')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Funnel por Valor")
        if funnel_values:
            fig = go.Figure(go.Funnel(
                y=list(funnel_values.keys()),
                x=list(funnel_values.values()),
                textinfo="value+percent initial"
            ))
            fig.update_layout(title='Valor Estimado por Etapa')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tasa_conversion = (funnel_data.get('Ganado', 0) / len(clientes) * 100) if clientes else 0
        st.metric("Tasa de Conversión", f"{tasa_conversion:.1f}%")
    
    with col2:
        valor_ganado = funnel_values.get('Ganado', 0)
        st.metric("Valor Ganado", f"${valor_ganado:,.0f}")
    
    with col3:
        pipeline_value = sum(v for k, v in funnel_values.items() if k not in ['Ganado', 'Perdido'])
        st.metric("Pipeline Total", f"${pipeline_value:,.0f}")

def show_vendor_performance(db):
    st.subheader("Performance de Vendedores")
    
    vendedores = db.query(Vendedor).filter(Vendedor.activo == 1).all()
    
    performance_data = []
    
    for vendedor in vendedores:
        clientes_count = db.query(Cliente).filter(Cliente.vendedor_id == vendedor.id).count()
        
        clientes_ganados = db.query(Cliente).filter(
            Cliente.vendedor_id == vendedor.id,
            Cliente.estado_funnel == EstadoFunnelEnum.ganado
        ).count()
        
        valor_cartera = db.query(func.sum(Cliente.valor_estimado)).filter(
            Cliente.vendedor_id == vendedor.id
        ).scalar() or 0
        
        actividades_mes = db.query(ActividadVenta).filter(
            ActividadVenta.vendedor_id == vendedor.id,
            ActividadVenta.fecha >= (datetime.now().date() - timedelta(days=30))
        ).count()
        
        ventas_mes = db.query(func.sum(Factura.monto_total)).join(
            Cliente
        ).filter(
            Cliente.vendedor_id == vendedor.id,
            Factura.fecha_emision >= (datetime.now().date() - timedelta(days=30))
        ).scalar() or 0
        
        cumplimiento = (ventas_mes / vendedor.meta_mensual * 100) if vendedor.meta_mensual > 0 else 0
        
        performance_data.append({
            'Vendedor': vendedor.nombre,
            'Clientes': clientes_count,
            'Clientes Ganados': clientes_ganados,
            'Valor Cartera': valor_cartera,
            'Actividades (30d)': actividades_mes,
            'Ventas Mes': ventas_mes,
            'Meta Mensual': vendedor.meta_mensual,
            'Cumplimiento %': cumplimiento
        })
    
    if performance_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Cumplimiento de Metas")
            df_cumplimiento = pd.DataFrame([{
                'Vendedor': p['Vendedor'],
                'Cumplimiento': p['Cumplimiento %']
            } for p in performance_data])
            
            fig = px.bar(df_cumplimiento, x='Vendedor', y='Cumplimiento',
                        title='% Cumplimiento Meta Mensual')
            fig.add_hline(y=100, line_dash="dash", line_color="green", 
                         annotation_text="Meta 100%")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Ventas del Mes")
            df_ventas = pd.DataFrame([{
                'Vendedor': p['Vendedor'],
                'Ventas': p['Ventas Mes']
            } for p in performance_data])
            
            fig = px.bar(df_ventas, x='Vendedor', y='Ventas',
                        title='Ventas Realizadas (Últimos 30 días)')
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### Detalle por Vendedor")
        
        df_performance = pd.DataFrame(performance_data)
        df_performance['Valor Cartera'] = df_performance['Valor Cartera'].apply(lambda x: f"${x:,.0f}")
        df_performance['Ventas Mes'] = df_performance['Ventas Mes'].apply(lambda x: f"${x:,.0f}")
        df_performance['Meta Mensual'] = df_performance['Meta Mensual'].apply(lambda x: f"${x:,.0f}")
        df_performance['Cumplimiento %'] = df_performance['Cumplimiento %'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(df_performance, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    show_commercial_dashboard()
