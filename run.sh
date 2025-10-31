#!/bin/bash
# OAPCE Multitrans - Run Script
# This script starts the Streamlit application with optimized settings

echo "🚀 Starting OAPCE Multitrans..."
echo "📊 Dashboard for Grupo OM"
echo ""
echo "🔧 Configuration:"
echo "   - Port: 5001"
echo "   - Address: 0.0.0.0"
echo "   - Headless: true"
echo ""
echo "🌐 Access your application at:"
echo "   http://localhost:5001"
echo "   http://127.0.0.1:5001"
echo ""
echo "⏳ Starting server..."
echo ""

# Kill any existing Streamlit processes
pkill -f streamlit || echo "No existing processes to kill"

# Start the application with optimized settings
streamlit run app.py \
    --server.port 5001 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false
