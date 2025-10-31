# Abrir presentación de demo automáticamente

Write-Host "DEMO OAPCE MULTITRANS - PRESENTACION" -ForegroundColor Green
Write-Host ("=" * 50) -ForegroundColor Yellow

Write-Host ""
Write-Host "Archivos disponibles:" -ForegroundColor Cyan

# Verificar archivos
Get-ChildItem -Path "demo_images_final" | ForEach-Object {
    $size = $_.Length / 1024
    Write-Host "   $($_.Name) (${size:.1f} KB)" -ForegroundColor White
}

Write-Host ""
Write-Host "Opciones de presentacion:" -ForegroundColor Cyan
Write-Host "1. Presentacion HTML corregida (recomendada)" -ForegroundColor White
Write-Host "2. Presentacion HTML original" -ForegroundColor White
Write-Host "3. Solo ver imagenes individuales" -ForegroundColor White

$choice = Read-Host "Selecciona opcion (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Abriendo presentacion HTML corregida..." -ForegroundColor Green
        Start-Process "demo_images_final\demo_presentation_fixed.html"
        Write-Host ""
        Write-Host "Presentacion abierta en tu navegador!" -ForegroundColor Green
        Write-Host "Usa las flechas del teclado para navegar" -ForegroundColor Yellow
        Write-Host "O los botones Anterior/Siguiente" -ForegroundColor Yellow
    }

    "2" {
        Write-Host ""
        Write-Host "Abriendo presentacion HTML original..." -ForegroundColor Green
        Start-Process "demo_images_final\demo_presentation.html"
        Write-Host ""
        Write-Host "Nota: Esta version puede tener problemas de rutas" -ForegroundColor Yellow
    }

    "3" {
        Write-Host ""
        Write-Host "Abriendo carpeta con imagenes..." -ForegroundColor Green
        Start-Process "demo_images_final"
        Write-Host ""
        Write-Host "Imagenes listas para usar en PowerPoint u otras presentaciones" -ForegroundColor Yellow
    }

    default {
        Write-Host "Opcion no valida" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Para mostrar a los dueños:" -ForegroundColor Cyan
Write-Host "   - Navegacion: Flechas del teclado (izq/der)" -ForegroundColor White
Write-Host "   - Auto-play: 5 segundos por slide" -ForegroundColor White
Write-Host "   - Responsive: Se adapta a cualquier pantalla" -ForegroundColor White

Write-Host ""
Write-Host "Presentacion profesional lista!" -ForegroundColor Green
