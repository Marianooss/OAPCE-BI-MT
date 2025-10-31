import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import get_db
from models import Factura, Cobranza, MovimientoCaja, Cliente, EstadoFacturaEnum
from sqlalchemy import func, extract
from datetime import datetime, timedelta

def show_finance_dashboard():
    st.title("💰 Módulo Administración y Finanzas")
    
    db = get_db()
    
    try:
        tab1, tab2, tab3, tab4 = st.tabs(["Facturación", "Cobranzas", "Flujo de Caja", "Cuentas por Cobrar"])
        
        with tab1:
            show_billing(db)
        
        with tab2:
            show_collections(db)
        
        with tab3:
            show_cash_flow(db)
        
        with tab4:
            show_accounts_receivable(db)

        st.markdown("---")

        # AGENTES INTELIGENTES PARA FINANZAS - AL NIVEL DEL MÓDULO COMPLETO
        show_finance_ai_agents()

    finally:
        db.close()

def show_billing(db):
    st.subheader("Facturación")
    
    facturas = db.query(Factura).all()
    
    total_facturado = sum(f.monto_total for f in facturas)
    facturas_mes = [f for f in facturas if f.fecha_emision >= (datetime.now().date() - timedelta(days=30))]
    facturado_mes = sum(f.monto_total for f in facturas_mes)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Facturado", f"${total_facturado:,.0f}")
    
    with col2:
        st.metric("Facturado este Mes", f"${facturado_mes:,.0f}")
    
    with col3:
        st.metric("Total Facturas", len(facturas))
    
    with col4:
        pendientes = len([f for f in facturas if f.estado == EstadoFacturaEnum.pendiente])
        st.metric("Facturas Pendientes", pendientes)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Facturación por Estado")
        estado_data = {}
        for factura in facturas:
            estado = factura.estado.value
            estado_data[estado] = estado_data.get(estado, 0) + factura.monto_total
        
        if estado_data:
            df_estados = pd.DataFrame(list(estado_data.items()), columns=['Estado', 'Monto'])
            fig = px.pie(df_estados, values='Monto', names='Estado',
                        title='Distribución por Estado')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Facturación Mensual")
        facturas_sorted = sorted(facturas, key=lambda x: x.fecha_emision)
        
        monthly_data = {}
        for factura in facturas_sorted:
            mes = factura.fecha_emision.strftime('%Y-%m')
            monthly_data[mes] = monthly_data.get(mes, 0) + factura.monto_total
        
        if monthly_data:
            df_monthly = pd.DataFrame(list(monthly_data.items()), columns=['Mes', 'Facturación'])
            fig = px.line(df_monthly, x='Mes', y='Facturación',
                         title='Evolución Mensual de Facturación',
                         markers=True)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### Últimas Facturas")
    
    ultimas_facturas = sorted(facturas, key=lambda x: x.fecha_emision, reverse=True)[:10]
    
    df_facturas = pd.DataFrame([{
        'N° Factura': f.numero_factura,
        'Cliente': f.cliente.nombre if f.cliente else 'N/A',
        'Fecha Emisión': f.fecha_emision.strftime('%d/%m/%Y'),
        'Vencimiento': f.fecha_vencimiento.strftime('%d/%m/%Y'),
        'Monto Total': f"${f.monto_total:,.0f}",
        'Pagado': f"${f.monto_pagado:,.0f}",
        'Estado': f.estado.value
    } for f in ultimas_facturas])
    
    if not df_facturas.empty:
        st.dataframe(df_facturas, use_container_width=True, hide_index=True)

