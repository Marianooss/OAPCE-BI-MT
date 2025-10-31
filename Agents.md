# 🤖 agents.md  
**Agentes para la Evolución de OAPCE Multitrans a una Plataforma de BI Completo**

---

## 📋 Resumen Ejecutivo

Este documento detalla la arquitectura de agentes inteligentes para transformar OAPCE Multitrans de un dashboard operativo a una **plataforma de BI completa y autónoma**. Los agentes están organizados en 4 fases de evolución, priorizando valor de negocio y simplicidad técnica.

**Objetivos Clave:**
- **Automatización**: Reducir intervención manual en 80%
- **Predicción**: Alertas proactivas vs análisis retrospectivo
- **Empoderamiento**: Usuarios no técnicos crean sus propios reportes
- **Inteligencia**: Respuestas naturales a consultas complejas

**Beneficios Esperados:**
- ROI: 300% en eficiencia operativa
- Tiempo de respuesta: De días a minutos
- Precisión: +40% en predicciones de venta/cobranza

---

## 🧱 1. Agente: Data Pipeline Orchestrator (DPO)  
**Fase:** Fase 1 – Consolidación de Datos  
**Responsabilidad:** Extraer, transformar y cargar (ETL/ELT) datos desde el sistema operativo hacia el Data Warehouse.  
**Entradas:**  
- Tablas operativas: Clientes, Facturas, Cobranzas, Movimientos de Caja, Actividades  
- Reglas de transformación (limpieza, estandarización)  
**Salidas:**  
- Tablas de hechos y dimensiones en el DWH  
- Logs de ejecución y métricas de calidad de datos  
**Tecnologías Sugeridas:**  
- Apache Airflow / Prefect (orquestación)  
- dbt (transformación)  
- PostgreSQL / BigQuery / Snowflake (almacenamiento)  
**Frecuencia:** Diaria (incremental) + carga inicial completa  

**Implementación Técnica:**
- Integrar con `database.py` y `database_config.py` existentes
- Usar SQLAlchemy para extracción desde SQLite/PostgreSQL
- Agregar tabla `data_quality_logs` para métricas
- Programar con cron jobs o Airflow en producción

---

## 📚 2. Agente: Data Catalog Manager (DCM)  
**Fase:** Fase 1 – Consolidación de Datos  
**Responsabilidad:** Mantener un catálogo actualizado de todos los activos de datos del DWH.  
**Entradas:**  
- Esquemas del DWH  
- Metadatos de negocio (propietarios, definiciones, SLAs)  
**Salidas:**  
- Catálogo accesible vía UI o API  
- Etiquetas de sensibilidad y gobernanza  
**Tecnologías Sugeridas:**  
- Apache Atlas, DataHub, o Amundsen  
- Integración con herramientas de BI (Power BI, Metabase)  

**Implementación Técnica:**
- Crear módulo `catalog.py` con funciones para escanear esquemas
- Integrar con `models.py` para extraer metadatos automáticamente
- Agregar endpoint en Streamlit para visualización del catálogo
- Usar etiquetas en base de datos para clasificación de datos sensibles

---

## 🔮 3. Agente: Predictive Model Engine (PME)  
**Fase:** Fase 2 – Análisis Predictivo  
**Responsabilidad:** Predice ventas futuras y cierre del pipeline con 85% de precisión. La ejecución de la previsión del agente se muestra en esta pantalla y no se abre en una nueva sección de Agentes IA.  
**Beneficio:** Planificación precisa de metas y recursos de venta.  
**Casos de uso principales:**  
- Previsión de ingresos trimestrales  
- Predicción de ganancia vs pérdida de negocios  
- Ajuste de cuotas basado en tendencias  
**Modelos Soportados:**  
- Predicción de ventas (Prophet, SARIMA)  
- Riesgo de morosidad (XGBoost, Random Forest)  
- Probabilidad de cierre de oportunidades (Regresión logística, LightGBM)  
**Entradas:**  
- Datos históricos del DWH  
- Parámetros de configuración (horizonte de predicción, umbrales)  
**Salidas:**  
- Predicciones actualizadas diariamente  
- Métricas de desempeño del modelo (precisión, AUC, MAPE)  
**Tecnologías Sugeridas:**  
- Python (scikit-learn, Prophet, XGBoost)  
- MLflow (gestión de experimentos)  
- FastAPI o Flask (API de inferencia)  

