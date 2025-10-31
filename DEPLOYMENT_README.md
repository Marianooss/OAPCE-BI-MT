# 🚀 OAPCE BI MT - Guía de Deployment y Setup

## 📋 Información del Proyecto

**Sistema:** OAPCE BI Multitrans v1.0
**Arquitectura:** 7 Agentes Inteligentes + UI Streamlit
**Estado:** ✅ PRODUCCIÓN LISTO

---

## 🛠️ DEPENDENCIAS TÉCNICAS

### Requerimientos del Sistema

| Componente | Versión Mínima | Recomendada | Crítico |
|------------|----------------|-------------|---------|
| **Python** | 3.8 | 3.9+ | ✅ |
| **SQLite** | 3.35+ | 3.35+ | ✅ |
| **RAM** | 4GB | 8GB+ | ⚠️ |
| **Disco** | 1GB | 2GB+ | |
| **OS** | Windows/Mac/Linux | Windows 11/MacOS | ✅ |

### Librerías Python (pyproject.toml)

```toml
[project]
name = "oapce-bi-mt"
version = "1.0.0"
description = "Sistema BI Multitrans con 7 Agentes Inteligentes"
requires-python = ">=3.8"

dependencies = [
    "streamlit>=1.28.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "sqlalchemy>=2.0.0",
    "python-dotenv>=1.0.0",
    "scikit-learn>=1.3.0",
    "requests>=2.31.0",
    "plotly>=5.15.0",
    "python-dateutil>=2.8.0",
    "urllib3>=2.0.0"
]
```

### Instalación Automática

1. **Clonar repositorio**
   ```bash
   git clone [repositorio]
   cd oapce-bi-mt
   ```

2. **Instalar con uv** (recomendado)
   ```bash
   pip install uv
   uv pip install -e .
   ```

3. **O instalar manualmente**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🗄️ CONFIGURACIÓN DE BASE DE DATOS

### Estructura de Datos
- **17 tablas** principales
- **170 columnas** catalogadas
- **7 agentes** con esquemas específicos

### Inicialización Automática
```bash
# Ejecutar una sola vez después de instalación
python init_db.py
python create_ssbf_tables.py
```

### Archivos de Configuración
- `.env` - Variables de entorno
- `database_config.py` - Configuración BD
- `oapce_multitrans.db` - Base de datos SQLite

---

## 🚀 EJECUCIÓN DEL SISTEMA

### Modo Desarrollo
```bash
# Opción 1: Streamlit directo
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Opción 2: Script batch
./run.bat  # Windows
./run.sh   # Linux/Mac

# Opción 3: Python directo
python -m streamlit run app.py
```

### Modo Producción

#### Opción A: Streamlit Cloud
1. Subir código a GitHub
2. Conectar con Streamlit Cloud
3. Configurar secrets en dashboard
4. Deploy automático

#### Opción B: VPS/Docker
```docker
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

#### Opción C: Azure/Google Cloud
- Configurar App Service/Cloud Run
- Database externa (PostgreSQL/MySQL)
- Variables de entorno seguras

### Verificación de Funcionamiento
```bash
# Ejecutar suite de pruebas integrada
python test_integrated.py

# Verificar métricas específicas
python test_pme.py
python test_pa.py
python test_ad.py
python test_dqg.py
```

---

## 🔧 CONFIGURACIÓN AVANZADA

### Variables de Entorno (.env)
```env
# Base de datos
DATABASE_URL=sqlite:///oapce_multitrans.db

# Metabase (opcional)
METABASE_URL=http://localhost:3000
METABASE_USER=admin
METABASE_PASS=metabase123

# Auth (para futuras versiones)
JWT_SECRET=tu_clave_secreta_aqui
```

### Optimizaciones de Rendimiento

#### Base de Datos
```python
# En production usar PostgreSQL
DATABASE_URL = "postgresql://user:pass@localhost:5432/oapce_bi"
```

#### Cache (Futuras versiones)
```python
# Redis para cache inteligente
REDIS_URL = "redis://localhost:6379"
CACHE_TTL = 3600  # 1 hora
```

---

## 📊 MONITOREO Y MANTENIMIENTO

### Health Checks
```bash
# Ejecutar diariamente/semanalmente
python test_integrated.py > health_check.log
```

### Backups
```bash
# Base de datos
cp oapce_multitrans.db backup_$(date +%Y%m%d).db

# Código y configuración
tar -czf backup_code_$(date +%Y%m%d).tar.gz .
```

### Logs y Alertas
- Archivos de log: `logs/` directory
- Unified Logger: `unified_logger.py`
- Alertas: Sistema integrado con agentes de monitoreo

---

## 🏗️ ARQUITECTURA TÉCNICA

### Módulos Principales
```
oapce-bi-mt/
├── app.py                 # UI Principal Streamlit
├── agents_ui.py           # Interfaces de agentes
├── database.py           # Configuración BD
├── models.py             # Modelos SQLAlchemy
├── agents/               # 7 Agentes IA
│   ├── catalog.py        # DCM
│   ├── data_pipeline.py  # DPO
│   ├── predictive_models.py # PME
│   ├── prescriptive_advisor.py # PA
│   ├── data_quality.py   # DQG
│   ├── anomaly_detector.py # AD
│   └── ssbf_facilitator.py # SSBF
├── tests/                # Suite de pruebas
└── docs/                 # Documentación
```

### Flujo de Datos
1. **Entrada** → UI Streamlit
2. **Procesamiento** → Agentes IA especializados
3. **Almacenamiento** → SQLite/PostgreSQL
4. **Salida** → Dashboards y reportes

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### Problemas Comunes

**Error: "Tabla X no existe"**
```bash
# Re-inicializar base de datos
rm oapce_multitrans.db
python init_db.py
python create_ssbf_tables.py
```

**Error: "Modulo Y no encontrado"**
```bash
# Re-instalar dependencias
pip install -r requirements.txt --force-reinstall
```

**Error: "Puerto 8501 ocupado"**
```bash
# Cambiar puerto
streamlit run app.py --server.port 8502
```

### Soporte y Contacto

**Para soporte técnico:**
- Crear issue en GitHub
- Revisar logs en `logs/` folder
- Ejecutar `python test_integrated.py` y compartir output

---

## 📈 RUTA DE MEJORAS (ROADMAP)

### Fase 2: Expansión (Próximos 3-6 meses)
- [ ] Integración Metabase completa
- [ ] Sistema de alertas inteligente
- [ ] Chatbot de IA conversacional
- [ ] BD distribuida (PostgreSQL)
- [ ] Autenticación avanzada JWT

### Fase 3: Escalabilidad (6-12 meses)
- [ ] Procesamiento distribuido
- [ ] Machine Learning avanzado
- [ ] APIs RESTful
- [ ] Microservicios

---

**✅ SISTEMA LISTO PARA DEPLOYMENT EN PRODUCCIÓN**
