"""
SCRIPT PRINCIPAL PARA GENERAR VIDEO DEMO AUTOMÁTICO
Ejecuta todo el proceso de un solo comando
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Ejecutar comando y mostrar progreso"""
    print(f"\n🔄 {description}...")
    print(f"   Comando: {command}")

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ {description} completado")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Error en {description}")
            print(f"   Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Excepción en {description}: {e}")
        return False

def check_requirements():
    """Verificar requisitos del sistema"""
    print("🔍 VERIFICANDO REQUISITOS...")

    # Verificar Python
    try:
        import platform
        python_version = platform.python_version()
        print(f"✅ Python: {python_version}")
    except:
        print("❌ Python no encontrado")
        return False

    # Verificar dependencias críticas
    required_modules = ['selenium', 'PIL', 'pandas', 'moviepy', 'gtts']
    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} - FALTA")

    if missing_modules:
        print(f"\n⚠️ Faltan módulos: {', '.join(missing_modules)}")
        print("💡 Instala con: pip install selenium webdriver-manager pillow pandas moviepy opencv-python gtts")
        return False

    # Verificar servidor
    try:
        import requests
        response = requests.get('http://localhost:5001', timeout=5)
        if response.status_code == 200:
            print("✅ Servidor OAPCE funcionando")
        else:
            print("❌ Servidor no responde correctamente")
            return False
    except:
        print("❌ Servidor no disponible")
        print("💡 Inicia: streamlit run app.py --server.port 5001 --server.address localhost")
        return False

    return True

def generate_complete_demo():
    """Generar demo completa"""
    print("\n🎬 GENERANDO DEMO COMPLETA...")
    print("=" * 50)

    steps = [
        {
            'command': 'python demo_generator.py',
            'description': 'Generando screenshots, carteles y audio'
        },
        {
            'command': 'python create_video.py',
            'description': 'Creando videos demo'
        }
    ]

    success_count = 0

    for step in steps:
        if run_command(step['command'], step['description']):
            success_count += 1
        else:
            print(f"⚠️ Continuando con siguiente paso...")

    return success_count == len(steps)

def create_demo_package():
    """Crear paquete de demo para distribución"""
    print("\n📦 CREANDO PAQUETE DE DEMO...")

    # Crear directorio de distribución
    dist_dir = "./demo_package"
    os.makedirs(dist_dir, exist_ok=True)

    # Copiar archivos de video
    video_files = ['demo_oapce_multitrans.mp4', 'demo_presentacion.mp4', 'demo_instagram_stories.mp4']
    copied_videos = []

    for video in video_files:
        if os.path.exists(video):
            import shutil
            shutil.copy2(video, f"{dist_dir}/{video}")
            copied_videos.append(video)
            print(f"✅ {video} copiado")

    # Copiar resumen
    if os.path.exists('demo_summary.xlsx'):
        shutil.copy2('demo_summary.xlsx', f"{dist_dir}/demo_summary.xlsx")
        print("✅ demo_summary.xlsx copiado")

    # Crear README del paquete
    readme_content = f"""# 🎬 DEMO OAPCE MULTITRANS

## 📁 CONTENIDO DEL PAQUETE

### Videos Generados:
{chr(10).join([f"- {video}" for video in copied_videos])}

### Documentación:
- demo_summary.xlsx - Resumen de pasos de la demo

## 🎯 CÓMO USAR

1. **Video principal:** `demo_oapce_multitrans.mp4`
   - Demo completa del sistema
   - Duración: ~{len(copied_videos) * 15} segundos

2. **Versión presentación:** `demo_presentacion.mp4`
   - Con efectos y transiciones
   - Ideal para reuniones

3. **Instagram Stories:** `demo_instagram_stories.mp4`
   - Formato vertical 9:16
   - Perfecto para redes sociales

## 📊 LO QUE SE DEMUESTRA

✅ Sistema de login seguro
✅ Dashboard ejecutivo con KPIs
✅ Módulos comerciales y financieros
✅ Gestión de datos y formularios
✅ Integración con datos reales

## 🚀 PRÓXIMOS PASOS

1. **Personalizar** con tus datos reales
2. **Agregar** tu logo y branding
3. **Grabar** con narración profesional
4. **Compartir** con clientes y dueños

---
*Generado automáticamente por OAPCE Multitrans Demo Generator*
"""

    with open(f"{dist_dir}/README.md", 'w') as f:
        f.write(readme_content)

    print(f"\n✅ PAQUETE CREADO: {dist_dir}")
    print(f"📁 Contiene: {len(copied_videos)} videos + documentación")

    return True

def main():
    """Función principal"""
    print("🎬 GENERADOR DE DEMO AUTOMÁTICA - OAPCE MULTITRANS")
    print("=" * 60)
    print("Este script crea una demostración completa y automática")
    print("de tu aplicación con screenshots, carteles y videos.")
    print()

    # Verificar requisitos
    if not check_requirements():
        print("\n❌ Requisitos no cumplidos. Revisa los errores arriba.")
        return

    print("\n✅ Todos los requisitos verificados")

    # Menú de opciones
    print("\n📋 OPCIONES DISPONIBLES:")
    print("1. Generar demo completa (recomendado)")
    print("2. Solo probar componentes")
    print("3. Crear paquete de distribución")
    print("4. Ver estado actual")
    print()

    choice = input("Selecciona opción (1-4): ").strip()

    if choice == '1':
        print("\n🚀 GENERANDO DEMO COMPLETA...")
        if generate_complete_demo():
            create_demo_package()
            print("\n🎉 ¡DEMO COMPLETA GENERADA!")
            print("\n📁 Archivos creados:")
            print("   - Screenshots: ./demo_screenshots/")
            print("   - Carteles: ./demo_carteles/")
            print("   - Audio: ./demo_audio/")
            print("   - Videos: *.mp4")
            print("   - Paquete: ./demo_package/")
        else:
            print("\n❌ Error generando demo completa")

    elif choice == '2':
        print("\n🧪 EJECUTANDO PRUEBAS...")
        run_command('powershell -File test_demo.ps1', 'Ejecutando pruebas de componentes')

    elif choice == '3':
        print("\n📦 CREANDO PAQUETE...")
        if create_demo_package():
            print("\n✅ Paquete creado exitosamente")
        else:
            print("\n❌ Error creando paquete")

    elif choice == '4':
        print("\n📊 ESTADO ACTUAL:")
        print(f"   Screenshots: {len(os.listdir('./demo_screenshots')) if os.path.exists('./demo_screenshots') else 0}")
        print(f"   Carteles: {len(os.listdir('./demo_carteles')) if os.path.exists('./demo_carteles') else 0}")
        print(f"   Audio: {len(os.listdir('./demo_audio')) if os.path.exists('./demo_audio') else 0}")
        print(f"   Videos: {len([f for f in os.listdir('.') if f.endswith('.mp4')])}")

    else:
        print("❌ Opción no válida")

if __name__ == "__main__":
    main()