**Implementación Técnica:**
- Crear módulo `predictive_models.py` con clases para cada modelo
- Integrar con `database.py` para acceso a datos históricos
- Agregar tabla `model_predictions` y `model_metrics` en base de datos
- Usar job scheduling para re-entrenamiento semanal
- Exponer API REST para inferencia en tiempo real

---

## 💡 4. Agente: Prescriptive Advisor (PA)  
**Fase:** Fase 2 – Análisis Prescriptivo  
**Responsabilidad:** Generar recomendaciones accionables basadas en predicciones y reglas de negocio. La ejecución de las recomendaciones del agente se muestra en esta pantalla y no se abre en una nueva sección de Agentes IA.  
**Entradas:**  
- Salidas del PME  
- Reglas de negocio (ej: "Si probabilidad < 60% y deuda > $5000 → priorizar")  
- Perfil del usuario (rol, territorio, metas)  
**Salidas:**  
- Recomendaciones contextualizadas (texto + acción sugerida)  
- Puntuación de impacto esperado  
**Integración:**  
- Inyecta alertas en el módulo "Alertas y Notificaciones" del frontend  
- Botones de acción rápida (API REST → sistema de tareas)  

**Implementación Técnica:**
- Crear módulo `prescriptive_advisor.py` con motor de reglas
- Integrar con `auth.py` para obtener perfil de usuario
- Agregar componente Streamlit `st.info` o `st.warning` para mostrar recomendaciones
- Usar base de datos para almacenar reglas configurables

---

## 🧩 5. Agente: Self-Service BI Facilitator (SSBF)  
**Fase:** Fase 3 – Empoderamiento del Usuario  
**Responsabilidad:** Habilitar la creación autónoma de reportes por parte de usuarios no técnicos. La ejecución de la creación y visualización de dashboards se muestra en esta pantalla y no se abre en una nueva sección de Agentes IA.  
**Funcionalidades:**  
- Interfaz drag & drop  
- Acceso a métricas predefinidas (desde la Biblioteca de Métricas)  
- Guardado y compartición de dashboards  
**Tecnologías Sugeridas:**  
- Metabase (open-source, fácil integración)  
- Power BI Embedded (si ya se usa Microsoft)  
- Superset (alternativa ligera)  
**Seguridad:**  
- Control de acceso basado en roles (RBAC)  
- Filtros dinámicos por usuario (ej: vendedores solo ven sus clientes)  

**Implementación Técnica:**
- Integrar Metabase o similar como iframe en Streamlit
- Crear módulo `bi_facilitator.py` para configuración de dashboards
- Usar roles de `models.py` para control de acceso
- Agregar tabla `user_dashboards` para guardar configuraciones personalizadas

---

## 📏 6. Agente: Metrics Definition Hub (MDH)  
**Fase:** Fase 3 – Empoderamiento del Usuario  
**Responsabilidad:** Centralizar y versionar definiciones de métricas clave.  
**Entradas:**  
- Fórmulas de negocio (ej: `Tasa de Conversión = Oportunidades Cerradas / Oportunidades Creadas`)  
- Dimensiones permitidas (tiempo, región, producto)  
**Salidas:**  
- API de métricas estandarizadas  
- Documentación visible en el SSBF  
**Formato:**  
- Archivos YAML o JSON (compatible con herramientas como dbt o Cube.js)  

**Implementación Técnica:**
- Crear directorio `metrics/` con archivos YAML para definiciones
- Agregar módulo `metrics_hub.py` para parsing y validación
- Integrar con `database.py` para queries dinámicas
- Exponer API REST para acceso desde BI tools

---

