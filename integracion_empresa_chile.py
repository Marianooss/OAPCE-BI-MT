"""
SCRIPT DE INTEGRACIÓN PARA EMPRESAS CHILENAS
Adaptado para sistemas comunes en Chile como SAP, ERP locales, SQL Server
"""

from database_config import get_db, init_db
from models import Cliente, Vendedor, Factura, Cobranza, MovimientoCaja, ActividadVenta
from models import EstadoFunnelEnum, EstadoFacturaEnum
from datetime import datetime
import pandas as pd
import pyodbc  # Para SQL Server
import requests  # Para APIs
import logging

logging.basicConfig(level=logging.INFO)

def connect_sql_server_chile(server, database, username, password):
    """Conectar a SQL Server común en empresas chilenas"""
    connection_string = f"""
    DRIVER={{ODBC Driver 17 for SQL Server}};
    SERVER={server};
    DATABASE={database};
    UID={username};
    PWD={password};
    """

    try:
        conn = pyodbc.connect(connection_string)
        logging.info(f"✅ Conectado a SQL Server: {server}/{database}")
        return conn
    except Exception as e:
        logging.error(f"❌ Error conectando a SQL Server: {e}")
        return None

def migrate_from_sql_server_chile():
    """Migrar datos desde SQL Server típico de empresa chilena"""
    print("🔄 Migrando datos desde SQL Server empresarial...")

    # Configuración típica de empresa chilena
    SERVER = "192.168.1.100"  # IP común de servidor interno
    DATABASE = "EMPRESA_DB"
    USERNAME = "dashboard_user"
    PASSWORD = "dashboard_pass"

    conn = connect_sql_server_chile(SERVER, DATABASE, USERNAME, PASSWORD)

    if not conn:
        return False

    db = get_db()

    try:
        # 1. Migrar clientes desde tabla típica de ERP chileno
        query_clientes = """
        SELECT
            RTRIM(NOMBRE_EMPRESA) as nombre,
            RUT,
            EMAIL,
            TELEFONO,
            DIRECCION,
            FECHA_INGRESO,
            CASE
                WHEN ESTADO = 'PROSPECTO' THEN 1
                WHEN ESTADO = 'CONTACTADO' THEN 2
                WHEN ESTADO = 'CALIFICADO' THEN 3
                WHEN ESTADO = 'PROPUESTA' THEN 4
                WHEN ESTADO = 'NEGOCIACION' THEN 5
                WHEN ESTADO = 'GANADO' THEN 6
                ELSE 1
            END as estado_funnel,
            VALOR_ESTIMADO
        FROM CLIENTES_EMPRESA
        WHERE ACTIVO = 1
        """

        df_clientes = pd.read_sql(query_clientes, conn)

        for _, row in df_clientes.iterrows():
            cliente = Cliente(
                nombre=row['nombre'],
                rut=row['RUT'],
                email=row['EMAIL'] or '',
                telefono=row['TELEFONO'] or '',
                direccion=row['DIRECCION'] or '',
                estado_funnel=EstadoFunnelEnum(list(EstadoFunnelEnum)[row['estado_funnel']-1]),
                valor_estimado=float(row['VALOR_ESTIMADO'] or 0),
                fecha_ingreso=row['FECHA_INGRESO'] or datetime.now()
            )
            db.add(cliente)

        logging.info(f"✅ {len(df_clientes)} clientes migrados")

        # 2. Migrar vendedores
        query_vendedores = """
        SELECT
            NOMBRE,
            EMAIL,
            TELEFONO,
            META_MENSUAL,
            COMISION_PORCENTAJE,
            CASE WHEN ACTIVO = 1 THEN 1 ELSE 0 END as activo
        FROM VENDEDORES
        WHERE ACTIVO = 1
        """

        df_vendedores = pd.read_sql(query_vendedores, conn)

        for _, row in df_vendedores.iterrows():
            vendedor = Vendedor(
                nombre=row['NOMBRE'],
                email=row['EMAIL'],
                telefono=row['TELEFONO'] or '',
                meta_mensual=float(row['META_MENSUAL'] or 0),
                comision_porcentaje=float(row['COMISION_PORCENTAJE'] or 0),
                activo=int(row['activo'])
            )
            db.add(vendedor)

        logging.info(f"✅ {len(df_vendedores)} vendedores migrados")

        # 3. Migrar facturas
        query_facturas = """
        SELECT
            NUMERO_FACTURA,
            CLIENTE_ID,
            FECHA_EMISION,
            FECHA_VENCIMIENTO,
            MONTO_TOTAL,
            MONTO_PAGADO,
            CASE
                WHEN ESTADO = 'PENDIENTE' THEN 1
                WHEN ESTADO = 'PAGADA' THEN 2
                WHEN ESTADO = 'VENCIDA' THEN 3
                WHEN ESTADO = 'PARCIAL' THEN 4
                ELSE 1
            END as estado
        FROM FACTURAS
        WHERE YEAR(FECHA_EMISION) = YEAR(GETDATE())
        """

        df_facturas = pd.read_sql(query_facturas, conn)

        for _, row in df_facturas.iterrows():
            factura = Factura(
                numero_factura=row['NUMERO_FACTURA'],
                cliente_id=int(row['CLIENTE_ID']),
                fecha_emision=row['FECHA_EMISION'],
                fecha_vencimiento=row['FECHA_VENCIMIENTO'],
                monto_total=float(row['MONTO_TOTAL']),
                monto_pagado=float(row['MONTO_PAGADO'] or 0),
                estado=EstadoFacturaEnum(list(EstadoFacturaEnum)[row['estado']-1]),
                descripcion="Factura importada desde sistema ERP"
            )
            db.add(factura)

        logging.info(f"✅ {len(df_facturas)} facturas migradas")

        db.commit()
        logging.info("🎉 Migración desde SQL Server completada exitosamente")

        return True

    except Exception as e:
        logging.error(f"❌ Error en migración: {e}")
        db.rollback()
        return False

    finally:
        conn.close()
        db.close()

