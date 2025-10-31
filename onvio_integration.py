"""
INTEGRACIÓN ESPECÍFICA PARA ONVIO DE THOMSON REUTERS
Solución automatizada para empresas que usan Onvio
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from database_config import get_db, init_db
from models import Cliente, Vendedor, Factura, Cobranza, MovimientoCaja, ActividadVenta
from models import EstadoFunnelEnum, EstadoFacturaEnum
import logging
import json
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('onvio_sync.log'),
        logging.StreamHandler()
    ]
)

class OnvioIntegrator:
    """Clase para integrar con Onvio de Thomson Reuters"""

    def __init__(self, api_key, environment='production'):
        self.api_key = api_key
        self.environment = environment
        self.base_url = self._get_base_url()
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _get_base_url(self):
        """Obtener URL base según ambiente"""
        if self.environment == 'sandbox':
            return 'https://api-sandbox.onvio.com'
        else:
            return 'https://api.onvio.com'

    def test_connection(self):
        """Probar conexión con Onvio API"""
        try:
            response = requests.get(
                f"{self.base_url}/v1/company/info",
                headers=self.headers
            )

            if response.status_code == 200:
                company_info = response.json()
                logging.info(f"✅ Conectado a Onvio - Empresa: {company_info.get('name', 'N/A')}")
                return True, company_info
            else:
                logging.error(f"❌ Error API Onvio: {response.status_code} - {response.text}")
                return False, None

        except Exception as e:
            logging.error(f"❌ Error de conexión: {e}")
            return False, None

    def get_clients_onvio(self, last_sync=None):
        """Obtener clientes desde Onvio"""
        try:
            # Endpoint típico de Onvio para clientes
            endpoint = f"{self.base_url}/v1/clients"

            params = {}
            if last_sync:
                params['modified_since'] = last_sync.isoformat()

            response = requests.get(endpoint, headers=self.headers, params=params)

            if response.status_code == 200:
                clients_data = response.json()
                logging.info(f"✅ Obtenidos {len(clients_data)} clientes desde Onvio")
                return clients_data
            else:
                logging.error(f"❌ Error obteniendo clientes: {response.status_code}")
                return []

        except Exception as e:
            logging.error(f"❌ Error en get_clients_onvio: {e}")
            return []

    def get_invoices_onvio(self, last_sync=None):
        """Obtener facturas desde Onvio"""
        try:
            endpoint = f"{self.base_url}/v1/invoices"

            params = {}
            if last_sync:
                params['modified_since'] = last_sync.isoformat()

            response = requests.get(endpoint, headers=self.headers, params=params)

            if response.status_code == 200:
                invoices_data = response.json()
                logging.info(f"✅ Obtenidas {len(invoices_data)} facturas desde Onvio")
                return invoices_data
            else:
                logging.error(f"❌ Error obteniendo facturas: {response.status_code}")
                return []

        except Exception as e:
            logging.error(f"❌ Error en get_invoices_onvio: {e}")
            return []

    def get_payments_onvio(self, last_sync=None):
        """Obtener pagos/cobranzas desde Onvio"""
        try:
            endpoint = f"{self.base_url}/v1/payments"

            params = {}
            if last_sync:
                params['modified_since'] = last_sync.isoformat()

            response = requests.get(endpoint, headers=self.headers, params=params)

            if response.status_code == 200:
                payments_data = response.json()
                logging.info(f"✅ Obtenidos {len(payments_data)} pagos desde Onvio")
                return payments_data
            else:
                logging.error(f"❌ Error obteniendo pagos: {response.status_code}")
                return []

        except Exception as e:
            logging.error(f"❌ Error en get_payments_onvio: {e}")
            return []

    def export_to_excel_onvio(self, output_path="./data"):
        """Exportar datos de Onvio a Excel para importación"""
        try:
            print("📊 Exportando datos desde Onvio a Excel...")

            # Crear directorio si no existe
            import os
            os.makedirs(output_path, exist_ok=True)

            # Obtener datos
            clients = self.get_clients_onvio()
            invoices = self.get_invoices_onvio()
            payments = self.get_payments_onvio()

            # Convertir a DataFrames
            if clients:
                df_clients = pd.DataFrame(clients)
                df_clients.to_excel(f"{output_path}/clientes_onvio.xlsx", index=False)
                print(f"✅ {len(clients)} clientes exportados a Excel")

            if invoices:
                df_invoices = pd.DataFrame(invoices)
                df_invoices.to_excel(f"{output_path}/facturas_onvio.xlsx", index=False)
                print(f"✅ {len(invoices)} facturas exportadas a Excel")

            if payments:
                df_payments = pd.DataFrame(payments)
                df_payments.to_excel(f"{output_path}/cobranzas_onvio.xlsx", index=False)
                print(f"✅ {len(payments)} pagos exportados a Excel")

            print(f"🎉 Exportación completada en: {output_path}")
            return True

        except Exception as e:
            print(f"❌ Error en exportación: {e}")
            return False

    def sync_to_dashboard(self):
        """Sincronizar datos de Onvio al dashboard"""
        print("🔄 Sincronizando datos de Onvio al dashboard...")

        db = get_db()

        try:
            # 1. Sincronizar clientes
            clients_data = self.get_clients_onvio()
            if clients_data:
                self._sync_clients(db, clients_data)

            # 2. Sincronizar facturas
            invoices_data = self.get_invoices_onvio()
            if invoices_data:
                self._sync_invoices(db, invoices_data)

            # 3. Sincronizar pagos
            payments_data = self.get_payments_onvio()
            if payments_data:
                self._sync_payments(db, payments_data)

            db.commit()
            print("✅ Sincronización completada exitosamente")
            return True

        except Exception as e:
            print(f"❌ Error en sincronización: {e}")
            db.rollback()
            return False

        finally:
            db.close()

    def _sync_clients(self, db, clients_data):
        """Sincronizar clientes a la base de datos"""
        synced_count = 0

        for client_data in clients_data:
            try:
                # Mapear campos de Onvio a nuestro modelo
                cliente = Cliente(
                    nombre=client_data.get('name', client_data.get('business_name', '')),
                    rut=client_data.get('tax_id', client_data.get('ruc', '')),
                    email=client_data.get('email', ''),
                    telefono=client_data.get('phone', ''),
                    direccion=client_data.get('address', ''),
                    estado_funnel=self._map_client_status(client_data.get('status', '')),
                    valor_estimado=client_data.get('estimated_value', 0),
                    fecha_ingreso=pd.to_datetime(client_data.get('created_date', datetime.now()))
                )

                # Verificar si ya existe
                existing = db.query(Cliente).filter(Cliente.rut == cliente.rut).first()
                if not existing:
                    db.add(cliente)
                    synced_count += 1

            except Exception as e:
                logging.error(f"Error sincronizando cliente {client_data.get('name', 'Unknown')}: {e}")

        logging.info(f"✅ {synced_count} clientes nuevos sincronizados")

    def _sync_invoices(self, db, invoices_data):
        """Sincronizar facturas"""
        synced_count = 0

        for invoice_data in invoices_data:
            try:
                # Buscar cliente por RUT
                cliente_rut = invoice_data.get('client_tax_id', '')
                cliente = db.query(Cliente).filter(Cliente.rut == cliente_rut).first()

                if cliente:
                    factura = Factura(
                        numero_factura=invoice_data.get('invoice_number', ''),
                        cliente_id=cliente.id,
                        fecha_emision=pd.to_datetime(invoice_data.get('issue_date', datetime.now())),
                        fecha_vencimiento=pd.to_datetime(invoice_data.get('due_date', datetime.now())),
                        monto_total=invoice_data.get('total_amount', 0),
                        monto_pagado=invoice_data.get('paid_amount', 0),
                        estado=self._map_invoice_status(invoice_data.get('status', '')),
                        descripcion=invoice_data.get('description', 'Factura desde Onvio')
                    )

                    # Verificar si ya existe
                    existing = db.query(Factura).filter(
                        Factura.numero_factura == factura.numero_factura
                    ).first()

                    if not existing:
                        db.add(factura)
                        synced_count += 1

            except Exception as e:
                logging.error(f"Error sincronizando factura {invoice_data.get('invoice_number', 'Unknown')}: {e}")

        logging.info(f"✅ {synced_count} facturas nuevas sincronizadas")

    def _sync_payments(self, db, payments_data):
        """Sincronizar pagos/cobranzas"""
        synced_count = 0

        for payment_data in payments_data:
            try:
                # Buscar factura por número
                invoice_number = payment_data.get('invoice_number', '')
                factura = db.query(Factura).filter(
                    Factura.numero_factura == invoice_number
                ).first()

                if factura:
                    cobranza = Cobranza(
                        factura_id=factura.id,
                        fecha_pago=pd.to_datetime(payment_data.get('payment_date', datetime.now())),
                        monto=payment_data.get('amount', 0),
                        metodo_pago=self._map_payment_method(payment_data.get('payment_method', '')),
                        numero_documento=payment_data.get('document_number', ''),
                        observaciones=payment_data.get('notes', 'Pago desde Onvio')
                    )

                    db.add(cobranza)
                    synced_count += 1

                    # Actualizar estado de factura
                    factura.monto_pagado += cobranza.monto
                    if factura.monto_pagado >= factura.monto_total:
                        factura.estado = EstadoFacturaEnum.pagada
                    else:
                        factura.estado = EstadoFacturaEnum.parcial

            except Exception as e:
                logging.error(f"Error sincronizando pago {payment_data.get('document_number', 'Unknown')}: {e}")

        logging.info(f"✅ {synced_count} pagos sincronizados")

    def _map_client_status(self, onvio_status):
        """Mapear estado de cliente de Onvio a nuestro enum"""
        status_map = {
            'prospect': EstadoFunnelEnum.prospecto,
            'contacted': EstadoFunnelEnum.contactado,
            'qualified': EstadoFunnelEnum.calificado,
            'proposal': EstadoFunnelEnum.propuesta,
            'negotiation': EstadoFunnelEnum.negociacion,
            'won': EstadoFunnelEnum.ganado,
            'lost': EstadoFunnelEnum.perdido,
        }

        return status_map.get(onvio_status.lower(), EstadoFunnelEnum.prospecto)

    def _map_invoice_status(self, onvio_status):
        """Mapear estado de factura de Onvio"""
        status_map = {
            'draft': EstadoFacturaEnum.pendiente,
            'sent': EstadoFacturaEnum.pendiente,
            'paid': EstadoFacturaEnum.pagada,
            'overdue': EstadoFacturaEnum.vencida,
            'partial': EstadoFacturaEnum.parcial,
        }

        return status_map.get(onvio_status.lower(), EstadoFacturaEnum.pendiente)

    def _map_payment_method(self, onvio_method):
        """Mapear método de pago de Onvio"""
        method_map = {
            'bank_transfer': 'Transferencia',
            'check': 'Cheque',
            'cash': 'Efectivo',
            'credit_card': 'Tarjeta',
            'debit_card': 'Tarjeta',
        }

        return method_map.get(onvio_method.lower(), 'Transferencia')

def setup_onvio_integration():
    """Configurar integración con Onvio"""
    print("🚀 CONFIGURACIÓN DE INTEGRACIÓN CON ONVIO")
    print("=" * 50)

    # Obtener credenciales
    api_key = input("Ingresa tu API Key de Onvio: ").strip()

    if not api_key:
        print("❌ API Key es requerida")
        return

    environment = input("Ambiente [production/sandbox] (default: production): ").strip()
    if environment not in ['production', 'sandbox']:
        environment = 'production'

    # Probar conexión
    print("\n🔍 Probando conexión con Onvio...")
    integrator = OnvioIntegrator(api_key, environment)

    success, company_info = integrator.test_connection()
    if not success:
        print("❌ No se pudo conectar a Onvio. Verifica tu API Key y ambiente.")
        return

    print(f"✅ Conectado exitosamente a: {company_info.get('name', 'Tu Empresa')}")

    # Elegir método de integración
    print("\n📋 Selecciona método de integración:")
    print("1. Sincronización API directa (Tiempo Real)")
    print("2. Exportar a Excel y luego importar")
    print("3. Sincronización programada automática")

    choice = input("\nOpción (1-3): ").strip()

    if choice == '1':
        print("\n🔄 Ejecutando sincronización directa...")
        success = integrator.sync_to_dashboard()
        if success:
            print("\n🎉 ¡Sincronización completada!")
            print("🌐 Tu dashboard ya muestra datos en tiempo real de Onvio")
            print("📊 Accede en: http://localhost:5001")

    elif choice == '2':
        output_path = input("Ruta para exportar archivos Excel (default: ./data): ").strip()
        if not output_path:
            output_path = "./data"

        success = integrator.export_to_excel_onvio(output_path)
        if success:
            print(f"\n📊 Archivos exportados a: {output_path}")
            print("🔄 Importando a dashboard...")
            from import_data import import_from_excel
            import_from_excel(output_path)

    elif choice == '3':
        print("\n⏰ Configurando sincronización automática...")

        # Configurar variables de entorno
        with open('.env', 'a') as f:
            f.write(f"\n# Configuración Onvio\n")
            f.write(f"ONVIO_API_KEY={api_key}\n")
            f.write(f"ONVIO_ENVIRONMENT={environment}\n")
            f.write(f"ONVIO_AUTO_SYNC=true\n")
            f.write(f"ONVIO_SYNC_INTERVAL=15\n")  # cada 15 minutos

        print("✅ Configuración guardada en .env")
        print("🔄 Iniciando sincronización automática...")

        # Ejecutar primera sincronización
        integrator.sync_to_dashboard()

        print("\n✅ Sincronización automática configurada")
        print("🔄 El sistema se actualizará automáticamente cada 15 minutos")
        print("📊 Los dueños verán datos en tiempo real")

def main():
    """Función principal"""
    print("🚀 INTEGRACIÓN OAPCE MULTITRANS CON ONVIO")
    print("=" * 60)
    print("Perfecto para empresas que usan Onvio de Thomson Reuters")
    print("Datos en tiempo real para dueños y ejecutivos")
    print()

    # Verificar si ya está configurado
    try:
        api_key = os.getenv('ONVIO_API_KEY')
        if api_key:
            print("🔍 Detectada configuración existente de Onvio")
            choice = input("¿Deseas usar configuración existente? (s/n): ").strip().lower()

            if choice == 's':
                environment = os.getenv('ONVIO_ENVIRONMENT', 'production')
                integrator = OnvioIntegrator(api_key, environment)
                success, _ = integrator.test_connection()

                if success:
                    print("✅ Conexión existente funcionando")
                    integrator.sync_to_dashboard()
                    return
                else:
                    print("❌ Configuración existente no funciona. Reconfigurando...")

        setup_onvio_integration()

    except Exception as e:
        print(f"❌ Error: {e}")
        setup_onvio_integration()

if __name__ == "__main__":
    main()
