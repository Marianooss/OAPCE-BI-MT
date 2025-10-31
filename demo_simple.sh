#!/bin/bash
# Script simplificado para generar demo (Linux/Mac)

echo "🎬 GENERADOR DE DEMO AUTOMÁTICA - OAPCE MULTITRANS"
echo "=================================================="

# Verificar servidor
echo ""
echo "🌐 Verificando servidor de la aplicación..."

if curl -s http://localhost:5001 > /dev/null 2>&1; then
    echo "✅ Servidor funcionando correctamente"
else
    echo "❌ No se puede conectar al servidor"
    echo "💡 Inicia la aplicación:"
    echo "   streamlit run app.py --server.port 5001 --server.address localhost"
    exit 1
fi

echo ""
echo "🚀 OPCIONES DE DEMO:"
echo "1. Demo rápida (prueba componentes)"
echo "2. Demo completa (screenshots + carteles + audio)"
echo "3. Solo crear videos"
echo "4. Crear paquete de distribución"

read -p "Selecciona opción (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🧪 EJECUTANDO DEMO RAPIDA..."
        python quick_demo.py
        ;;

    2)
        echo ""
        echo "🎬 GENERANDO DEMO COMPLETA..."
        echo "Esto tomará unos minutos..."
        python demo_generator.py
        ;;

    3)
        echo ""
        echo "🎬 CREANDO VIDEOS..."
        python create_video.py
        ;;

    4)
        echo ""
        echo "📦 CREANDO PAQUETE DE DEMO..."

        mkdir -p demo_package

        # Copiar videos
        for video in *.mp4; do
            if [ -f "$video" ]; then
                cp "$video" "demo_package/"
                echo "✅ $video copiado"
            fi
        done

        # Copiar resumen
        if [ -f "demo_summary.xlsx" ]; then
            cp "demo_summary.xlsx" "demo_package/"
            echo "✅ demo_summary.xlsx copiado"
        fi

        echo "📦 Paquete creado: demo_package/"
        ;;

    *)
        echo "❌ Opción no válida"
        ;;
esac

echo ""
echo "💡 Para más opciones, revisa DEMO_README.md"
