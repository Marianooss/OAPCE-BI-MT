# Script de prueba rápido para Onvio
import os
from onvio_integration import OnvioIntegrator

def quick_test():
    api_key = os.getenv('ONVIO_API_KEY')
    if not api_key:
        print("❌ ONVIO_API_KEY no encontrada en .env")
        print("💡 Configura tu API Key primero con:")
        print("   python setup_onvio.py")
        return

    print("🔄 Probando conexión con Onvio...")
    integrator = OnvioIntegrator(api_key, os.getenv('ONVIO_ENVIRONMENT', 'production'))

    success, company_info = integrator.test_connection()
    if success:
        print("✅ ¡Conexión exitosa!")
        print(f"📊 Empresa: {company_info.get('name', 'N/A')}")
        print("")
        print("🚀 Ejecutando primera sincronización...")
        integrator.sync_to_dashboard()
        print("")
        print("🎉 ¡Listo! Tu dashboard ya tiene datos de Onvio")
        print("🌐 Accede en: http://localhost:5001")
    else:
        print("❌ Error de conexión")
        print("💡 Verifica tu API Key y conexión a internet")

if __name__ == "__main__":
    quick_test()
