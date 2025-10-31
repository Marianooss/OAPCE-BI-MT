# BiOss – Data Driven Decisions

## Overview

BiOss is a comprehensive business intelligence and data operations platform built with Streamlit. The application provides a suite of analytical tools designed to help organizations make data-driven decisions through predictive modeling, data quality monitoring, anomaly detection, and automated reporting.

The platform consists of a main dashboard (Home.py) and nine specialized modules accessible through a multi-page Streamlit application structure. Each module addresses a specific aspect of data intelligence and operations, from cataloging data assets to generating prescriptive recommendations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework**: Streamlit (multi-page application pattern)
- **Decision**: Streamlit was chosen for rapid development of data applications with minimal boilerplate
- **Structure**: Uses Streamlit's native multi-page apps feature (pages/ directory convention)
- **Rationale**: Allows quick iteration and deployment of data-focused interfaces without requiring separate frontend/backend development

**Styling Approach**: Custom CSS with dark theme and neon accent colors
- **Color Palette**: Dark background (#0F0F15) with cyan (#00F3FF) and magenta (#FF00F7) accents
- **Implementation**: Inline CSS via st.markdown() with unsafe_allow_html=True
- **Rationale**: Creates a consistent, modern aesthetic across all pages while maintaining brand identity

**Visualization Library**: Plotly
- **Decision**: Plotly Graph Objects and Express for interactive charts
- **Alternatives**: Could use matplotlib/seaborn, but Plotly provides better interactivity
- **Pros**: Interactive, modern visualizations that integrate seamlessly with Streamlit
- **Cons**: Slightly larger bundle size compared to static plotting libraries

### Module Architecture

The application follows a modular, page-based architecture with the following components:

1. **Home Dashboard** (Home.py): Central hub displaying key metrics and trends
2. **Data Catalog** (1_📊_Catálogo_de_Datos.py): Data asset inventory and metadata management
3. **Predictive Analytics** (2_📈_Análisis_Predictivo.py): Forecasting and risk modeling
4. **Prescriptive Advisor** (3_💡_Recomendaciones.py): Actionable recommendations engine
5. **Self-Service BI** (4_📊_BI_Self_Service.py): Custom dashboard creation framework
6. **Metrics Hub** (5_📘_Centro_de_Métricas.py): Centralized metric definitions and formulas
7. **Generative Assistant** (6_🤖_Asistente_Generativo.py): Conversational data querying interface
8. **Anomaly Detection** (7_⚠️_Detección_de_Anomalías.py): Pattern deviation identification
9. **Data Quality Control** (8_🔍_Calidad_de_Datos.py): Data validation and quality scoring
10. **Report Scheduling** (9_📬_Programación_de_Reportes.py): Automated report distribution

**Design Pattern**: Each page is self-contained with its own configuration, styling, and logic
- **Rationale**: Enables independent development and testing of features
- **Trade-off**: Some code duplication (CSS, config) across pages, but improves modularity

### Data Management

**Current State**: Mock/simulated data using pandas DataFrames
- **Implementation**: Static data generation within each page for demonstration
- **Note**: No persistent data storage layer currently implemented

**Expected Evolution**: Integration with external data sources
- **Candidates**: SQL databases (Postgres likely), data warehouses, or file-based storage
- **Architecture Pattern**: Will likely adopt a repository pattern or data access layer to centralize data operations

### State Management

**Approach**: Streamlit's native session_state
- **Usage**: Currently implemented in the Generative Assistant (6_🤖) for chat history
- **Scope**: Session-based, not persistent across user sessions
- **Limitation**: State is lost on app restart; no cross-user data sharing

### Authentication & Authorization

**Current State**: No authentication implemented
- **Access Control**: Data catalog mentions access levels ("público", "confidencial", "restringido") but no enforcement
- **Future Consideration**: Will require integration with identity provider or custom auth system

## External Dependencies

### Python Libraries

**Core Framework**:
- `streamlit`: Web application framework and UI components
- `pandas`: Data manipulation and DataFrame operations
- `plotly`: Interactive data visualization (graph_objects and express)
- `numpy`: Numerical computations (used in predictive analytics)

### Potential Future Integrations

**Business Intelligence Tools** (mentioned in Self-Service BI module):
- Metabase
- Apache Superset  
- Power BI
- **Integration Method**: iframe embedding or API connections

**Language Models/AI** (for Generative Assistant):
- The assistant module currently uses mock responses
- Future integration likely requires OpenAI API, Anthropic Claude, or similar LLM service
- **Architecture Note**: Will need API key management and rate limiting

**Data Sources**:
- No specific databases currently connected
- Expected integrations: PostgreSQL, data warehouses (Snowflake, BigQuery), or cloud storage (S3, Azure Blob)

**Notification/Communication Services** (for Report Scheduling):
- Email delivery service (SendGrid, Amazon SES, SMTP)
- Required for automated report distribution functionality

**Anomaly Detection/ML Services**:
- Current implementation uses static mock data
- Production system may integrate with ML platforms (AWS SageMaker, Azure ML, or custom models)

### Configuration Requirements

**Environment Variables** (not currently configured but will be needed):
- Database connection strings
- API keys for external services
- Email service credentials
- Authentication secrets

**Deployment Considerations**:
- Requires Python 3.7+
- No containerization currently configured
- Suitable for deployment on Streamlit Cloud, Heroku, or similar platforms