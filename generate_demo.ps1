# Script completo para generar demo automática (Windows PowerShell)

Write-Host "🎬 DEMO AUTOMÁTICA - OAPCE MULTITRANS" -ForegroundColor Green
Write-Host ("=" * 50) -ForegroundColor Yellow

# Verificar dependencias
Write-Host ""
Write-Host "🔍 Verificando dependencias..." -ForegroundColor Cyan

try {
    python -c "import selenium, PIL, pandas, moviepy, gtts; print('✅ Todas las dependencias instaladas')"
    Write-Host "✅ Dependencias verificadas" -ForegroundColor Green
} catch {
    Write-Host "❌ Faltan dependencias" -ForegroundColor Red
    Write-Host "💡 Instala con: pip install selenium webdriver-manager pillow pandas moviepy opencv-python gtts" -ForegroundColor Yellow
    exit 1
}

# Verificar servidor
Write-Host ""
Write-Host "🌐 Verificando servidor de la aplicación..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5001" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Servidor funcionando en http://localhost:5001" -ForegroundColor Green
    } else {
        Write-Host "❌ Servidor no responde correctamente" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ No se puede conectar al servidor" -ForegroundColor Red
    Write-Host "💡 Inicia la aplicación con:" -ForegroundColor Yellow
    Write-Host "   streamlit run app.py --server.port 5001 --server.address localhost" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "🚀 GENERANDO DEMO AUTOMÁTICA..." -ForegroundColor Green
Write-Host "Esto tomará unos minutos..." -ForegroundColor Yellow
Write-Host ""

# Ejecutar generador de demo
Write-Host "📸 Generando screenshots y carteles..." -ForegroundColor Cyan
python demo_generator.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ DEMO GENERADA EXITOSAMENTE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Archivos creados:" -ForegroundColor Cyan
    Write-Host "   - Screenshots: ./demo_screenshots/" -ForegroundColor White
    Write-Host "   - Carteles: ./demo_carteles/" -ForegroundColor White
    Write-Host "   - Audio: ./demo_audio/" -ForegroundColor White
    Write-Host "   - Resumen: demo_summary.xlsx" -ForegroundColor White
    Write-Host ""
    Write-Host "🎬 CREANDO VIDEO..." -ForegroundColor Green
    Write-Host ""

    # Crear video
    python create_video.py

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 ¡VIDEO DEMO COMPLETADO!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📁 VIDEOS FINALES:" -ForegroundColor Cyan

        Get-ChildItem -Path "*.mp4" -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "   - $($_.Name)" -ForegroundColor White
        }

        if (-not (Get-ChildItem -Path "*.mp4" -ErrorAction SilentlyContinue)) {
            Write-Host "   💡 Ejecuta manualmente: python create_video.py" -ForegroundColor Yellow
        }

        Write-Host ""
        Write-Host "📊 Archivos generados:" -ForegroundColor Cyan
        Write-Host "   - demo_oapce_multitrans.mp4 (versión completa)" -ForegroundColor White
        Write-Host "   - demo_presentacion.mp4 (con efectos)" -ForegroundColor White
        Write-Host "   - demo_instagram_stories.mp4 (vertical)" -ForegroundColor White
        Write-Host ""
        Write-Host "✅ ¡Listo para mostrar a los dueños!" -ForegroundColor Green

    } else {
        Write-Host "❌ Error creando video" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Error generando demo" -ForegroundColor Red
}

Write-Host ""
Write-Host "💡 Para soporte: revisa los logs en la consola" -ForegroundColor Cyan
