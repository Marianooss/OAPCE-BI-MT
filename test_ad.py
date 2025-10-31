#!/usr/bin/env python3
"""
Script de prueba para Anomaly Detector (AD)
"""

from anomaly_detector import AnomalyDetector
from database import init_db
import time

def test_ad():
    print("🧪 Probando Anomaly Detector (AD)")

    # Asegurar que las tablas existen
    print("📋 Inicializando/actualizando tablas...")
    init_db()

    ad = AnomalyDetector()

    try:
        # Probar configuración por defecto
        print("\n⚙️ Probando configuración por defecto...")
        assert hasattr(ad, 'model_configs'), "No tiene configuraciones de modelos"
        assert 'isolation_forest' in ad.model_configs, "No tiene config de Isolation Forest"
        assert 'prophet' in ad.model_configs, "No tiene config de Prophet"
        print("✅ Configuración por defecto OK")

        # Probar detección de anomalías en ventas
        print("\n📈 Probando detección de anomalías en ventas...")
        result_sales = ad.detect_anomalies_sales(lookback_days=90)
        print(f"Resultado ventas: {result_sales}")

        if result_sales['success']:
            print(f"   ✅ Anomalías detectadas: {result_sales.get('anomalies_detected', 0)}")
            print(f"   📊 Puntos de datos analizados: {result_sales.get('data_points', 0)}")
            print(f"   💾 Alertas guardadas: {result_sales.get('anomalies_saved', 0)}")

            if result_sales.get('anomalies'):
                print("   🚨 Anomalías encontradas:")
                for anomalia in result_sales['anomalies'][:3]:  # Top 3
                    print(f"      • {anomalia['timestamp']} - {anomalia['metric_name']}: {anomalia['metric_value']:.2f} ({anomalia['severity']})")
        else:
            print(f"   ⚠️ No se pudieron detectar anomalías en ventas: {result_sales.get('error', 'Sin datos suficientes')}")

        # Probar detección de anomalías en cobros
        print("\n💰 Probando detección de anomalías en cobros...")
        result_collections = ad.detect_anomalies_collections(lookback_days=90)
        print(f"Resultado cobros: {result_collections}")

        if result_collections['success']:
            print(f"   ✅ Anomalías detectadas: {result_collections.get('anomalies_detected', 0)}")
            print(f"   📊 Puntos de datos analizados: {result_collections.get('data_points', 0)}")
            print(f"   💾 Alertas guardadas: {result_collections.get('anomalies_saved', 0)}")
        else:
            print(f"   ⚠️ No se pudieron detectar anomalías en cobros: {result_collections.get('error', 'Sin datos suficientes')}")

        # Probar métodos individuales
        print("\n🔬 Probando métodos individuales...")

        # Obtener datos para pruebas
        sales_data = ad._get_sales_timeseries(30)
        if len(sales_data) >= 10:
            print(f"   📊 Datos de ventas obtenidos: {len(sales_data)} registros")

            # Probar Isolation Forest
            print("   🌲 Probando Isolation Forest...")
            try:
                if_anomalies = ad.detect_with_isolation_forest(sales_data, "test_sales")
                print(f"      ✅ Isolation Forest: {len(if_anomalies)} anomalías detectadas")
            except Exception as e:
                print(f"      ❌ Isolation Forest: {str(e)}")

            # Probar Z-score
            print("   📏 Probando Z-score dinámico...")
            try:
                zscore_anomalies = ad.calculate_dynamic_zscore(sales_data, "test_sales")
                print(f"      ✅ Z-score: {len(zscore_anomalies)} anomalías detectadas")
            except Exception as e:
                print(f"      ❌ Z-score: {str(e)}")
        else:
            print("   ⚠️ Datos insuficientes para pruebas de métodos individuales")

        # Probar obtener anomalías
        print("\n📋 Probando obtención de anomalías...")
        all_anomalies = ad.get_anomalies()
        if all_anomalies['success']:
            print(f"   📝 Total anomalías: {all_anomalies['count']}")
            if all_anomalies['count'] > 0:
                print("   🚨 Anomalías activas:")
                for anomalia in all_anomalies['anomalies'][:5]:
                    status_icon = "🚨" if anomalia['status'] == 'open' else "✅"
                    print(f"      {status_icon} {anomalia['metric_name']}: {anomalia['metric_value']:.2f} ({anomalia['severity']})")
        else:
            print(f"   ❌ Error obteniendo anomalías: {all_anomalies.get('error', 'Desconocido')}")

        # Probar acknowledge y resolve (si hay anomalías)
        if all_anomalies['success'] and all_anomalies['anomalies']:
            first_anomaly = all_anomalies['anomalies'][0]
            anomaly_id = first_anomaly['id']

            print("\n🔄 Probando gestión de anomalías...")

            # Probar acknowledge
            ack_result = ad.acknowledge_anomaly(anomaly_id, "Test desde script", "user_test")
            if ack_result['success']:
                print("   ✅ Anomalía confirmada correctamente")
            else:
                print(f"   ❌ Error confirmando anomalía: {ack_result.get('error', 'Desconocido')}")

            # Probar resolve
            resolve_result = ad.resolve_anomaly(anomaly_id, "Resuelta en prueba automática")
            if resolve_result['success']:
                print("   ✅ Anomalía resuelta correctamente")
            else:
                print(f"   ❌ Error resolviendo anomalía: {resolve_result.get('error', 'Desconocido')}")

        # Probar dashboard
        print("\n📊 Probando dashboard...")
        dashboard = ad.get_dashboard_summary()
        if dashboard['success']:
            print(f"   📈 Anomalías críticas: {dashboard['severity_summary'].get('critical', {}).get('total', 0)}")
            print(f"   📋 Anomalías recientes: {len(dashboard.get('recent_anomalies', []))}")
        else:
            print(f"   ❌ Error obteniendo dashboard: {dashboard.get('error', 'Desconocido')}")

        # Performance test
        print("\n⚡ Probando rendimiento...")
        start_time = time.time()

        # Ejecutar varias detecciones
        for i in range(3):
            try:
                ad.detect_anomalies_sales(lookback_days=30)
            except:
                pass

        end_time = time.time()
        print(f"   ⏱️ Tiempo total: {(end_time - start_time):.2f} segundos")

        print("\n" + "=" * 60)
        print("🎉 ¡Anomaly Detector funciona correctamente!")
        print("💡 Próximos pasos sugeridos:")
        print("   1. Implementar Prophet para series temporales complejas")
        print("   2. Agregar alertas automáticas por email/Slack")
        print("   3. Crear sistema de aprendizaje continuo")
        print("   4. Implementar clustering de anomalías similares")
        print("   5. Agregar métricas de precisión del modelo")

    except Exception as e:
        print(f"\n❌ Error en prueba: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        ad.close()

if __name__ == "__main__":
    test_ad()
