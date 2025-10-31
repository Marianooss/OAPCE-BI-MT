"""
Self-Service BI Facilitator (SSBF) - Agente 5
Módulo para facilitar la creación autónoma de reportes por usuarios no técnicos
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database import get_db
from models import PredefinedMetric, UserDashboard, DashboardPermission, DashboardTemplate, Usuario
from sqlalchemy import text, func
import logging
import urllib.parse

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSBFFacilitator:
    """
    Facilitador de BI autoservicio para empoderamiento de usuarios
    """

    def __init__(self, metabase_config: Dict = None):
        self.db = get_db()
        self.metabase_config = metabase_config or self._get_metabase_config_default()
        self.session_token = None
        self.authenticated = False

    def _get_metabase_config_default(self) -> dict:
        """Configuración por defecto de Metabase"""
        return {
            'base_url': 'http://localhost:3000',
            'username': 'admin',
            'password': 'metabase123',
            'database_id': 2,  # ID de la BD OAPCE en Metabase
            'auto_login': False
        }

    # =========== MÉTRICAS PREDEFINIDAS ===========

    def initialize_default_metrics(self) -> Dict:
        """
        Inicializa métricas predefinidas comunes
        """
        default_metrics = [
            # === MÉTRICAS DE VENTAS ===
            {
                'name': 'ventas_total_mes_actual',
                'display_name': 'Ventas Total Mes Actual',
                'description': 'Total de ventas pagadas en el mes actual',
                'category': 'ventas',
                'formula': """
                    SELECT COALESCE(SUM(f.monto_total), 0) as valor
                    FROM facturas f
                    WHERE f.estado = 'Pagada'
                    AND strftime('%Y-%m', f.fecha_emision) = strftime('%Y-%m', 'now')
                """,
                'data_type': 'currency',
                'unit': '$',
                'created_by': 'admin'
            },
            {
                'name': 'ventas_proyectadas_mes',
                'display_name': 'Ventas Proyectadas Mes',
                'description': 'Proyección de ventas para el mes actual basada en promedio histórico',
                'category': 'ventas',
                'formula': """
                    SELECT
                        ROUND(
                            (SELECT AVG(mes_ventas) * 1.0
                             FROM (SELECT SUM(f.monto_total) as mes_ventas
                                   FROM facturas f
                                   WHERE f.estado = 'Pagada'
                                   GROUP BY strftime('%Y-%m', f.fecha_emision)
                                   ORDER BY strftime('%Y-%m', f.fecha_emision) DESC
                                   LIMIT 3)) *
                            (strftime('%d', date('now', 'start of month', '+1 month', '-1 day')) -
                             strftime('%d', 'now') + 1) /
                            strftime('%d', date('now', 'start of month', '+1 month', '-1 day')), 2
                        ) as valor
                """,
                'data_type': 'currency',
                'unit': '$',
                'created_by': 'admin'
            },
            {
                'name': 'conversion_ventas_porcentaje',
                'display_name': 'Tasa Conversión Ventas',
                'description': 'Porcentaje de oportunidades convertidas a ventas',
                'category': 'ventas',
                'formula': """
                    SELECT ROUND(
                        (SELECT COUNT(*) FROM clientes WHERE estado_funnel = 'Ganado') * 100.0 /
                        NULLIF((SELECT COUNT(*) FROM clientes), 0), 2
                    ) as valor
                """,
                'data_type': 'percentage',
                'unit': '%',
                'created_by': 'admin'
            },
            {
                'name': 'top_vendedor_mes',
                'display_name': 'Top Vendedor del Mes',
                'description': 'Vendedor con más ventas en el mes actual',
                'category': 'ventas',
                'formula': """
                    SELECT v.nombre as valor
                    FROM vendedores v
                    JOIN clientes c ON v.id = c.vendedor_id
                    JOIN facturas f ON c.id = f.cliente_id
                    WHERE f.estado = 'Pagada'
                    AND strftime('%Y-%m', f.fecha_emision) = strftime('%Y-%m', 'now')
                    GROUP BY v.id, v.nombre
                    ORDER BY SUM(f.monto_total) DESC
                    LIMIT 1
                """,
                'data_type': 'text',
                'unit': '',
                'created_by': 'admin'
            },

            # === MÉTRICAS DE COBRANZA ===
            {
                'name': 'cobranza_total_mes',
                'display_name': 'Cobranza Total Mes',
                'description': 'Total cobrado en el mes actual',
                'category': 'cobranza',
                'formula': """
                    SELECT COALESCE(SUM(c.monto), 0) as valor
                    FROM cobranzas c
                    WHERE strftime('%Y-%m', c.fecha_pago) = strftime('%Y-%m', 'now')
                """,
                'data_type': 'currency',
                'unit': '$',
                'created_by': 'admin'
            },
            {
                'name': 'facturas_pendientes_total',
                'display_name': 'Facturas Pendientes Total',
                'description': 'Monto total de facturas pendientes de pago',
                'category': 'cobranza',
                'formula': """
                    SELECT COALESCE(SUM(f.monto_total - f.monto_pagado), 0) as valor
                    FROM facturas f
                    WHERE f.estado IN ('Pendiente', 'Parcial')
                """,
                'data_type': 'currency',
                'unit': '$',
                'created_by': 'admin'
            },
            {
                'name': 'dias_promedio_cobro',
                'display_name': 'Días Promedio de Cobro',
                'description': 'Promedio de días que tardan en pagar las facturas',
                'category': 'cobranza',
                'formula': """
                    SELECT ROUND(AVG(julianday(c.fecha_pago) - julianday(f.fecha_emision)), 1) as valor
                    FROM cobranzas c
                    JOIN facturas f ON c.factura_id = f.id
                    WHERE c.fecha_pago >= '2024-01-01'
                """,
                'data_type': 'number',
                'unit': 'días',
                'created_by': 'admin'
            },

            # === MÉTRICAS DE FINANZAS ===
            {
                'name': 'flujo_caja_mes',
                'display_name': 'Flujo de Caja Mes',
                'description': 'Flujo de caja neto del mes actual',
                'category': 'finanzas',
                'formula': """
                    SELECT
                        (SELECT COALESCE(SUM(monto), 0) FROM movimientos_caja WHERE tipo = 'Ingreso' AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')) -
                        (SELECT COALESCE(SUM(monto), 0) FROM movimientos_caja WHERE tipo = 'Egreso' AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now'))
                    as valor
                """,
                'data_type': 'currency',
                'unit': '$',
                'created_by': 'admin'
            },
            {
                'name': 'margen_bruto_porcentaje',
                'display_name': 'Margen Bruto',
                'description': 'Margen bruto aproximado (estimado)',
                'category': 'finanzas',
                'formula': """
                    SELECT ROUND(
                        (SELECT COALESCE(SUM(f.monto_total), 0) FROM facturas f WHERE f.estado = 'Pagada') * 0.25 /
                        NULLIF((SELECT COALESCE(SUM(f.monto_total), 0) FROM facturas f WHERE f.estado = 'Pagada'), 0) * 100, 1
                    ) as valor
                """,
                'data_type': 'percentage',
                'unit': '%',
                'created_by': 'admin'
            },

            # === MÉTRICAS OPERACIONALES ===
            {
                'name': 'clientes_activos_total',
                'display_name': 'Clientes Activos Total',
                'description': 'Total de clientes únicos con actividad',
                'category': 'operaciones',
                'formula': """
                    SELECT COUNT(DISTINCT c.id) as valor
                    FROM clientes c
                    JOIN facturas f ON c.id = f.cliente_id
                    WHERE f.fecha_emision >= date('now', '-90 days')
                """,
                'data_type': 'number',
                'unit': '',
                'created_by': 'admin'
            },
            {
                'name': 'actividad_comercial_hoy',
                'display_name': 'Actividad Comercial Hoy',
                'description': 'Número de actividades comerciales realizadas hoy',
                'category': 'operaciones',
                'formula': """
                    SELECT COUNT(*) as valor
                    FROM actividades_venta
                    WHERE date(fecha) = date('now')
                """,
                'data_type': 'number',
                'unit': '',
                'created_by': 'admin'
            }
        ]

        created_count = 0
        for metric_data in default_metrics:
            try:
                # Verificar si ya existe
                existing = self.db.query(PredefinedMetric).filter(
                    PredefinedMetric.name == metric_data['name']
                ).first()

                if not existing:
                    metric = PredefinedMetric(**metric_data)
                    self.db.add(metric)
                    created_count += 1

            except Exception as e:
                logger.warning(f"Error creando métrica {metric_data['name']}: {str(e)}")

        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error guardando métricas: {str(e)}")
            self.db.rollback()

        return {
            "success": True,
            "metrics_created": created_count,
            "total_default_metrics": len(default_metrics)
        }

    def get_predefined_metrics(self, category: str = None, active_only: bool = True) -> List[Dict]:
        """
        Obtiene métricas predefinidas
        """
        try:
            query = self.db.query(PredefinedMetric)
            if category:
                query = query.filter(PredefinedMetric.category == category)
            if active_only:
                query = query.filter(PredefinedMetric.is_active == 1)

            metrics = query.order_by(PredefinedMetric.category, PredefinedMetric.display_name).all()

            result = []
            for metric in metrics:
                result.append({
                    'id': metric.id,
                    'name': metric.name,
                    'display_name': metric.display_name,
                    'description': metric.description,
                    'category': metric.category,
                    'formula': metric.formula,
                    'data_type': metric.data_type,
                    'unit': metric.unit,
                    'is_active': bool(metric.is_active),
                    'created_by': metric.created_by,
                    'created_at': str(metric.created_at)
                })

            return result

        except Exception as e:
            logger.error(f"Error obteniendo métricas predefinidas: {str(e)}")
            return []

    def calculate_metric_value(self, metric_id: int) -> Dict:
        """
        Calcula el valor actual de una métrica específica
        """
        try:
            metric = self.db.query(PredefinedMetric).filter(PredefinedMetric.id == metric_id).first()
            if not metric:
                return {"success": False, "error": "Métrica no encontrada"}

            # Ejecutar consulta SQL directamente usando text()
            result = self.db.execute(text(metric.formula)).fetchone()

            if result is None or len(result) == 0:
                value = 0
            else:
                value = result[0]

            # Formatear según tipo de datos
            if metric.data_type == 'currency' and isinstance(value, (int, float)):
                formatted_value = f"${value:,.0f}"
            elif metric.data_type == 'percentage' and isinstance(value, (int, float)):
                formatted_value = f"{value:.1f}%"
            elif metric.data_type == 'number' and isinstance(value, (int, float)):
                formatted_value = f"{value:,.0f}"
            else:
                formatted_value = str(value) if value is not None else "N/A"

            return {
                "success": True,
                "metric_id": metric_id,
                "metric_name": metric.name,
                "raw_value": value,
                "formatted_value": formatted_value,
                "unit": metric.unit,
                "data_type": metric.data_type,
                "calculated_at": datetime.now()
            }

        except Exception as e:
            logger.error(f"Error calculando valor de métrica {metric_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    # =========== PLANTILLAS DE DASHBOARDS ===========

    def initialize_dashboard_templates(self) -> Dict:
        """
        Inicializa plantillas de dashboards prediseñadas
        """
        default_templates = [
            {
                'name': 'dashboard_ejecutivo',
                'display_name': 'Dashboard Ejecutivo',
                'description': 'Vista general para dirección con KPIs principales',
                'category': 'direccion',
                'config': json.dumps({
                    'sections': [
                        {'title': 'Ventas', 'metrics': ['ventas_total_mes_actual', 'ventas_proyectadas_mes', 'conversion_ventas_porcentaje']},
                        {'title': 'Cobranza', 'metrics': ['cobranza_total_mes', 'facturas_pendientes_total', 'dias_promedio_cobro']},
                        {'title': 'Finanzas', 'metrics': ['flujo_caja_mes', 'margen_bruto_porcentaje']},
                        {'title': 'Operaciones', 'metrics': ['clientes_activos_total', 'actividad_comercial_hoy', 'top_vendedor_mes']}
                    ],
                    'charts': ['ventas_mensual_grafico', 'cobranza_status_grafico']
                }),
                'created_by': 'admin'
            },
            {
                'name': 'dashboard_comercial',
                'display_name': 'Dashboard Comercial',
                'description': 'Métricas de ventas para equipo comercial',
                'category': 'ventas',
                'config': json.dumps({
                    'sections': [
                        {'title': 'Desempeño Ventas', 'metrics': ['ventas_total_mes_actual', 'ventas_proyectadas_mes']},
                        {'title': 'Conversión', 'metrics': ['conversion_ventas_porcentaje', 'top_vendedor_mes']},
                        {'title': 'Clientes', 'metrics': ['clientes_activos_total']}
                    ],
                    'charts': ['pipeline_ventas_grafico', 'performance_vendedores_grafico']
                }),
                'created_by': 'admin'
            },
            {
                'name': 'dashboard_finanzas',
                'display_name': 'Dashboard Finanzas',
                'description': 'Métricas financieras y de cobranza',
                'category': 'finanzas',
                'config': json.dumps({
                    'sections': [
                        {'title': 'Flujo de Caja', 'metrics': ['flujo_caja_mes']},
                        {'title': 'Cobranza', 'metrics': ['cobranza_total_mes', 'facturas_pendientes_total', 'dias_promedio_cobro']},
                        {'title': 'Margen', 'metrics': ['margen_bruto_porcentaje']}
                    ],
                    'charts': ['flujo_caja_grafico', 'cobranza_aging_grafico']
                }),
                'created_by': 'admin'
            },
            {
                'name': 'dashboard_operaciones',
                'display_name': 'Dashboard Operaciones',
                'description': 'Métricas operativas y de productividad',
                'category': 'operaciones',
                'config': json.dumps({
                    'sections': [
                        {'title': 'Actividad', 'metrics': ['actividad_comercial_hoy', 'clientes_activos_total']},
                        {'title': 'Eficiencia', 'metrics': ['conversion_ventas_porcentaje']}
                    ],
                    'charts': ['actividad_diaria_grafico', 'productividad_equipo_grafico']
                }),
                'created_by': 'admin'
            }
        ]

        created_count = 0
        for template_data in default_templates:
            try:
                # Verificar si ya existe
                existing = self.db.query(DashboardTemplate).filter(
                    DashboardTemplate.name == template_data['name']
                ).first()

                if not existing:
                    template = DashboardTemplate(**template_data)
                    self.db.add(template)
                    created_count += 1

            except Exception as e:
                logger.warning(f"Error creando plantilla {template_data['name']}: {str(e)}")

        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error guardando plantillas: {str(e)}")
            self.db.rollback()

        return {
            "success": True,
            "templates_created": created_count,
            "total_default_templates": len(default_templates)
        }

    def get_dashboard_templates(self, category: str = None, public_only: bool = True) -> List[Dict]:
        """
        Obtiene plantillas de dashboards disponibles
        """
        try:
            query = self.db.query(DashboardTemplate)
            if category:
                query = query.filter(DashboardTemplate.category == category)
            if public_only:
                query = query.filter(DashboardTemplate.is_public == 1)

            templates = query.order_by(DashboardTemplate.category, DashboardTemplate.display_name).all()

            result = []
            for template in templates:
                result.append({
                    'id': template.id,
                    'name': template.name,
                    'display_name': template.display_name,
                    'description': template.description,
                    'category': template.category,
                    'config': json.loads(template.config) if template.config else {},
                    'thumbnail_url': template.thumbnail_url,
                    'use_count': template.use_count,
                    'is_public': bool(template.is_public),
                    'created_by': template.created_by,
                    'created_at': str(template.created_at)
                })

            return result

        except Exception as e:
            logger.error(f"Error obteniendo plantillas de dashboards: {str(e)}")
            return []

    # =========== GESTIÓN DE DASHBOARDS ===========

    def create_user_dashboard(self, user_id: int, title: str, template_name: str = None,
                           description: str = "", is_public: int = 0) -> Dict:
        """
        Crea un nuevo dashboard para un usuario
        """
        try:
            # Si hay template, cargar configuración base
            config = {}
            if template_name:
                template = self.db.query(DashboardTemplate).filter(
                    DashboardTemplate.name == template_name
                ).first()
                if template:
                    config = json.loads(template.config) if template.config else {}
                    # Incrementar contador de uso
                    template.use_count += 1

            dashboard = UserDashboard(
                title=title,
                description=description,
                user_id=user_id,
                is_public=is_public,
                config=json.dumps(config) if config else None,
                dashboard_type='metabase'
            )

            self.db.add(dashboard)
            self.db.commit()

            # Crear permiso por defecto para el creador
            permission = DashboardPermission(
                dashboard_id=dashboard.id,
                user_id=user_id,
                permission_level='admin',
                granted_by=user_id
            )
            self.db.add(permission)
            self.db.commit()

            return {
                "success": True,
                "dashboard_id": dashboard.id,
                "message": "Dashboard creado exitosamente"
            }

        except Exception as e:
            logger.error(f"Error creando dashboard: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}

    def get_user_dashboards(self, user_id: int) -> List[Dict]:
        """
        Obtiene dashboards accesibles para un usuario
        """
        try:
            # Dashboards propios
            owned_dashboards = self.db.query(UserDashboard).filter(
                UserDashboard.user_id == user_id
            ).all()

            # Dashboards compartidos
            shared_permissions = self.db.query(DashboardPermission).filter(
                DashboardPermission.user_id == user_id
            ).all()

            shared_dashboard_ids = [p.dashboard_id for p in shared_permissions]

            shared_dashboards = []
            if shared_dashboard_ids:
                shared_dashboards = self.db.query(UserDashboard).filter(
                    UserDashboard.id.in_(shared_dashboard_ids)
                ).all()

            # Combinar y eliminar duplicados
            all_dashboards = owned_dashboards + shared_dashboards
            unique_dashboards = list(set(all_dashboards))

            result = []
            for dashboard in unique_dashboards:
                # Obtener permisos del usuario para este dashboard
                user_permissions = self.db.query(DashboardPermission).filter(
                    DashboardPermission.dashboard_id == dashboard.id,
                    DashboardPermission.user_id == user_id
                ).first()

                permission_level = 'admin' if dashboard.user_id == user_id else (
                    user_permissions.permission_level if user_permissions else 'view'
                )

                result.append({
                    'id': dashboard.id,
                    'title': dashboard.title,
                    'description': dashboard.description,
                    'user_id': dashboard.user_id,
                    'is_public': bool(dashboard.is_public),
                    'dashboard_type': dashboard.dashboard_type,
                    'config': json.loads(dashboard.config) if dashboard.config else {},
                    'thumbnail_url': dashboard.thumbnail_url,
                    'tags': json.loads(dashboard.tags) if dashboard.tags else [],
                    'view_count': dashboard.view_count,
                    'last_viewed': str(dashboard.last_viewed) if dashboard.last_viewed else None,
                    'user_permission': permission_level,
                    'created_at': str(dashboard.created_at),
                    'updated_at': str(dashboard.updated_at)
                })

            return result

        except Exception as e:
            logger.error(f"Error obteniendo dashboards del usuario {user_id}: {str(e)}")
            return []

    def update_dashboard_config(self, dashboard_id: int, user_id: int, config: dict) -> Dict:
        """
        Actualiza la configuración de un dashboard
        """
        try:
            dashboard = self.db.query(UserDashboard).filter(
                UserDashboard.id == dashboard_id
            ).first()

            if not dashboard:
                return {"success": False, "error": "Dashboard no encontrado"}

            # Verificar permisos
            if dashboard.user_id != user_id:
                permission = self.db.query(DashboardPermission).filter(
                    DashboardPermission.dashboard_id == dashboard_id,
                    DashboardPermission.user_id == user_id,
                    DashboardPermission.permission_level.in_(['admin', 'edit'])
                ).first()

                if not permission:
                    return {"success": False, "error": "Sin permisos para editar este dashboard"}

            dashboard.config = json.dumps(config) if config else None
            dashboard.updated_at = datetime.now()

            self.db.commit()

            return {
                "success": True,
                "message": "Dashboard actualizado exitosamente"
            }

        except Exception as e:
            logger.error(f"Error actualizando dashboard {dashboard_id}: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}

    def share_dashboard(self, dashboard_id: int, user_id: int, target_user_id: int,
                       permission_level: str = 'view') -> Dict:
        """
        Comparte un dashboard con otro usuario
        """
        try:
            dashboard = self.db.query(UserDashboard).filter(
                UserDashboard.id == dashboard_id,
                UserDashboard.user_id == user_id
            ).first()

            if not dashboard:
                return {"success": False, "error": "Dashboard no encontrado o sin permisos"}

            # Verificar si ya existe el permiso
            existing_permission = self.db.query(DashboardPermission).filter(
                DashboardPermission.dashboard_id == dashboard_id,
                DashboardPermission.user_id == target_user_id
            ).first()

            if existing_permission:
                # Actualizar permiso existente
                existing_permission.permission_level = permission_level
                existing_permission.granted_at = datetime.now()
            else:
                # Crear nuevo permiso
                permission = DashboardPermission(
                    dashboard_id=dashboard_id,
                    user_id=target_user_id,
                    permission_level=permission_level,
                    granted_by=user_id
                )
                self.db.add(permission)

            self.db.commit()

            return {
                "success": True,
                "message": f"Dashboard compartido con permisos '{permission_level}'"
            }

        except Exception as e:
            logger.error(f"Error compartiendo dashboard {dashboard_id}: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}

    # =========== INTEGRACIÓN METABASE ===========

    def authenticate_metabase(self) -> bool:
        """
        Autentica con Metabase para obtener session token
        """
        try:
            if self.authenticated and self.session_token:
                return True

            url = f"{self.metabase_config['base_url']}/api/session"
            payload = {
                "username": self.metabase_config['username'],
                "password": self.metabase_config['password']
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            session_data = response.json()
            self.session_token = session_data['id']
            self.authenticated = True

            logger.info("Autenticación con Metabase exitosa")
            return True

        except Exception as e:
            logger.error(f"Error autenticando con Metabase: {str(e)}")
            self.authenticated = False
            return False

    def get_metabase_dashboard_url(self, dashboard_id: str, params: dict = None) -> str:
        """
        Genera URL pública o embebida de un dashboard de Metabase
        """
        try:
            base_url = self.metabase_config['base_url']
            url = f"{base_url}/public/dashboard/{dashboard_id}"

            if params:
                param_string = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
                url += f"?{param_string}"

            return url

        except Exception as e:
            logger.error(f"Error generando URL de Metabase: {str(e)}")
            return ""

    def get_dashboard_embed_code(self, dashboard_id: str, width: int = 800,
                               height: int = 600) -> str:
        """
        Genera código HTML para embeber dashboard
        """
        try:
            embed_url = self.get_metabase_dashboard_url(dashboard_id)

            embed_code = f"""
            <iframe
                src="{embed_url}"
                frameborder="0"
                width="{width}"
                height="{height}"
                allowtransparency
            ></iframe>
            """

            return embed_code

        except Exception as e:
            logger.error(f"Error generando código embed: {str(e)}")
            return ""

    # =========== ANÁLISIS DE USO ===========

    def get_dashboard_usage_stats(self) -> Dict:
        """
        Obtiene estadísticas de uso de dashboards
        """
        try:
            # Total de dashboards por tipo
            dashboard_types = self.db.query(
                UserDashboard.dashboard_type,
                func.count(UserDashboard.id).label('count')
            ).group_by(UserDashboard.dashboard_type).all()

            # Dashboards más usados
            top_dashboards = self.db.query(UserDashboard).order_by(
                UserDashboard.view_count.desc()
            ).limit(10).all()

            # Actividad reciente
            recent_activity = self.db.query(UserDashboard).filter(
                UserDashboard.updated_at >= datetime.now() - timedelta(days=7)
            ).count()

            # Métricas más usadas
            metrics_usage = self.db.query(PredefinedMetric).order_by(
                PredefinedMetric.id  # En producción, agregar campo de uso
            ).limit(10).all()

            return {
                "success": True,
                "dashboard_types": {dt[0]: dt[1] for dt in dashboard_types},
                "total_dashboards": sum(dt[1] for dt in dashboard_types),
                "top_dashboards": [{
                    'id': d.id,
                    'title': d.title,
                    'views': d.view_count,
                    'user_id': d.user_id
                } for d in top_dashboards],
                "recent_activity": recent_activity,
                "popular_metrics": [{
                    'id': m.id,
                    'name': m.name,
                    'display_name': m.display_name,
                    'category': m.category
                } for m in metrics_usage]
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de uso: {str(e)}")
            return {"success": False, "error": str(e)}

    def close(self):
        """Cierra la sesión de base de datos"""
        self.db.close()
