from database import get_db
from models import Factura, Cliente
from datetime import datetime

db = get_db()

# Check for overdue invoices
overdue_invoices = db.query(Factura).filter(
    Factura.estado.in_(["Vencida", "Parcial"]),
    Factura.fecha_vencimiento < datetime.now().date()
).all()

print(f'Overdue invoices: {len(overdue_invoices)}')

for inv in overdue_invoices[:5]:  # Show first 5
    client = db.query(Cliente).filter(Cliente.id == inv.cliente_id).first()
    client_name = client.nombre if client else "Unknown"
    days_overdue = (datetime.now().date() - inv.fecha_vencimiento).days
    pendiente = inv.monto_total - inv.monto_pagado
    print(f'Invoice {inv.numero_factura}: {client_name}, ${pendiente:,.0f} overdue by {days_overdue} days')

# Check high-value clients
high_value_clients = db.query(Cliente).filter(Cliente.valor_estimado > 1000000).all()
print(f'\nHigh-value clients (>1M): {len(high_value_clients)}')

for client in high_value_clients[:5]:
    print(f'{client.nombre}: ${client.valor_estimado:,.0f}')

db.close()
