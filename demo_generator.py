import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from datetime import datetime

class AppDemoGenerator:
    """Genera demostración automática de la aplicación OAPCE Multitrans"""

    def __init__(self):
        self.screenshots_dir = "./demo_screenshots"
        self.audio_dir = "./demo_audio"
        self.carteles_dir = "./demo_carteles"

        # Crear directorios
        for dir_path in [self.screenshots_dir, self.audio_dir, self.carteles_dir]:
            os.makedirs(dir_path, exist_ok=True)

        # Configuración del navegador
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')  # Sin interfaz gráfica
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')

        # Script de demostración
        self.demo_script = [
            {
                'action': 'navigate',
                'url': 'http://localhost:5001',
                'wait': 5,
                'description': 'Pantalla de login del sistema',
                'cartel': '¡Bienvenidos al Sistema OAPCE Multitrans! Dashboard de control y gestión empresarial.'
            },
            {
                'action': 'login',
                'email': 'admin@grupoom.com',
                'password': 'admin123',
                'wait': 3,
                'description': 'Login con credenciales de administrador',
                'cartel': 'Iniciamos sesión como administrador para mostrar todas las funcionalidades.'
            },
            {
                'action': 'navigate_tab',
                'tab': 'Dirección General',
                'wait': 4,
                'description': 'Dashboard ejecutivo con KPIs principales',
                'cartel': 'Dashboard Ejecutivo: KPIs en tiempo real, análisis financiero y tendencias de negocio.'
            },
            {
                'action': 'navigate_tab',
                'tab': 'Comercial',
                'wait': 4,
                'description': 'Dashboard comercial con ventas y clientes',
                'cartel': 'Módulo Comercial: Seguimiento de ventas, pipeline de clientes y métricas de vendedores.'
            },
            {
                'action': 'navigate_tab',
                'tab': 'Finanzas',
                'wait': 4,
                'description': 'Dashboard financiero con facturación y cobranzas',
                'cartel': 'Módulo Financiero: Control de facturación, cobranzas y flujo de caja.'
            },
            {
                'action': 'navigate_tab',
                'tab': 'Gestión de Datos',
                'wait': 4,
                'description': 'Formularios de gestión de datos',
                'cartel': 'Gestión de Datos: Formularios para clientes, facturas, cobranzas y actividades.'
            },
            {
                'action': 'logout',
                'wait': 2,
                'description': 'Cierre de sesión',
                'cartel': 'Sistema seguro con control de acceso por roles. ¡Gracias por ver la demo!'
            }
        ]

    def setup_driver(self):
        """Configurar driver de Selenium"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)

            # Configurar espera implícita
            driver.implicitly_wait(10)
            return driver

        except Exception as e:
            print(f"[ERROR] Error configurando driver: {e}")
            return None

    def take_screenshot(self, driver, step_name):
        """Tomar captura de pantalla"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.screenshots_dir}/{timestamp}_{step_name}.png"

        try:
            # Tomar screenshot completo
            driver.save_screenshot(filename)

            # Recortar y optimizar imagen
            self.optimize_screenshot(filename)

            print(f"[OK] Screenshot guardado: {filename}")
            return filename

        except Exception as e:
            print(f"[ERROR] Error tomando screenshot: {e}")
            return None

    def optimize_screenshot(self, image_path):
        """Optimizar imagen para demo"""
        try:
            img = Image.open(image_path)

            # Convertir a RGB si es necesario
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Redimensionar si es muy grande
            max_size = (1920, 1080)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.LANCZOS)

            img.save(image_path, 'PNG', optimize=True)
            print(f"[OK] Imagen optimizada: {image_path}")

        except Exception as e:
            print(f"[WARNING] Error optimizando imagen: {e}")

    def create_cartel(self, text, step_name):
        """Crear cartel informativo"""
        try:
            # Crear imagen de cartel
            width, height = 800, 200
            cartel = Image.new('RGBA', (width, height), (0, 0, 0, 180))  # Fondo negro semi-transparente

            # Agregar texto
            draw = ImageDraw.Draw(cartel)

            try:
                # Intentar usar fuente del sistema
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                # Usar fuente por defecto
                font = ImageFont.load_default()

            # Dividir texto en líneas si es muy largo
            lines = self.wrap_text(text, font, width - 40)

            # Dibujar texto centrado
            y = (height - len(lines) * 30) // 2
            for line in lines:
                text_width = draw.textlength(line, font=font)
                x = (width - text_width) // 2
                draw.text((x, y), line, font=font, fill='white')
                y += 30

            # Guardar cartel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cartel_filename = f"{self.carteles_dir}/{timestamp}_{step_name}_cartel.png"
            cartel.save(cartel_filename, 'PNG')

            print(f"Cartel creado: {cartel_filename}")
            return cartel_filename

        except Exception as e:
            print(f"Error creando cartel: {e}")
            return None

    def wrap_text(self, text, font, max_width):
        """Dividir texto en líneas"""
        words = text.split(' ')
        lines = []
        current_line = ''

        for word in words:
            test_line = current_line + ' ' + word if current_line else word
            if font.getlength(test_line) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def generate_audio_narration(self, text, step_name):
        """Generar audio con narración"""
        try:
            from gtts import gTTS

            # Crear archivo de audio
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"{self.audio_dir}/{timestamp}_{step_name}.mp3"

            # Generar audio con Google Text-to-Speech
            tts = gTTS(text=text, lang='es', slow=False)
            tts.save(audio_filename)

            print(f"[OK] Audio generado: {audio_filename}")
            return audio_filename

        except Exception as e:
            print(f"[ERROR] Error generando audio: {e}")
            return None

    def execute_demo_step(self, driver, step):
        """Ejecutar un paso de la demostración"""
        try:
            action = step['action']
            wait_time = step.get('wait', 3)

            print(f"[DEMO] Ejecutando: {step['description']}")

            if action == 'navigate':
                driver.get(step['url'])
                time.sleep(wait_time)

            elif action == 'login':
                # Esperar que cargue la página de login
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'input'))
                )

                # Encontrar campos de email y password
                email_field = driver.find_element(By.XPATH, "//input[@placeholder='usuario@grupoom.com' or @placeholder='Email']")
                password_field = driver.find_element(By.XPATH, "//input[@placeholder='Ingrese su contraseña' or @placeholder='Password']")

                # Ingresar credenciales
                email_field.clear()
                email_field.send_keys(step['email'])
                password_field.clear()
                password_field.send_keys(step['password'])

                # Hacer clic en login
                login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Ingresar') or contains(text(), 'Login')]")
                login_button.click()

                time.sleep(wait_time)

            elif action == 'navigate_tab':
                # Esperar que cargue el sidebar
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'sidebar'))
                )

                # Encontrar y hacer clic en la pestaña
                tab_xpath = f"//div[contains(@class, 'radio')]//label[contains(text(), '{step['tab']}')]"
                tab_element = driver.find_element(By.XPATH, tab_xpath)
                tab_element.click()

                time.sleep(wait_time)

            elif action == 'logout':
                # Buscar botón de logout
                try:
                    logout_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Cerrar') or contains(text(), 'Logout')]")
                    logout_button.click()
                    time.sleep(wait_time)
                except:
                    print("[WARNING] Boton de logout no encontrado")

            return True

        except Exception as e:
            print(f"[ERROR] Error ejecutando paso {step['description']}: {e}")
            return False

    def generate_demo(self):
        """Generar demostración completa"""
        print("[DEMO] INICIANDO GENERACION DE DEMO AUTOMATICA")
        print("=" * 50)

        driver = self.setup_driver()
        if not driver:
            print("[ERROR] No se pudo configurar el navegador")
            return

        try:
            demo_data = []

            for i, step in enumerate(self.demo_script, 1):
                print(f"\n[STEP] Paso {i}/{len(self.demo_script)}: {step['description']}")

                # Ejecutar acción
                success = self.execute_demo_step(driver, step)

                if success:
                    # Tomar screenshot
                    screenshot = self.take_screenshot(driver, f"step_{i:02d}_{step['action']}")

                    # Crear cartel
                    cartel = self.create_cartel(step['cartel'], f"step_{i:02d}")

                    # Generar audio
                    audio = self.generate_audio_narration(step['cartel'], f"step_{i:02d}")

                    # Registrar datos del paso
                    demo_data.append({
                        'step': i,
                        'description': step['description'],
                        'cartel_text': step['cartel'],
                        'screenshot': screenshot,
                        'cartel_image': cartel,
                        'audio': audio,
                        'duration': step.get('wait', 3)
                    })

                    print(f"[OK] Paso {i} completado")
                else:
                    print(f"[ERROR] Paso {i} fallo")

                # Pausa entre pasos
                time.sleep(1)

            # Crear resumen de la demo
            self.create_demo_summary(demo_data)

            print(f"\n[DEMO] DEMO GENERADA EXITOSAMENTE!")
            print(f"[INFO] Screenshots: {len([d for d in demo_data if d['screenshot']])} capturas")
            print(f"[INFO] Carteles: {len([d for d in demo_data if d['cartel_image']])} carteles")
            print(f"[INFO] Audio: {len([d for d in demo_data if d['audio']])} narraciones")
            print(f"\n[INFO] Archivos generados en:")
            print(f"   - Screenshots: {self.screenshots_dir}")
            print(f"   - Carteles: {self.carteles_dir}")
            print(f"   - Audio: {self.audio_dir}")
            print(f"\n[INFO] Resumen: demo_summary.xlsx")

        except Exception as e:
            print(f"[ERROR] Error generando demo: {e}")

        finally:
            driver.quit()

    def create_demo_summary(self, demo_data):
        """Crear resumen de la demostración"""
        try:
            df = pd.DataFrame(demo_data)
            summary_file = "demo_summary.xlsx"
            df.to_excel(summary_file, index=False)

            # Crear script de video
            self.create_video_script(demo_data)

            print(f"[OK] Resumen creado: {summary_file}")

        except Exception as e:
            print(f"[ERROR] Error creando resumen: {e}")

    def create_video_script(self, demo_data):
        """Crear script para edición de video"""
        script_content = f"""# Script para crear video demo
# Ejecutar con: python create_video.py

import moviepy.editor as mp
from moviepy.audio.io.AudioArrayClip import AudioArrayClip
import numpy as np

# Datos de la demo
demo_steps = {demo_data}

def create_demo_video():
    clips = []

    for step in demo_steps:
        if step['screenshot'] and step['audio']:
            # Cargar imagen
            img_clip = mp.ImageClip(step['screenshot'])

            # Cargar audio
            audio_clip = mp.AudioFileClip(step['audio'])

            # Crear clip con imagen y audio
            video_clip = img_clip.set_duration(step['duration'])
            video_clip = video_clip.set_audio(audio_clip)

            clips.append(video_clip)

    # Concatenar todos los clips
    final_video = mp.concatenate_videoclips(clips, method='compose')

    # Exportar video
    final_video.write_videofile(
        'demo_oapce_multitrans.mp4',
        fps=24,
        codec='libx264',
        audio_codec='aac'
    )

if __name__ == "__main__":
    create_demo_video()
"""

        with open('create_video.py', 'w') as f:
            f.write(script_content)

        print("[OK] Script de video creado: create_video.py")

def main():
    """Función principal"""
    print("[DEMO] GENERADOR DE DEMO AUTOMATICA - OAPCE MULTITRANS")
    print("=" * 60)
    print("Este script crea una demostración automática de la aplicación")
    print("incluyendo screenshots, carteles informativos y narración.")
    print()

    # Verificar que el servidor esté corriendo
    import requests
    try:
        response = requests.get('http://localhost:5001', timeout=5)
        if response.status_code == 200:
            print("[OK] Servidor de la aplicación detectado")
        else:
            print("[ERROR] Servidor no responde correctamente")
            return
    except:
        print("[ERROR] No se puede conectar al servidor. Inicia la aplicación primero:")
        print("   streamlit run app.py --server.port 5001")
        return

    # Generar demo
    demo_gen = AppDemoGenerator()
    demo_gen.generate_demo()

if __name__ == "__main__":
    main()
