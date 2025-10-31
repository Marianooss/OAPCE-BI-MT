import schedule
import time
import logging
from datetime import datetime
import os
from onvio_integration import OnvioIntegrator
from database_config import get_db

# Configurar logging específico para Onvio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ONVIO - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('onvio_sync.log'),
        logging.StreamHandler()
    ]
)

class OnvioAutoSync:
    """Sincronización automática con Onvio"""

    def __init__(self):
        self.api_key = os.getenv('ONVIO_API_KEY')
        self.environment = os.getenv('ONVIO_ENVIRONMENT', 'production')
        self.sync_interval = int(os.getenv('ONVIO_SYNC_INTERVAL', '15'))
        self.export_to_excel = os.getenv('ONVIO_EXPORT_TO_EXCEL', 'true').lower() == 'true'
        self.export_path = os.getenv('ONVIO_EXPORT_PATH', './data/onvio_export')

        if not self.api_key:
            logging.error("❌ ONVIO_API_KEY no configurada en .env")
            return

        self.integrator = OnvioIntegrator(self.api_key, self.environment)
        self.last_sync = None

    def sync_once(self):
        """Ejecutar una sincronización completa"""
        try:
            logging.info("🔄 Iniciando sincronización con Onvio...")

            # Probar conexión
            success, company_info = self.integrator.test_connection()
            if not success:
                logging.error("❌ No se pudo conectar a Onvio")
                return False

            logging.info(f"📊 Empresa: {company_info.get('name', 'N/A')}")

            # Sincronización principal
            sync_success = self.integrator.sync_to_dashboard()

            if sync_success:
                self.last_sync = datetime.now()
                logging.info("✅ Sincronización completada exitosamente")

                # Exportar a Excel si está habilitado
                if self.export_to_excel:
                    self.integrator.export_to_excel_onvio(self.export_path)

                return True
            else:
                logging.error("❌ Error en sincronización")
                return False

        except Exception as e:
            logging.error(f"❌ Error en sincronización: {e}")
            return False

    def run_continuous_sync(self):
        """Ejecutar sincronización continua"""
        logging.info("🚀 Iniciando sincronización automática con Onvio")
        logging.info(f"⏰ Intervalo: {self.sync_interval} minutos")

        # Ejecutar sincronización inicial
        self.sync_once()

        # Programar sincronizaciones regulares
        schedule.every(self.sync_interval).minutes.do(self.sync_once)

        try:
            while True:
                schedule.run_pending()

                # Log de estado cada hora
                if datetime.now().minute == 0:
                    logging.info("💚 Sincronización automática activa - Onvio conectado")

                time.sleep(60)  # Verificar cada minuto

        except KeyboardInterrupt:
            logging.info("🛑 Sincronización detenida por usuario")
        except Exception as e:
            logging.error(f"❌ Error en bucle de sincronización: {e}")

    def get_sync_status(self):
        """Obtener estado actual de sincronización"""
        try:
            success, company_info = self.integrator.test_connection()

            status = {
                'connected': success,
                'company': company_info.get('name', 'N/A') if company_info else 'N/A',
                'last_sync': self.last_sync.isoformat() if self.last_sync else 'Nunca',
                'sync_interval': f"{self.sync_interval} minutos",
                'environment': self.environment,
                'export_to_excel': self.export_to_excel
            }

            # Contar registros actuales
            db = get_db()
            try:
                status.update({
                    'total_clients': db.query('SELECT COUNT(*) FROM clientes').first()[0],
                    'total_invoices': db.query('SELECT COUNT(*) FROM facturas').first()[0],
                    'total_payments': db.query('SELECT COUNT(*) FROM cobranzas').first()[0],
                })
            finally:
                db.close()

            return status

        except Exception as e:
            logging.error(f"Error obteniendo status: {e}")
            return {'connected': False, 'error': str(e)}

def main():
    """Función principal"""
    print("🚀 SINCRONIZACIÓN AUTOMÁTICA CON ONVIO")
    print("=" * 50)
    print("Para empresas que usan Onvio de Thomson Reuters")
    print("Datos en tiempo real para dueños y ejecutivos")
    print()

    # Verificar configuración
    api_key = os.getenv('ONVIO_API_KEY')
    if not api_key:
        print("❌ ONVIO_API_KEY no encontrada en .env")
        print("💡 Configura tu API Key de Onvio primero")
        print("📖 Ver: INTEGRATION_README.md")
        return

    # Crear sincronizador
    sync = OnvioAutoSync()

    # Mostrar estado actual
    print("📊 Estado de sincronización:")
    status = sync.get_sync_status()

    if status.get('connected'):
        print(f"✅ Conectado a: {status['company']}")
        print(f"📈 Registros actuales: {status['total_clients']} clientes, {status['total_invoices']} facturas")
        print(f"⏰ Última sync: {status['last_sync']}")
        print(f"🔄 Intervalo: {status['sync_interval']}")

        choice = input("\n¿Iniciar sincronización automática? (s/n): ").strip().lower()

        if choice == 's':
            print("\n🔄 Iniciando sincronización automática...")
            print("💡 Presiona Ctrl+C para detener")
            sync.run_continuous_sync()
        else:
            print("🔄 Ejecutando sincronización única...")
            sync.sync_once()

    else:
        print(f"❌ No conectado: {status.get('error', 'Error desconocido')}")
        print("💡 Verifica tu API Key y conexión a internet")

if __name__ == "__main__":
    main()
