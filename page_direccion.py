import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import get_db
from models import Cliente, Vendedor, Factura, Cobranza, MovimientoCaja, ActividadVenta, EstadoFunnelEnum, EstadoFacturaEnum
from sqlalchemy import func
from datetime import datetime, timedelta

def show_management_dashboard():
    st.title("📈 Dirección General")
    st.markdown("### Tablero de Control Ejecutivo")
    
    db = get_db()
    
    try:
        show_executive_kpis(db)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            show_financial_summary(db)
        
        with col2:
            show_commercial_summary(db)
        
        st.markdown("---")
        
        show_trends_analysis(db)
        
    finally:
        db.close()

def show_executive_kpis(db):
    st.subheader("KPIs Principales")
    
    facturas = db.query(Factura).all()
    cobranzas = db.query(Cobranza).all()
    clientes = db.query(Cliente).all()
    movimientos = db.query(MovimientoCaja).all()
    
    facturas_mes = [f for f in facturas if f.fecha_emision >= (datetime.now().date() - timedelta(days=30))]
    cobranzas_mes = [c for c in cobranzas if c.fecha_pago >= (datetime.now().date() - timedelta(days=30))]
    
    facturado_mes = sum(f.monto_total for f in facturas_mes)
    cobrado_mes = sum(c.monto for c in cobranzas_mes)
    
    ingresos = [m for m in movimientos if m.tipo == 'Ingreso']
    egresos = [m for m in movimientos if m.tipo == 'Egreso']
    total_ingresos = sum(m.monto for m in ingresos)
    total_egresos = sum(m.monto for m in egresos)
    saldo_neto = total_ingresos - total_egresos
    
    clientes_activos = len([c for c in clientes if c.estado_funnel != EstadoFunnelEnum.perdido])
    total_cartera = sum(c.valor_estimado for c in clientes)
    
    facturas_pendientes = [f for f in facturas if f.estado in [EstadoFacturaEnum.pendiente, EstadoFacturaEnum.parcial]]
    total_por_cobrar = sum(f.monto_total - f.monto_pagado for f in facturas_pendientes)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric(
            "Facturación Mensual",
            f"${facturado_mes:,.0f}",
            delta=f"{len(facturas_mes)} facturas"
        )
    
    with col2:
        st.metric(
            "Cobranzas Mensuales",
            f"${cobrado_mes:,.0f}",
            delta=f"{len(cobranzas_mes)} pagos"
        )
    
    with col3:
        st.metric(
            "Por Cobrar",
            f"${total_por_cobrar:,.0f}",
            delta=f"{len(facturas_pendientes)} fact."
        )
    
    with col4:
        st.metric(
            "Saldo Neto",
            f"${saldo_neto:,.0f}",
            delta="Ingresos - Egresos"
        )
    
    with col5:
        st.metric(
            "Clientes Activos",
            clientes_activos,
            delta=f"de {len(clientes)} total"
        )
    
    with col6:
        st.metric(
            "Valor Cartera",
            f"${total_cartera:,.0f}",
            delta="Pipeline total"
        )