## 🧠 7. Agente: Generative Data Assistant (GDA)  
**Fase:** Fase 4 – Inteligencia Artificial  
**Responsabilidad:** Responder consultas en lenguaje natural sobre los datos.  
**Entradas:**  
- Preguntas del usuario (texto)  
- Contexto del usuario (rol, métricas relevantes)  
- Esquema del DWH  
**Salidas:**  
- Respuestas en texto natural  
- Gráficos o tablas generados automáticamente  
- Enlaces a dashboards relevantes  
**Tecnologías Sugeridas:**  
- LLM (Llama 3, Mistral, o GPT-4o) + RAG (Retrieval-Augmented Generation)  
- Conectores a DWH (vía SQL generativo seguro)  
- Validación de queries (sandbox para evitar accesos no autorizados)  

**Implementación Técnica:**
- Crear módulo `generative_assistant.py` con integración LLM
- Usar embeddings para búsqueda semántica en esquemas
- Implementar guardrails para seguridad (filtrar queries peligrosas)
- Integrar con `auth.py` para contexto de usuario

---

## 🚨 8. Agente: Anomaly Detector (AD)  
**Fase:** Fase 4 – Automatización  
**Responsabilidad:** Detectar comportamientos atípicos en métricas clave. La ejecución de la detección de anomalías y sus resultados se muestran en esta pantalla y no se abre en una nueva sección de Agentes IA.  
**Métodos:**  
- Isolation Forest  
- Prophet (para series temporales con tendencia/estacionalidad)  
- Z-score dinámico  
**Entradas:**  
- Series temporales de KPIs (ventas, cobranzas, gastos)  
- Umbrales de sensibilidad  
**Salidas:**  
- Alertas con explicación (ej: "Cobranzas caídas un 40% vs promedio semanal")  
- Recomendación inicial (ej: "Revisar clientes grandes en región Sur")  
**Integración:**  
- Envío a canal de alertas (email, Slack, o módulo interno)  
- Dashboard de anomalías en tiempo real
- Integración con sistema de tickets

**Implementación Técnica:**  
- Crear módulo `anomaly_detector.py` con los siguientes componentes:
  - Clase `AnomalyDetector` con métodos para diferentes algoritmos:
    - `detect_with_isolation_forest()`: Para detección de anomalías no supervisada
    - `detect_with_prophet()`: Para series temporales con patrones estacionales
    - `calculate_dynamic_zscore()`: Para detección de valores atípicos estadísticos
  - Funciones de utilidad:
    - `preprocess_timeseries()`: Preparación y limpieza de datos
    - `calculate_performance_metrics()`: Cálculo de precisión, recall, F1-score
    - `generate_anomaly_report()`: Generación de informe ejecutivo
- Integración con `database.py` para:
  - Carga de datos históricos
  - Almacenamiento de anomalías detectadas
  - Registro de métricas de rendimiento
- Configuración de umbrales dinámicos basados en percentiles históricos
- Implementación de sistema de retroalimentación para mejorar precisión
- Documentación detallada de cada método y parámetros configurables
- **Integración con Base de Datos**:
  - Crear tablas `anomaly_alerts` (id, timestamp, metric, value, expected_range, severity, status, assigned_to, notes)
  - Crear tablas `anomaly_metrics` (id, model_name, precision, recall, f1_score, training_date, test_date, parameters)
  - Implementar índices para búsquedas rápidas por fecha y severidad

- **Sistema de Notificaciones**:
  - Configuración de umbrales por tipo de alerta (crítico, advertencia, informativo)
  - Integración con canales de comunicación (Email, Slack, Teams)
  - Plantillas personalizables para mensajes de alerta
  - Sistema de confirmación de recepción

- **Automatización**:
  - Jobs programados con Celery para ejecución periódica
  - Detección en tiempo real mediante WebSockets
  - Reprocesamiento automático ante fallos
  - Limpieza automática de alertas antiguas

- **API REST**:
  - `GET /api/anomalies`: Consulta de anomalías con filtros
  - `POST /api/anomalies/{id}/acknowledge`: Confirmar recepción de alerta
  - `POST /api/anomalies/detect`: Detección bajo demanda
  - Documentación Swagger/OpenAPI

