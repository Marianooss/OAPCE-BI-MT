import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import timedelta

# --- 1. CONFIGURACIÓN ---

# Inicialización de Faker para datos en español
fake = Faker('es_ES')

# Parámetros de la Base de Datos
NUM_CLIENTES = 5000
NUM_PRODUCTOS = 50
NUM_VENDEDORES = 20
FECHA_INICIO = pd.to_datetime('2021-01-01')
FECHA_FIN = pd.to_datetime('2025-10-31')
NUM_REGISTROS_VENTAS = 150000

# Tendencia y Estacionalidad
TASA_CRECIMIENTO_ANUAL = 0.05  # +5% de crecimiento anual
ESTACIONALIDAD_DIC = 1.30      # 30% más en Diciembre
ESTACIONALIDAD_ENE = 0.85      # 15% menos en Enero
PROB_COBRANZA_A_TIEMPO = 0.90  # 90% de las facturas se cobran (Relación PA)

# --- 2. FUNCIONES DE APOYO PARA INYECCIÓN DE COMPLEJIDAD ---

def generar_factor_tiempo(date):
    """Aplica tendencias y estacionalidad al volumen de ventas."""
    # Tendencia de crecimiento lineal con el tiempo
    years_since_start = (date - FECHA_INICIO).days / 365.25
    trend_factor = (1 + TASA_CRECIMIENTO_ANUAL) ** years_since_start

    # Estacionalidad
    month = date.month
    season_factor = 1.0
    if month == 12:
        season_factor = ESTACIONALIDAD_DIC
    elif month == 1:
        season_factor = ESTACIONALIDAD_ENE

    # Ruido aleatorio para simular fluctuaciones diarias
    noise = random.uniform(0.9, 1.1)

    return trend_factor * season_factor * noise

# --- 3. GENERACIÓN DE TABLAS DE DIMENSIÓN ---

print("Generando Dimensiones (Tiempo, Cliente, Producto, Vendedor)...")

# dim_tiempo
dates = pd.date_range(start=FECHA_INICIO, end=FECHA_FIN, freq='D')
df_tiempo = pd.DataFrame({'fecha': dates})
df_tiempo['anio'] = df_tiempo['fecha'].dt.year
df_tiempo['mes'] = df_tiempo['fecha'].dt.month
df_tiempo['dia_semana'] = df_tiempo['fecha'].dt.day_name(locale='es_ES')
df_tiempo['es_festivo'] = np.random.choice([True, False], size=len(df_tiempo), p=[0.02, 0.98])
df_tiempo.to_csv('dim_tiempo.csv', index=False, encoding='utf-8')

# dim_cliente
data_clientes = []
tipos_contrato = ['Mensual', 'Anual', 'Premium']
segmentos = ['PYME', 'Gran Empresa', 'Startup']
for i in range(1, NUM_CLIENTES + 1):
    data_clientes.append({
        'id_cliente': i,
        'nombre': fake.company(),
        'email': fake.email(),
        'segmento_demografico': random.choice(segmentos),
        'tipo_contrato': random.choice(tipos_contrato),
        'fecha_alta': fake.date_between(start_date=FECHA_INICIO, end_date=FECHA_FIN - timedelta(days=90))
    })
df_clientes = pd.DataFrame(data_clientes)
df_clientes.to_csv('dim_cliente.csv', index=False, encoding='utf-8')

# dim_producto
data_productos = []
categorias = ['SaaS Básico', 'SaaS Premium', 'Consultoría Estratégica', 'Soporte Técnico']
for i in range(1, NUM_PRODUCTOS + 1):
    categoria = random.choice(categorias)
    if 'Premium' in categoria:
        precio = round(random.uniform(500, 2000), 2)
        costo = round(precio * 0.2, 2)
    elif 'Consultoría' in categoria:
        precio = round(random.uniform(1000, 5000), 2)
        costo = round(precio * 0.15, 2)
    else:
        precio = round(random.uniform(50, 400), 2)
        costo = round(precio * 0.3, 2)

    # Inyectar valor atípico para DQG: un producto con margen negativo
    if i == 1:
        costo = precio * 1.5

    data_productos.append({
        'id_producto': i,
        'nombre_producto': f'{categoria} v{random.randint(1, 5)}',
        'categoria': categoria,
        'precio_unitario': precio,
        'costo_adquisicion': costo
    })
df_productos = pd.DataFrame(data_productos)
df_productos.to_csv('dim_producto.csv', index=False, encoding='utf-8')

# dim_vendedor
regiones = ['Norte', 'Sur', 'Este', 'Oeste', 'Internacional']
data_vendedores = []
for i in range(1, NUM_VENDEDORES + 1):
    data_vendedores.append({
        'id_vendedor': i,
        'nombre_vendedor': fake.name(),
        'region': random.choice(regiones),
        'cuota_asignada': random.randint(50000, 200000),
        'fecha_contratacion': fake.date_between(start_date=FECHA_INICIO - timedelta(days=365*5), end_date=FECHA_INICIO)
    })
df_vendedores = pd.DataFrame(data_vendedores)
df_vendedores.to_csv('dim_vendedor.csv', index=False, encoding='utf-8')

# --- 4. GENERACIÓN DE TABLAS DE HECHOS (FACTS) ---

# Factores de ponderación de tiempo para la distribución de fechas
df_tiempo['factor_peso'] = df_tiempo['fecha'].apply(generar_factor_tiempo)
pesos_fechas = df_tiempo['factor_peso'].tolist() / np.sum(df_tiempo['factor_peso'].tolist())
fechas_disponibles = df_tiempo['fecha'].tolist()

