#!/usr/bin/env python3
"""
Script de prueba para Data Pipeline Orchestrator (DPO)
"""

from data_pipeline import DataPipelineOrchestrator
from database import init_db

def test_dpo():
    print("🧪 Probando Data Pipeline Orchestrator (DPO)")

    # Asegurar que las tablas existen
    print("📋 Inicializando/actualizando tablas...")
    init_db()

    dpo = DataPipelineOrchestrator()

    try:
        # Probar extracción
        print("\n📊 Probando extracción de clientes...")
        result = dpo.extract_operational_data('clientes', limit=5)
        print(f"Resultado: {result}")

        # Probar transformación
        if result['success']:
            print("\n🔄 Probando transformación...")
            transform_result = dpo.transform_data(result)
            print(f"Resultado transformación: {transform_result}")

        # Probar métricas de calidad
        print("\n📈 Probando métricas de calidad...")
        metrics = dpo.get_quality_metrics()
        print(f"Métricas: {metrics}")

    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        dpo.close()

if __name__ == "__main__":
    test_dpo()
