# Script para instalar FFmpeg y generar videos completos

Write-Host "INSTALACION DE FFMPEG Y VIDEOS - OAPCE DEMO" -ForegroundColor Green
Write-Host ("=" * 50) -ForegroundColor Yellow

Write-Host ""
Write-Host "Instalando FFmpeg..." -ForegroundColor Cyan

try {
    choco --version 2>$null | Out-Null
    $chocoInstalled = $true
    Write-Host "   Chocolatey disponible" -ForegroundColor Green
} catch {
    Write-Host "   Instalando Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

choco install ffmpeg -y 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] FFmpeg instalado" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Error instalando FFmpeg" -ForegroundColor Red
    Write-Host "   Instalando versión portable..." -ForegroundColor Yellow

    # Descargar FFmpeg portable
    Invoke-WebRequest -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" -OutFile "ffmpeg.zip"
    Expand-Archive -Path "ffmpeg.zip" -DestinationPath "ffmpeg"
    Move-Item "ffmpeg\ffmpeg-*\bin\ffmpeg.exe" "ffmpeg.exe"
    Remove-Item "ffmpeg.zip" -Recurse -Force

    Write-Host "   [OK] FFmpeg portable instalado" -ForegroundColor Green
}

Write-Host ""
Write-Host "Verificando FFmpeg..." -ForegroundColor Cyan

try {
    $ffmpegVersion = & ffmpeg -version 2>$null | Select-Object -First 1
    Write-Host "   [OK] FFmpeg funcionando: $ffmpegVersion" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] FFmpeg no funciona" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Generando videos completos..." -ForegroundColor Cyan

# Ejecutar script de video simple
python create_video_simple.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Videos generados" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Error generando videos" -ForegroundColor Red
}

Write-Host ""
Write-Host "VERIFICANDO ARCHIVOS FINALES..." -ForegroundColor Cyan

# Verificar videos
Get-ChildItem -Path "*.mp4" -ErrorAction SilentlyContinue | ForEach-Object {
    $size = $_.Length / (1024 * 1024)
    Write-Host "   Video: $($_.Name) (${size:.1f} MB)" -ForegroundColor White
}

# Verificar imágenes
if (Test-Path "demo_images_final") {
    $images = Get-ChildItem -Path "demo_images_final" -Name
    Write-Host "   Imagenes: $images" -ForegroundColor White
}

Write-Host ""
Write-Host "DEMO COMPLETA GENERADA!" -ForegroundColor Green
Write-Host ""
Write-Host "ARCHIVOS DISPONIBLES:" -ForegroundColor Cyan
Write-Host "🎬 Videos:" -ForegroundColor White
Get-ChildItem -Path "*.mp4" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "   - $($_.Name)" -ForegroundColor Gray
}

Write-Host "🖼️ Imagenes:" -ForegroundColor White
Write-Host "   - demo_images_final/demo_step_*.png" -ForegroundColor Gray
Write-Host "   - demo_images_final/demo_presentation.html" -ForegroundColor Gray

Write-Host ""
Write-Host "Para presentaciones profesionales:" -ForegroundColor Cyan
Write-Host "   1. Abre demo_images_final/demo_presentation.html" -ForegroundColor White
Write-Host "   2. Usa las flechas del teclado para navegar" -ForegroundColor Gray
Write-Host "   3. O usa los botones Anterior/Siguiente" -ForegroundColor Gray

Write-Host ""
Write-Host "Listo para mostrar a los dueños!" -ForegroundColor Green