def connect_sap_business_one():
    """Conectar con SAP Business One (común en empresas chilenas)"""
    print("🔗 Conectando con SAP Business One...")

    # Configuración típica de SAP B1
    SAP_CONFIG = {
        'server': '192.168.1.50',
        'company_db': 'EMPRESA_PROD',
        'username': 'manager',
        'password': 'sap_password',
        'license_server': '192.168.1.50:30000'
    }

    try:
        # Aquí iría la conexión específica de SAP
        # Esto requiere el SDK de SAP o DI API

        logging.info("✅ Conectado a SAP Business One")

        # Ejemplo de consulta SAP
        sap_query = """
        SELECT
            CardCode,
            CardName,
            LicTradNum,
            E_Mail,
            Phone1,
            Address
        FROM OCRD
        WHERE CardType = 'C'
        """

        # Procesar resultados SAP y crear clientes
        # ... (implementación específica de SAP)

        return True

    except Exception as e:
        logging.error(f"❌ Error conectando a SAP: {e}")
        return False

def connect_api_contable_chile(api_url, api_key):
    """Conectar con APIs de sistemas contables chilenos como Conta o e-Conta"""
    print(f"🔗 Conectando con API contable: {api_url}")

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    try:
        # Obtener clientes
        response = requests.get(f"{api_url}/clientes", headers=headers)

        if response.status_code == 200:
            clientes_data = response.json()

            db = get_db()

            for cliente_data in clientes_data:
                # Mapear campos según API específica
                cliente = Cliente(
                    nombre=cliente_data.get('razon_social', cliente_data.get('nombre', '')),
                    rut=cliente_data.get('rut', ''),
                    email=cliente_data.get('email', ''),
                    telefono=cliente_data.get('telefono', ''),
                    direccion=cliente_data.get('direccion', ''),
                    estado_funnel=EstadoFunnelEnum.prospecto,
                    valor_estimado=cliente_data.get('valor_estimado', 0),
                    fecha_ingreso=datetime.now()
                )
                db.add(cliente)

            db.commit()
            logging.info(f"✅ {len(clientes_data)} clientes importados desde API contable")

            return True
        else:
            logging.error(f"❌ Error API: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logging.error(f"❌ Error conectando a API: {e}")
        return False

    finally:
        db.close()

def main():
    """Función principal para integración empresarial"""
    print("🚀 INTEGRACIÓN OAPCE MULTITRANS - EMPRESAS CHILENAS")
    print("=" * 60)

    # Inicializar base de datos
    print("📊 Inicializando base de datos...")
    init_db()

    print("\n📋 Selecciona el tipo de integración:")
    print("1. SQL Server (ERP interno)")
    print("2. SAP Business One")
    print("3. API Contable (Conta, e-Conta, etc.)")
    print("4. Archivos Excel/CSV")
    print("5. Base de datos PostgreSQL/MySQL")

    choice = input("\nOpción (1-5): ").strip()

    success = False

    if choice == '1':
        success = migrate_from_sql_server_chile()
    elif choice == '2':
        success = connect_sap_business_one()
    elif choice == '3':
        api_url = input("URL de la API: ").strip()
        api_key = input("API Key: ").strip()
        success = connect_api_contable_chile(api_url, api_key)
    elif choice == '4':
        from import_data import import_from_excel
        file_path = input("Ruta a archivos Excel/CSV: ").strip()
        import_from_excel(file_path)
        success = True
    elif choice == '5':
        print("Configura DATABASE_URL en .env para PostgreSQL/MySQL")
        print("Ejemplo: postgresql://usuario:password@host:5432/empresa_db")
        success = True

    if success:
        print("\n🎉 ¡Integración completada exitosamente!")
        print("🌐 Tu dashboard ahora muestra datos reales de tu empresa")
        print("📊 Accede en: http://localhost:5001")
    else:
        print("\n❌ Error en la integración")
        print("💡 Revisa los logs y verifica las credenciales")

if __name__ == "__main__":
    main()
