# 🚀 INTEGRACIÓN ESPECÍFICA PARA ONVIO DE THOMSON REUTERS

## 📋 ¿QUÉ ES ONVIO?

Onvio es un software de contabilidad y gestión empresarial de Thomson Reuters, muy popular en Chile y Latinoamérica. Permite:

- ✅ Gestión contable completa
- ✅ Facturación electrónica
- ✅ Control de clientes y proveedores
- ✅ Reportes financieros
- ✅ API para integración con otros sistemas

## 🎯 VENTAJAS PARA TU EMPRESA

### **Tiempo Real para Dueños:**
- 📊 **KPIs actualizados automáticamente** cada 15 minutos
- 📈 **Dashboard ejecutivo** con métricas reales de Onvio
- 🚨 **Alertas de facturas vencidas** desde Onvio
- 💰 **Control de cobranzas** sincronizado

### **Automatización Completa:**
- 🔄 **Sin intervención manual** - datos fluyen automáticamente
- 📧 **Reportes automáticos** a dueños
- 📱 **Acceso móvil** a datos de Onvio
- 🔐 **Seguridad empresarial** con autenticación Onvio

## ⚙️ CONFIGURACIÓN PASO A PASO

### **Paso 1: Obtener API Key de Onvio**

1. **Entra a tu cuenta de Onvio:**
   - Ve a https://onvio.thomsonreuters.com
   - Inicia sesión con tus credenciales

2. **Accede a la sección de APIs:**
   - Busca "API" o "Integraciones" en el menú
   - O ve a Configuración → APIs → Generar API Key

3. **Genera tu API Key:**
   - Haz clic en "Generar nueva API Key"
   - Copia la key generada
   - **Guárdala en lugar seguro**

### **Paso 2: Configurar Variables de Entorno**

```bash
# 1. Copia el archivo de configuración
cp .env.example .env

# 2. Edita .env con tus datos de Onvio
ONVIO_API_KEY=tu_api_key_copiada_aqui
ONVIO_ENVIRONMENT=production
ONVIO_AUTO_SYNC=true
ONVIO_SYNC_INTERVAL=15
```

### **Paso 3: Ejecutar Integración**

```bash
# Opción A: Configuración inicial
python onvio_integration.py

# Opción B: Sincronización automática continua
python onvio_auto_sync.py

# Opción C: Sincronización única
python -c "from onvio_integration import OnvioIntegrator; sync = OnvioIntegrator('tu_api_key'); sync.sync_to_dashboard()"
```

## 📊 QUÉ DATOS SE SINCRONIZAN

### **Desde Onvio a tu Dashboard:**

| **Datos de Onvio** | **Se convierte en** | **Beneficio** |
|-------------------|-------------------|---------------|
| Clientes | Clientes con estado de funnel | Seguimiento comercial real |
| Facturas | Facturas con estados de pago | Control de facturación |
| Pagos/Cobranzas | Movimientos de caja | Flujo de efectivo real |
| Información de empresa | Configuración del sistema | Personalización automática |

### **Mapeo de Estados:**

| **Onvio Status** | **Dashboard Status** | **Color en Dashboard** |
|-----------------|-------------------|------------------------|
| Prospect | Prospecto | 🟡 Amarillo |
| Contacted | Contactado | 🟠 Naranja |
| Qualified | Calificado | 🟢 Verde claro |
| Proposal | Propuesta | 🔵 Azul |
| Won | Ganado | 🟢 Verde |
| Lost | Perdido | 🔴 Rojo |

## ⏰ SINCRONIZACIÓN AUTOMÁTICA

### **Configuración para Dueños:**

```bash
# En .env
ONVIO_AUTO_SYNC=true
ONVIO_SYNC_INTERVAL=15  # cada 15 minutos
ONVIO_EXPORT_TO_EXCEL=true  # respaldo automático
```

### **Lo que ven los dueños:**

1. **Dashboard actualizado** cada 15 minutos
2. **KPIs en tiempo real** desde Onvio
3. **Alertas automáticas** de facturas vencidas
4. **Reportes ejecutivos** con datos reales
5. **Tendencias** basadas en datos históricos de Onvio

## 📈 MÉTRICAS QUE VERÁN LOS DUEÑOS

