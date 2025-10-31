#!/bin/bash
# OAPCE BI Pro - Startup Script para Free Tiers

echo "🚀 Iniciando OAPCE BI Pro..."

# Verificar Python
python3 --version || python --version || echo "Python no encontrado"

# Instalar dependencias si requirements.txt existe
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando dependencias..."
    pip install -r requirements.txt --quiet || pip3 install -r requirements.txt --quiet
fi

# Inicializar base de datos solo si no existe
if [ ! -f "oapce_multitrans.db" ]; then
    echo "🗄️ Inicializando base de datos..."
    python init_db.py 2>/dev/null || python3 init_db.py 2>/dev/null || echo "init_db.py no encontrado"
    python create_ssbf_tables.py 2>/dev/null || python3 create_ssbf_tables.py 2>/dev/null || echo "create_ssbf_tables.py no encontrado"
fi

echo "✅ Sistema listo. Ejecutando Streamlit..."
streamlit run app.py --server.headless true --server.port $PORT --server.address 0.0.0.0
