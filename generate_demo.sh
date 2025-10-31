#!/bin/bash
# Script completo para generar demo automática

echo "🎬 DEMO AUTOMÁTICA - OAPCE MULTITRANS"
echo "=" * 50

# Verificar dependencias
echo "🔍 Verificando dependencias..."

python -c "
try:
    import selenium, PIL, pandas, moviepy, gtts
    print('✅ Todas las dependencias instaladas')
except ImportError as e:
    print(f'❌ Falta dependencia: {e}')
    print('💡 Instala con: pip install selenium webdriver-manager pillow pandas moviepy opencv-python gtts')
"

if [ $? -ne 0 ]; then
    echo "❌ Instala las dependencias primero"
    exit 1
fi

# Verificar servidor
echo ""
echo "🌐 Verificando servidor de la aplicación..."

python -c "
import requests
import time

try:
    response = requests.get('http://localhost:5001', timeout=5)
    if response.status_code == 200:
        print('✅ Servidor funcionando en http://localhost:5001')
    else:
        print('❌ Servidor no responde correctamente')
        exit(1)
except:
    print('❌ No se puede conectar al servidor')
    print('💡 Inicia la aplicación con:')
    print('   streamlit run app.py --server.port 5001 --server.address localhost')
    exit(1)
"

echo ""
echo "🚀 GENERANDO DEMO AUTOMÁTICA..."
echo "Esto tomará unos minutos..."
echo ""

# Ejecutar generador de demo
python demo_generator.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ DEMO GENERADA EXITOSAMENTE!"
    echo ""
    echo "📋 Archivos creados:"
    echo "   - Screenshots: ./demo_screenshots/"
    echo "   - Carteles: ./demo_carteles/"
    echo "   - Audio: ./demo_audio/"
    echo "   - Resumen: demo_summary.xlsx"
    echo ""
    echo "🎬 CREANDO VIDEO..."
    echo ""

    # Crear video
    python create_video.py

    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 ¡VIDEO DEMO COMPLETADO!"
        echo ""
        echo "📁 VIDEO FINAL:"
        echo "   - demo_oapce_multitrans.mp4 (versión completa)"
        echo ""
        echo "📱 VERSIONES ADICIONALES:"
        echo "   - demo_presentacion.mp4 (con efectos)"
        echo "   - demo_instagram_stories.mp4 (vertical)"
        echo ""
        echo "🎯 RESULTADOS:"
        ls -la *.mp4 2>/dev/null || echo "💡 Ejecuta: python create_video.py"
        echo ""
        echo "✅ ¡Listo para mostrar a los dueños!"
    fi
else
    echo "❌ Error generando demo"
fi