- **Monitoreo y Logging**:
  - Integración con sistema centralizado de logs
  - Métricas de rendimiento en tiempo real
  - Alertas de salud del sistema

---

## 🔄 9. Agente: Data Quality Guardian (DQG)  
**Fase:** Fase 4 – Automatización  
**Responsabilidad:** Monitorear y garantizar la calidad de los datos en todo momento.  

### 📊 Métricas de Calidad  
- **Completitud**: Porcentaje de valores no nulos en campos obligatorios  
- **Exactitud**: Grado en que los datos representan correctamente la realidad  
- **Consistencia**: Coherencia entre diferentes fuentes de datos  
- **Actualidad**: Frecuencia de actualización de los datos  
- **Validez**: Cumplimiento de formatos y reglas de negocio  
- **Unicidad**: Ausencia de duplicados no deseados  

### 🔍 Entradas  
- **Datos en bruto** de fuentes operacionales  
- **Metadatos** de esquemas y reglas de negocio  
- **Umbrales de aceptación** por tipo de métrica  
- **Reglas de limpieza** y estandarización  

### 📤 Salidas  
- **Reportes detallados** de calidad por conjunto de datos  
- **Alertas automáticas** para problemas críticos  
- **Puntuación global** de calidad (0-100)  
- **Recomendaciones** para mejorar la calidad  
- **Certificados** de calidad para conjuntos de datos validados  

### 🔄 Integración  
- **Dashboard interactivo** con métricas en tiempo real  
- **Sistema de tickets** para seguimiento de problemas  
- **API REST** para integración con otras herramientas  
- **Notificaciones** a equipos responsables  
- **Sistema de aprobación** para datos críticos  

### 🛠️ Implementación Técnica  

#### 1. Módulo Principal `data_quality.py`  
```python
class ValidadorCalidadDatos:
    def __init__(self, config_path='config/calidad.yaml'):
        self.cargar_configuracion(config_path)
        self.conexion_db = DatabaseConnection()
        self.metricas = {}
        
    def ejecutar_validaciones(self, dataset_id):
        """Ejecuta todas las validaciones configuradas para un conjunto de datos"""
        resultados = {}
        datos = self.obtener_datos(dataset_id)
        
        for regla in self.config['reglas']:
            if regla['activa']:
                resultado = self.aplicar_regla(regla, datos)
                resultados[regla['nombre']] = resultado
                
        return self.generar_reporte(resultados)
    
    def monitorear_continuo(self):
        """Monitoreo continuo de la calidad de datos"""
        while True:
            for dataset in self.config['datasets']:
                self.ejecutar_validaciones(dataset['id'])
            time.sleep(self.config['intervalo_monitoreo'])
```

#### 2. Estructura de Base de Datos  
```sql
-- Tabla de problemas de calidad
CREATE TABLE dq_issues (
    id SERIAL PRIMARY KEY,
    dataset_id VARCHAR(50) NOT NULL,
    tipo_problema VARCHAR(50) NOT NULL,
    severidad VARCHAR(20) CHECK (severidad IN ('baja', 'media', 'alta', 'critica')),
    descripcion TEXT,
    filas_afectadas INT,
    fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'abierto',
    asignado_a VARCHAR(100),
    fecha_resolucion TIMESTAMP,
    solucion TEXT
);

-- Tabla de métricas de calidad
CREATE TABLE dq_metrics (
    id SERIAL PRIMARY KEY,
    dataset_id VARCHAR(50) NOT NULL,
    metrica_id VARCHAR(50) NOT NULL,
    valor_actual DECIMAL(10,2),
    valor_anterior DECIMAL(10,2),
    tendencia VARCHAR(10),
    fecha_medicion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    umbral_alerta DECIMAL(10,2),
    en_alerta BOOLEAN DEFAULT FALSE
);
```

