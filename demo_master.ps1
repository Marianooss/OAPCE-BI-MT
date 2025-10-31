# Script maestro para generar demo completa (Windows PowerShell)

param(
    [string]$Action = "full",  # full, test, package
    [string]$OutputDir = "demo_output"
)

Write-Host "GENERADOR DE DEMO AUTOMATICA - OAPCE MULTITRANS" -ForegroundColor Green
Write-Host ("=" * 50) -ForegroundColor Yellow

# Función para verificar dependencias
function Test-Dependencies {
    Write-Host "Verificando dependencias..." -ForegroundColor Cyan

    $requiredModules = @("selenium", "PIL", "pandas", "moviepy", "gtts")
    $missingModules = @()

    foreach ($module in $requiredModules) {
        try {
            python -c "import $module" 2>$null
            Write-Host "[OK] $module" -ForegroundColor Green
        } catch {
            $missingModules += $module
            Write-Host "[ERROR] $module - FALTA" -ForegroundColor Red
        }
    }

    if ($missingModules.Count -gt 0) {
        Write-Host "" -ForegroundColor Red
        Write-Host "Faltan módulos: $($missingModules -join ', ')" -ForegroundColor Red
        Write-Host "Instala con: pip install $($missingModules -join ' ')" -ForegroundColor Yellow
        return $false
    }

    return $true
}

# Función para verificar servidor
function Test-Server {
    Write-Host "Verificando servidor..." -ForegroundColor Cyan

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5001" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] Servidor funcionando" -ForegroundColor Green
            return $true
        } else {
            Write-Host "[ERROR] Servidor no responde" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "[ERROR] No se puede conectar al servidor" -ForegroundColor Red
        Write-Host "Inicia la aplicación:" -ForegroundColor Yellow
        Write-Host "   streamlit run app.py --server.port 5001 --server.address localhost" -ForegroundColor Gray
        return $false
    }
}

# Función para ejecutar demo completa
function Start-FullDemo {
    Write-Host "GENERANDO DEMO COMPLETA..." -ForegroundColor Green

    # Verificar prerrequisitos
    if (-not (Test-Dependencies)) {
        return $false
    }

    if (-not (Test-Server)) {
        return $false
    }

    # Crear directorios
    $dirs = @("demo_screenshots", "demo_carteles", "demo_audio", $OutputDir)
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir | Out-Null
            Write-Host "Creado: $dir" -ForegroundColor Gray
        }
    }

    Write-Host ""
    Write-Host "Paso 1: Generando screenshots y carteles..." -ForegroundColor Cyan
    python demo_generator.py

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Screenshots generados" -ForegroundColor Green

        Write-Host ""
        Write-Host "Paso 2: Creando videos..." -ForegroundColor Cyan
        python create_video.py

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Videos creados" -ForegroundColor Green

            Write-Host ""
            Write-Host "Paso 3: Creando paquete..." -ForegroundColor Cyan
            python -c "
import os
import shutil

# Crear directorio de paquete
os.makedirs('$OutputDir', exist_ok=True)

# Copiar videos
videos = [f for f in os.listdir('.') if f.endswith('.mp4')]
for video in videos:
    shutil.copy2(video, '$OutputDir/' + video)
    print(f'[OK] {video} copiado')

# Copiar resumen
if os.path.exists('demo_summary.xlsx'):
    shutil.copy2('demo_summary.xlsx', '$OutputDir/demo_summary.xlsx')
    print('[OK] demo_summary.xlsx copiado')

print(f'Paquete creado: $OutputDir')
"

            Write-Host ""
            Write-Host "DEMO COMPLETA GENERADA!" -ForegroundColor Green
            Write-Host ""
            Write-Host "RESULTADOS:" -ForegroundColor Cyan
            Get-ChildItem -Path "*.mp4" -ErrorAction SilentlyContinue | ForEach-Object {
                Write-Host "   - $($_.Name)" -ForegroundColor White
            }
            Write-Host "   - Paquete: $OutputDir/" -ForegroundColor White
            Write-Host ""
            Write-Host "Listo para mostrar a los dueños!" -ForegroundColor Green

            return $true
        }
    }

    Write-Host "[ERROR] Error en la generación" -ForegroundColor Red
    return $false
}

# Función principal
switch ($Action) {
    "test" {
        Write-Host "EJECUTANDO PRUEBAS..." -ForegroundColor Green
        powershell -File test_demo.ps1
    }

    "package" {
        Write-Host "CREANDO PAQUETE..." -ForegroundColor Green
        python -c "
import os
import shutil

os.makedirs('$OutputDir', exist_ok=True)
videos = [f for f in os.listdir('.') if f.endswith('.mp4')]
for video in videos:
    shutil.copy2(video, '$OutputDir/' + video)
    print(f'[OK] {video} copiado')

if os.path.exists('demo_summary.xlsx'):
    shutil.copy2('demo_summary.xlsx', '$OutputDir/demo_summary.xlsx')
    print('[OK] demo_summary.xlsx copiado')
"
        Write-Host "[OK] Paquete creado: $OutputDir" -ForegroundColor Green
    }

    "full" {
        Start-FullDemo
    }

    default {
        Write-Host "[ERROR] Acción no válida: $Action" -ForegroundColor Red
        Write-Host "Opciones válidas: full, test, package" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Para soporte: revisa los logs en la consola" -ForegroundColor Cyan