def show_collections(db):
    st.subheader("Cobranzas")
    
    cobranzas = db.query(Cobranza).all()
    
    total_cobrado = sum(c.monto for c in cobranzas)
    cobranzas_mes = [c for c in cobranzas if c.fecha_pago >= (datetime.now().date() - timedelta(days=30))]
    cobrado_mes = sum(c.monto for c in cobranzas_mes)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cobrado", f"${total_cobrado:,.0f}")
    
    with col2:
        st.metric("Cobrado este Mes", f"${cobrado_mes:,.0f}")
    
    with col3:
        st.metric("Total Cobranzas", len(cobranzas))
    
    with col4:
        cobranzas_hoy = len([c for c in cobranzas if c.fecha_pago == datetime.now().date()])
        st.metric("Cobranzas Hoy", cobranzas_hoy)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Cobranzas por Método de Pago")
        metodo_data = {}
        for cobranza in cobranzas:
            metodo = cobranza.metodo_pago or 'No especificado'
            metodo_data[metodo] = metodo_data.get(metodo, 0) + cobranza.monto
        
        if metodo_data:
            df_metodos = pd.DataFrame(list(metodo_data.items()), columns=['Método', 'Monto'])
            fig = px.bar(df_metodos, x='Método', y='Monto',
                        title='Cobranzas por Método de Pago')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Evolución de Cobranzas")
        cobranzas_sorted = sorted(cobranzas, key=lambda x: x.fecha_pago)
        
        monthly_collections = {}
        for cobranza in cobranzas_sorted:
            mes = cobranza.fecha_pago.strftime('%Y-%m')
            monthly_collections[mes] = monthly_collections.get(mes, 0) + cobranza.monto
        
        if monthly_collections:
            df_monthly = pd.DataFrame(list(monthly_collections.items()), columns=['Mes', 'Cobranzas'])
            fig = px.line(df_monthly, x='Mes', y='Cobranzas',
                         title='Evolución Mensual de Cobranzas',
                         markers=True)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### Últimas Cobranzas")
    
    ultimas_cobranzas = sorted(cobranzas, key=lambda x: x.fecha_pago, reverse=True)[:15]
    
    df_cobranzas = pd.DataFrame([{
        'Fecha': c.fecha_pago.strftime('%d/%m/%Y'),
        'N° Factura': c.factura.numero_factura if c.factura else 'N/A',
        'Cliente': c.factura.cliente.nombre if c.factura and c.factura.cliente else 'N/A',
        'Monto': f"${c.monto:,.0f}",
        'Método': c.metodo_pago or 'N/A',
        'Doc': c.numero_documento or 'N/A'
    } for c in ultimas_cobranzas])
    
    if not df_cobranzas.empty:
        st.dataframe(df_cobranzas, use_container_width=True, hide_index=True)

def show_cash_flow(db):
    st.subheader("Flujo de Caja")
    
    movimientos = db.query(MovimientoCaja).all()
    
    ingresos = [m for m in movimientos if m.tipo == 'Ingreso']
    egresos = [m for m in movimientos if m.tipo == 'Egreso']
    
    total_ingresos = sum(m.monto for m in ingresos)
    total_egresos = sum(m.monto for m in egresos)
    saldo = total_ingresos - total_egresos
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Ingresos", f"${total_ingresos:,.0f}", delta=None)
    
    with col2:
        st.metric("Total Egresos", f"${total_egresos:,.0f}", delta=None)
    
    with col3:
        delta_color = "normal" if saldo >= 0 else "inverse"
        st.metric("Saldo Neto", f"${saldo:,.0f}", delta=f"${saldo:,.0f}")
    
    with col4:
        movimientos_mes = [m for m in movimientos if m.fecha >= datetime.now().date() - timedelta(days=30)]
        st.metric("Movimientos del Mes", len(movimientos_mes))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Distribución de Ingresos")
        if ingresos:
            categoria_ingresos = {}
            for ing in ingresos:
                cat = ing.categoria or 'Sin categoría'
                categoria_ingresos[cat] = categoria_ingresos.get(cat, 0) + ing.monto
            
            df_ing = pd.DataFrame(list(categoria_ingresos.items()), columns=['Categoría', 'Monto'])
            fig = px.pie(df_ing, values='Monto', names='Categoría',
                        title='Ingresos por Categoría')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Distribución de Egresos")
        if egresos:
            categoria_egresos = {}
            for egr in egresos:
                cat = egr.categoria or 'Sin categoría'
                categoria_egresos[cat] = categoria_egresos.get(cat, 0) + egr.monto
            
            df_egr = pd.DataFrame(list(categoria_egresos.items()), columns=['Categoría', 'Monto'])
            fig = px.pie(df_egr, values='Monto', names='Categoría',
                        title='Egresos por Categoría')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### Flujo de Caja Mensual")
    
    movimientos_sorted = sorted(movimientos, key=lambda x: x.fecha)
    monthly_flow = {}
    
    for mov in movimientos_sorted:
        mes = mov.fecha.strftime('%Y-%m')
        if mes not in monthly_flow:
            monthly_flow[mes] = {'Ingresos': 0, 'Egresos': 0}
        
        if mov.tipo == 'Ingreso':
            monthly_flow[mes]['Ingresos'] += mov.monto
        else:
            monthly_flow[mes]['Egresos'] += mov.monto
    
    if monthly_flow:
        df_flow = pd.DataFrame([
            {'Mes': mes, 'Tipo': 'Ingresos', 'Monto': data['Ingresos']}
            for mes, data in monthly_flow.items()
        ] + [
            {'Mes': mes, 'Tipo': 'Egresos', 'Monto': data['Egresos']}
            for mes, data in monthly_flow.items()
        ])
        
        fig = px.bar(df_flow, x='Mes', y='Monto', color='Tipo', barmode='group',
                    title='Comparación Ingresos vs Egresos Mensual')
        st.plotly_chart(fig, use_container_width=True)

