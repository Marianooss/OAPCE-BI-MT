# Script para crear video demo
# Ejecutar con: python create_video.py

import moviepy.editor as mp
from moviepy.audio.io.AudioArrayClip import AudioArrayClip
import numpy as np

# Datos de la demo
demo_steps = [{'step': 1, 'description': 'Pantalla de login del sistema', 'cartel_text': '¡Bienvenidos al Sistema OAPCE Multitrans! Dashboard de control y gestión empresarial.', 'screenshot': './demo_screenshots/20251030_235313_step_01_navigate.png', 'cartel_image': './demo_carteles/20251030_235315_step_01_cartel.png', 'audio': './demo_audio/20251030_235315_step_01.mp3', 'duration': 5}, {'step': 7, 'description': 'Cierre de sesión', 'cartel_text': 'Sistema seguro con control de acceso por roles. ¡Gracias por ver la demo!', 'screenshot': './demo_screenshots/20251030_235429_step_07_logout.png', 'cartel_image': './demo_carteles/20251030_235429_step_07_cartel.png', 'audio': './demo_audio/20251030_235429_step_07.mp3', 'duration': 2}]

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
