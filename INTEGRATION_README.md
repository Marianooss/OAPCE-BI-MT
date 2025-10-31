# 🚀 INTEGRACIÓN CON DATOS REALES DE LA EMPRESA

Este documento explica cómo conectar tu dashboard OAPCE Multitrans con los datos reales de tu empresa.

## 📋 OPCIONES DE INTEGRACIÓN

### 1. **Base de Datos Externa (Recomendado)**
Conecta directamente a tu base de datos empresarial.

### 2. **Archivos Excel/CSV**
Importa datos desde hojas de cálculo existentes.

### 3. **API REST**
Sincroniza con sistemas externos vía API.

### 4. **Conexión Directa**
Acceso directo a SQL Server, PostgreSQL, MySQL, etc.

## 🗄️ ESTRUCTURA DE DATOS REQUERIDA

Tu sistema espera los siguientes datos:

### **Clientes**
```sql
- nombre: Razón social de la empresa
- rut: RUT único del cliente
- email: Correo de contacto
- telefono: Teléfono de contacto
- direccion: Dirección completa
- estado_funnel: prospecto/contactado/calificado/propuesta/negociacion/ganado/perdido
- valor_estimado: Valor potencial del negocio
- fecha_ingreso: Fecha de primer contacto
```

### **Vendedores**
```sql
- nombre: Nombre del vendedor
- email: Email del vendedor
- telefono: Teléfono del vendedor
- meta_mensual: Meta de ventas mensual
- comision_porcentaje: % de comisión
- activo: 1=activo, 0=inactivo
```

### **Facturas**
```sql
- numero_factura: Número único de factura
- cliente_id: ID del cliente
- fecha_emision: Fecha de emisión
- fecha_vencimiento: Fecha de vencimiento
- monto_total: Monto total de la factura
- monto_pagado: Monto pagado hasta ahora
- estado: pendiente/pagada/vencida/parcial
- descripcion: Descripción del servicio
```

### **Cobranzas**
```sql
- factura_id: ID de la factura pagada
- fecha_pago: Fecha del pago
- monto: Monto pagado
- metodo_pago: transferencia/cheque/efectivo/tarjeta
- numero_documento: Número de documento
- observaciones: Observaciones del pago
```

## ⚙️ CONFIGURACIÓN PASO A PASO

### Paso 1: Configurar Base de Datos

1. **Copia el archivo de ejemplo:**
   ```bash
   cp .env.example .env
   ```

2. **Edita el archivo `.env`:**
   ```bash
   # Para PostgreSQL
   DATABASE_URL=postgresql://usuario:password@host:5432/tu_base_datos

   # Para SQL Server
   DATABASE_URL=mssql+pyodbc://usuario:password@server/tu_base_datos?driver=ODBC+Driver+17+for+SQL+Server

   # Para MySQL
   DATABASE_URL=mysql://usuario:password@host:3306/tu_base_datos
   ```

### Paso 2: Instalar Dependencias

```bash
# Para PostgreSQL
pip install psycopg2-binary

# Para SQL Server
pip install pyodbc

# Para MySQL
pip install pymysql

# Para Excel
pip install openpyxl
```

### Paso 3: Importar Datos Existentes

```bash
# Opción A: Desde Excel/CSV
python import_data.py

# Opción B: Conexión directa a BD existente
python -c "
from database_config import *
from models import *
init_db()
print('✅ Base de datos configurada')
"
```

## 📊 FORMATOS DE ARCHIVOS SOPORTADOS

### Excel (Clientes.xlsx)
```excel
| NOMBRE_EMPRESA | RUT | EMAIL | TELEFONO | DIRECCION | ESTADO | VALOR_ESTIMADO | FECHA_INGRESO |
|----------------|-----|-------|----------|-----------|--------|----------------|---------------|
| Empresa ABC | 12345678-9 | contacto@abc.cl | 987654321 | Av. Principal 123 | prospecto | 50000000 | 2024-01-15 |
```

### CSV (Vendedores.csv)
```csv
nombre,email,telefono,meta_mensual,comision_porcentaje
Juan Pérez,juan@empresa.cl,987654321,50000000,3.5
María González,maria@empresa.cl,912345678,45000000,3.0
```

## 🔄 SINCRONIZACIÓN AUTOMÁTICA

### Configurar Sincronización Programada

1. **Editar `.env`:**
   ```bash
   AUTO_SYNC=true
   SYNC_INTERVAL_MINUTES=60  # cada hora
   API_URL=https://api.tuempresa.com/v1
   API_KEY=tu_api_key
   ```

