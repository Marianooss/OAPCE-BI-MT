#!/usr/bin/env python3
"""
DEMO RÁPIDA - PRUEBA DEL SISTEMA
Ejecuta una demostración básica sin generar videos completos
"""

from demo_generator import AppDemoGenerator
import time
import os

def quick_demo():
    """Demo rápida para probar el sistema"""
    print("DEMO RAPIDA - OAPCE MULTITRANS")
    print("=" * 40)

    # Verificar servidor
    import requests
    try:
        response = requests.get('http://localhost:5001', timeout=5)
        if response.status_code == 200:
            print("Servidor funcionando OK")
        else:
            print("Servidor no responde correctamente")
            return
    except:
        print("No se puede conectar al servidor")
        print("Inicia: streamlit run app.py --server.port 5001")
        return

    # Crear generador
    demo = AppDemoGenerator()

    # Probar solo algunas funciones básicas
    print("\nProbando funciones basicas...")

    # 1. Crear cartel de prueba
    print("Creando cartel...")
    cartel = demo.create_cartel(
        "Sistema OAPCE Multitrans - Dashboard de Control y Gestion",
        "test_cartel"
    )
    if cartel:
        print(f"Cartel creado: {cartel}")
    else:
        print("Error creando cartel")

    # 2. Generar audio de prueba
    print("Generando audio...")
    audio = demo.generate_audio_narration(
        "Bienvenidos al sistema de control y gestion OAPCE Multitrans",
        "test_audio"
    )
    if audio:
        print(f"Audio generado: {audio}")
    else:
        print("Error generando audio")

    # 3. Configurar navegador (sin ejecutar demo completa)
    print("Configurando navegador...")
    driver = demo.setup_driver()
    if driver:
        try:
            print("Navegador configurado OK")

            # Navegar a la app
            driver.get('http://localhost:5001')
            time.sleep(2)

            # Tomar screenshot de prueba
            screenshot = demo.take_screenshot(driver, "test_screenshot")
            if screenshot:
                print(f"Screenshot guardado: {screenshot}")
            else:
                print("Error tomando screenshot")

        except Exception as e:
            print(f"Error en navegador: {e}")
        finally:
            driver.quit()
    else:
        print("No se pudo configurar navegador")

    print("\nDEMO RAPIDA COMPLETADA!")
    print("\nArchivos generados:")
    print(f"  Carteles: {len(os.listdir('./demo_carteles')) if os.path.exists('./demo_carteles') else 0}")
    print(f"  Audio: {len(os.listdir('./demo_audio')) if os.path.exists('./demo_audio') else 0}")
    print(f"  Screenshots: {len(os.listdir('./demo_screenshots')) if os.path.exists('./demo_screenshots') else 0}")

    print("\nPara demo completa:")
    print("  python demo_generator.py")
    print("  python create_video.py")

if __name__ == "__main__":
    quick_demo()
