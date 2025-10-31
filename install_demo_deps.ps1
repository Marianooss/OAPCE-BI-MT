# Script de instalación automática de dependencias

Write-Host "INSTALACION DE DEPENDENCIAS - DEMO GENERATOR" -ForegroundColor Green
Write-Host ("=" * 50) -ForegroundColor Yellow

Write-Host ""
Write-Host "Instalando dependencias de Python..." -ForegroundColor Cyan

# Lista de dependencias
$dependencies = @(
    "selenium",
    "webdriver-manager",
    "pillow",
    "pandas",
    "moviepy",
    "opencv-python",
    "gtts",
    "requests"
)

foreach ($dep in $dependencies) {
    Write-Host "   Instalando $dep..." -ForegroundColor Gray
    pip install $dep
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] $dep instalado" -ForegroundColor Green
    } else {
        Write-Host "   [ERROR] Error instalando $dep" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Instalando herramientas del sistema..." -ForegroundColor Cyan

# Verificar si Chocolatey está instalado
try {
    choco --version | Out-Null
    $chocoInstalled = $true
} catch {
    $chocoInstalled = $false
}

if (-not $chocoInstalled) {
    Write-Host "Instalando Chocolatey (gestor de paquetes)..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

Write-Host "Instalando FFmpeg..." -ForegroundColor Yellow
choco install ffmpeg -y

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] FFmpeg instalado" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Error instalando FFmpeg" -ForegroundColor Red
    Write-Host "Instala manualmente: choco install ffmpeg" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Verificando instalación..." -ForegroundColor Cyan

$testScript = @"
try:
    import selenium, PIL, pandas, moviepy, gtts, requests
    print('[OK] Todas las dependencias instaladas correctamente')
    print('Sistema listo para generar demos automáticas')
except ImportError as e:
    print(f'[ERROR] {e}')
    print('Revisa la instalación de dependencias')
"@

python -c $testScript

Write-Host ""
Write-Host "INSTALACION COMPLETADA!" -ForegroundColor Green
Write-Host ""
Write-Host "PROXIMOS PASOS:" -ForegroundColor Cyan
Write-Host "1. Inicia la aplicación:" -ForegroundColor White
Write-Host "   streamlit run app.py --server.port 5001 --server.address localhost" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Ejecuta la demo:" -ForegroundColor White
Write-Host "   powershell -File demo_simple.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Opciones disponibles:" -ForegroundColor White
Write-Host "   1. Demo rápida" -ForegroundColor Gray
Write-Host "   2. Demo completa" -ForegroundColor Gray
Write-Host "   3. Solo videos" -ForegroundColor Gray
Write-Host "   4. Crear paquete" -ForegroundColor Gray

Write-Host ""
Write-Host "Para soporte: revisa DEMO_README.md" -ForegroundColor Cyan
