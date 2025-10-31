from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class RolEnum(enum.Enum):
    admin = "admin"
    operador = "operador"
    cliente = "cliente"

class EstadoFacturaEnum(enum.Enum):
    pendiente = "Pendiente"
    pagada = "Pagada"
    vencida = "Vencida"
    parcial = "Parcial"

class EstadoFunnelEnum(enum.Enum):
    prospecto = "Prospecto"
    contactado = "Contactado"
    calificado = "Calificado"
    propuesta = "Propuesta"
    negociacion = "Negociación"
    ganado = "Ganado"
    perdido = "Perdido"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(RolEnum), default=RolEnum.operador)
    created_at = Column(DateTime, default=datetime.utcnow)

    dashboards = relationship("UserDashboard", back_populates="user")
    dashboard_permissions = relationship("DashboardPermission", foreign_keys="[DashboardPermission.user_id]")
    granted_permissions = relationship("DashboardPermission", foreign_keys="[DashboardPermission.granted_by]")

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    rut = Column(String(20), unique=True, nullable=False)
    email = Column(String(100))
    telefono = Column(String(20))
    direccion = Column(Text)
    vendedor_id = Column(Integer, ForeignKey("vendedores.id"))
    estado_funnel = Column(Enum(EstadoFunnelEnum), default=EstadoFunnelEnum.prospecto)
    valor_estimado = Column(Float, default=0.0)
    fecha_ingreso = Column(Date, default=datetime.utcnow)
    
    vendedor = relationship("Vendedor", back_populates="clientes")
    facturas = relationship("Factura", back_populates="cliente")

class Vendedor(Base):
    __tablename__ = "vendedores"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(20))
    meta_mensual = Column(Float, default=0.0)
    comision_porcentaje = Column(Float, default=0.0)
    activo = Column(Integer, default=1)
    
    clientes = relationship("Cliente", back_populates="vendedor")
    actividades = relationship("ActividadVenta", back_populates="vendedor")

class Factura(Base):
    __tablename__ = "facturas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_factura = Column(String(50), unique=True, nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    fecha_emision = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    monto_total = Column(Float, nullable=False)
    monto_pagado = Column(Float, default=0.0)
    estado = Column(Enum(EstadoFacturaEnum), default=EstadoFacturaEnum.pendiente)
    descripcion = Column(Text)
    
    cliente = relationship("Cliente", back_populates="facturas")
    cobranzas = relationship("Cobranza", back_populates="factura")

class Cobranza(Base):
    __tablename__ = "cobranzas"
    
    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("facturas.id"))
    fecha_pago = Column(Date, nullable=False)
    monto = Column(Float, nullable=False)
    metodo_pago = Column(String(50))
    numero_documento = Column(String(50))
    observaciones = Column(Text)
    
    factura = relationship("Factura", back_populates="cobranzas")

class MovimientoCaja(Base):
    __tablename__ = "movimientos_caja"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    tipo = Column(String(20), nullable=False)
    concepto = Column(String(200), nullable=False)
    monto = Column(Float, nullable=False)
    categoria = Column(String(100))
    observaciones = Column(Text)
    numero_documento = Column(String(50))

class ActividadVenta(Base):
    __tablename__ = "actividades_venta"
    
    id = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(Integer, ForeignKey("vendedores.id"))
    fecha = Column(Date, nullable=False)
    tipo_actividad = Column(String(50), nullable=False)
    cliente_nombre = Column(String(200))
    resultado = Column(Text)
    monto_estimado = Column(Float, default=0.0)
    
    vendedor = relationship("Vendedor", back_populates="actividades")

# Agente DPO: Tabla para logs de calidad de datos
class DataQualityLog(Base):
    __tablename__ = "data_quality_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    operation = Column(String(50), nullable=False)  # 'extract', 'transform', 'load', 'validate'
    records_processed = Column(Integer, default=0)
    records_successful = Column(Integer, default=0)
    errors_found = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)  # Porcentaje 0-100
    execution_time_seconds = Column(Float, default=0.0)
    details = Column(Text)  # JSON con detalles específicos
    status = Column(String(20), default="completed")  # 'completed', 'failed', 'running'

