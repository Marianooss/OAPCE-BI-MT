# OAPCE Multitrans - Sistema de Control y Gestión

## 🚀 INTEGRACIÓN CON ONVIO (THOMSON REUTERS)

**¡Perfecto para empresas chilenas que usan Onvio!**

### ✅ Integración Automática con Onvio
- **Datos en tiempo real** desde tu ERP Onvio
- **Sincronización automática** cada 15 minutos
- **Sin intervención manual** - todo automatizado
- **Dueños ven KPIs reales** actualizados automáticamente

### 🔧 Configuración Rápida
```bash
# 1. Configurar API Key de Onvio
python setup_onvio.py

# 2. Sincronización automática
python onvio_auto_sync.py

# 3. Acceder dashboard
http://localhost:5001
```

### 📊 Lo que obtienes:
- 🏢 **Clientes** desde Onvio con estados reales
- 📄 **Facturas** con estados de pago actualizados
- 💰 **Cobranzas** sincronizadas automáticamente
- 📈 **KPIs ejecutivos** en tiempo real
- 🚨 **Alertas** de facturas vencidas

---

## 🎬 GENERADOR DE DEMO AUTOMÁTICA

**¡Crea videos profesionales automáticamente!**

### ✅ Funcionalidades Automáticas
- **Navegación automática** por toda la aplicación
- **Capturas de pantalla** de cada funcionalidad
- **Carteles informativos** con texto explicativo
- **Narración automática** con voz en español
- **Videos profesionales** listos para presentar

### 🚀 Generación Rápida
```bash
# 1. Instalar dependencias
powershell -File install_demo_deps.ps1

# 2. Iniciar aplicación
streamlit run app.py --server.port 5001 --server.address localhost

# 3. Generar demo (elige opción)
powershell -File demo_simple.ps1
```

### 📁 Archivos Generados
- `demo_oapce_multitrans.mp4` - Video principal
- `demo_presentacion.mp4` - Versión con efectos
- `demo_instagram_stories.mp4` - Formato vertical
- `./demo_screenshots/` - Capturas de pantalla
- `./demo_carteles/` - Carteles informativos

### 🎯 Perfecto Para
- **Presentar a dueños** con datos reales
- **Marketing digital** en redes sociales
- **Documentación técnica** con visuales
- **Capacitación** de usuarios

---

OAPCE Multitrans is a comprehensive management control system designed for Grupo OM. It's a multi-module dashboard application built with Streamlit that provides business intelligence and operational control across different departments including executive management, commercial operations, and finance/administration.

The system implements role-based access control with three user types (admin, operador, cliente) and provides data visualization, KPI tracking, and data management capabilities for sales, invoicing, collections, and cash flow operations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework**: Streamlit (Python-based web framework)
- **Rationale**: Rapid development of data-centric dashboards with minimal frontend code
- **Pros**: Fast prototyping, built-in components for data visualization, Python-native
- **Cons**: Limited customization compared to traditional web frameworks, single-page architecture constraints

**Page Structure**: Multi-page application with modular dashboard pages
- Main entry point: `app.py` handles routing and authentication
- Separate modules for each business area:
  - `page_direccion.py`: Executive/Management dashboard
  - `page_comercial.py`: Commercial operations dashboard
  - `page_finanzas.py`: Finance/Administration dashboard
  - `page_forms.py`: Data entry and management forms

**Visualization**: Plotly for interactive charts and graphs
- Used across all dashboard modules for KPI visualization
- Provides interactive, responsive data visualizations

### Backend Architecture

**ORM**: SQLAlchemy with declarative base pattern
- **Rationale**: Python-native ORM with strong type safety and relationship management
- **Implementation**: Declarative models in `models.py`, session management in `database.py`

**Authentication System**:
- Session-based authentication using Streamlit's session state
- Password hashing with bcrypt
- Role-based access control (RBAC) with three roles: admin, operador, cliente
- Implementation in `auth.py` and `utils.py`

**Business Logic Organization**:
- Utility functions in `utils.py` for authentication and user management
- Database operations embedded in page modules (query and display pattern)
- Each dashboard page manages its own database queries

### Data Storage

**Database**: SQLite (development/default)
- **File**: `oapce_multitrans.db`
- **Rationale**: Lightweight, serverless, zero-configuration for initial deployment
- **Note**: Architecture supports migration to PostgreSQL or MySQL via SQLAlchemy

**Schema Design**:
- **Users**: `Usuario` table with role-based access
- **Commercial**: `Cliente`, `Vendedor`, `ActividadVenta` tables
- **Finance**: `Factura`, `Cobranza`, `MovimientoCaja` tables
- Enumerations for standardized states: `RolEnum`, `EstadoFacturaEnum`, `EstadoFunnelEnum`

**Relationships**:
- Foreign key relationships between clients and vendors
- Activity tracking linked to sales funnel stages
- Financial records linked to clients

### Authentication & Authorization

**Authentication Flow**:
1. Login page validates credentials against database
2. Password verification using bcrypt hashing
3. Successful login stores user data in Streamlit session state
4. Session persists until logout or session timeout

**Authorization**:
- Role-based access stored in enum: admin, operador, cliente
- Currently implemented at navigation level (module visibility)
- Expandable to page-level and data-level permissions

