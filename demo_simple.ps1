# Script simplificado para generar demo (Windows PowerShell)

Write-Host "GENERADOR DE DEMO AUTOMATICA - OAPCE MULTITRANS" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Yellow

# Verificar servidor
Write-Host ""
Write-Host "Verificando servidor de la aplicación..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5001" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] Servidor funcionando correctamente" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Servidor no responde" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] No se puede conectar al servidor" -ForegroundColor Red
    Write-Host "Inicia la aplicación:" -ForegroundColor Yellow
    Write-Host "   streamlit run app.py --server.port 5001 --server.address localhost" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "OPCIONES DE DEMO:" -ForegroundColor Cyan
Write-Host "1. Demo rápida (prueba componentes)" -ForegroundColor White
Write-Host "2. Demo completa (screenshots + carteles + audio)" -ForegroundColor White
Write-Host "3. Solo crear videos" -ForegroundColor White
Write-Host "4. Crear paquete de distribución" -ForegroundColor White

$choice = Read-Host "Selecciona opción (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "EJECUTANDO DEMO RAPIDA..." -ForegroundColor Green
        python quick_demo.py
    }

    "2" {
        Write-Host ""
        Write-Host "GENERANDO DEMO COMPLETA..." -ForegroundColor Green
        Write-Host "Esto tomará unos minutos..." -ForegroundColor Yellow
        python demo_generator.py
    }

    "3" {
        Write-Host ""
        Write-Host "CREANDO VIDEOS..." -ForegroundColor Green
        python create_video.py
    }

    "4" {
        Write-Host ""
        Write-Host "CREANDO PAQUETE DE DEMO..." -ForegroundColor Green
        python -c "
import os
import shutil

# Crear directorio
os.makedirs('demo_package', exist_ok=True)

# Copiar videos
videos = [f for f in os.listdir('.') if f.endswith('.mp4')]
for video in videos:
    shutil.copy2(video, 'demo_package/' + video)
    print(f'[OK] {video}')

# Copiar resumen
if os.path.exists('demo_summary.xlsx'):
    shutil.copy2('demo_summary.xlsx', 'demo_package/demo_summary.xlsx')
    print('[OK] demo_summary.xlsx')

print('Paquete creado: demo_package/')
"
        Write-Host "[OK] Paquete creado en ./demo_package/" -ForegroundColor Green
    }

    default {
        Write-Host "[ERROR] Opción no válida" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Para más opciones, revisa DEMO_README.md" -ForegroundColor Cyan
