#!/bin/bash
# Script automático para configurar integración con Onvio

echo "🚀 CONFIGURACIÓN AUTOMÁTICA - INTEGRACIÓN CON ONVIO"
echo "=" * 60

# Verificar Python
python --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Python no encontrado. Instala Python 3.8+ primero."
    exit 1
fi

echo "✅ Python detectado"

# Verificar si .env existe
if [ ! -f .env ]; then
    echo "📋 Creando archivo .env..."
    cp .env.example .env
fi

# Obtener API Key de Onvio
echo ""
echo "🔑 CONFIGURACIÓN DE ONVIO"
echo "Necesitas tu API Key de Onvio (Thomson Reuters)"
echo ""
echo "💡 Cómo obtener tu API Key:"
echo "1. Entra a https://onvio.thomsonreuters.com"
echo "2. Ve a Configuración → APIs → Generar API Key"
echo "3. Copia la key generada"
echo ""

read -p "Ingresa tu API Key de Onvio: " api_key

if [ -z "$api_key" ]; then
    echo "❌ API Key es requerida"
    exit 1
fi

# Configurar ambiente
read -p "Ambiente [production/sandbox] (default: production): " environment
if [ -z "$environment" ]; then
    environment="production"
fi

# Actualizar .env
sed -i.bak "s/ONVIO_API_KEY=.*/ONVIO_API_KEY=$api_key/" .env
sed -i.bak "s/ONVIO_ENVIRONMENT=.*/ONVIO_ENVIRONMENT=$environment/" .env

# Configurar sincronización automática
sed -i.bak "s/ONVIO_AUTO_SYNC=.*/ONVIO_AUTO_SYNC=true/" .env
sed -i.bak "s/ONVIO_SYNC_INTERVAL=.*/ONVIO_SYNC_INTERVAL=15/" .env

echo ""
echo "✅ Configuración guardada en .env"
echo ""
echo "🔄 Probando conexión con Onvio..."

# Probar conexión
python -c "
import os
from onvio_integration import OnvioIntegrator

api_key = os.getenv('ONVIO_API_KEY')
environment = os.getenv('ONVIO_ENVIRONMENT', 'production')

if api_key:
    integrator = OnvioIntegrator(api_key, environment)
    success, company_info = integrator.test_connection()
    
    if success:
        print('✅ Conexión exitosa con Onvio')
        if company_info:
            print(f'📊 Empresa: {company_info.get(\"name\", \"N/A\")}')
        print('🎉 ¡Integración lista!')
    else:
        print('❌ Error de conexión. Verifica tu API Key.')
else:
    print('❌ API Key no encontrada')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 ¡CONEXIÓN EXITOSA CON ONVIO!"
    echo ""
    echo "📋 PRÓXIMOS PASOS:"
    echo "1. Ejecutar primera sincronización:"
    echo "   python onvio_integration.py"
    echo ""
    echo "2. Configurar sincronización automática:"
    echo "   python onvio_auto_sync.py"
    echo ""
    echo "3. Acceder al dashboard:"
    echo "   http://localhost:5001"
    echo ""
    echo "✅ Tu dashboard mostrará datos reales de Onvio en tiempo real"
    echo "⏰ Los dueños verán actualizaciones cada 15 minutos"
else
    echo ""
    echo "❌ Error de conexión. Verifica:"
    echo "- Tu API Key de Onvio"
    echo "- Conexión a internet"
    echo "- Que Onvio esté funcionando"
    echo ""
    echo "💡 Tip: Prueba con ambiente 'sandbox' si es cuenta nueva"
fi
