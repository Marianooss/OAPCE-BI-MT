import schedule
import time
import logging
from datetime import datetime
from database import get_db
from import_data import import_from_excel, connect_to_external_api
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_sync.log'),
        logging.StreamHandler()
    ]
)

class DataSynchronizer:
    def __init__(self):
        self.db = None
        self.sync_config = {
            'excel_path': os.getenv('EXCEL_DATA_PATH', './data'),
            'api_url': os.getenv('API_URL'),
            'api_key': os.getenv('API_KEY'),
            'sync_interval': int(os.getenv('SYNC_INTERVAL_MINUTES', '60')),  # cada hora
            'auto_sync': os.getenv('AUTO_SYNC', 'false').lower() == 'true'
        }

    def connect_db(self):
        """Conectar a base de datos"""
        try:
            self.db = get_db()
            logging.info("✅ Conexión a base de datos establecida")
            return True
        except Exception as e:
            logging.error(f"❌ Error conectando a base de datos: {e}")
            return False

    def sync_from_excel(self):
        """Sincronizar desde archivos Excel"""
        try:
            excel_path = self.sync_config['excel_path']
            if os.path.exists(excel_path):
                logging.info(f"📊 Iniciando sincronización desde Excel: {excel_path}")
                import_from_excel(excel_path)
                logging.info("✅ Sincronización Excel completada")
            else:
                logging.warning(f"⚠️ Ruta de Excel no encontrada: {excel_path}")
        except Exception as e:
            logging.error(f"❌ Error en sincronización Excel: {e}")

    def sync_from_api(self):
        """Sincronizar desde API"""
        try:
            api_url = self.sync_config['api_url']
            api_key = self.sync_config['api_key']

            if api_url:
                logging.info(f"🔗 Iniciando sincronización desde API: {api_url}")
                connect_to_external_api(api_url, api_key)
                logging.info("✅ Sincronización API completada")
            else:
                logging.info("ℹ️ No hay API configurada para sincronización")
        except Exception as e:
            logging.error(f"❌ Error en sincronización API: {e}")

    def incremental_sync(self):
        """Sincronización incremental - solo datos nuevos/modificados"""
        try:
            logging.info("🔄 Iniciando sincronización incremental")

            # Aquí puedes implementar lógica para detectar cambios
            # Por ejemplo, comparar timestamps o IDs

            self.sync_from_excel()
            self.sync_from_api()

            logging.info("✅ Sincronización incremental completada")

        except Exception as e:
            logging.error(f"❌ Error en sincronización incremental: {e}")

    def full_sync(self):
        """Sincronización completa - limpiar y recargar todos los datos"""
        try:
            logging.info("🔄 Iniciando sincronización completa")

            # Backup de datos actuales (opcional)
            self.backup_current_data()

            # Limpiar datos existentes
            self.clear_existing_data()

            # Recargar todos los datos
            self.sync_from_excel()
            self.sync_from_api()

            logging.info("✅ Sincronización completa finalizada")

        except Exception as e:
            logging.error(f"❌ Error en sincronización completa: {e}")

    def backup_current_data(self):
        """Crear backup de datos actuales"""
        try:
            backup_dir = f"./backups/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)

            # Exportar datos actuales a CSV
            from models import Cliente, Vendedor, Factura, Cobranza

            # Backup clientes
            clientes = self.db.query(Cliente).all()
            if clientes:
                df = pd.DataFrame([{
                    'id': c.id,
                    'nombre': c.nombre,
                    'rut': c.rut,
                    'email': c.email,
                    'telefono': c.telefono,
                    'estado_funnel': c.estado_funnel.value,
                    'valor_estimado': c.valor_estimado,
                    'fecha_ingreso': c.fecha_ingreso
                } for c in clientes])
                df.to_csv(f"{backup_dir}/clientes_backup.csv", index=False)

            logging.info(f"💾 Backup creado en: {backup_dir}")

        except Exception as e:
            logging.error(f"❌ Error creando backup: {e}")

    def clear_existing_data(self):
        """Limpiar datos existentes (excepto usuarios)"""
        try:
            from models import Cliente, Vendedor, Factura, Cobranza, MovimientoCaja, ActividadVenta

            # Limpiar en orden para respetar foreign keys
            self.db.query(ActividadVenta).delete()
            self.db.query(Cobranza).delete()
            self.db.query(Factura).delete()
            self.db.query(MovimientoCaja).delete()
            self.db.query(Cliente).delete()
            self.db.query(Vendedor).delete()

            self.db.commit()
            logging.info("🧹 Datos existentes limpiados")

        except Exception as e:
            logging.error(f"❌ Error limpiando datos: {e}")
            self.db.rollback()

    def run_sync(self):
        """Ejecutar sincronización programada"""
        if not self.connect_db():
            return

        try:
            logging.info("🔄 Ejecutando sincronización programada")

            if self.sync_config.get('full_sync', False):
                self.full_sync()
            else:
                self.incremental_sync()

        except Exception as e:
            logging.error(f"❌ Error en sincronización programada: {e}")
        finally:
            if self.db:
                self.db.close()

def main():
    """Función principal del sincronizador"""
    print("🚀 Iniciando Sincronizador de Datos OAPCE")
    print("=" * 50)

    synchronizer = DataSynchronizer()

    # Ejecutar sincronización inicial
    print("🔄 Ejecutando sincronización inicial...")
    synchronizer.run_sync()

    # Configurar sincronización automática
    if synchronizer.sync_config['auto_sync']:
        interval = synchronizer.sync_config['sync_interval']
        print(f"⏰ Sincronización automática configurada cada {interval} minutos")

        schedule.every(interval).minutes.do(synchronizer.run_sync)

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
        except KeyboardInterrupt:
            print("\n🛑 Sincronización detenida por usuario")
    else:
        print("ℹ️ Sincronización automática desactivada")
        print("💡 Para activar, configura AUTO_SYNC=true en .env")

if __name__ == "__main__":
    main()