### **KPI Principales:**
- 💰 **Facturación del mes** (desde Onvio)
- 💵 **Cobranzas del mes** (desde Onvio)
- 📊 **Clientes activos** (desde Onvio)
- ⏰ **Facturas vencidas** (alertas desde Onvio)
- 📈 **Crecimiento mensual** (cálculos automáticos)

### **Dashboard Ejecutivo:**
- 🏢 **Resumen financiero** actualizado
- 👥 **Estado de clientes** por vendedor
- 📋 **Pipeline de ventas** real
- 💳 **Control de cobranzas** automático

## 🔧 SOLUCIÓN DE PROBLEMAS

### **Error: "API Key inválida"**
```bash
# 1. Verifica que copiaste correctamente la API Key
# 2. Asegúrate que no tenga espacios extra
# 3. Confirma que la key esté activa en Onvio

python -c "
from onvio_integration import OnvioIntegrator
integrator = OnvioIntegrator('tu_api_key')
success, info = integrator.test_connection()
print('Conectado:', success)
if info:
    print('Empresa:', info.get('name'))
"
```

### **Error: "No se puede conectar a Onvio"**
```bash
# 1. Verifica conexión a internet
# 2. Confirma que Onvio esté funcionando
# 3. Prueba con ambiente 'sandbox' si es cuenta de prueba

# En .env cambia:
ONVIO_ENVIRONMENT=sandbox
```

### **Datos no se actualizan**
```bash
# 1. Verifica logs
tail -f onvio_sync.log

# 2. Ejecuta sincronización manual
python onvio_integration.py

# 3. Verifica configuración en .env
cat .env | grep ONVIO
```

## 📱 ACCESO PARA DUEÑOS

### **URL del Dashboard:**
```
http://localhost:5001
```

### **Credenciales de Dueños:**
```bash
# Configura usuarios con rol 'admin' en la base de datos
python -c "
from database_config import get_db
from models import Usuario, RolEnum
from utils import hash_password

db = get_db()
admin = Usuario(
    nombre='Dueño Principal',
    email='dueno@tuempresa.cl',
    password_hash=hash_password('password_seguro'),
    rol=RolEnum.admin
)
db.add(admin)
db.commit()
print('Usuario admin creado')
"
```

## 🚨 MONITOREO Y ALERTAS

### **Logs de Sincronización:**
```bash
# Ver actividad en tiempo real
tail -f onvio_sync.log

# Ver últimas 10 sincronizaciones
grep "✅\|❌" onvio_sync.log | tail -10
```

### **Alertas por Email (Próximamente):**
```bash
# Configurar notificaciones automáticas
EMAIL_ALERTS=true
ADMIN_EMAIL=dueno@tuempresa.cl
```

## 💡 EJEMPLO DE CONFIGURACIÓN COMPLETA

```bash
# .env completo para Onvio
DATABASE_URL=sqlite:///oapce_multitrans.db

# Configuración Onvio
ONVIO_API_KEY=tr_onvio_1234567890abcdef
ONVIO_ENVIRONMENT=production
ONVIO_AUTO_SYNC=true
ONVIO_SYNC_INTERVAL=15
ONVIO_EXPORT_TO_EXCEL=true
ONVIO_EXPORT_PATH=./data/onvio_export

# Logs y monitoreo
LOG_LEVEL=INFO
LOG_FILE=onvio_sync.log
AUTO_BACKUP=true
```

## 🎉 RESULTADO FINAL

Después de la configuración:

✅ **Dueños ven datos reales** de Onvio cada 15 minutos  
✅ **Sin intervención manual** - todo automatizado  
✅ **KPIs actualizados** automáticamente  
✅ **Alertas de facturas** vencidas desde Onvio  
✅ **Dashboard ejecutivo** con métricas reales  
✅ **Backups automáticos** de datos Onvio  
✅ **Sincronización en la nube** - funciona desde cualquier lugar  

## 📞 SOPORTE TÉCNICO

Si tienes problemas:

1. **Verifica tu API Key** de Onvio
2. **Confirma conexión a internet**
3. **Revisa logs** en `onvio_sync.log`
4. **Prueba ambiente sandbox** si es cuenta nueva

**¿Todo listo para conectar con Onvio?** 🚀

---

**💡 Tip:** La integración con Onvio es la más común en empresas chilenas. ¡Tus dueños verán datos reales en minutos!
