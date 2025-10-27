from database import init_db, get_db
from models import Usuario, Cliente, Vendedor, Factura, Cobranza, MovimientoCaja, ActividadVenta
from models import RolEnum, EstadoFacturaEnum, EstadoFunnelEnum
from utils import hash_password
from datetime import datetime, timedelta
import random

def initialize_database():
    print("Inicializando base de datos...")
    init_db()
    
    db = get_db()
    
    try:
        if db.query(Usuario).count() > 0:
            print("La base de datos ya contiene datos.")
            return
        
        print("Creando usuarios...")
        usuarios = [
            Usuario(
                nombre="Admin Sistema",
                email="admin@grupoom.com",
                password_hash=hash_password("admin123"),
                rol=RolEnum.admin
            ),
            Usuario(
                nombre="Operador 1",
                email="operador@grupoom.com",
                password_hash=hash_password("operador123"),
                rol=RolEnum.operador
            ),
            Usuario(
                nombre="Cliente Demo",
                email="cliente@example.com",
                password_hash=hash_password("cliente123"),
                rol=RolEnum.cliente
            )
        ]
        db.add_all(usuarios)
        db.commit()
        
        print("Creando vendedores...")
        vendedores = [
            Vendedor(nombre="Juan Pérez", email="juan.perez@grupoom.com", telefono="+56912345678", meta_mensual=50000000, comision_porcentaje=3.0),
            Vendedor(nombre="María González", email="maria.gonzalez@grupoom.com", telefono="+56987654321", meta_mensual=45000000, comision_porcentaje=3.5),
            Vendedor(nombre="Carlos Rodríguez", email="carlos.rodriguez@grupoom.com", telefono="+56911223344", meta_mensual=40000000, comision_porcentaje=3.0),
            Vendedor(nombre="Ana Martínez", email="ana.martinez@grupoom.com", telefono="+56955667788", meta_mensual=35000000, comision_porcentaje=2.5)
        ]
        db.add_all(vendedores)
        db.commit()
        
        print("Creando clientes...")
        estados_funnel = list(EstadoFunnelEnum)
        clientes = []
        empresas = [
            "Transportes del Sur S.A.", "Importadora Central Ltda.", "Logística Express SpA",
            "Comercial Norte S.A.", "Distribuidora Regional", "Agencia Aduanera Premium",
            "Freight Solutions Chile", "Global Trade Partners", "Cargo Masters S.A.",
            "Pacific Logistics", "Andean Transport", "Chilean Export Group",
            "South American Trading", "Continental Shipping", "Maritime Solutions",
            "Air Cargo Chile", "Border Customs Services", "Quick Delivery SpA",
            "Warehouse Management Co.", "Supply Chain Experts"
        ]
        
        for i, empresa in enumerate(empresas):
            cliente = Cliente(
                nombre=empresa,
                rut=f"{76000000 + i * 1000}-{random.randint(0, 9)}",
                email=f"contacto{i}@{empresa.lower().replace(' ', '').replace('.', '')}.cl",
                telefono=f"+569{random.randint(10000000, 99999999)}",
                direccion=f"Av. Principal {random.randint(100, 9999)}, Santiago",
                vendedor_id=vendedores[i % len(vendedores)].id,
                estado_funnel=random.choice(estados_funnel),
                valor_estimado=random.randint(5000000, 100000000),
                fecha_ingreso=datetime.now() - timedelta(days=random.randint(30, 365))
            )
            clientes.append(cliente)
        
        db.add_all(clientes)
        db.commit()
        
        print("Creando facturas...")
        facturas = []
        for i in range(50):
            cliente = random.choice(clientes)
            fecha_emision = datetime.now() - timedelta(days=random.randint(1, 120))
            monto_total = random.randint(1000000, 50000000)
            monto_pagado = random.choice([0, monto_total * 0.3, monto_total * 0.5, monto_total])
            
            if monto_pagado == 0:
                estado = EstadoFacturaEnum.pendiente
            elif monto_pagado >= monto_total:
                estado = EstadoFacturaEnum.pagada
            else:
                estado = EstadoFacturaEnum.parcial
            
            factura = Factura(
                numero_factura=f"F-2024-{1000 + i}",
                cliente_id=cliente.id,
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_emision + timedelta(days=30),
                monto_total=monto_total,
                monto_pagado=monto_pagado,
                estado=estado,
                descripcion=f"Servicios de {random.choice(['transporte', 'logística', 'aduana', 'almacenaje'])}"
            )
            facturas.append(factura)
        
        db.add_all(facturas)
        db.commit()
        
        print("Creando cobranzas...")
        cobranzas = []
        for factura in facturas:
            if factura.monto_pagado > 0:
                num_pagos = random.randint(1, 3)
                monto_por_pago = factura.monto_pagado / num_pagos
                
                for j in range(num_pagos):
                    cobranza = Cobranza(
                        factura_id=factura.id,
                        fecha_pago=factura.fecha_emision + timedelta(days=random.randint(1, 45)),
                        monto=monto_por_pago,
                        metodo_pago=random.choice(["Transferencia", "Cheque", "Efectivo"]),
                        numero_documento=f"DOC-{random.randint(10000, 99999)}",
                        observaciones="Pago procesado correctamente"
                    )
                    cobranzas.append(cobranza)
        
        db.add_all(cobranzas)
        db.commit()
        
        print("Creando movimientos de caja...")
        movimientos = []
        categorias_ingreso = ["Servicios", "Comisiones", "Otros ingresos"]
        categorias_egreso = ["Sueldos", "Arriendo", "Servicios básicos", "Combustible", "Mantención", "Seguros", "Marketing"]
        
        for i in range(100):
            tipo = random.choice(["Ingreso", "Egreso"])
            if tipo == "Ingreso":
                concepto = random.choice(categorias_ingreso)
                monto = random.randint(500000, 15000000)
                categoria = concepto
            else:
                concepto = random.choice(categorias_egreso)
                monto = random.randint(200000, 8000000)
                categoria = concepto
            
            movimiento = MovimientoCaja(
                fecha=datetime.now() - timedelta(days=random.randint(1, 90)),
                tipo=tipo,
                concepto=concepto,
                monto=monto,
                categoria=categoria,
                numero_documento=f"MOV-{random.randint(1000, 9999)}"
            )
            movimientos.append(movimiento)
        
        db.add_all(movimientos)
        db.commit()
        
        print("Creando actividades de venta...")
        actividades = []
        tipos_actividad = ["Llamada", "Reunión", "Email", "Visita", "Cotización", "Seguimiento"]
        
        for i in range(80):
            vendedor = random.choice(vendedores)
            actividad = ActividadVenta(
                vendedor_id=vendedor.id,
                fecha=datetime.now() - timedelta(days=random.randint(1, 60)),
                tipo_actividad=random.choice(tipos_actividad),
                cliente_nombre=random.choice(clientes).nombre,
                resultado=random.choice([
                    "Cliente interesado",
                    "Solicita más información",
                    "Programar nueva reunión",
                    "Enviar propuesta",
                    "Negociación en proceso",
                    "Cliente no disponible"
                ]),
                monto_estimado=random.randint(2000000, 30000000)
            )
            actividades.append(actividad)
        
        db.add_all(actividades)
        db.commit()
        
        print("✓ Base de datos inicializada correctamente con datos de ejemplo")
        print(f"  - {len(usuarios)} usuarios creados")
        print(f"  - {len(vendedores)} vendedores creados")
        print(f"  - {len(clientes)} clientes creados")
        print(f"  - {len(facturas)} facturas creadas")
        print(f"  - {len(cobranzas)} cobranzas registradas")
        print(f"  - {len(movimientos)} movimientos de caja")
        print(f"  - {len(actividades)} actividades de venta")
        print("\nCredenciales de acceso:")
        print("  Admin: admin@grupoom.com / admin123")
        print("  Operador: operador@grupoom.com / operador123")
        print("  Cliente: cliente@example.com / cliente123")
        
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    initialize_database()
