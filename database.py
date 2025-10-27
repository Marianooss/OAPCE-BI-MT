from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///oapce_multitrans.db")

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
    from models import Usuario, Cliente, Vendedor, Factura, Cobranza, MovimientoCaja, ActividadVenta
    Base.metadata.create_all(bind=engine)
