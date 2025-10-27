import streamlit as st
import pandas as pd
from database import get_db
from models import Cliente, Vendedor, Factura, Cobranza, MovimientoCaja, ActividadVenta
from models import EstadoFunnelEnum, EstadoFacturaEnum
from datetime import datetime, date

def show_data_forms():
    st.title("📝 Gestión de Datos")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Clientes",
        "Facturas",
        "Cobranzas",
        "Movimientos Caja",
        "Actividades Venta"
    ])
    
    with tab1:
        show_client_form()
    
    with tab2:
        show_invoice_form()
    
    with tab3:
        show_collection_form()
    
    with tab4:
        show_cash_movement_form()
    
    with tab5:
        show_sales_activity_form()

def show_client_form():
    st.subheader("Gestión de Clientes")
    
    db = get_db()
    
    try:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Registrar Nuevo Cliente")
            
            with st.form("client_form"):
                nombre = st.text_input("Nombre/Razón Social*")
                rut = st.text_input("RUT*")
                email = st.text_input("Email")
                telefono = st.text_input("Teléfono")
                direccion = st.text_area("Dirección")
                
                vendedores = db.query(Vendedor).filter(Vendedor.activo == 1).all()
                vendedor_options = {v.nombre: v.id for v in vendedores}
                vendedor_selected = st.selectbox("Vendedor Asignado*", options=list(vendedor_options.keys()))
                
                estado_funnel = st.selectbox(
                    "Estado en Funnel",
                    options=[e.value for e in EstadoFunnelEnum],
                    index=0
                )
                
                valor_estimado = st.number_input("Valor Estimado ($)", min_value=0, value=0, step=100000)
                
                submitted = st.form_submit_button("Registrar Cliente")
                
                if submitted:
                    if nombre and rut and vendedor_selected:
                        try:
                            cliente = Cliente(
                                nombre=nombre,
                                rut=rut,
                                email=email,
                                telefono=telefono,
                                direccion=direccion,
                                vendedor_id=vendedor_options[vendedor_selected],
                                estado_funnel=EstadoFunnelEnum[estado_funnel.replace(' ', '_').replace('ó', 'o').lower()],
                                valor_estimado=valor_estimado,
                                fecha_ingreso=datetime.now()
                            )
                            db.add(cliente)
                            db.commit()
                            st.success(f"✅ Cliente {nombre} registrado exitosamente!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al registrar cliente: {str(e)}")
                            db.rollback()
                    else:
                        st.warning("Por favor complete los campos obligatorios (*)")
        
        with col2:
            st.markdown("#### Clientes Recientes")
            clientes = db.query(Cliente).order_by(Cliente.fecha_ingreso.desc()).limit(10).all()
            
            for cliente in clientes:
                with st.expander(f"{cliente.nombre}"):
                    st.write(f"**RUT:** {cliente.rut}")
                    st.write(f"**Estado:** {cliente.estado_funnel.value}")
                    st.write(f"**Vendedor:** {cliente.vendedor.nombre if cliente.vendedor else 'N/A'}")
                    st.write(f"**Valor Est.:** ${cliente.valor_estimado:,.0f}")
    
    finally:
        db.close()

def show_invoice_form():
    st.subheader("Gestión de Facturas")
    
    db = get_db()
    
    try:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Emitir Nueva Factura")
            
            with st.form("invoice_form"):
                numero_factura = st.text_input("Número de Factura*")
                
                clientes = db.query(Cliente).all()
                cliente_options = {f"{c.nombre} ({c.rut})": c.id for c in clientes}
                cliente_selected = st.selectbox("Cliente*", options=list(cliente_options.keys()))
                
                col_a, col_b = st.columns(2)
                with col_a:
                    fecha_emision = st.date_input("Fecha Emisión*", value=date.today())
                with col_b:
                    fecha_vencimiento = st.date_input("Fecha Vencimiento*", value=date.today())
                
                monto_total = st.number_input("Monto Total ($)*", min_value=0, value=0, step=10000)
                descripcion = st.text_area("Descripción del Servicio")
                
                submitted = st.form_submit_button("Emitir Factura")
                
                if submitted:
                    if numero_factura and cliente_selected and monto_total > 0:
                        try:
                            factura = Factura(
                                numero_factura=numero_factura,
                                cliente_id=cliente_options[cliente_selected],
                                fecha_emision=fecha_emision,
                                fecha_vencimiento=fecha_vencimiento,
                                monto_total=monto_total,
                                monto_pagado=0,
                                estado=EstadoFacturaEnum.pendiente,
                                descripcion=descripcion
                            )
                            db.add(factura)
                            db.commit()
                            st.success(f"✅ Factura {numero_factura} emitida exitosamente!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al emitir factura: {str(e)}")
                            db.rollback()
                    else:
                        st.warning("Por favor complete los campos obligatorios (*)")
        
        with col2:
            st.markdown("#### Facturas Recientes")
            facturas = db.query(Factura).order_by(Factura.fecha_emision.desc()).limit(10).all()
            
            for factura in facturas:
                with st.expander(f"{factura.numero_factura}"):
                    st.write(f"**Cliente:** {factura.cliente.nombre if factura.cliente else 'N/A'}")
                    st.write(f"**Monto:** ${factura.monto_total:,.0f}")
                    st.write(f"**Estado:** {factura.estado.value}")
                    st.write(f"**Vence:** {factura.fecha_vencimiento.strftime('%d/%m/%Y')}")
    
    finally:
        db.close()

