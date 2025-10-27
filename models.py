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
