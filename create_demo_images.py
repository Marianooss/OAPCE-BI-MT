import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont

def create_demo_images():
    """Crear imágenes de demo con screenshots y carteles combinados"""

    print("CREANDO IMAGENES DE DEMO COMBINADAS")
    print("=" * 40)

    try:
        df = pd.read_excel('demo_summary.xlsx')
        print(f"[OK] Datos cargados: {len(df)} pasos")
    except FileNotFoundError:
        print("[ERROR] No se encontro demo_summary.xlsx")
        print("[INFO] Ejecuta primero: python demo_generator.py")
        return

    output_dir = "demo_images_final"
    os.makedirs(output_dir, exist_ok=True)

    created_images = []

    for i, row in df.iterrows():
        step_num = int(row['step'])
        screenshot_path = row['screenshot']
        cartel_text = row['cartel_text']

        print(f"[IMAGE] Procesando paso {step_num}")

        if screenshot_path and os.path.exists(screenshot_path):
            # Crear imagen combinada
            combined_path = create_combined_image(screenshot_path, cartel_text, f"{output_dir}/demo_step_{step_num:02d}.png")

            if combined_path:
                created_images.append(combined_path)
                print(f"[OK] Imagen creada: {combined_path}")
            else:
                print(f"[ERROR] Error creando imagen paso {step_num}")
        else:
            print(f"[WARNING] Screenshot no encontrado: {screenshot_path}")

    if created_images:
        print(f"\n[OK] {len(created_images)} imagenes de demo creadas!")
        print(f"[INFO] Archivos guardados en: {output_dir}")
        print(f"\n[FILES] Imagenes generadas:")
        for img in created_images:
            size = os.path.getsize(img) / 1024  # KB
            print(f"   {os.path.basename(img)} ({size:.1f} KB)")

        # Crear HTML de presentacion
        create_html_presentation(created_images, df, output_dir)

        print(f"\n[HTML] Presentacion HTML creada: {output_dir}/demo_presentation.html")
        print(f"\n[READY] Demo visual lista para presentar!")
        print(f"[TIP] Abre demo_presentation.html en tu navegador")

    else:
        print("[ERROR] No se pudieron crear imagenes")

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

def create_html_presentation(images, df, output_dir="demo_images_final"):
    """Crear presentacion HTML"""

    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Demo OAPCE Multitrans</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .slide {
            display: none;
            text-align: center;
            background: white;
            padding: 40px;
            margin: 20px auto;
            max-width: 1200px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .slide.active {
            display: block;
        }
        img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .controls {
            text-align: center;
            margin: 20px;
        }
        button {
            padding: 10px 20px;
            margin: 0 10px;
            font-size: 16px;
            cursor: pointer;
        }
        .slide-info {
            margin-top: 20px;
            padding: 15px;
            background: #e8f4f8;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1 style="text-align: center; color: #333;">DEMO OAPCE MULTITRANS</h1>
    <p style="text-align: center; color: #666;">Presentacion automatica generada</p>

    <div id="slideContainer">
"""

    for i, (img_path, (_, row)) in enumerate(zip(images, df.iterrows())):
        step_num = int(row['step'])
        description = row['description']
        cartel_text = row['cartel_text']

        html_content += f"""
        <div class="slide {'active' if i == 0 else ''}" id="slide{i}">
            <h2>Paso {step_num}: {description}</h2>
            <img src="{img_path}" alt="Paso {step_num}">
            <div class="slide-info">
                <strong>Descripcion:</strong> {cartel_text}
            </div>
        </div>
"""

    html_content += """
    </div>

    <div class="controls">
        <button onclick="prevSlide()">Anterior</button>
        <button onclick="nextSlide()">Siguiente</button>
        <button onclick="autoPlay()">Reproduccion Automatica</button>
    </div>

    <script>
        let currentSlide = 0;
        const totalSlides = """ + str(len(images)) + """;

        function showSlide(n) {
            const slides = document.querySelectorAll('.slide');
            slides.forEach(slide => slide.classList.remove('active'));

            if (n >= totalSlides) currentSlide = 0;
            if (n < 0) currentSlide = totalSlides - 1;

            slides[currentSlide].classList.add('active');
        }

        function nextSlide() {
            currentSlide++;
            showSlide(currentSlide);
        }

        function prevSlide() {
            currentSlide--;
            showSlide(currentSlide);
        }

        function autoPlay() {
            setInterval(() => {
                currentSlide++;
                showSlide(currentSlide);
            }, 5000); // 5 segundos por slide
        }

        // Navegacion con teclado
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') nextSlide();
            if (e.key === 'ArrowLeft') prevSlide();
        });
    </script>
</body>
</html>
"""

    with open(f"{output_dir}/demo_presentation.html", 'w') as f:
        f.write(html_content)

    print(f"[HTML] Presentacion HTML creada: {output_dir}/demo_presentation.html")

def main():
    """Función principal"""
    print("DEMO VISUAL - OAPCE MULTITRANS")
    print("=" * 40)
    print("Creando presentacion visual con imagenes combinadas")
    print()

    create_demo_images()

if __name__ == "__main__":
    main()
