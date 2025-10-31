# -*- coding: utf-8 -*-
import moviepy.editor as mp
import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_video_demo():
    """Crear video demo completo"""

    print("[VIDEO] CREANDO VIDEO DEMO COMPLETO")
    print("=" * 40)

    # Cargar datos de la demo
    try:
        df = pd.read_excel('demo_summary.xlsx')
        print(f"[OK] Datos cargados: {len(df)} pasos")
    except FileNotFoundError:
        print("[ERROR] No se encontro demo_summary.xlsx")
        print("[INFO] Ejecuta primero: python demo_generator.py")
        return

    clips = []

    for i, row in df.iterrows():
        step_num = int(row['step'])
        description = row['description']
        cartel_text = row['cartel_text']
        duration = float(row['duration'])

        print(f"[VIDEO] Procesando paso {step_num}: {description}")

        # Cargar screenshot si existe
        screenshot_path = row['screenshot']
        if screenshot_path and os.path.exists(screenshot_path):
            # Crear clip de imagen
            img_clip = mp.ImageClip(screenshot_path)

            # Crear cartel overlay si existe
            cartel_path = row['cartel_image']
            if cartel_path and os.path.exists(cartel_path):
                # Cargar cartel
                cartel = mp.ImageClip(cartel_path)

                # Posicionar cartel en la parte inferior
                cartel = cartel.set_position(('center', 'bottom')).set_start(0.5)

                # Composicion: imagen + cartel
                img_clip = mp.CompositeVideoClip([img_clip, cartel])

            # Cargar audio si existe
            audio_path = row['audio']
            if audio_path and os.path.exists(audio_path):
                audio_clip = mp.AudioFileClip(audio_path)
                img_clip = img_clip.set_audio(audio_clip)
            else:
                # Crear silencio si no hay audio
                img_clip = img_clip.set_audio(mp.AudioArrayClip(np.zeros((int(44100 * duration), 2)), fps=44100))

            # Configurar duracion
            img_clip = img_clip.set_duration(duration)

            clips.append(img_clip)
            print(f"[OK] Clip {step_num} creado")
        else:
            print(f"[WARNING] Screenshot no encontrado: {screenshot_path}")

    if not clips:
        print("[ERROR] No se encontraron clips para crear el video")
        return

    print(f"[INFO] {len(clips)} clips listos para concatenar")

    # Concatenar todos los clips
    print("[INFO] Concatenando clips...")
    final_video = mp.concatenate_videoclips(clips, method='compose')

    # Configurar metadatos del video
    final_video = final_video.set_fps(24)

    # Exportar video
    output_filename = 'demo_oapce_multitrans.mp4'

    print(f"[VIDEO] Exportando video: {output_filename}")
    print("[INFO] Esto puede tomar unos minutos...")

    try:
        final_video.write_videofile(
            output_filename,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp_audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None
        )

        print("[VIDEO] DEMO CREADO EXITOSAMENTE!")
        print(f"[INFO] Archivo: {output_filename}")
        print(f"[INFO] Duracion aproximada: {len(clips) * 3} segundos")
        print(f"[INFO] {len(clips)} pasos demostrados")

        # Mostrar informacion del video
        video_info = final_video.duration
        print(f"[INFO] Duracion final: {video_info:.1f} segundos")

    except Exception as e:
        print(f"[ERROR] Error creando video: {e}")
        print("[INFO] Posibles soluciones:")
        print("   - Instala ffmpeg: choco install ffmpeg (Windows)")
        print("   - Verifica que todos los archivos existan")
        print("   - Cierra otros programas que usen video")

    finally:
        final_video.close()

def create_presentation_version():
    """Crear version de presentacion con transiciones suaves"""

    print("[PRESENTATION] CREANDO VERSION DE PRESENTACION")
    print("=" * 40)

    try:
        df = pd.read_excel('demo_summary.xlsx')
    except FileNotFoundError:
        print("[ERROR] No se encontro demo_summary.xlsx")
        return

    clips = []

    for i, row in df.iterrows():
        step_num = int(row['step'])
        description = row['description']
        duration = float(row['duration'])

        print(f"[STEP] Procesando paso {step_num}")

        # Cargar screenshot
        screenshot_path = row['screenshot']
        if screenshot_path and os.path.exists(screenshot_path):
            # Crear clip de imagen
            img_clip = mp.ImageClip(screenshot_path)

            # Crear cartel con texto
            cartel_text = row['cartel_text']
            cartel = create_text_overlay(cartel_text, duration)

            # Composicion
            composition = mp.CompositeVideoClip([img_clip, cartel])
            composition = composition.set_duration(duration)

            # Agregar fade in/out
            composition = composition.fadein(0.5).fadeout(0.5)

            # Cargar audio
            audio_path = row['audio']
            if audio_path and os.path.exists(audio_path):
                audio_clip = mp.AudioFileClip(audio_path)
                composition = composition.set_audio(audio_clip)

            clips.append(composition)
            print(f"[OK] Clip {step_num} con efectos creado")

    if clips:
        # Concatenar con transiciones
        print("[INFO] Aplicando transiciones...")
        final_video = mp.concatenate_videoclips(clips, method='compose')

        # Exportar version de presentacion
        output_filename = 'demo_presentacion.mp4'

        print(f"[VIDEO] Exportando version de presentacion...")
        final_video.write_videofile(
            output_filename,
            fps=24,
            codec='libx264',
            audio_codec='aac'
        )

        print(f"[PRESENTATION] CREADA!")
        print(f"[INFO] Archivo: {output_filename}")