def show_collection_form():
    st.subheader("Gestión de Cobranzas")
    
    db = get_db()
    
    try:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Registrar Pago")
            
            facturas_pendientes = db.query(Factura).filter(
                Factura.estado.in_([EstadoFacturaEnum.pendiente, EstadoFacturaEnum.parcial])
            ).all()
            
            if not facturas_pendientes:
                st.info("No hay facturas pendientes de pago.")
            else:
                with st.form("collection_form"):
                    factura_options = {
                        f"{f.numero_factura} - {f.cliente.nombre if f.cliente else 'N/A'} (Saldo: ${f.monto_total - f.monto_pagado:,.0f})": f.id
                        for f in facturas_pendientes
                    }
                    factura_selected = st.selectbox("Factura a Pagar*", options=list(factura_options.keys()))
                    
                    fecha_pago = st.date_input("Fecha de Pago*", value=date.today())
                    
                    factura_id = factura_options[factura_selected]
                    factura = db.query(Factura).filter(Factura.id == factura_id).first()
                    saldo = factura.monto_total - factura.monto_pagado if factura else 0
                    
                    monto = st.number_input(
                        f"Monto a Pagar ($)* - Saldo: ${saldo:,.0f}",
                        min_value=0,
                        max_value=int(saldo),
                        value=int(saldo),
                        step=10000
                    )
                    
                    metodo_pago = st.selectbox(
                        "Método de Pago*",
                        options=["Transferencia", "Cheque", "Efectivo", "Tarjeta"]
                    )
                    
                    numero_documento = st.text_input("Número de Documento")
                    observaciones = st.text_area("Observaciones")
                    
                    submitted = st.form_submit_button("Registrar Pago")
                    
                    if submitted:
                        if factura_selected and monto > 0:
                            try:
                                cobranza = Cobranza(
                                    factura_id=factura_id,
                                    fecha_pago=fecha_pago,
                                    monto=monto,
                                    metodo_pago=metodo_pago,
                                    numero_documento=numero_documento,
                                    observaciones=observaciones
                                )
                                db.add(cobranza)
                                
                                factura.monto_pagado += monto
                                if factura.monto_pagado >= factura.monto_total:
                                    factura.estado = EstadoFacturaEnum.pagada
                                else:
                                    factura.estado = EstadoFacturaEnum.parcial
                                
                                db.commit()
                                st.success(f"✅ Pago de ${monto:,.0f} registrado exitosamente!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al registrar pago: {str(e)}")
                                db.rollback()
                        else:
                            st.warning("Por favor complete los campos obligatorios (*)")
        
        with col2:
            st.markdown("#### Cobranzas Recientes")
            cobranzas = db.query(Cobranza).order_by(Cobranza.fecha_pago.desc()).limit(10).all()
            
            for cobranza in cobranzas:
                with st.expander(f"${cobranza.monto:,.0f} - {cobranza.fecha_pago.strftime('%d/%m/%Y')}"):
                    st.write(f"**Factura:** {cobranza.factura.numero_factura if cobranza.factura else 'N/A'}")
                    st.write(f"**Método:** {cobranza.metodo_pago}")
                    if cobranza.numero_documento:
                        st.write(f"**Doc:** {cobranza.numero_documento}")
    
    finally:
        db.close()

