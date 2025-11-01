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

@contextmanager
def get_connection():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def execute_query(query, params=None):
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)

def execute_update(query, params=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