def create_text_overlay(text, duration):
    """Crear overlay de texto elegante"""

    # Crear imagen de texto
    width, height = 800, 150
    text_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_img)

    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()

    # Texto centrado
    lines = wrap_text(text, font, width - 40)
    y = (height - len(lines) * 35) // 2

    for line in lines:
        text_width = draw.textlength(line, font=font)
        x = (width - text_width) // 2
        draw.text((x, y), line, font=font, fill='white')
        y += 35

    # Convertir a clip
    text_clip = mp.ImageClip(np.array(text_img))
    text_clip = text_clip.set_position(('center', 'bottom')).set_start(0.5)
    text_clip = text_clip.set_duration(duration)

    return text_clip

def wrap_text(text, font, max_width):
    """Dividir texto en lineas"""
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

def create_instagram_story():
    """Crear version para Instagram Stories (vertical)"""

    print("[STORIES] CREANDO VERSION INSTAGRAM STORIES")
    print("=" * 40)

    try:
        df = pd.read_excel('demo_summary.xlsx')
    except FileNotFoundError:
        print("[ERROR] No se encontro demo_summary.xlsx")
        return

    # Crear version vertical (1080x1920)
    story_clips = []

    for i, row in df.iterrows():
        step_num = int(row['step'])

        # Cargar screenshot y convertir a vertical
        screenshot_path = row['screenshot']
        if screenshot_path and os.path.exists(screenshot_path):
            # Cargar y recortar para formato vertical
            img = Image.open(screenshot_path)

            # Crear fondo negro vertical
            story_img = Image.new('RGB', (1080, 1920), (0, 0, 0))
            draw = ImageDraw.Draw(story_img)

            # Pegar screenshot en el centro superior
            img_resized = img.resize((1080, 608))  # 1080x608 para 9:16
            story_img.paste(img_resized, (0, 200))

            # Agregar titulo
            try:
                title_font = ImageFont.truetype("arial.ttf", 40)
            except:
                title_font = ImageFont.load_default()

            title = f"Paso {step_num}"
            title_width = draw.textlength(title, font=title_font)
            draw.text(((1080 - title_width) // 2, 50), title, font=title_font, fill='white')

            # Agregar texto del cartel
            cartel_text = row['cartel_text']
            lines = wrap_text(cartel_text, ImageFont.load_default(), 1000)
            y = 900
            for line in lines[:3]:  # Maximo 3 lineas
                text_width = draw.textlength(line, font=ImageFont.load_default())
                draw.text(((1080 - text_width) // 2, y), line, font=ImageFont.load_default(), fill='white')
                y += 40

            # Guardar imagen de story
            story_path = f"./demo_screenshots/story_step_{step_num:02d}.png"
            story_img.save(story_path)

            # Crear clip de video
            story_clip = mp.ImageClip(story_path)
            story_clip = story_clip.set_duration(5)  # 5 segundos por story

            story_clips.append(story_clip)
            print(f"[OK] Story {step_num} creado")

    if story_clips:
        # Concatenar stories
        final_story = mp.concatenate_videoclips(story_clips, method='compose')

        # Exportar
        output_filename = 'demo_instagram_stories.mp4'
        final_story.write_videofile(output_filename, fps=24)

        print(f"[STORIES] CREADOS!")
        print(f"[INFO] Archivo: {output_filename}")
        print(f"[INFO] {len(story_clips)} stories generados")

def main():
    """Funcion principal"""
    print("[VIDEO] CREADOR DE VIDEOS DEMO - OAPCE MULTITRANS")
    print("=" * 50)
    print("Opciones disponibles:")
    print("1. Video demo completo (horizontal)")
    print("2. Version de presentacion (con efectos)")
    print("3. Instagram Stories (vertical)")
    print()

    choice = input("Selecciona opcion (1-3): ").strip()

    if choice == '1':
        create_video_demo()
    elif choice == '2':
        create_presentation_version()
    elif choice == '3':
        create_instagram_story()
    else:
        print("[ERROR] Opcion no valida")

if __name__ == "__main__":
    main()
