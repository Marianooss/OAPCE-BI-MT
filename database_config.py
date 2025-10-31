import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Configuración para diferentes tipos de bases de datos
DATABASE_CONFIGS = {
    'sqlite': {
        'url': 'sqlite:///oapce_multitrans.db',
        'description': 'Base de datos local SQLite (actual)'
    },
    'postgresql': {
        'url': 'postgresql://usuario:password@localhost:5432/oapce_db',
        'description': 'PostgreSQL (recomendado para producción)'
    },
    'mysql': {
        'url': 'mysql://usuario:password@localhost:3306/oapce_db',
        'description': 'MySQL/MariaDB'
    },
    'sqlserver': {
        'url': 'mssql+pyodbc://usuario:password@server/oapce_db?driver=ODBC+Driver+17+for+SQL+Server',
        'description': 'SQL Server'
    }
}

# Configuración actual
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///oapce_multitrans.db')

# Para producción, usar variables de entorno
# DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@host:port/dbname')

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        print(f"Error de conexión a base de datos: {e}")
        db.close()
        raise

def init_db():
    """Inicializar tablas en la base de datos"""
    from models import (
        Usuario, Cliente, Vendedor, Factura,
        Cobranza, MovimientoCaja, ActividadVenta
    )
    Base.metadata.create_all(bind=engine)
    print("✓ Tablas creadas exitosamente")

def test_connection():
    """Probar conexión a la base de datos"""
    try:
        db = get_db()
        db.execute("SELECT 1")
        db.close()
        return True, "Conexión exitosa"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"

if __name__ == "__main__":
    print("🔍 Probando conexión a base de datos...")
    success, message = test_connection()
    print(f"{'✅' if success else '❌'} {message}")
    print(f"📊 Base de datos: {DATABASE_URL}")
