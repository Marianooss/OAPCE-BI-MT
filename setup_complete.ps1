# Script de instalación completo (Windows PowerShell)

param(
    [switch]$SkipFFmpeg,
    [switch]$SkipPythonDeps
)

Write-Host "🚀 INSTALACIÓN COMPLETA - OAPCE MULTITRANS + DEMO GENERATOR" -ForegroundColor Green
Write-Host ("=" * 65) -ForegroundColor Yellow

if (-not $SkipPythonDeps) {
    Write-Host ""
    Write-Host "📦 1. Instalando dependencias de Python..." -ForegroundColor Cyan

    $dependencies = @(
        "selenium",
        "webdriver-manager",
        "pillow",
        "pandas",
        "moviepy",
        "opencv-python",
        "gtts",
        "requests",
        "streamlit",
        "plotly",
        "sqlalchemy",
        "python-dotenv",
        "bcrypt"
    )

    foreach ($dep in $dependencies) {
        Write-Host "   Instalando $dep..." -ForegroundColor Gray
        pip install $dep --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $dep" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $dep" -ForegroundColor Red
        }
    }
}

if (-not $SkipFFmpeg) {
    Write-Host ""
    Write-Host "🛠️ 2. Instalando herramientas del sistema..." -ForegroundColor Cyan

    # Verificar Chocolatey
    try {
        choco --version 2>$null | Out-Null
        $chocoInstalled = $true
        Write-Host "   ✅ Chocolatey disponible" -ForegroundColor Green
    } catch {
        Write-Host "   📦 Instalando Chocolatey..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    }

    # Instalar FFmpeg
    Write-Host "   Instalando FFmpeg..." -ForegroundColor Gray
    choco install ffmpeg -y --quiet

    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ FFmpeg instalado" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Error instalando FFmpeg" -ForegroundColor Red
        Write-Host "   💡 Instala manualmente: choco install ffmpeg" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🧪 3. Verificando instalación..." -ForegroundColor Cyan

$verificationScript = @"
try:
    import selenium, PIL, pandas, moviepy, gtts, requests, streamlit, plotly, sqlalchemy
    print('✅ Todas las dependencias instaladas')
    print('🎬 Sistema listo para generar demos automáticas')
except ImportError as e:
    print(f'❌ Error: {e}')
    print('💡 Revisa la instalación de dependencias')
"@

python -c $verificationScript

Write-Host ""
Write-Host "🎯 4. Configuración inicial..." -ForegroundColor Cyan

# Crear directorios necesarios
$dirs = @("demo_screenshots", "demo_carteles", "demo_audio", "demo_package", "backups")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "   📁 Creado: $dir" -ForegroundColor Gray
    }
}

# Configurar .env si no existe
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "   📋 Archivo .env creado" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 ¡INSTALACIÓN COMPLETADA!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 PRÓXIMOS PASOS:" -ForegroundColor Cyan
Write-Host "1. Inicia la aplicación:" -ForegroundColor White
Write-Host "   streamlit run app.py --server.port 5001 --server.address localhost" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Configura integración con Onvio:" -ForegroundColor White
Write-Host "   python setup_onvio.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Genera demo automática:" -ForegroundColor White
Write-Host "   powershell -File demo_simple.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Opciones de demo:" -ForegroundColor White
Write-Host "   1. Demo rápida (prueba)" -ForegroundColor Gray
Write-Host "   2. Demo completa (screenshots + audio + video)" -ForegroundColor Gray
Write-Host "   3. Solo videos" -ForegroundColor Gray
Write-Host "   4. Crear paquete de distribución" -ForegroundColor Gray

Write-Host ""
Write-Host "💡 Para soporte:" -ForegroundColor Cyan
Write-Host "   - ONVIO_README.md (integración con Onvio)" -ForegroundColor Gray
Write-Host "   - DEMO_README.md (generador de demos)" -ForegroundColor Gray
Write-Host "   - INTEGRATION_README.md (integración general)" -ForegroundColor Gray

Write-Host ""
Write-Host "✅ ¡Sistema completo listo para usar!" -ForegroundColor Green