# Agente DCM: Tabla para catálogo de datos
class CatalogMetadata(Base):
    __tablename__ = "catalog_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    column_name = Column(String(100), nullable=False)
    data_type = Column(String(50), nullable=False)
    is_nullable = Column(Integer, default=1)  # 0=False, 1=True
    is_primary_key = Column(Integer, default=0)
    is_foreign_key = Column(Integer, default=0)
    foreign_table = Column(String(100))
    description = Column(Text)
    sensitivity_level = Column(String(20), default="public")  # public, internal, confidential, restricted
    business_owner = Column(String(100))
    technical_owner = Column(String(100))
    last_updated = Column(DateTime, default=datetime.utcnow)
    row_count = Column(Integer, default=0)
    tags = Column(Text)  # JSON array de tags

# Agente PME: Tabla para predicciones de modelos
class ModelPrediction(Base):
    __tablename__ = "model_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    prediction_type = Column(String(50), nullable=False)  # 'sales_forecast', 'risk_assessment', 'conversion_probability'
    target_date = Column(Date, nullable=False, index=True)
    predicted_value = Column(Float, nullable=False)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    actual_value = Column(Float)  # Para comparar después
    accuracy_score = Column(Float)  # Precisión de la predicción
    created_at = Column(DateTime, default=datetime.utcnow)
    input_features = Column(Text)  # JSON con features usados
    
    # Relaciones
    entity_id = Column(Integer)  # ID del cliente, vendedor, etc.
    entity_type = Column(String(50))  # 'cliente', 'vendedor', 'producto'

# Agente PME: Tabla para métricas de modelos
class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    metric_date = Column(Date, nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # 'accuracy', 'precision', 'recall', 'auc', 'mape'
    metric_value = Column(Float, nullable=False)
    dataset_size = Column(Integer)
    training_time_seconds = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    additional_info = Column(Text)  # JSON con detalles adicionales

# Agente AD: Tabla para alertas de anomalías
class AnomalyAlert(Base):
    __tablename__ = "anomaly_alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    expected_range_min = Column(Float)
    expected_range_max = Column(Float)
    severity = Column(String(20), default="medium")  # 'low', 'medium', 'high', 'critical'
    status = Column(String(20), default="open")  # 'open', 'acknowledged', 'resolved', 'false_positive'
    assigned_to = Column(String(100))
    detection_method = Column(String(50))  # 'isolation_forest', 'prophet', 'zscore'
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Agente AD: Tabla para métricas de modelos de anomalías
class AnomalyMetric(Base):
    __tablename__ = "anomaly_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    training_date = Column(Date, nullable=False, index=True)
    test_date = Column(Date)
    parameters = Column(Text)  # JSON con parámetros del modelo
    dataset_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

# Agente SSBF: Tabla para métricas predefinidas
class PredefinedMetric(Base):
    __tablename__ = "predefined_metrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # 'ventas', 'cobranza', 'finanzas', 'operaciones'
    formula = Column(Text, nullable=False)  # SQL o expresión para cálculo
    parameters = Column(Text)  # JSON con parámetros necesarios
    data_type = Column(String(20), default='number')  # 'number', 'percentage', 'currency'
    unit = Column(String(20))  # '$', '%' , etc.
    is_active = Column(Integer, default=1)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Agente SSBF: Tabla para dashboards de usuarios
class UserDashboard(Base):
    __tablename__ = "user_dashboards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    is_public = Column(Integer, default=0)  # 0=privado, 1=compartido en equipo, 2=público
    dashboard_type = Column(String(20), default='metabase')  # 'metabase', 'powerbi', 'streamlit'
    config = Column(Text)  # JSON con configuración del dashboard
    metabase_dashboard_id = Column(String(50))  # ID del dashboard en Metabase
    thumbnail_url = Column(String(500))  # URL de preview/imagen del dashboard
    tags = Column(Text)  # JSON array de tags
    view_count = Column(Integer, default=0)
    last_viewed = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Usuario", back_populates="dashboards")

# Agente SSBF: Tabla para permisos de acceso a dashboards
class DashboardPermission(Base):
    __tablename__ = "dashboard_permissions"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("user_dashboards.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    team_id = Column(String(50))  # Para permisos por equipo
    permission_level = Column(String(20), default='view')  # 'view', 'edit', 'admin'
    granted_by = Column(Integer, ForeignKey("usuarios.id"))
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

# Agente SSBF: Tabla para plantillas de dashboards
class DashboardTemplate(Base):
    __tablename__ = "dashboard_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # 'ventas', 'finanzas', 'operaciones'
    thumbnail_url = Column(String(500))
    config = Column(Text)  # JSON con configuración de plantilla
    use_count = Column(Integer, default=0)
    is_public = Column(Integer, default=1)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
