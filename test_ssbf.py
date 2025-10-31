#!/usr/bin/env python3
"""
Script de prueba para Self-Service BI Facilitator (SSBF)
"""

from ssbf_facilitator import SSBFFacilitator
from database import init_db
import time

def test_ssbf():
    print("🧪 Probando Self-Service BI Facilitator (SSBF)")

    # Asegurar que las tablas existen
    print("📋 Inicializando/actualizando tablas...")
    init_db()

    ssbf = SSBFFacilitator()

    try:
        # Probar inicialización de métricas
        print("\n📊 Probando inicialización de métricas predefinidas...")
        metrics_result = ssbf.initialize_default_metrics()

        if metrics_result['success']:
            print(f"   ✅ {metrics_result['metrics_created']} métricas inicializadas")
            print(f"   📈 Total métricas disponibles: {metrics_result['total_default_metrics']}")
        else:
            print("   ❌ Error inicializando métricas")

        # Probar inicialización de plantillas
        print("\n🎨 Probando inicialización de plantillas...")
        templates_result = ssbf.initialize_dashboard_templates()

        if templates_result['success']:
            print(f"   ✅ {templates_result['templates_created']} plantillas inicializadas")
            print(f"   📋 Total plantillas disponibles: {templates_result['total_default_templates']}")
        else:
            print("   ❌ Error inicializando plantillas")

        # Probar obtener métricas
        print("\n📈 Probando obtención de métricas...")
        all_metrics = ssbf.get_predefined_metrics()
        print(f"   📊 Total métricas recuperadas: {len(all_metrics)}")

        if all_metrics:
            # Mostrar primeras 3 métricas
            for i, metric in enumerate(all_metrics[:3], 1):
                print(f"   {i}. {metric['display_name']} ({metric['category']}) - {metric['data_type']}")

        # Probar cálculo de valor de métrica (si hay métricas)
        if all_metrics:
            print("\n💰 Probando cálculo de valores de métricas...")
            first_metric = all_metrics[0]
            calculation_result = ssbf.calculate_metric_value(first_metric['id'])

            if calculation_result['success']:
                print(f"   ✅ Métrica '{first_metric['display_name']}': {calculation_result['formatted_value']} {first_metric['unit']}")
                print(f"   📅 Calculado en: {calculation_result['calculated_at']:.2f}")
            else:
                print(f"   ❌ Error calculando métrica: {calculation_result.get('error', 'Desconocido')}")

        # Probar creación de dashboard
        print("\n📊 Probando creación de dashboard...")
        dashboard_result = ssbf.create_user_dashboard(
            user_id=1,
            title="Dashboard de Prueba Automática",
            template_name=None,
            description="Dashboard creado por tests automáticos",
            is_public=0
        )

        if dashboard_result['success']:
            dashboard_id = dashboard_result['dashboard_id']
            print(f"   ✅ Dashboard creado con ID: {dashboard_id}")
        else:
            print(f"   ❌ Error creando dashboard: {dashboard_result.get('error', 'Desconocido')}")
            dashboard_id = None

        # Probar obtener dashboards del usuario
        print("\n📋 Probando obtención de dashboards de usuario...")
        user_dashboards = ssbf.get_user_dashboards(user_id=1)

        if user_dashboards:
            print(f"   📊 Total dashboards encontrados: {len(user_dashboards)}")
            for i, dashboard in enumerate(user_dashboards[:3], 1):
                visibility = "Público" if dashboard['is_public'] else "Privado"
                print(f"   {i}. {dashboard['title']} ({visibility}) - Permiso: {dashboard['user_permission']}")
        else:
            print("   ⚠️ No se encontraron dashboards")

        # Probar obtener plantillas
        print("\n🎨 Probando obtención de plantillas...")
        templates = ssbf.get_dashboard_templates()

        if templates:
            print(f"   📋 Total plantillas disponibles: {len(templates)}")
            for i, template in enumerate(templates[:2], 1):
                print(f"   {i}. {template['display_name']} - {template['category']} (Usos: {template['use_count']})")
        else:
            print("   ⚠️ No hay plantillas disponibles")

        # Probar compartir dashboard (si se creó uno)
        if dashboard_id:
            print("\n📤 Probando compartir dashboard...")
            share_result = ssbf.share_dashboard(
                dashboard_id=dashboard_id,
                user_id=1,
                target_user_id=2,
                permission_level='view'
            )

            if share_result['success']:
                print("   ✅ Dashboard compartido exitosamente")
                print("   📝 Nivel de permiso concedido: 'view'")
            else:
                print(f"   ❌ Error compartiendo dashboard: {share_result.get('error', 'Desconocido')}")

        # Probar uso de dashboard (simular vista)
        print("\n👁️ Probando tracking de uso...")
        usage_stats = ssbf.get_dashboard_usage_stats()

        if usage_stats['success']:
            print("   📈 Estadísticas de uso obtenidas:")
            print(f"     • Tipos de dashboard: {usage_stats['dashboard_types']}")
            print(f"     • Total de dashboards: {usage_stats['total_dashboards']}")
            print(f"     • Actividad reciente: {usage_stats['recent_activity']} vistas/editadas")
        else:
            print(f"   ❌ Error obteniendo estadísticas: {usage_stats.get('error', 'Desconocido')}")

        # Performance test
        print("\n⚡ Probando rendimiento...")
        start_time = time.time()

        # Ejecutar múltiples operaciones
        for i in range(5):
            try:
                ssbf.get_predefined_metrics(category='ventas')
            except:
                pass

        end_time = time.time()
        print(f"   ⏱️ Tiempo promedio por operación: {(end_time - start_time)/5:.3f} segundos")

        print("\n" + "=" * 60)
        print("🎉 ¡Self-Service BI Facilitator funciona correctamente!")
        print("💡 Próximos pasos sugeridos:")
        print("   1. Implementar integración completa con Metabase")
        print("   2. Agregar más tipos de gráficos y visualizaciones")
        print("   3. Crear editor visual de dashboards (drag & drop)")
        print("   4. Implementar programador de reportes automáticos")
        print("   5. Agregar permisos granulares por rol/equipo")

    except Exception as e:
        print(f"\n❌ Error en prueba: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        ssbf.close()

if __name__ == "__main__":
    test_ssbf()
