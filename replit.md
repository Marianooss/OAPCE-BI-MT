# OAPCE Multitrans - Sistema de Control y Gestión

## Overview

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

## External Dependencies

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