def show_accounts_receivable(db):
    st.subheader("Cuentas por Cobrar")
    
    facturas_pendientes = db.query(Factura).filter(
        Factura.estado.in_([EstadoFacturaEnum.pendiente, EstadoFacturaEnum.parcial])
    ).all()
    
    total_por_cobrar = sum(f.monto_total - f.monto_pagado for f in facturas_pendientes)
    vencidas = [f for f in facturas_pendientes if f.fecha_vencimiento < datetime.now().date()]
    por_vencer = [f for f in facturas_pendientes if f.fecha_vencimiento >= datetime.now().date()]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total por Cobrar", f"${total_por_cobrar:,.0f}")
    
    with col2:
        total_vencido = sum(f.monto_total - f.monto_pagado for f in vencidas)
        st.metric("Vencido", f"${total_vencido:,.0f}", delta=f"-{len(vencidas)} facturas")
    
    with col3:
        total_por_vencer = sum(f.monto_total - f.monto_pagado for f in por_vencer)
        st.metric("Por Vencer", f"${total_por_vencer:,.0f}")
    
    with col4:
        st.metric("Facturas Pendientes", len(facturas_pendientes))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Antigüedad de Saldos")
        
        antiguedad = {
            '0-30 días': 0,
            '31-60 días': 0,
            '61-90 días': 0,
            '90+ días': 0
        }
        
        for factura in facturas_pendientes:
            dias_vencido = (datetime.now().date() - factura.fecha_vencimiento).days
            saldo = factura.monto_total - factura.monto_pagado
            
            if dias_vencido <= 30:
                antiguedad['0-30 días'] += saldo
            elif dias_vencido <= 60:
                antiguedad['31-60 días'] += saldo
            elif dias_vencido <= 90:
                antiguedad['61-90 días'] += saldo
            else:
                antiguedad['90+ días'] += saldo
        
        df_antiguedad = pd.DataFrame(list(antiguedad.items()), columns=['Rango', 'Monto'])
        fig = px.bar(df_antiguedad, x='Rango', y='Monto',
                    title='Antigüedad de Cuentas por Cobrar')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Top 5 Clientes con Mayor Deuda")
        
        deudas_cliente = {}
        for factura in facturas_pendientes:
            if factura.cliente:
                cliente = factura.cliente.nombre
                saldo = factura.monto_total - factura.monto_pagado
                deudas_cliente[cliente] = deudas_cliente.get(cliente, 0) + saldo
        
        if deudas_cliente:
            top_deudores = sorted(deudas_cliente.items(), key=lambda x: x[1], reverse=True)[:5]
            df_deudores = pd.DataFrame(top_deudores, columns=['Cliente', 'Deuda'])
            
            fig = px.bar(df_deudores, x='Deuda', y='Cliente', orientation='h',
                        title='Top 5 Clientes con Mayor Deuda')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### Detalle de Cuentas por Cobrar")
    
    df_cuentas = pd.DataFrame([{
        'N° Factura': f.numero_factura,
        'Cliente': f.cliente.nombre if f.cliente else 'N/A',
        'Fecha Emisión': f.fecha_emision.strftime('%d/%m/%Y'),
        'Vencimiento': f.fecha_vencimiento.strftime('%d/%m/%Y'),
        'Días Vencido': (datetime.now().date() - f.fecha_vencimiento).days,
        'Monto Total': f"${f.monto_total:,.0f}",
        'Pagado': f"${f.monto_pagado:,.0f}",
        'Saldo': f"${f.monto_total - f.monto_pagado:,.0f}",
        'Estado': f.estado.value
    } for f in sorted(facturas_pendientes, key=lambda x: x.fecha_vencimiento)])
    
    if not df_cuentas.empty:
        st.dataframe(df_cuentas, use_container_width=True, hide_index=True)