2. **Ejecutar sincronizador:**
   ```bash
   python data_sync.py
   ```

### Programar con CRON (Linux/Mac)

```bash
# Editar crontab
crontab -e

# Agregar (ejecutar cada hora)
0 * * * * cd /ruta/a/tu/proyecto && python data_sync.py
```

### Programar con Task Scheduler (Windows)

1. Crear tarea programada en Windows
2. Acción: Iniciar programa
3. Programa: `python`
4. Argumentos: `data_sync.py`
5. Configurar horario deseado

## 🛠️ EJEMPLOS PRÁCTICOS

### Conectar a SQL Server Existente

```python
# database_config.py
import pyodbc
from sqlalchemy import create_engine

# Conexión a SQL Server existente
DATABASE_URL = "mssql+pyodbc://usuario:password@server/empresa_db?driver=ODBC+Driver+17+for+SQL+Server"

# Migrar datos existentes
def migrate_existing_data():
    db = get_db()

    # Conectar a base de datos antigua
    old_engine = create_engine("mssql+pyodbc://...")

    # Migrar clientes
    old_clients = pd.read_sql("SELECT * FROM clientes_empresa", old_engine)
    for _, client in old_clients.iterrows():
        new_client = Cliente(
            nombre=client['NOMBRE_EMPRESA'],
            rut=client['RUT'],
            email=client['EMAIL'],
            # ... mapear otros campos
        )
        db.add(new_client)

    db.commit()
```

### Sincronización con ERP

```python
def sync_with_sap():
    """Ejemplo de sincronización con SAP"""

    # Conectar a SAP via API
    sap_api = "https://sap.tuempresa.com/api"
    headers = {"Authorization": "Bearer tu_token"}

    # Obtener clientes
    response = requests.get(f"{sap_api}/clientes", headers=headers)
    sap_clients = response.json()

    db = get_db()
    for sap_client in sap_clients:
        cliente = Cliente(
            nombre=sap_client['CardName'],
            rut=sap_client['LicTradNum'],
            email=sap_client['E_Mail'],
            telefono=sap_client['Phone1'],
            # Mapear otros campos según tu ERP
        )
        db.add(cliente)

    db.commit()
```

## 📈 MONITOREO Y LOGS

### Ver Logs de Sincronización

```bash
# Ver logs en tiempo real
tail -f data_sync.log

# Ver últimas sincronizaciones
grep "✅\|❌" data_sync.log
```

### Métricas de Sincronización

```python
def get_sync_metrics():
    """Obtener métricas de sincronización"""
    db = get_db()

    # Clientes sincronizados hoy
    today = datetime.now().date()
    new_clients_today = db.query(Cliente).filter(
        Cliente.fecha_ingreso >= today
    ).count()

    # Facturas del mes
    first_day = datetime.now().replace(day=1)
    monthly_invoices = db.query(Factura).filter(
        Factura.fecha_emision >= first_day
    ).count()

    return {
        'new_clients_today': new_clients_today,
        'monthly_invoices': monthly_invoices,
        'total_clients': db.query(Cliente).count(),
        'total_invoices': db.query(Factura).count()
    }
```

## 🚨 SOLUCIÓN DE PROBLEMAS

### Error de Conexión
```bash
# Probar conexión
python -c "from database_config import test_connection; print(test_connection())"
```

### Error de Permisos
- Verificar credenciales de base de datos
- Asegurar permisos de lectura/escritura
- Configurar firewall correctamente

### Datos Inconsistentes
```python
# Limpiar y reiniciar
python -c "
from database_config import init_db
init_db()
print('✅ Base de datos reinicializada')
"
```

## 📞 SOPORTE TÉCNICO

Para soporte en la integración:

1. **Documenta tu estructura actual** de base de datos
2. **Identifica campos clave** que necesitas migrar
3. **Prueba con datos de muestra** antes de producción
4. **Configura backups automáticos** antes de cualquier migración

## 🎯 PRÓXIMOS PASOS

1. ✅ Configura tu archivo `.env`
2. ✅ Elige método de integración
3. ✅ Prueba con datos de muestra
4. ✅ Programa sincronización automática
5. ✅ Monitorea logs y métricas
6. ✅ Capacita usuarios finales

---

**💡 Tip:** Comienza con SQLite para pruebas, luego migra a PostgreSQL para producción.
