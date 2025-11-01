import streamlit as st
import os
import pandas as pd
from contextlib import contextmanager

def get_db_connection():
    db_url = None
    # Check if running in Streamlit Cloud and secrets are configured
    if hasattr(st, 'secrets') and "DATABASE_URL" in st.secrets:
        db_url = st.secrets["DATABASE_URL"]
    else:
        # Fallback to local environment variable for local development
        db_url = os.environ.get('DATABASE_URL')

    if not db_url:
        st.error("La URL de la base de datos no está configurada. Por favor, configúrala en los secretos de Streamlit o como una variable de entorno local.")
        st.stop()

    # Detect database type and use appropriate driver
    if db_url.startswith('sqlite://'):
        import sqlite3
        # Extract path from sqlite:// URL
        db_path = db_url.replace('sqlite:///', '')
        return sqlite3.connect(db_path)
    elif db_url.startswith('postgresql://'):
        import psycopg2
        return psycopg2.connect(db_url)
    else:
        st.error(f"Tipo de base de datos no soportado en URL: {db_url}")
        st.stop()

def is_sqlite_url(url):
    """Check if URL is for SQLite database"""
    return url.startswith('sqlite:')

# Get database URL from environment or use default SQLite
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///oapce_multitrans.db')

@contextmanager
def get_connection():
    """Context manager for database connections"""
    if is_sqlite_url(DB_URL):
        # Strip sqlite:/// prefix to get file path
        db_path = DB_URL.replace('sqlite:///', '')
        import sqlite3
        conn = sqlite3.connect(db_path)
        try:
            yield conn
        finally:
            conn.close()
    else:
        # Assume PostgreSQL connection
        import psycopg2
        conn = psycopg2.connect(DB_URL)
        try:
            yield conn
        finally:
            conn.close()

def execute_query(query, params=None):
    """Execute SQL query and return results as pandas DataFrame"""
    with get_connection() as conn:
        # SQLite driver needs special handling for datetime
        if is_sqlite_url(DB_URL):
            import sqlite3
            conn.row_factory = sqlite3.Row
        try:
            if params:
                df = pd.read_sql_query(query, conn, params=params)
            else:
                df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            print(f"Database error: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error

def execute_write_query(query, params=None):
    """Execute INSERT/UPDATE/DELETE query"""
    with get_connection() as conn:
        try:
            cur = conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False

def execute_update(query, params=None):
    """Alias for execute_write_query for backward compatibility"""
    return execute_write_query(query, params)

def init_db():
    """Initialize database with required tables"""
    tables = [
        """
        CREATE TABLE IF NOT EXISTS dataset_catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            propietario TEXT,
            ultima_actualizacion TIMESTAMP,
            etiqueta TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS quality_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_date DATE NOT NULL,
            quality_score FLOAT NOT NULL,
            metric_type TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS anomalies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_date TIMESTAMP NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Abierta'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS scheduled_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            activo BOOLEAN DEFAULT true,
            ultima_ejecucion TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ventas_diarias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE NOT NULL,
            monto DECIMAL(10,2) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS model_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            prediction_date TIMESTAMP NOT NULL,
            target_date TIMESTAMP NOT NULL,
            metric_name TEXT NOT NULL,
            predicted_value FLOAT NOT NULL,
            confidence_score FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS model_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value FLOAT NOT NULL,
            evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS data_quality_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_name TEXT NOT NULL,
            issue_type TEXT NOT NULL,
            severity TEXT CHECK (severity IN ('baja', 'media', 'alta', 'critica')),
            description TEXT NOT NULL,
            affected_rows INTEGER,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'abierto',
            assigned_to TEXT,
            resolved_at TIMESTAMP,
            resolution TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS agent_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]

    with get_connection() as conn:
        cur = conn.cursor()
        for table in tables:
            # Modify table creation for PostgreSQL if needed
            if not is_sqlite_url(DB_URL):
                table = table.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
            try:
                cur.execute(table)
            except Exception as e:
                st.error(f"Error creating table: {e}")
                print(f"Error creating table: {e}")
        conn.commit()

def log_agent_event(agent_name, event_type, message, status="info"):
    """Log agent events to database"""
    query = """
    INSERT INTO agent_logs (agent_name, event_type, message, status)
    VALUES (?, ?, ?, ?)
    """
    params = (agent_name, event_type, message, status)
    return execute_write_query(query, params)

def get_agent_logs(agent_name=None, limit=100):
    """Retrieve agent logs with optional filtering"""
    query = """
    SELECT * FROM agent_logs
    WHERE agent_name = COALESCE(?, agent_name)
    ORDER BY created_at DESC
    LIMIT ?
    """
    params = (agent_name, limit)
    return execute_query(query, params)