clientes_ids = df_clientes['id_cliente'].tolist()
productos_ids = df_productos['id_producto'].tolist()
vendedores_ids = df_vendedores['id_vendedor'].tolist()

# --- 4.1. fact_ventas ---
print("Generando fact_ventas (con tendencias y estacionalidad)...")

data_ventas = {
    'id_factura': range(1, NUM_REGISTROS_VENTAS + 1),
    'fecha_venta': np.random.choice(fechas_disponibles, size=NUM_REGISTROS_VENTAS, p=pesos_fechas),
    'id_cliente': np.random.choice(clientes_ids, size=NUM_REGISTROS_VENTAS, p=np.random.dirichlet(np.ones(NUM_CLIENTES)*50)),
    'id_producto': np.random.choice(productos_ids, size=NUM_REGISTROS_VENTAS, p=np.random.dirichlet(np.ones(NUM_PRODUCTOS)*10)),
    'id_vendedor': np.random.choice(vendedores_ids, size=NUM_REGISTROS_VENTAS),
    'cantidad': np.random.randint(1, 15, size=NUM_REGISTROS_VENTAS),
    'estado_venta': np.random.choice(['Completada', 'Completada', 'Completada', 'Pendiente', 'Cancelada'], size=NUM_REGISTROS_VENTAS),
    'descuento_aplicado': np.random.uniform(0.00, 0.25, size=NUM_REGISTROS_VENTAS)
}

df_ventas = pd.DataFrame(data_ventas).sort_values(by='fecha_venta').reset_index(drop=True)
df_ventas = pd.merge(df_ventas, df_productos[['id_producto', 'precio_unitario']], on='id_producto', how='left')
df_ventas['monto_total'] = df_ventas['cantidad'] * df_ventas['precio_unitario'] * (1 - df_ventas['descuento_aplicado'])
df_ventas['monto_total'] = df_ventas['monto_total'].round(2)

# Inyección de Anomalías y Errores de Calidad (Para AD y DQG)
print("Inyectando anomalías y errores de calidad en fact_ventas...")

# Anomalía Fuerte (Pico de Venta)
anomalia_fecha = pd.to_datetime('2024-03-15')
idx_anomalia = df_ventas[df_ventas['fecha_venta'] == anomalia_fecha].index
if not idx_anomalia.empty:
    # Aumentar drásticamente el monto de las 10 ventas en ese día
    df_ventas.loc[idx_anomalia[0]:idx_anomalia[0]+9, 'monto_total'] *= 10
    df_ventas.loc[idx_anomalia[0]:idx_anomalia[0]+9, 'estado_venta'] = 'Completada'

# Errores de Calidad (NULLs en Monto Total) - 1%
null_indices = np.random.choice(df_ventas.index, size=int(NUM_REGISTROS_VENTAS * 0.01), replace=False)
df_ventas.loc[null_indices, 'monto_total'] = np.nan

# Errores de Formato (Monto negativo)
neg_indices = np.random.choice(df_ventas.index, size=10, replace=False)
df_ventas.loc[neg_indices, 'monto_total'] *= -1

df_ventas.drop(columns=['precio_unitario'], inplace=True)
df_ventas.to_csv('fact_ventas.csv', index=False, encoding='utf-8')


# --- 4.2. fact_cobranzas ---
print("Generando fact_cobranzas (relacionado con fact_ventas para PA)...")

data_cobranzas = []
metodos_pago = ['Transferencia', 'Cheque', 'Tarjeta', 'Pago en Línea']
cobranza_id = 1

# Solo consideramos las ventas completadas para generar cobranzas
df_cobrables = df_ventas[df_ventas['estado_venta'] == 'Completada'].copy()

for index, row in df_cobrables.iterrows():
    # El 90% se cobra a tiempo (para validar la relación del PA)
    if random.random() < PROB_COBRANZA_A_TIEMPO:
        # Cobranza normal: 30 a 60 días después de la venta
        dias_desfase = random.randint(30, 60)
        fecha_cobranza = row['fecha_venta'] + timedelta(days=dias_desfase)
        dias_atraso = 0 # Cobrado a tiempo

    else:
        # 10% de facturas con DÍAS DE ATRASO para que el PA lo detecte
        dias_atraso = random.randint(61, 180) # Más de 60 días
        fecha_cobranza = row['fecha_venta'] + timedelta(days=dias_atraso)

    data_cobranzas.append({
        'id_cobranza': cobranza_id,
        'id_cliente': row['id_cliente'],
        'id_factura': row['id_factura'],
        'fecha_cobranza': fecha_cobranza.strftime('%Y-%m-%d'),
        'monto_cobrado': row['monto_total'], # Asumimos que se cobra el total (con NULLs arriba)
        'dias_atraso': dias_atraso,
        'metodo_pago': random.choice(metodos_pago)
    })
    cobranza_id += 1

df_cobranzas = pd.DataFrame(data_cobranzas)

# Inyectar Error de Calidad (Días de atraso negativo)
neg_indices_cob = np.random.choice(df_cobranzas.index, size=10, replace=False)
df_cobranzas.loc[neg_indices_cob, 'dias_atraso'] = random.randint(-10, -1)

df_cobranzas.to_csv('fact_cobranzas.csv', index=False, encoding='utf-8')

print("\n--- ¡Generación de Datos Complejos Finalizada! ---")
print(f"Total de Registros de Ventas: {NUM_REGISTROS_VENTAS:,}")
print(f"Total de Registros de Cobranzas: {len(df_cobranzas):,}")
print("Archivos CSV generados y listos para cargar: dim_tiempo.csv, dim_cliente.csv, dim_producto.csv, dim_vendedor.csv, fact_ventas.csv, fact_cobranzas.csv")
