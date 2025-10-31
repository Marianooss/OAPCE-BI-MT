from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "sqlite:///oapce_multitrans.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        return db
    except:
        db.close()
        raise

def init_db():
    from models import (Usuario, Cliente, Vendedor, Factura, Cobranza, MovimientoCaja, ActividadVenta,
                       DataQualityLog, CatalogMetadata, ModelPrediction, ModelMetric,
                       AnomalyAlert, AnomalyMetric, PredefinedMetric, UserDashboard,
                       DashboardPermission, DashboardTemplate)
    Base.metadata.create_all(bind=engine)

def init_db_real_data():
    """
    Inicializa la base de datos para datos de producción (real_data flag)
    Esta función se ejecuta después de migrar de demo a producción
    """
    # Crear índices para mejor rendimiento con datos reales
    try:
        with engine.connect() as conn:
            # Crear índices para tablas principales
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_clientes_estado_funnel ON clientes (estado_funnel);
                CREATE INDEX IF NOT EXISTS idx_clientes_fecha_ingreso ON clientes (fecha_ingreso);
                CREATE INDEX IF NOT EXISTS idx_facturas_cliente_id ON facturas (cliente_id);
                CREATE INDEX IF NOT EXISTS idx_facturas_fecha_emision ON facturas (fecha_emision);
                CREATE INDEX IF NOT EXISTS idx_facturas_estado ON facturas (estado);
                CREATE INDEX IF NOT EXISTS idx_actividades_cliente ON actividades_venta (cliente_id);
                CREATE INDEX IF NOT EXISTS idx_actividades_fecha ON actividades_venta (fecha);
                CREATE INDEX IF NOT EXISTS idx_model_predictions_type ON model_predictions (prediction_type);
                CREATE INDEX IF NOT EXISTS idx_anomalies_metric ON anomaly_alerts (metric_name);
                CREATE INDEX IF NOT EXISTS idx_anomalies_status ON anomaly_alerts (status);
            """)

            # Crear vista para métricas consolidadas (útil para production)
            conn.execute("""
                CREATE VIEW IF NOT EXISTS vw_kpi_consolidated AS
                SELECT
                    'total_clients' as metric_name,
                    COUNT(*) as value,
                    'count' as unit,
                    datetime('now') as calculated_at
                FROM clientes
                UNION ALL
                SELECT
                    'total_invoices' as metric_name,
                    COUNT(*) as value,
                    'count' as unit,
                    datetime('now') as calculated_at
                FROM facturas
                UNION ALL
                SELECT
                    'paid_invoices' as metric_name,
                    COUNT(*) as value,
                    'count' as unit,
                    datetime('now') as calculated_at
                FROM facturas
                WHERE estado = 'Pagada'
                UNION ALL
                SELECT
                    'total_revenue' as metric_name,
                    COALESCE(SUM(monto_pagado), 0) as value,
                    'currency' as unit,
                    datetime('now') as calculated_at
                FROM facturas
                WHERE estado = 'Pagada';
            """)

            conn.commit()

    except Exception as e:
        print(f"Error inicializando índices para producción: {e}")
        # No fallar completamente si hay error en índices

    print("✅ Base de datos inicializada para datos de producción")