def show_cash_movement_form():
    st.subheader("Gestión de Movimientos de Caja")
    
    db = get_db()
    
    try:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Registrar Movimiento")
            
            with st.form("cash_movement_form"):
                tipo = st.selectbox("Tipo de Movimiento*", options=["Ingreso", "Egreso"])
                
                fecha = st.date_input("Fecha*", value=date.today())
                
                if tipo == "Ingreso":
                    categorias = ["Servicios", "Comisiones", "Otros ingresos"]
                else:
                    categorias = ["Sueldos", "Arriendo", "Servicios básicos", "Combustible", 
                                 "Mantención", "Seguros", "Marketing", "Otros gastos"]
                
                categoria = st.selectbox("Categoría*", options=categorias)
                concepto = st.text_input("Concepto*")
                monto = st.number_input("Monto ($)*", min_value=0, value=0, step=10000)
                numero_documento = st.text_input("Número de Documento")
                observaciones = st.text_area("Observaciones")
                
                submitted = st.form_submit_button("Registrar Movimiento")
                
                if submitted:
                    if concepto and monto > 0:
                        try:
                            movimiento = MovimientoCaja(
                                fecha=fecha,
                                tipo=tipo,
                                concepto=concepto,
                                monto=monto,
                                categoria=categoria,
                                numero_documento=numero_documento,
                                observaciones=observaciones
                            )
                            db.add(movimiento)
                            db.commit()
                            st.success(f"✅ Movimiento de {tipo.lower()} por ${monto:,.0f} registrado!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al registrar movimiento: {str(e)}")
                            db.rollback()
                    else:
                        st.warning("Por favor complete los campos obligatorios (*)")
        
        with col2:
            st.markdown("#### Movimientos Recientes")
            movimientos = db.query(MovimientoCaja).order_by(MovimientoCaja.fecha.desc()).limit(10).all()
            
            for mov in movimientos:
                emoji = "🟢" if mov.tipo == "Ingreso" else "🔴"
                with st.expander(f"{emoji} ${mov.monto:,.0f} - {mov.concepto[:30]}"):
                    st.write(f"**Tipo:** {mov.tipo}")
                    st.write(f"**Categoría:** {mov.categoria}")
                    st.write(f"**Fecha:** {mov.fecha.strftime('%d/%m/%Y')}")
    
    finally:
        db.close()

def show_sales_activity_form():
    st.subheader("Gestión de Actividades de Venta")
    
    db = get_db()
    
    try:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Registrar Actividad")
            
            with st.form("sales_activity_form"):
                vendedores = db.query(Vendedor).filter(Vendedor.activo == 1).all()
                vendedor_options = {v.nombre: v.id for v in vendedores}
                vendedor_selected = st.selectbox("Vendedor*", options=list(vendedor_options.keys()))
                
                fecha = st.date_input("Fecha*", value=date.today())
                
                tipo_actividad = st.selectbox(
                    "Tipo de Actividad*",
                    options=["Llamada", "Reunión", "Email", "Visita", "Cotización", "Seguimiento"]
                )
                
                cliente_nombre = st.text_input("Nombre del Cliente/Prospecto*")
                resultado = st.text_area("Resultado/Observaciones*")
                monto_estimado = st.number_input("Monto Estimado ($)", min_value=0, value=0, step=100000)
                
                submitted = st.form_submit_button("Registrar Actividad")
                
                if submitted:
                    if vendedor_selected and cliente_nombre and resultado:
                        try:
                            actividad = ActividadVenta(
                                vendedor_id=vendedor_options[vendedor_selected],
                                fecha=fecha,
                                tipo_actividad=tipo_actividad,
                                cliente_nombre=cliente_nombre,
                                resultado=resultado,
                                monto_estimado=monto_estimado
                            )
                            db.add(actividad)
                            db.commit()
                            st.success(f"✅ Actividad de {tipo_actividad.lower()} registrada exitosamente!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al registrar actividad: {str(e)}")
                            db.rollback()
                    else:
                        st.warning("Por favor complete los campos obligatorios (*)")
        
        with col2:
            st.markdown("#### Actividades Recientes")
            actividades = db.query(ActividadVenta).order_by(ActividadVenta.fecha.desc()).limit(10).all()
            
            for act in actividades:
                with st.expander(f"{act.tipo_actividad} - {act.cliente_nombre[:30]}"):
                    st.write(f"**Vendedor:** {act.vendedor.nombre if act.vendedor else 'N/A'}")
                    st.write(f"**Fecha:** {act.fecha.strftime('%d/%m/%Y')}")
                    st.write(f"**Resultado:** {act.resultado[:100]}")
                    if act.monto_estimado > 0:
                        st.write(f"**Monto Est.:** ${act.monto_estimado:,.0f}")
    
    finally:
        db.close()

if __name__ == "__main__":
    show_data_forms()
