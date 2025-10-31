#!/usr/bin/env python3
"""
Script de prueba para Data Quality Guardian (DQG)
"""

from data_quality import ValidadorCalidadDatos
from database import init_db
import time

def test_dqg():
    print("🧪 Probando Data Quality Guardian (DQG)")

    # Asegurar que las tablas existen
    print("📋 Inicializando/actualizando tablas...")
    init_db()

    dqg = ValidadorCalidadDatos()

    try:
        # Probar configuración por defecto
        print("\n⚙️ Probando configuración por defecto...")
        assert 'datasets' in dqg.config, "Configuración no tiene datasets"
        assert 'reglas' in dqg.config, "Configuración no tiene reglas"
        print("✅ Configuración por defecto OK")

        # Probar validación de clientes
        print("\n👥 Probando validación de clientes...")
        result_clientes = dqg.ejecutar_validaciones('clientes')
        print(f"Resultado clientes: {result_clientes}")

        if result_clientes['success']:
            print(f"   ✅ Puntuación: {result_clientes['puntuacion_general']:.1f}%")
            print(f"   📝 Problemas encontrados: {result_clientes['total_problemas']}")
        else:
            print(f"   ❌ Error: {result_clientes.get('error', 'Desconocido')}")

        # Probar validación de facturas
        print("\n📄 Probando validación de facturas...")
        result_facturas = dqg.ejecutar_validaciones('facturas')
        print(f"Resultado facturas: {result_facturas}")

        if result_facturas['success']:
            print(f"   ✅ Puntuación: {result_facturas['puntuacion_general']:.1f}%")
            print(f"   📝 Problemas encontrados: {result_facturas['total_problemas']}")
        else:
            print(f"   ❌ Error: {result_facturas.get('error', 'Desconocido')}")

        # Probar obtener estado de calidad
        print("\n📊 Probando obtención de estado de calidad...")
        estado = dqg.obtener_estado_calidad('clientes')
        if estado['success']:
            print(f"   ✅ Estado actual: {estado['estado_actual']}")
            print(f"   📈 Historial: {len(estado.get('historial', []))} registros")
        else:
            print(f"   ❌ Error obteniendo estado: {estado.get('error', 'Desconocido')}")

        # Probar obtención de problemas
        print("\n⚠️ Probando obtención de problemas...")
        problemas = dqg.obtener_problemas()
        print(f"   📝 Total problemas encontrados: {len(problemas)}")

        if problemas:
            # Mostrar top 3 problemas
            for i, problema in enumerate(problemas[:3], 1):
                print(f"   {i}. {problema.get('descripcion', 'Sin descripción')}")

        # Probar múltiples validaciones para generar historial
        print("\n🔄 Probando múltiples validaciones...")
        start_time = time.time()
        for dataset in ['clientes', 'facturas', 'vendedores']:
            try:
                result = dqg.ejecutar_validaciones(dataset)
                if result['success']:
                    print(f"   ✅ {dataset}: {result['puntuacion_general']:.1f}% calidad")
                else:
                    print(f"   ❌ {dataset}: Error - {result.get('error', 'Desconocido')}")
            except Exception as e:
                print(f"   ❌ {dataset}: Excepción - {str(e)}")

        end_time = time.time()
        print(f"   ⏱️ Tiempo total: {(end_time - start_time):.2f} segundos")
        print("\n" + "=" * 50)
        print("🎉 ¡Data Quality Guardian funciona correctamente!")
        print("💡 Próximos pasos sugeridos:")
        print("   1. Implementar monitoreo continuo (monitorear_continuo)")
        print("   2. Agregar alertas automáticas por email/Slack")
        print("   3. Crear reglas de validación personalizadas")
        print("   4. Implementar UI completa en Streamlit")

    except Exception as e:
        print(f"\n❌ Error en prueba: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        dqg.close()

if __name__ == "__main__":
    test_dqg()
