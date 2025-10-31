#!/usr/bin/env python3
"""
Script de prueba para Data Catalog Manager (DCM)
"""

from catalog import DataCatalogManager
from database import init_db

def test_dcm():
    print("🧪 Probando Data Catalog Manager (DCM)")

    # Asegurar que las tablas existen
    print("📋 Inicializando/actualizando tablas...")
    init_db()

    dcm = DataCatalogManager()

    try:
        # Probar escaneo del esquema
        print("\n🔍 Escaneando esquema de base de datos...")
        scan_result = dcm.scan_database_schema()
        print(f"Resultado del escaneo: {scan_result}")

        # Probar obtener resumen del catálogo
        if scan_result['success']:
            print("\n📊 Obteniendo resumen del catálogo...")
            summary = dcm.get_catalog_summary()
            print(f"Resumen: {summary}")

            # Probar búsqueda
            print("\n🔎 Probando búsqueda en catálogo...")
            search_result = dcm.search_catalog(query="cliente")
            print(f"Resultados de búsqueda: {len(search_result.get('results', []))} encontrados")

            # Mostrar algunas entradas
            if search_result['success'] and search_result['results']:
                print("\n📋 Muestra de entradas del catálogo:")
                for entry in search_result['results'][:3]:
                    print(f"  - {entry['table_name']}.{entry['column_name']}: {entry['description']} (Sensibilidad: {entry['sensitivity_level']})")

            # Probar exportación
            print("\n💾 Probando exportación del catálogo...")
            export_result = dcm.export_catalog_to_json("catalog_export.json")
            print(f"Exportación: {export_result}")

    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        dcm.close()

if __name__ == "__main__":
    test_dcm()