#### 3. Sistema de Reglas Configurables  
```yaml
# config/reglas_calidad.yaml
reglas:
  - id: completitud_campos_obligatorios
    nombre: "Validar campos obligatorios"
    descripcion: "Verifica que los campos marcados como obligatorios no sean nulos"
    tipo: "completitud"
    severidad: "alta"
    activa: true
    parametros:
      campos_obligatorios: ["id_cliente", "fecha_venta", "monto"]
      
  - id: rango_valores
    nombre: "Validar rangos aceptables"
    descripcion: "Verifica que los valores estén dentro de los rangos definidos"
    tipo: "rango"
    severidad: "media"
    activa: true
    parametros:
      campos:
        - nombre: "edad"
          min: 18
          max: 100
        - nombre: "monto_venta"
          min: 0
          max: 1000000
```

#### 4. Panel de Control Streamlit  
```python
# dashboard_control_calidad.py
import streamlit as st
from data_quality import ValidadorCalidadDatos

def main():
    st.set_page_config(page_title="Panel de Control de Calidad de Datos", layout="wide")
    st.title("🔍 Monitor de Calidad de Datos")
    
    # Inicializar validador
    validador = ValidadorCalidadDatos()
    
    # Sidebar con controles
    with st.sidebar:
        st.header("Opciones")
        dataset_seleccionado = st.selectbox("Seleccionar conjunto de datos", 
                                         ["ventas", "clientes", "productos"])
        
        if st.button("Ejecutar validaciones"):
            with st.spinner("Validando datos..."):
                reporte = validador.ejecutar_validaciones(dataset_seleccionado)
                st.session_state.ultimo_reporte = reporte
    
    # Mostrar métricas principales
    if 'ultimo_reporte' in st.session_state:
        reporte = st.session_state.ultimo_reporte
        
        # Resumen ejecutivo
        st.subheader("Resumen de Calidad")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Puntuación General", f"{reporte['puntuacion']}%")
        with col2:
            st.metric("Problemas Críticos", reporte['problemas_criticos'])
        with col3:
            st.metric("Datos Validados", f"{reporte['porcentaje_validado']}%")
        
        # Gráfico de tendencia
        st.subheader("Tendencia de Calidad")
        st.line_chart(reporte['tendencia_mensual'])
        
        # Tabla de problemas
        st.subheader("Problemas Detectados")
        st.dataframe(reporte['problemas'])

if __name__ == "__main__":
    main()
```

#### 5. API REST  
```python
# api_calidad.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from data_quality import ValidadorCalidadDatos

app = FastAPI(title="API de Calidad de Datos")
validador = ValidadorCalidadDatos()

class ProblemaCalidad(BaseModel):
    dataset_id: str
    tipo: str
    descripcion: str
    severidad: str
    filas_afectadas: int

@app.get("/api/calidad/datasets/{dataset_id}")
async def obtener_estado_calidad(dataset_id: str):
    """Obtiene el estado actual de calidad para un dataset"""
    try:
        return validador.obtener_estado(dataset_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/calidad/validar/{dataset_id}")
async def validar_dataset(dataset_id: str):
    """Ejecuta validaciones en un dataset específico"""
    try:
        return validador.ejecutar_validaciones(dataset_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calidad/problemas", response_model=List[ProblemaCalidad])
async def listar_problemas(severidad: Optional[str] = None):
    """Lista problemas de calidad con filtro opcional por severidad"""
    return validador.obtener_problemas(severidad=severidad)
```

#### 6. Plan de Implementación  
1. **Semanas 1-2**: Configuración inicial y desarrollo del núcleo  
   - Estructura base del módulo `data_quality.py`  
   - Implementación de validaciones básicas  
   - Configuración de la base de datos  

2. **Semanas 3-4**: Integración y automatización  
   - Integración con fuentes de datos existentes  
   - Configuración de jobs programados  
   - Desarrollo de API REST  

3. **Semanas 5-6**: Interfaz y monitoreo  
   - Desarrollo del panel de control Streamlit  
   - Configuración de alertas y notificaciones  
   - Documentación técnica y de usuario  

