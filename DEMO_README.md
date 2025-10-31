# 🎬 GENERADOR DE DEMO AUTOMÁTICA - OAPCE MULTITRANS

¡Impresiona a los dueños con un video demo profesional que se genera automáticamente!

## 🎯 QUÉ HACE ESTE SISTEMA

✅ **Explora automáticamente** tu aplicación OAPCE Multitrans
✅ **Toma screenshots** de cada funcionalidad
✅ **Crea carteles informativos** con texto explicativo
✅ **Genera narración automática** con voz en español
✅ **Produce videos profesionales** listos para presentar
✅ **Optimiza para redes sociales** (Instagram Stories)

## 🚀 USO RÁPIDO

### **Opción 1: Todo Automático (Recomendado)**
```bash
# Windows PowerShell
powershell -File demo_master.ps1 -Action full

# Linux/Mac
python demo_master.py
```

### **Opción 2: Paso a Paso**
```bash
# 1. Generar screenshots y carteles
python demo_generator.py

# 2. Crear videos
python create_video.py

# 3. Crear paquete de distribución
python demo_master.py  # opción 3
```

## 📋 QUÉ SE DEMUESTRA AUTOMÁTICAMENTE

### **Flujo de la Demo:**
1. **🏠 Pantalla de Login** - Sistema seguro
2. **👑 Dashboard Ejecutivo** - KPIs y métricas principales
3. **📊 Módulo Comercial** - Ventas y clientes
4. **💰 Módulo Financiero** - Facturación y cobranzas
5. **📝 Gestión de Datos** - Formularios y administración
6. **🚪 Logout** - Cierre de sesión seguro

### **Narración Automática:**
- 🎙️ **Texto a voz** en español con Google TTS
- 📝 **Carteles explicativos** en cada paso
- ⏱️ **Tiempo optimizado** (3-5 segundos por paso)
- 🎵 **Audio profesional** con entonación natural

## 📁 ARCHIVOS GENERADOS

### **Videos Finales:**
- `demo_oapce_multitrans.mp4` - Video principal (horizontal)
- `demo_presentacion.mp4` - Versión con efectos (reuniones)
- `demo_instagram_stories.mp4` - Formato vertical (redes sociales)

### **Componentes:**
- `./demo_screenshots/` - Capturas de pantalla de cada paso
- `./demo_carteles/` - Imágenes de carteles informativos
- `./demo_audio/` - Archivos de narración de audio
- `demo_summary.xlsx` - Resumen completo de la demo

## ⚙️ REQUISITOS

### **Dependencias de Python:**
```bash
pip install selenium webdriver-manager pillow pandas moviepy opencv-python gtts
```

### **Herramientas del Sistema:**
```bash
# Windows
choco install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### **Servidor de la App:**
```bash
streamlit run app.py --server.port 5001 --server.address localhost
```

## 🎬 VERSIONES DE VIDEO

### **1. Video Principal** (`demo_oapce_multitrans.mp4`)
- **Formato:** Horizontal (16:9)
- **Duración:** ~30-45 segundos
- **Uso:** Presentaciones, email, sitio web
- **Calidad:** HD 1080p

### **2. Versión Presentación** (`demo_presentacion.mp4`)
- **Efectos:** Transiciones suaves, fade in/out
- **Duración:** ~45-60 segundos
- **Uso:** Reuniones ejecutivas, webinars
- **Estilo:** Profesional con efectos visuales

### **3. Instagram Stories** (`demo_instagram_stories.mp4`)
- **Formato:** Vertical (9:16)
- **Duración:** 15 segundos por story
- **Uso:** Redes sociales, LinkedIn Stories
- **Optimización:** Texto grande, visual impactante

## 🛠️ PERSONALIZACIÓN

### **Modificar Script de Demo:**
Edita `demo_generator.py` para cambiar:
```python
# Personalizar pasos de la demo
demo_script = [
    {
        'action': 'navigate',
        'url': 'http://localhost:5001',
        'wait': 5,
        'description': 'Pantalla principal',
        'cartel': '¡Tu texto personalizado aquí!'
    },
    # Agregar más pasos...
]
```

### **Cambiar Narración:**
```python
# En demo_generator.py, línea ~50
'cartel': 'Tu mensaje personalizado para los dueños aquí.'
```

### **Ajustar Tiempos:**
```python
'wait': 3,  # segundos que espera en cada paso
'duration': 3  # duración del audio narración
```

## 📱 OPTIMIZACIÓN PARA PRESENTACIONES

### **Para Dueños y Ejecutivos:**
1. **Usa la versión con efectos** (más profesional)
2. **Agrega tu logo** en los carteles
3. **Personaliza los textos** con nombres reales
4. **Incluye métricas específicas** de tu empresa

### **Para Redes Sociales:**
1. **Usa Instagram Stories** (vertical)
2. **Textos cortos y impactantes**
3. **Colores de marca** en carteles
4. **Música de fondo** opcional

## 🔧 SOLUCIÓN DE PROBLEMAS

### **Error: "Chrome driver not found"**
```bash
pip install webdriver-manager
```

### **Error: "MoviePy no puede crear video"**
```bash
# Instala ffmpeg
choco install ffmpeg  # Windows
sudo apt install ffmpeg  # Linux
brew install ffmpeg  # macOS
```

### **Error: "Servidor no disponible"**
```bash
# Inicia la aplicación primero
streamlit run app.py --server.port 5001 --server.address localhost
```

### **Audio no se genera**
```bash
# Verifica conexión a internet (usa Google TTS)
# O usa texto en lugar de audio
```

## 🎯 EJEMPLOS DE USO

### **Para Presentar a Dueños:**
```bash
# Generar demo profesional
python demo_master.py  # opción 1

# Resultado: Video con efectos y narración
# Perfecto para mostrar en reuniones
```

### **Para Marketing Digital:**
```bash
# Generar versión redes sociales
python create_video.py  # opción 3

# Resultado: Stories verticales
# Ideal para LinkedIn, Instagram
```

### **Para Documentación:**
```bash
# Solo generar screenshots
python demo_generator.py

# Resultado: Imágenes para manuales
# Perfecto para documentación técnica
```

## 📊 MÉTRICAS DE LA DEMO

### **Tiempo de Generación:**
- **Screenshots:** ~2 minutos
- **Carteles:** ~1 minuto
- **Audio:** ~3 minutos
- **Video:** ~5-10 minutos
- **Total:** ~15-20 minutos

### **Calidad de Salida:**
- **Resolución:** 1920x1080 HD
- **Frame Rate:** 24 FPS
- **Audio:** 44.1kHz, MP3
- **Formato:** MP4 H.264

## 🚀 PRÓXIMOS PASOS

1. **Ejecuta** la demo automática
2. **Revisa** los archivos generados
3. **Personaliza** textos y narración
4. **Comparte** con dueños y clientes

## 💡 TIPS PARA DUEÑOS

✅ **"Muestra datos reales"** - Conecta con Onvio primero
✅ **"Enfócate en beneficios"** - No en características técnicas
✅ **"Manténlo corto"** - 30-60 segundos máximo
✅ **"Agrega tu branding"** - Logo y colores de empresa
✅ **"Incluye llamada a acción"** - "Contáctanos para implementación"

---

**🎬 ¡Impresiona a los dueños con una demo profesional automática!**

**¿Listo para generar tu video demo?** 🚀