def show_finance_ai_agents():
    """Agentes IA especializados para el módulo financiero"""
    st.markdown("## 🤖 **Agentes IA para Control Financiero**")
    st.markdown("**Herramientas inteligentes específicamente para finanzas y flujo de caja**")

    with st.expander("🔮 PME (Forecasting Financiero) - Predicción de Flujo de Caja", expanded=False):
        st.markdown("**¿Qué hace?** Predice ingresos, gastos y situación financiera futura")
        st.markdown("**Beneficio:** Decisiones financieras basadas en proyecciones exactas")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**Casos de uso principales:**")
            st.markdown("- Predicción flujo de caja en 6-12 meses")
            st.markdown("- Budgeting automático de ingresos/gastos")
            st.markdown("- Alertas de situaciones financieras críticas")
        with col2:
            if st.button("🚀 Ejecutar PME - Cash Flow Forecasting", key="finance_pme_cashflow_forecast", use_container_width=True):
                from agents_ui import show_predictive_models_page
                st.info("Abierto en nueva sección de Agentes IA")

    with st.expander("🔄 DPO (Consolidación Contable) - ETL Financiero", expanded=False):
        st.markdown("**¿Qué hace?** Integra automáticamente datos financieros de múltiples fuentes")
        st.markdown("**Beneficio:** Consolidación automática de estados financieros sin errores")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**Casos de uso principales:**")
            st.markdown("- Estados financieros actualizados automáticamente")
            st.markdown("- Eliminación de delay en reconciliations")
            st.markdown("- Integración de múltiples bases contables")
        with col2:
            if st.button("🚀 Ejecutar DPO - Data Consolidation", key="finance_dpo_consolidation", use_container_width=True):
                from agents_ui import show_data_pipeline_page
                st.info("Abierto en nueva sección de Agentes IA")

    with st.expander("🚨 AD (Detección Fraudulenta) - Alertas Financieras", expanded=False):
        st.markdown("**¿Qué hace?** Detecta automáticamente irregularidades financieras y fraudes")
        st.markdown("**Beneficio:** Prevención de fraudes y cumplimiento financiero automático")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**Casos de uso principales:**")
            st.markdown("- Detección de transacciones inusuales")
            st.markdown("- Alertas de irregularidades bancarias")
            st.markdown("- Compliance financiero automático")
        with col2:
            if st.button("🚀 Ejecutar AD - Fraud Detection", key="finance_ad_fraud", use_container_width=True):
                from agents_ui import show_anomaly_detector_page
                st.info("Abierto en nueva sección de Agentes IA")

    with st.expander("💡 PA (Optimización Financiera) - Mejora de Ratios", expanded=False):
        st.markdown("**¿Qué hace?** Recomendaciones para optimizar ratios y cuentas financieras")
        st.markdown("**Beneficio:** Mejora automática y constante de métricas financieras")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**Casos de uso principales:**")
            st.markdown("- Optimización de cuentas por cobrar/pagar")
            st.markdown("- Mejora automática de ratios financieros")
            st.markdown("- Recomendaciones de inversión financiera")
        with col2:
            if st.button("🚀 Ejecutar PA - Financial Optimization", key="finance_pa_optimization", use_container_width=True):
                from agents_ui import show_prescriptive_advisor_page
                st.info("Abierto en nueva sección de Agentes IA")

    st.markdown("---")
    st.info("💡 **Todos estos agentes se ejecutan desde el módulo '🤖 Agentes IA' en el menú lateral. Aquí se muestra su utilidad específica para el control financiero y gestión del cash flow.**")

if __name__ == "__main__":
    show_finance_dashboard()