4. **Semanas 7-8**: Pruebas y ajustes  
   - Pruebas de carga y rendimiento  
   - Ajuste de umbrales y reglas  
   - Capacitación a usuarios finales  

### 📈 Métricas de Éxito  
- Reducción del 90% en problemas de calidad de datos críticos  
- Tiempo de detección de problemas reducido en un 80%  
- Puntuación media de calidad de datos por encima del 95%  
- Satisfacción del usuario con el sistema de monitoreo superior al 4.5/5

---

## 📤 10. Agente: Automated Reporting Dispatcher (ARD)  
**Fase:** Fase 4 – Automatización  
**Responsabilidad:** Generar y distribuir reportes programados.  
**Funcionalidades:**  
- Programación por usuario/rol/frecuencia  
- Formatos: PDF, Excel, enlace a dashboard  
- Personalización dinámica (ej: cada vendedor recibe su propio reporte)  
**Tecnologías Sugeridas:**  
- Power Automate / Zapier (si se usa Power BI)  
- Scripts personalizados con Puppeteer (PDF) + SMTP  
- Integración con SSBF para renderizado  

**Implementación Técnica:**
- Crear módulo `reporting_dispatcher.py` con scheduling
- Usar librerías como `reportlab` para PDF o `openpyxl` para Excel
- Integrar con `auth.py` para personalización por usuario
- Configurar cron jobs o Celery para ejecución automática

---

## 🔄 11. Agente: System Integrator (SI)  
**Fase:** Todas  
**Responsabilidad:** Garantizar la cohesión entre agentes y el sistema OAPCE Multitrans existente.  
**Funciones Clave:**  
- Mantener la identidad visual (tema oscuro, colores verde/azul)  
- Gestionar autenticación única (SSO)  
- Exponer APIs seguras entre módulos  
- Registrar eventos de uso para mejora continua  

**Implementación Técnica:**
- Actualizar `app.py` para incluir componentes de agentes
- Crear módulo `system_integrator.py` como orquestador central
- Agregar logging unificado en `utils.py`
- Mantener compatibilidad con estructura existente

---

## 📊 Roadmap de Implementación

### **Fase 1 (1-3 meses): Fundación**
1. Implementar DPO básico con dbt
2. Crear DCM simple con metadatos en DB
3. Desarrollar PME inicial para predicción de ventas
4. Implementar DQG para monitoreo de calidad básico

### **Fase 2 (2-4 meses): Inteligencia**
1. Agregar PA con reglas básicas
2. Integrar PME con más modelos
3. Desarrollar AD para KPIs críticos
4. Mejorar DQG con validaciones avanzadas

### **Fase 3 (3-6 meses): Empoderamiento**
1. Implementar SSBF con Metabase
2. Crear MDH con métricas versionadas
3. Agregar personalización por usuario

### **Fase 4 (6+ meses): Autonomía**
1. Desarrollar GDA con LLM
2. Automatizar ARD completo
3. Optimizar SI para escalabilidad

---

## 📈 Métricas de Éxito

- **Técnicas:** 99.9% uptime, <5min latencia en predicciones
- **Negocio:** +50% en ventas por alertas proactivas
- **Usuario:** 80% de reportes autogenerados
- **ROI:** Recuperación de inversión en <12 meses

---

## 🛠️ Dependencias Técnicas

- **Python 3.11+** para compatibilidad
- **PostgreSQL** para escalabilidad
- **Docker/Kubernetes** para despliegue
- **API Keys** para servicios externos (LLM, BI tools)

---

## 📌 Notas Finales

- **Todos los agentes deben ser monitorizados** (logs, métricas de rendimiento, errores).  
- **Priorizar la gobernanza de datos**: calidad, privacidad y cumplimiento (ej: GDPR si aplica).  
- **Fasear la implementación**: comenzar con DPO + PME + PA para generar valor rápido.  
- **Mantener el enfoque en el usuario no técnico**: simplicidad > complejidad técnica.
- **Integración no disruptiva**: Los agentes se agregan como módulos opcionales sin romper la funcionalidad existente.