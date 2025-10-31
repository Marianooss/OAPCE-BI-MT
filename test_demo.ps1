# Script de prueba para Windows PowerShell

Write-Host "🧪 PRUEBA DEL GENERADOR DE DEMO" -ForegroundColor Green
Write-Host ("=" * 40) -ForegroundColor Yellow

# Verificar servidor
Write-Host ""
Write-Host "🌐 Verificando servidor..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5001" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Servidor funcionando" -ForegroundColor Green
    } else {
        Write-Host "❌ Servidor no responde" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ No se puede conectar al servidor" -ForegroundColor Red
    Write-Host "💡 Inicia: streamlit run app.py --server.port 5001 --server.address localhost" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔧 Verificando dependencias..." -ForegroundColor Cyan

try {
    python -c "import selenium; from PIL import Image; import pandas as pd; print('✅ Dependencias básicas OK')"
    Write-Host "✅ Dependencias básicas OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Faltan dependencias básicas" -ForegroundColor Red
}

try {
    python -c "import moviepy.editor as mp; print('✅ MoviePy OK')"
    Write-Host "✅ MoviePy OK" -ForegroundColor Green
} catch {
    Write-Host "⚠️ MoviePy no disponible" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📸 Probando captura de pantalla manual..." -ForegroundColor Cyan

python -c "
from demo_generator import AppDemoGenerator
import time

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

Write-Host ""
Write-Host "🎨 Probando creación de cartel..." -ForegroundColor Cyan

python -c "
from demo_generator import AppDemoGenerator

demo = AppDemoGenerator()
cartel = demo.create_cartel('¡Hola! Esta es una prueba del sistema OAPCE.', 'test_cartel')

if cartel:
    print(f'✅ Cartel creado: {cartel}')
else:
    print('❌ Error creando cartel')
"

Write-Host ""
Write-Host "🎵 Probando audio..." -ForegroundColor Cyan

python -c "
from demo_generator import AppDemoGenerator

demo = AppDemoGenerator()
audio = demo.generate_audio_narration('Esta es una prueba de narración automática', 'test_audio')

if audio:
    print(f'✅ Audio generado: {audio}')
else:
    print('❌ Error generando audio')
"

Write-Host ""
Write-Host "📋 PRUEBA COMPLETA:" -ForegroundColor Green
Write-Host "Si todos los pasos anteriores funcionaron, puedes ejecutar:" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎬 Generar demo completa:" -ForegroundColor White
Write-Host "   python demo_generator.py" -ForegroundColor Gray
Write-Host ""
Write-Host "🎬 Crear video:" -ForegroundColor White
Write-Host "   python create_video.py" -ForegroundColor Gray
Write-Host ""
Write-Host "🎬 Todo en uno:" -ForegroundColor White
Write-Host "   powershell -File generate_demo.ps1" -ForegroundColor Gray

Write-Host ""
Write-Host "💡 Para soporte: revisa los logs en la consola" -ForegroundColor Cyan
