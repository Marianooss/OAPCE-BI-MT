import os
import psycopg2
import pandas as pd
from contextlib import contextmanager

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

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