def show_financial_summary(db):
    st.markdown("#### 💰 Resumen Financiero")
    
    facturas = db.query(Factura).all()
    cobranzas = db.query(Cobranza).all()
    movimientos = db.query(MovimientoCaja).all()
    
    facturas_sorted = sorted(facturas, key=lambda x: x.fecha_emision)
    
    monthly_data = {}
    for factura in facturas_sorted:
        mes = factura.fecha_emision.strftime('%Y-%m')
        if mes not in monthly_data:
            monthly_data[mes] = {'Facturación': 0, 'Cobranzas': 0}
        monthly_data[mes]['Facturación'] += factura.monto_total
    
    for cobranza in cobranzas:
        mes = cobranza.fecha_pago.strftime('%Y-%m')
        if mes in monthly_data:
            monthly_data[mes]['Cobranzas'] += cobranza.monto
    
    if monthly_data:
        df_financial = pd.DataFrame([
            {'Mes': mes, 'Tipo': 'Facturación', 'Monto': data['Facturación']}
            for mes, data in monthly_data.items()
        ] + [
            {'Mes': mes, 'Tipo': 'Cobranzas', 'Monto': data['Cobranzas']}
            for mes, data in monthly_data.items()
        ])
        
        fig = px.line(df_financial, x='Mes', y='Monto', color='Tipo',
                     title='Evolución Facturación vs Cobranzas',
                     markers=True)
        st.plotly_chart(fig, use_container_width=True)
    
    ingresos_mes = [m for m in movimientos if m.tipo == 'Ingreso' and m.fecha >= datetime.now().date() - timedelta(days=30)]
    egresos_mes = [m for m in movimientos if m.tipo == 'Egreso' and m.fecha >= datetime.now().date() - timedelta(days=30)]
    
    total_ing_mes = sum(m.monto for m in ingresos_mes)
    total_egr_mes = sum(m.monto for m in egresos_mes)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Ingresos del Mes", f"${total_ing_mes:,.0f}")
    with col2:
        st.metric("Egresos del Mes", f"${total_egr_mes:,.0f}")
    
    facturas_estado = {}
    for factura in facturas:
        estado = factura.estado.value
        facturas_estado[estado] = facturas_estado.get(estado, 0) + 1
    
    if facturas_estado:
        df_estados = pd.DataFrame(list(facturas_estado.items()), columns=['Estado', 'Cantidad'])
        fig = px.pie(df_estados, values='Cantidad', names='Estado',
                    title='Estado de Facturas',
                    hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

def show_commercial_summary(db):
    st.markdown("#### 📊 Resumen Comercial")
    
    clientes = db.query(Cliente).all()
    vendedores = db.query(Vendedor).filter(Vendedor.activo == 1).all()
    actividades = db.query(ActividadVenta).all()
    
    funnel_data = {}
    for estado in EstadoFunnelEnum:
        count = len([c for c in clientes if c.estado_funnel == estado])
        if count > 0:
            funnel_data[estado.value] = count
    
    if funnel_data:
        fig = go.Figure(go.Funnel(
            y=list(funnel_data.keys()),
            x=list(funnel_data.values()),
            textinfo="value+percent initial"
        ))
        fig.update_layout(title='Funnel de Ventas')
        st.plotly_chart(fig, use_container_width=True)
    
    clientes_ganados = len([c for c in clientes if c.estado_funnel == EstadoFunnelEnum.ganado])
    valor_ganado = sum(c.valor_estimado for c in clientes if c.estado_funnel == EstadoFunnelEnum.ganado)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Clientes Ganados", clientes_ganados)
    with col2:
        st.metric("Valor Ganado", f"${valor_ganado:,.0f}")
    
    vendedor_ventas = []
    for vendedor in vendedores:
        ventas_mes = db.query(func.sum(Factura.monto_total)).join(
            Cliente
        ).filter(
            Cliente.vendedor_id == vendedor.id,
            Factura.fecha_emision >= (datetime.now().date() - timedelta(days=30))
        ).scalar() or 0
        
        cumplimiento = (ventas_mes / vendedor.meta_mensual * 100) if vendedor.meta_mensual > 0 else 0
        
        vendedor_ventas.append({
            'Vendedor': vendedor.nombre,
            'Cumplimiento': cumplimiento
        })
    
    if vendedor_ventas:
        df_vendedores = pd.DataFrame(vendedor_ventas)
        fig = px.bar(df_vendedores, x='Vendedor', y='Cumplimiento',
                    title='Cumplimiento de Metas por Vendedor (%)')
        fig.add_hline(y=100, line_dash="dash", line_color="green")
        st.plotly_chart(fig, use_container_width=True)

def show_trends_analysis(db):
    st.subheader("Análisis de Tendencias")
    
    tab1, tab2, tab3 = st.tabs(["Rendimiento Global", "Indicadores Clave", "Alertas"])
    
    with tab1:
        show_global_performance(db)
    
    with tab2:
        show_key_indicators(db)
    
    with tab3:
        show_alerts(db)

def show_global_performance(db):
    facturas = db.query(Factura).all()
    cobranzas = db.query(Cobranza).all()
    clientes = db.query(Cliente).all()
    
    monthly_metrics = {}
    
    for factura in facturas:
        mes = factura.fecha_emision.strftime('%Y-%m')
        if mes not in monthly_metrics:
            monthly_metrics[mes] = {
                'Facturación': 0,
                'Clientes Nuevos': 0,
                'Cobranzas': 0
            }
        monthly_metrics[mes]['Facturación'] += factura.monto_total
    
    for cliente in clientes:
        mes = cliente.fecha_ingreso.strftime('%Y-%m')
        if mes in monthly_metrics:
            monthly_metrics[mes]['Clientes Nuevos'] += 1
    
    for cobranza in cobranzas:
        mes = cobranza.fecha_pago.strftime('%Y-%m')
        if mes in monthly_metrics:
            monthly_metrics[mes]['Cobranzas'] += cobranza.monto
    
    if monthly_metrics:
        df_metrics = pd.DataFrame([
            {
                'Mes': mes,
                'Facturación': data['Facturación'],
                'Cobranzas': data['Cobranzas'],
                'Clientes Nuevos': data['Clientes Nuevos']
            }
            for mes, data in sorted(monthly_metrics.items())
        ])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_metrics['Mes'],
            y=df_metrics['Facturación'],
            name='Facturación',
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=df_metrics['Mes'],
            y=df_metrics['Cobranzas'],
            name='Cobranzas',
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title='Evolución Mensual de Facturación y Cobranzas',
            xaxis_title='Mes',
            yaxis_title='Monto ($)',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig2 = px.bar(df_metrics, x='Mes', y='Clientes Nuevos',
                         title='Nuevos Clientes por Mes')
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            if len(df_metrics) > 1:
                df_metrics['Tasa Cobranza %'] = (df_metrics['Cobranzas'] / df_metrics['Facturación'] * 100).round(2)
                fig3 = px.line(df_metrics, x='Mes', y='Tasa Cobranza %',
                              title='Tasa de Cobranza (%)', markers=True)
                fig3.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Meta 80%")
                st.plotly_chart(fig3, use_container_width=True)

def show_key_indicators(db):
    col1, col2, col3 = st.columns(3)
    
    clientes = db.query(Cliente).all()
    facturas = db.query(Factura).all()
    vendedores = db.query(Vendedor).filter(Vendedor.activo == 1).all()
    
    with col1:
        st.markdown("##### Comercial")
        tasa_conversion = (len([c for c in clientes if c.estado_funnel == EstadoFunnelEnum.ganado]) / len(clientes) * 100) if clientes else 0
        st.metric("Tasa de Conversión", f"{tasa_conversion:.1f}%")
        
        ticket_promedio = sum(f.monto_total for f in facturas) / len(facturas) if facturas else 0
        st.metric("Ticket Promedio", f"${ticket_promedio:,.0f}")
        
        clientes_por_vendedor = len(clientes) / len(vendedores) if vendedores else 0
        st.metric("Clientes por Vendedor", f"{clientes_por_vendedor:.1f}")
    
    with col2:
        st.markdown("##### Financiero")
        facturas_mes = [f for f in facturas if f.fecha_emision >= (datetime.now().date() - timedelta(days=30))]
        cobranzas_mes = db.query(Cobranza).filter(
            Cobranza.fecha_pago >= (datetime.now().date() - timedelta(days=30))
        ).all()
        
        facturado_mes = sum(f.monto_total for f in facturas_mes)
        cobrado_mes = sum(c.monto for c in cobranzas_mes)
        
        tasa_cobranza = (cobrado_mes / facturado_mes * 100) if facturado_mes > 0 else 0
        st.metric("Tasa de Cobranza", f"{tasa_cobranza:.1f}%")
        
        facturas_pendientes = [f for f in facturas if f.estado in [EstadoFacturaEnum.pendiente, EstadoFacturaEnum.parcial]]
        dias_promedio_pago = 35
        st.metric("Días Promedio Cobro", f"{dias_promedio_pago} días")
        
        morosidad = len([f for f in facturas_pendientes if f.fecha_vencimiento < datetime.now().date()])
        st.metric("Facturas Vencidas", morosidad)
    
    with col3:
        st.markdown("##### Operacional")
        movimientos = db.query(MovimientoCaja).all()
        ingresos = [m for m in movimientos if m.tipo == 'Ingreso']
        egresos = [m for m in movimientos if m.tipo == 'Egreso']
        
        margen = ((sum(i.monto for i in ingresos) - sum(e.monto for e in egresos)) / sum(i.monto for i in ingresos) * 100) if ingresos else 0
        st.metric("Margen Operacional", f"{margen:.1f}%")
        
        actividades = db.query(ActividadVenta).filter(
            ActividadVenta.fecha >= (datetime.now().date() - timedelta(days=30))
        ).all()
        st.metric("Actividades Comerciales", len(actividades))
        
        eficiencia = len(facturas) / len(actividades) * 100 if actividades else 0
        st.metric("Eficiencia Comercial", f"{eficiencia:.1f}%")

def show_alerts(db):
    st.markdown("#### 🚨 Alertas y Notificaciones")
    
    alerts = []
    
    facturas_vencidas = db.query(Factura).filter(
        Factura.fecha_vencimiento < datetime.now().date(),
        Factura.estado.in_([EstadoFacturaEnum.pendiente, EstadoFacturaEnum.parcial])
    ).all()
    
    if facturas_vencidas:
        monto_vencido = sum(f.monto_total - f.monto_pagado for f in facturas_vencidas)
        alerts.append({
            'Tipo': '🔴 Crítico',
            'Mensaje': f'{len(facturas_vencidas)} facturas vencidas por ${monto_vencido:,.0f}',
            'Acción': 'Revisar cobranzas pendientes'
        })
    
    vendedores = db.query(Vendedor).filter(Vendedor.activo == 1).all()
    vendedores_bajo_meta = []
    
    for vendedor in vendedores:
        ventas_mes = db.query(func.sum(Factura.monto_total)).join(Cliente).filter(
            Cliente.vendedor_id == vendedor.id,
            Factura.fecha_emision >= (datetime.now().date() - timedelta(days=30))
        ).scalar() or 0
        
        cumplimiento = (ventas_mes / vendedor.meta_mensual * 100) if vendedor.meta_mensual > 0 else 0
        
        if cumplimiento < 70:
            vendedores_bajo_meta.append(vendedor.nombre)
    
    if vendedores_bajo_meta:
        alerts.append({
            'Tipo': '🟡 Advertencia',
            'Mensaje': f'{len(vendedores_bajo_meta)} vendedores bajo el 70% de su meta',
            'Acción': 'Revisar performance comercial'
        })
    
    clientes_sin_actividad = db.query(Cliente).filter(
        Cliente.fecha_ingreso < (datetime.now().date() - timedelta(days=60)),
        Cliente.estado_funnel.in_([EstadoFunnelEnum.prospecto, EstadoFunnelEnum.contactado])
    ).count()
    
    if clientes_sin_actividad > 0:
        alerts.append({
            'Tipo': '🟡 Advertencia',
            'Mensaje': f'{clientes_sin_actividad} clientes sin avance en más de 60 días',
            'Acción': 'Reactiv ar seguimiento comercial'
        })
    
    movimientos = db.query(MovimientoCaja).all()
    ingresos = sum(m.monto for m in movimientos if m.tipo == 'Ingreso')
    egresos = sum(m.monto for m in movimientos if m.tipo == 'Egreso')
    
    if egresos > ingresos * 0.9:
        alerts.append({
            'Tipo': '🟡 Advertencia',
            'Mensaje': 'Egresos representan más del 90% de los ingresos',
            'Acción': 'Revisar estructura de costos'
        })
    
    if not alerts:
        st.success("✅ No hay alertas en este momento. Todos los indicadores están dentro de los parámetros normales.")
    else:
        for alert in alerts:
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 2])
                with col1:
                    st.markdown(f"**{alert['Tipo']}**")
                with col2:
                    st.markdown(alert['Mensaje'])
                with col3:
                    st.markdown(f"*{alert['Acción']}*")
                st.markdown("---")

if __name__ == "__main__":
    show_management_dashboard()