**Security Measures**:
- Password hashing with bcrypt salt
- Session-based state management
- Email-based user identification

### Initialization & Setup

**Database Initialization**:
- `database.py`: Creates engine and session factory
- `init_db()`: Creates all tables from SQLAlchemy models
- `init_db.py`: Seed script for demo data including test users, vendors, clients

**Application Bootstrap** (`app.py`):
- Checks for database existence
- Initializes tables if needed
- Configures Streamlit page settings (wide layout, expanded sidebar)
- Routes to login or main dashboard based on authentication state

## Browser Compatibility & Standards Mode

### Quirks Mode Fix

**Issue**: Modern browsers were rendering the application in Quirks Mode, which could cause layout inconsistencies and prevent modern CSS features from working properly.

**Solution**: Implemented a custom HTML template with proper DOCTYPE declaration:

- **Custom HTML Template**: `.streamlit/index.html`
  - Includes `<!DOCTYPE html>` declaration for Standards Mode
  - Proper meta tags for charset, viewport, and theme color
  - CSS reset for consistent box-sizing across all elements
  - Spanish language attribute for accessibility

- **Configuration**: `.streamlit/config.toml`
  - Server settings optimized for production deployment
  - Theme configuration for consistent UI
  - Template configuration to use custom HTML wrapper

**Benefits**:
- Ensures consistent rendering across all modern browsers
- Enables modern CSS features and proper layout behavior
- Improves accessibility and SEO with proper meta tags
- Prevents layout issues caused by Quirks Mode rendering

**Files Modified**:
- `.streamlit/index.html`: Custom HTML template with DOCTYPE
- `.streamlit/config.toml`: Streamlit configuration with theme and server settings

### Python Packages

**Core Framework**:
- `streamlit`: Web application framework and UI components

**Data & Visualization**:
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive charts and graphs (express and graph_objects modules)

**Database**:
- `sqlalchemy`: ORM and database toolkit
- `sqlite3`: Database engine (standard library, implicit)

**Security**:
- `bcrypt`: Password hashing and verification
- Built-in session management via Streamlit

**Environment**:
- `python-dotenv`: Environment variable management (imported but not actively used)

### Database

**Primary**: SQLite 3
- Local file-based storage
- Connection string: `sqlite:///oapce_multitrans.db`
- No external server required

**Potential Migration Path**: PostgreSQL or MySQL
- SQLAlchemy abstraction allows database switching
- Would require connection string update in `database.py`

### Third-Party Services

**None Currently Integrated**
- System is self-contained with no external API dependencies
- Email functionality referenced but not implemented
- Future integrations may include email services, payment gateways, or ERP systems

### Development Tools

**Initialization**:
- `init_db.py`: Database seeding script with sample data
- Demo credentials system for testing (hardcoded in login page)

**Configuration**:
- Environment variables supported via dotenv (DATABASE_URL configurable)
- Streamlit configuration in `app.py` (page config, layout settings)
- Custom HTML template in `.streamlit/index.html` to prevent Quirks Mode
- Streamlit config in `.streamlit/config.toml` for server settings and theme

**Quick Start**:
```bash
# Clean start (Windows)
start.bat

# Clean start (Linux/Mac)
./start.sh

# Or direct command
streamlit run app.py --server.port 5001 --server.address 0.0.0.0 --server.headless true
```

**Configuration Files**:
- `.streamlit/config.toml`: **Fixed** - Only valid Streamlit options
- `.streamlit/index.html`: Custom HTML template for Standards Mode and accessibility
- `start.bat` / `start.sh`: **NEW** - Clean startup scripts with process cleanup

**Performance Optimizations**:
- **Caching**: Implemented comprehensive caching strategy with `@st.cache_data`
- **Database**: Optimized database queries with connection pooling
- **Configuration**: Streamlit config optimized for production performance
- **HTML Template**: Enhanced with performance-focused CSS and accessibility features
- **Font Loading**: Uses system fonts instead of external @import for faster loading
- **Bundle Optimization**: Configured for optimal JavaScript and CSS delivery

**SEO Improvements**:
- **Meta Tags**: Comprehensive meta description, keywords, and author information
- **Robots.txt**: Proper search engine crawling directives
- **Sitemap.xml**: XML sitemap for better search engine indexing
- **Semantic HTML**: Proper HTML5 landmarks and accessibility structure
- **Performance**: Optimized for Core Web Vitals scoring

**Accessibility Enhancements**:
- **ARIA Labels**: Proper ARIA attributes for screen readers
- **Keyboard Navigation**: Enhanced focus indicators and navigation
- **Skip Links**: Skip-to-content functionality for screen readers
- **Semantic Structure**: Proper HTML5 landmarks (main, nav, etc.)
- **Color Contrast**: Ensured WCAG compliant color contrasts

**CSS Standards Compliance**:
- **@import Rules**: Eliminated @import rules, using system fonts for better performance
- **Standards Mode**: Proper DOCTYPE ensures browser renders in Standards Mode
- **Font Loading**: System fonts eliminate external font loading delays
- **CSS Organization**: All styles properly organized and optimized
- **Performance**: Reduced CSS complexity for faster rendering