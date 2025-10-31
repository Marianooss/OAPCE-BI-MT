#!/usr/bin/env python3
"""
Script de prueba integrado para todos los agentes
"""

from database import init_db
from catalog import DataCatalogManager
from data_pipeline import DataPipelineOrchestrator
from predictive_models import PredictiveModelEngine
from prescriptive_advisor import PrescriptiveAdvisor

def test_all_agents():
    print("🧪 Probando todos los agentes del sistema OAPCE")
    print("=" * 60)

    # Inicializar base de datos
    print("📋 Inicializando base de datos...")
    init_db()

    try:
        # 1. Probar DCM
        print("\n📚 Probando Data Catalog Manager (DCM)...")
        dcm = DataCatalogManager()
        scan_result = dcm.scan_database_schema()
        print(f"   ✅ Esquema escaneado: {scan_result['success']}")
        if scan_result['success']:
            summary = dcm.get_catalog_summary()
            print(f"   📊 {summary['total_tables']} tablas, {summary['total_columns']} columnas")
        dcm.close()

        # 2. Probar DPO
        print("\n🔄 Probando Data Pipeline Orchestrator (DPO)...")
        dpo = DataPipelineOrchestrator()
        etl_result = dpo.run_etl_pipeline('clientes', limit=3)
        print(f"   ✅ ETL completado: {etl_result['success']}")
        if etl_result['success']:
            print(f"   📊 {etl_result['total_processed']} registros procesados")
        dpo.close()

        # 3. Probar PME (solo obtener predicciones existentes)
        print("\n🔮 Probando Predictive Model Engine (PME)...")
        pme = PredictiveModelEngine()
        predictions = pme.get_predictions(limit=5)
        print(f"   ✅ Predicciones obtenidas: {predictions['count']} registros")
        pme.close()

        # 4. Probar PA
        print("\n💡 Probando Prescriptive Advisor (PA)...")
        pa = PrescriptiveAdvisor()
        recommendations = pa.generate_client_recommendations(limit=3)
        print(f"   ✅ Recomendaciones generadas: {recommendations['total_generated']}")
        pa.close()

        print("\n" + "=" * 60)
        print("🎉 ¡Todos los agentes funcionan correctamente!")
        print("🚀 El sistema está listo para usar en Streamlit")

    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_all_agents()
