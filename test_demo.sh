#!/bin/bash
# Script simplificado para probar la demo

echo "🧪 PRUEBA DEL GENERADOR DE DEMO"
echo "=" * 40

# Verificar que el servidor esté corriendo
echo "🌐 Verificando servidor..."
python -c "
import requests
try:
    response = requests.get('http://localhost:5001', timeout=5)
    if response.status_code == 200:
        print('✅ Servidor funcionando')
    else:
        print('❌ Servidor no responde')
except:
    print('❌ No se puede conectar al servidor')
    print('💡 Inicia: streamlit run app.py --server.port 5001 --server.address localhost')
"

echo ""
echo "🔧 Verificando dependencias..."

python -c "
try:
    import selenium
    from PIL import Image
    import pandas as pd
    print('✅ Dependencias básicas OK')
except ImportError as e:
    print(f'❌ Falta: {e}')
"

python -c "
try:
    import moviepy.editor as mp
    print('✅ MoviePy OK')
except ImportError as e:
    print(f'⚠️ MoviePy: {e}')
"

echo ""
echo "📸 Probando captura de pantalla manual..."

python -c "
from demo_generator import AppDemoGenerator
import time

# Probar solo la captura de screenshot
demo = AppDemoGenerator()
driver = demo.setup_driver()

if driver:
    try:
        driver.get('http://localhost:5001')
        time.sleep(3)
        
        screenshot = demo.take_screenshot(driver, 'test_manual')
        if screenshot:
            print(f'✅ Screenshot manual: {screenshot}')
        else:
            print('❌ Error en screenshot')
    except Exception as e:
        print(f'❌ Error: {e}')
    finally:
        driver.quit()
else:
    print('❌ No se pudo configurar navegador')
"

echo ""
echo "🎨 Probando creación de cartel..."

python -c "
from demo_generator import AppDemoGenerator

demo = AppDemoGenerator()
cartel = demo.create_cartel('¡Hola! Esta es una prueba del sistema OAPCE.', 'test_cartel')

if cartel:
    print(f'✅ Cartel creado: {cartel}')
else:
    print('❌ Error creando cartel')
"

echo ""
echo "🎵 Probando audio..."

python -c "
from demo_generator import AppDemoGenerator

demo = AppDemoGenerator()
audio = demo.generate_audio_narration('Esta es una prueba de narración automática', 'test_audio')

if audio:
    print(f'✅ Audio generado: {audio}')
else:
    print('❌ Error generando audio')
"

echo ""
echo "📋 PRUEBA COMPLETA:"
echo "Si todos los pasos anteriores funcionaron, puedes ejecutar:"
echo ""
echo "🎬 Generar demo completa:"
echo "   python demo_generator.py"
echo ""
echo "🎬 Crear video:"
echo "   python create_video.py"
echo ""
echo "🎬 Todo en uno:"
echo "   powershell -File generate_demo.ps1"
