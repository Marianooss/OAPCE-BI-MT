#!/usr/bin/env python3
"""
Script para generar datos de prueba sustanciales para OAPCE BI Pro
Crea una base de datos rica para pruebas de agentes IA
"""

import random
from datetime import datetime, timedelta, date
from database import get_db, init_db
from models import Cliente, Vendedor, Factura, Cobranza, MovimientoCaja, ActividadVenta, EstadoFunnelEnum, EstadoFacturaEnum
from sqlalchemy import func

def main():
    print('🚀 Iniciando generación de datos de prueba sustanciales...')

    # Inicializar base de datos
    init_db()
    db = get_db()

    try:
        # Limpiar datos existentes
        print('🧹 Limpiando datos existentes...')
        db.query(Cobranza).delete()
        db.query(MovimientoCaja).delete()
        db.query(ActividadVenta).delete()
        db.query(Factura).delete()
        db.query(Cliente).delete()
        db.query(Vendedor).delete()
        db.commit()

        # Crear vendedores
        print('👥 Creando vendedores...', end='')
        vendedores = []
        nombres_vendedores = ['Juan Pérez', 'María González', 'Pedro Ramírez', 'Ana López', 'Carlos Mendoza']
        for i, nombre in enumerate(nombres_vendedores):
            vendedor = Vendedor(
                nombre=nombre,
                email=f'{nombre.lower().replace(" ", "_")}@empresa.com',
                telefono=f'9{random.randint(10000000, 99999999)}',
                activo=1,
                meta_mensual=random.randint(50000000, 80000000)  # $50M - $80M
            )
            db.add(vendedor)
            vendedores.append(vendedor)

        db.commit()
        print(f'✓ {len(vendedores)} creados')

        # Crear clientes
        print('🏢 Creando clientes...', end='')
        clientes = []
        nombres_clientes = ['Corp. Industrial S.A.', 'Servicios Tech Ltda', 'Comercial Norte SpA', 'Distribuciones Sur Ltda',
                           'Importadora Global S.A.', 'Constructora Moderna SpA', 'Agroindustria Valle Ltda', 'Food Services SpA',
                           'Transporte Express Ltda', 'Automotriz Nacional S.A.', 'Tecnologías Avanzadas SpA', 'Retail Solutions Ltda',
                           'Fábrica de Metales Ltda', 'Centros Médicos SpA', 'Educational Systems Ltda', 'Tours & Tours SpA',
                           'Energías Renovables S.A.', 'Café y Restaurantes Ltda', 'Jurídica Integral SpA', 'Software Solutions Ltda']

        for nombre in nombres_clientes:
            cliente = Cliente(
                nombre=nombre,
                rut=f'{random.randint(1,99)}{random.randint(100000, 999999)}-{random.randint(0,9)}',
                email=f'contacto@{nombre.lower().replace(" ", "").replace(".", "").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")}.cl',
                telefono=f'{random.randint(2000, 2999)}{random.randint(100000, 999999)}',
                vendedor_id=random.choice(vendedores).id,
                estado_funnel=EstadoFunnelEnum.ganado,
                valor_estimado=random.randint(50000000, 500000000),  # $50M - $500M
                fecha_ingreso=datetime.now() - timedelta(days=random.randint(30, 180))
            )
            db.add(cliente)
            clientes.append(cliente)

        # Agregar más clientes en diferentes estados del funnel
        estados_extra = [EstadoFunnelEnum.prospecto, EstadoFunnelEnum.contactado, EstadoFunnelEnum.negociacion]
        for _ in range(150):  # 150 clientes adicionales
            estado = random.choice(estados_extra)
            cliente = Cliente(
                nombre=f'Prospecto {random.randint(100, 999)}',
                rut=f'{random.randint(1,99)}{random.randint(100000, 999999)}-{random.randint(0,9)}',
                email=None,
                telefono=None,
                vendedor_id=random.choice(vendedores).id,
                estado_funnel=estado,
                valor_estimado=random.randint(10000000, 300000000),
                fecha_ingreso=datetime.now() - timedelta(days=random.randint(1, 120))
            )
            db.add(cliente)
            clientes.append(cliente)

        db.commit()
        print(f'✓ {len(clientes)} clientes creados')

        # Crear facturas históricas (últimos 6 meses)
        print('📄 Creando facturas históricas...', end='')
        facturas = []
        for i in range(500):  # 500 facturas para datos ricos
            cliente = random.choice(clientes)
            base_date = datetime.now() - timedelta(days=random.randint(1, 180))

            factura = Factura(
                numero_factura='F' + str(i+1).zfill(4),
                cliente_id=cliente.id,
                fecha_emision=base_date.date(),
                fecha_vencimiento=(base_date + timedelta(days=random.randint(15, 45))).date(),
                monto_total=random.randint(300000, 15000000),  # $300K - $15M
                monto_pagado=0 if random.random() < 0.7 else random.randint(100000, 3000000),  # 70% pendientes
                estado=EstadoFacturaEnum.pendiente if random.random() < 0.7 else EstadoFacturaEnum.pagada,
                descripcion=f'Servicios profesionales {random.choice(["de consultoría", "de desarrollo", "de implementación", "de soporte"])}'
            )
            db.add(factura)
            facturas.append(factura)

        db.commit()
        print(f'✓ {len(facturas)} facturas creadas')

        # Crear cobranzas para facturas pagadas
        print('💰 Creando registros de cobranza...', end='')
        cobros_count = 0
        for factura in facturas:
            if factura.estado == EstadoFacturaEnum.pagada:
                # Crear cobro después de la fecha de emisión
                dias_post_emision = random.randint(15, 60)
                fecha_cobro = factura.fecha_emision + timedelta(days=dias_post_emision)

                cobranza = Cobranza(
                    factura_id=factura.id,
                    fecha_pago=fecha_cobro,
                    monto=min(factura.monto_pagado or factura.monto_total, factura.monto_total),
                    metodo_pago=random.choice(['Transferencia', 'Transferencia', 'Cheque', 'Efectivo', 'Tarjeta']),
                    numero_documento=f'C{random.randint(1000, 9999)}',
                    observaciones=random.choice(['Pago recibido', f'Pago parcial', 'Abono mensual', 'Transferencia bancaria'])
                )
                db.add(cobranza)
                cobros_count += 1

        db.commit()
        print(f'✓ {cobros_count} cobranzas creadas')

        # Crear movimientos de caja
        print('🏦 Creando movimientos de caja...', end='')
        movimientos = []
        for i in range(200):  # 200 movimientos
            base_date = datetime.now() - timedelta(days=random.randint(1, 180))

            if random.random() < 0.6:  # 60% ingresos
                tipo = 'Ingreso'
                categorias = ['Servicios', 'Comisiones', 'Otros ingresos']
                monto = random.randint(500000, 8000000)  # $500K - $8M
            else:  # 40% egresos
                tipo = 'Egreso'
                categorias = ['Sueldos', 'Servicios básicos', 'Mantenimiento', 'Marketing', 'Otros gastos']
                monto = random.randint(200000, 6000000)  # $200K - $6M

            movimiento = MovimientoCaja(
                fecha=base_date,
                tipo=tipo,
                concepto=random.choice(['Pago servicios', 'Comisión venta', 'Sueldo', 'Mantención equipos', 'Marketing digital',
                                      'Inversiones', 'Proveedores', 'Capital', 'Intereses', 'Otros']),
                monto=monto,
                categoria=random.choice(categorias),
                numero_documento=f'M{random.randint(1000, 9999)}',
                observaciones=f'Movimiento {tipo.lower()} generado automáticamente'
            )
            db.add(movimiento)

        db.commit()
        print(f'✓ {len(movimientos)} movimientos creados')

        # Crear actividades de venta
        print('📞 Creando actividades de venta...', end='')
        actividades = []
        for i in range(300):  # 300 actividades
            base_date = datetime.now() - timedelta(days=random.randint(1, 90))  # Últimos 3 meses

            actividad = ActividadVenta(
                vendedor_id=random.choice(vendedores).id,
                fecha=base_date.date(),
                tipo_actividad=random.choice(['Llamada', 'Reunión', 'Email', 'Reunión', 'Llamada', 'Cotización', 'Visita', 'Seguimiento']),
                cliente_nombre=random.choice(nombres_clientes) if random.random() < 0.7 else f'Prospecto {i+1}',
                resultado=random.choice([
                    'Presenté propuesta técnica', 'Definición de requisitos', 'Seguimiento post reunión',
                    'Envío cotización detallada', 'Negociación condiciones', 'Cierre deal positivo',
                    'Revisión feedback', 'Actualización de alcance', 'Clarificación requerimientos',
                    'Visita tecnica pilot', 'Presentación ejecutiva', 'Análisis competencia'
                ]),
                monto_estimado=random.choice([0, random.randint(5000000, 200000000)])  # 30% sin monto
            )
            db.add(actividad)

        db.commit()
        print(f'✓ {len(actividades)} actividades creadas')

        # Estadísticas finales
        print('\n' + '='*60)
        print('🎉 GENERACIÓN DE DATOS COMPLETADA EXITOSAMENTE')
        print('='*60)

        total_vendedores = db.query(Vendedor).count()
        total_clientes = db.query(Cliente).count()
        total_facturas = db.query(Factura).count()
        total_cobranzas = db.query(Cobranza).count()
        total_movimientos = db.query(MovimientoCaja).count()
        total_actividades = db.query(ActividadVenta).count()

        print(f'👥 Vendedores: {total_vendedores}')
        print(f'🏢 Clientes: {total_clientes}')
        print(f'📄 Facturas: {total_facturas}')
        print(f'💰 Cobranzas: {total_cobranzas}')
        print(f'🏦 Movimientos Caja: {total_movimientos}')
        print(f'📞 Actividades Venta: {total_actividades}')

        # Calcular KPIs de validación
        facturas_pagadas = db.query(Factura).filter(Factura.estado == EstadoFacturaEnum.pagada).count()
        monto_total_facturado = db.query(func.sum(Factura.monto_total)).scalar() or 0
        monto_total_cobrado = db.query(func.sum(Cobranza.monto)).scalar() or 0

        print('\n📊 KPIs PRUEBA:')
        print(f'✅ Facturas Pagadas: {facturas_pagadas} ({facturas_pagadas/total_facturas*100:.1f}%)')
        print(f'💰 Monto Total Facturado: ${monto_total_facturado:,.0f}')
        print(f'💰 Monto Total Cobrado: ${monto_total_cobrado:,.0f}')
        print(f'📈 Tasa de Cobranza: {monto_total_cobrado/monto_total_facturado*100:.1f}%')

        print('='*60)
        print('🔥 BASE DE DATOS LISTA PARA PRUEBAS DE AGENTES IA')
        print('Ya puedes ejecutar los agentes desde cualquier módulo!')

    finally:
        db.close()

if __name__ == "__main__":
    main()
