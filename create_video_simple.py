import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont
import subprocess

def create_simple_video():
    """Crear video simple usando FFmpeg"""

    print("CREANDO VIDEO SIMPLE CON FFMPEG")
    print("=" * 40)

    try:
        df = pd.read_excel('demo_summary.xlsx')
        print(f"[OK] Datos cargados: {len(df)} pasos")
    except FileNotFoundError:
        print("[ERROR] No se encontro demo_summary.xlsx")
        return

    # Crear lista de comandos FFmpeg
    ffmpeg_commands = []

    for i, row in df.iterrows():
        step_num = int(row['step'])
        screenshot_path = row['screenshot']
        audio_path = row['audio']
        duration = float(row['duration'])

        if screenshot_path and audio_path and os.path.exists(screenshot_path) and os.path.exists(audio_path):
            # Crear imagen con cartel superpuesto
            combined_image = create_combined_image(screenshot_path, row['cartel_text'], f"temp_step_{step_num}.png")

            if combined_image:
                # Comando FFmpeg para este paso
                output_video = f"temp_step_{step_num}.mp4"
                cmd = f'ffmpeg -loop 1 -i {combined_image} -i {audio_path} -c:v libx264 -t {duration} -pix_fmt yuv420p -vf scale=1920:1080 {output_video}'

                print(f"[FFMPEG] Procesando paso {step_num}...")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"[OK] Video paso {step_num} creado")
                    ffmpeg_commands.append(output_video)
                else:
                    print(f"[ERROR] Error en paso {step_num}: {result.stderr}")

    if ffmpeg_commands:
        # Concatenar todos los videos
        print("[INFO] Concatenando videos...")

        # Crear lista de archivos para concatenar
        with open('video_list.txt', 'w') as f:
            for video in ffmpeg_commands:
                f.write(f"file '{video}'\n")

        # Comando para concatenar
        concat_cmd = 'ffmpeg -f concat -safe 0 -i video_list.txt -c copy demo_oapce_multitrans.mp4'

        result = subprocess.run(concat_cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print("[OK] Video final creado exitosamente!")
            print("[INFO] Archivo: demo_oapce_multitrans.mp4")

            # Limpiar archivos temporales
            for video in ffmpeg_commands:
                os.remove(video)
                os.remove(video.replace('.mp4', '.png'))
            os.remove('video_list.txt')

            print("[OK] Archivos temporales limpiados")

        else:
            print(f"[ERROR] Error concatenando videos: {result.stderr}")

    else:
        print("[ERROR] No se pudieron crear videos individuales")

def create_combined_image(screenshot_path, cartel_text, output_path):
    """Crear imagen combinada con screenshot y cartel"""

    try:
        # Cargar screenshot
        screenshot = Image.open(screenshot_path)

        # Crear cartel
        cartel_width, cartel_height = 800, 120
        cartel = Image.new('RGBA', (cartel_width, cartel_height), (0, 0, 0, 180))
        draw = ImageDraw.Draw(cartel)

        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        # Texto centrado
        lines = wrap_text(cartel_text, font, cartel_width - 20)
        y = (cartel_height - len(lines) * 25) // 2

        for line in lines:
            text_width = draw.textlength(line, font=font)
            x = (cartel_width - text_width) // 2
            draw.text((x, y), line, font=font, fill='white')
            y += 25

        # Crear imagen final (screenshot + cartel abajo)
        final_width = max(screenshot.width, cartel_width)
        final_height = screenshot.height + cartel_height

        final_img = Image.new('RGB', (final_width, final_height), (255, 255, 255))
        final_img.paste(screenshot, (0, 0))
        final_img.paste(cartel, ((final_width - cartel_width) // 2, screenshot.height), cartel)

        final_img.save(output_path)
        print(f"[OK] Imagen combinada: {output_path}")
        return output_path

    except Exception as e:
        print(f"[ERROR] Error creando imagen combinada: {e}")
        return None

def wrap_text(text, font, max_width):
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

def main():
    """Función principal"""
    print("VIDEO SIMPLE - OAPCE MULTITRANS")
    print("=" * 40)

    # Verificar que tenemos los archivos necesarios
    required_files = ['demo_summary.xlsx']
    missing_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"[ERROR] Archivos faltantes: {missing_files}")
        print("[INFO] Ejecuta primero: python demo_generator.py")
        return

    # Verificar FFmpeg
    try:
        result = subprocess.run('ffmpeg -version', shell=True, capture_output=True)
        if result.returncode == 0:
            print("[OK] FFmpeg disponible")
        else:
            print("[ERROR] FFmpeg no disponible")
            print("[INFO] Instala: choco install ffmpeg")
            return
    except:
        print("[ERROR] FFmpeg no encontrado")
        return

    # Crear video
    create_simple_video()

if __name__ == "__main__":
    main()
