import pandas as pd
from database import get_db, init_db
from models import Cliente, Vendedor, Factura, Cobranza, MovimientoCaja, ActividadVenta
from models import EstadoFunnelEnum, EstadoFacturaEnum
from datetime import datetime
import os

def import_from_excel(file_path):
    """Importar datos desde archivos Excel"""
    print(f"📊 Importando datos desde: {file_path}")

    db = get_db()
    try:
        # Importar clientes
        if os.path.exists(f"{file_path}/clientes.xlsx"):
            df_clientes = pd.read_excel(f"{file_path}/clientes.xlsx")
            for _, row in df_clientes.iterrows():
                cliente = Cliente(
                    nombre=row['nombre'],
                    rut=row['rut'],
                    email=row.get('email', ''),
                    telefono=row.get('telefono', ''),
                    direccion=row.get('direccion', ''),
                    estado_funnel=EstadoFunnelEnum[row.get('estado', 'prospecto')],
                    valor_estimado=row.get('valor_estimado', 0),
                    fecha_ingreso=pd.to_datetime(row.get('fecha_ingreso', datetime.now()))
                )
                db.add(cliente)
            print(f"✅ {len(df_clientes)} clientes importados")

        # Importar vendedores
        if os.path.exists(f"{file_path}/vendedores.xlsx"):
            df_vendedores = pd.read_excel(f"{file_path}/vendedores.xlsx")
            for _, row in df_vendedores.iterrows():
                vendedor = Vendedor(
                    nombre=row['nombre'],
                    email=row['email'],
                    telefono=row.get('telefono', ''),
                    meta_mensual=row.get('meta_mensual', 0),
                    comision_porcentaje=row.get('comision', 0),
                    activo=1
                )
                db.add(vendedor)
            print(f"✅ {len(df_vendedores)} vendedores importados")

        # Importar facturas
        if os.path.exists(f"{file_path}/facturas.xlsx"):
            df_facturas = pd.read_excel(f"{file_path}/facturas.xlsx")
            for _, row in df_facturas.iterrows():
                factura = Factura(
                    numero_factura=row['numero_factura'],
                    cliente_id=row['cliente_id'],
                    fecha_emision=pd.to_datetime(row['fecha_emision']),
                    fecha_vencimiento=pd.to_datetime(row['fecha_vencimiento']),
                    monto_total=row['monto_total'],
                    monto_pagado=row.get('monto_pagado', 0),
                    estado=EstadoFacturaEnum[row.get('estado', 'pendiente')],
                    descripcion=row.get('descripcion', '')
                )
                db.add(factura)
            print(f"✅ {len(df_facturas)} facturas importadas")

        db.commit()
        print("🎉 Importación completada exitosamente!")

    except Exception as e:
        print(f"❌ Error durante la importación: {e}")
        db.rollback()
    finally:
        db.close()

def import_from_csv(file_path):
    """Importar datos desde archivos CSV"""
    print(f"📊 Importando datos desde CSV: {file_path}")

    db = get_db()
    try:
        # Ejemplo de importación de clientes desde CSV
        csv_file = f"{file_path}/clientes.csv"
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                cliente = Cliente(
                    nombre=row['NOMBRE_EMPRESA'],
                    rut=row['RUT'],
                    email=row.get('EMAIL', ''),
                    telefono=row.get('TELEFONO', ''),
                    direccion=row.get('DIRECCION', ''),
                    estado_funnel=EstadoFunnelEnum.prospecto,
                    valor_estimado=row.get('VALOR_ESTIMADO', 0),
                    fecha_ingreso=datetime.now()
                )
                db.add(cliente)
            db.commit()
            print(f"✅ {len(df)} clientes importados desde CSV")

    except Exception as e:
        print(f"❌ Error durante la importación CSV: {e}")
        db.rollback()
    finally:
        db.close()

def connect_to_external_api(api_url, api_key=None):
    """Conectar con APIs externas"""
    import requests

    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'

    try:
        response = requests.get(f"{api_url}/clientes", headers=headers)
        if response.status_code == 200:
            data = response.json()

            db = get_db()
            for cliente_data in data:
                cliente = Cliente(
                    nombre=cliente_data['nombre'],
                    rut=cliente_data['rut'],
                    email=cliente_data.get('email', ''),
                    telefono=cliente_data.get('telefono', ''),
                    direccion=cliente_data.get('direccion', ''),
                    estado_funnel=EstadoFunnelEnum[cliente_data.get('estado', 'prospecto')],
                    valor_estimado=cliente_data.get('valor_estimado', 0),
                    fecha_ingreso=pd.to_datetime(cliente_data.get('fecha_ingreso', datetime.now()))
                )
                db.add(cliente)
            db.commit()
            print(f"✅ {len(data)} registros importados desde API")
        else:
            print(f"❌ Error en API: {response.status_code}")

    except Exception as e:
        print(f"❌ Error conectando a API: {e}")

def setup_real_database():
    """Configurar base de datos para producción"""
    print("🚀 Configurando base de datos para datos reales...")

    # 1. Inicializar tablas
    init_db()

    # 2. Preguntar al usuario qué método usar
    print("\n📋 Selecciona el método de importación:")
    print("1. Desde archivos Excel/CSV")
    print("2. Desde API externa")
    print("3. Conexión directa a base de datos existente")
    print("4. Mantener datos actuales (solo para desarrollo)")

    choice = input("\nOpción (1-4): ").strip()

    if choice == '1':
        file_path = input("Ruta a la carpeta con archivos Excel/CSV: ").strip()
        import_from_excel(file_path)
    elif choice == '2':
        api_url = input("URL de la API: ").strip()
        api_key = input("API Key (opcional): ").strip() or None
        connect_to_external_api(api_url, api_key)
    elif choice == '3':
        print("Para conexión directa, configura las variables de entorno en .env")
        print("Ejemplo:")
        print("DATABASE_URL=postgresql://usuario:password@host:5432/empresa_db")
    else:
        print("✅ Manteniendo datos actuales")

if __name__ == "__main__":
    setup_real_database()
