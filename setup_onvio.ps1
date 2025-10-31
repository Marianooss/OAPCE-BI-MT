# Script automático para configurar integración con Onvio (Windows PowerShell)

Write-Host "🚀 CONFIGURACIÓN AUTOMÁTICA - INTEGRACIÓN CON ONVIO" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Yellow

# Verificar Python
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python detectado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado. Instala Python 3.8+ primero." -ForegroundColor Red
    exit 1
}

# Verificar si .env existe
if (-not (Test-Path .env)) {
    Write-Host "📋 Creando archivo .env..." -ForegroundColor Yellow
    Copy-Item .env.example .env
}

Write-Host ""
Write-Host "🔑 CONFIGURACIÓN DE ONVIO" -ForegroundColor Cyan
Write-Host "Necesitas tu API Key de Onvio (Thomson Reuters)"
Write-Host ""
Write-Host "💡 Cómo obtener tu API Key:" -ForegroundColor Yellow
Write-Host "1. Entra a https://onvio.thomsonreuters.com"
Write-Host "2. Ve a Configuración → APIs → Generar API Key"
Write-Host "3. Copia la key generada"
Write-Host ""

$apiKey = Read-Host "Ingresa tu API Key de Onvio"

if (-not $apiKey) {
    Write-Host "❌ API Key es requerida" -ForegroundColor Red
    exit 1
}

$environment = Read-Host "Ambiente [production/sandbox] (default: production)"

if (-not $environment) {
    $environment = "production"
}

# Actualizar .env
Write-Host ""
Write-Host "✅ Actualizando configuración..." -ForegroundColor Yellow

# Leer archivo .env
$envContent = Get-Content .env -Raw

# Reemplazar configuración de Onvio
$envContent = $envContent -replace "ONVIO_API_KEY=.*", "ONVIO_API_KEY=$apiKey"
$envContent = $envContent -replace "ONVIO_ENVIRONMENT=.*", "ONVIO_ENVIRONMENT=$environment"
$envContent = $envContent -replace "ONVIO_AUTO_SYNC=.*", "ONVIO_AUTO_SYNC=true"
$envContent = $envContent -replace "ONVIO_SYNC_INTERVAL=.*", "ONVIO_SYNC_INTERVAL=15"

# Agregar configuración si no existe
if ($envContent -notcontains "ONVIO_API_KEY") {
    $envContent += "`n# Configuración Onvio`n"
    $envContent += "ONVIO_API_KEY=$apiKey`n"
    $envContent += "ONVIO_ENVIRONMENT=$environment`n"
    $envContent += "ONVIO_AUTO_SYNC=true`n"
    $envContent += "ONVIO_SYNC_INTERVAL=15`n"
}

Set-Content -Path .env -Value $envContent

Write-Host "✅ Configuración guardada en .env" -ForegroundColor Green

Write-Host ""
Write-Host "🔄 Probando conexión con Onvio..." -ForegroundColor Yellow

# Probar conexión
$testScript = @"
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
            print(f'📊 Empresa: {company_info.get("name", "N/A")}')
        print('🎉 ¡Integración lista!')
        exit(0)
    else:
        print('❌ Error de conexión. Verifica tu API Key.')
        exit(1)
else:
    print('❌ API Key no encontrada')
    exit(1)
"@

$testResult = python -c $testScript 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 ¡CONEXIÓN EXITOSA CON ONVIO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 PRÓXIMOS PASOS:" -ForegroundColor Cyan
    Write-Host "1. Ejecutar primera sincronización:" -ForegroundColor White
    Write-Host "   python onvio_integration.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Configurar sincronización automática:" -ForegroundColor White
    Write-Host "   python onvio_auto_sync.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Acceder al dashboard:" -ForegroundColor White
    Write-Host "   http://localhost:5001" -ForegroundColor Gray
    Write-Host ""
    Write-Host "✅ Tu dashboard mostrará datos reales de Onvio en tiempo real" -ForegroundColor Green
    Write-Host "⏰ Los dueños verán actualizaciones cada 15 minutos" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Error de conexión. Verifica:" -ForegroundColor Red
    Write-Host "- Tu API Key de Onvio" -ForegroundColor White
    Write-Host "- Conexión a internet" -ForegroundColor White
    Write-Host "- Que Onvio esté funcionando" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Tip: Prueba con ambiente 'sandbox' si es cuenta nueva" -ForegroundColor Yellow

    # Mostrar logs si hay error
    Write-Host ""
    Write-Host "📄 Logs del error:" -ForegroundColor Yellow
    Write-Host $testResult -ForegroundColor Gray
}

Write-Host ""
Write-Host "💡 Para soporte adicional, revisa ONVIO_README.md" -ForegroundColor Cyan
