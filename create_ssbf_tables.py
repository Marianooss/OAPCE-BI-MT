#!/usr/bin/env python3
"""
Script para crear las nuevas tablas de SSBF (Self-Service BI Facilitator)
"""

from database import init_db

def create_ssbf_tables():
    """Crear tablas de SSBF"""
    print("Creando tablas de SSBF...")
    init_db()  # Esto debería crear todas las tablas incluyendo las nuevas de SSBF
    print("✅ Tablas de SSBF creadas/actualizadas")

if __name__ == "__main__":
    create_ssbf_tables()
