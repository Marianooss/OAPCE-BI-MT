"""
Automated Reporting Dispatcher (ARD) - Agente 5
Sistema automatizado de generación y distribución de reportes
"""

import os
import json
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from database import get_db
from models import Usuario
from metrics_hub import MetricsDefinitionHub
from unified_logger import unified_logger
from auth import get_current_user
import logging

logger = logging.getLogger(__name__)

class AutomatedReportingDispatcher:
    """
    Genera y distribuye reportes automáticos por email/Slack
    """

    def __init__(self, user: Optional[Dict] = None):
        self.db = get_db()
        self.mdh = MetricsDefinitionHub()
        self.templates_dir = 'report_templates/'
        self.output_dir = 'generated_reports/'
        self.user = user or get_current_user()

        # Crear directorios necesarios
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        # Configuración por defecto
        self.default_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'sender_email': os.getenv('SENDER_EMAIL', ''),
            'sender_password': os.getenv('SENDER_PASSWORD', ''),
            'webhook_slack': os.getenv('SLACK_WEBHOOK', '')
        }

    def generate_automated_report(self, report_config: Dict) -> Dict:
        """
        Genera un reporte automatizado basado en configuración

        Args:
            report_config: Configuración del reporte (tipo, métricas, destinatarios, etc.)

        Returns:
            Dict con resultado de la generación
        """
        start_time = time.time()

        try:
            # Validar configuración
            self._validate_report_config(report_config)

            # Generar contenido del reporte
            report_data = self._generate_report_content(report_config)

            # Formatear reporte según tipo
            formatted_report = self._format_report(report_config, report_data)

            # Guardar reporte si es necesario
            if report_config.get('save_to_file', True):
                file_path = self._save_report_to_file(formatted_report, report_config)
                report_data['file_path'] = file_path

            # Distribuir reporte
            distribution_results = self._distribute_report(formatted_report, report_config)

            # Registrar actividad
            processing_time = time.time() - start_time
            self._log_report_generation(report_config, processing_time)

            return {
                'success': True,
                'report_type': report_config['type'],
                'recipients': len(report_config.get('recipients', [])),
                'file_generated': report_data.get('file_path', None),
                'distribution_status': distribution_results,
                'processing_time': round(processing_time, 2)
            }

        except Exception as e:
            logger.error(f"Error generando reporte: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'report_type': report_config.get('type', 'unknown')
            }

    def _validate_report_config(self, config: Dict):
        """Valida que la configuración de reporte sea correcta"""
        required_fields = ['type', 'name']

        for field in required_fields:
            if field not in config:
                raise ValueError(f"Campo requerido faltante: {field}")

        if config['type'] not in ['weekly_summary', 'monthly_finance', 'kpi_dashboard', 'anomaly_alert', 'custom']:
            raise ValueError(f"Tipo de reporte inválido: {config['type']}")

        if 'recipients' in config and not isinstance(config['recipients'], list):
            raise ValueError("Los destinatarios deben ser una lista")

    def _generate_report_content(self, config: Dict) -> Dict:
        """Genera el contenido del reporte basado en su configuración"""

        report_type = config['type']
        
        # Personalizar título si el usuario está presente
        user_name = self.user['nombre'] if self.user else 'General'
        title = config.get('title', f'Reporte {report_type.title()} para {user_name}')

        content = {
            'title': title,
            'generated_at': datetime.now().isoformat(),
            'period': config.get('period', 'current'),
            'sections': []
        }

        # Generar contenido según tipo de reporte y rol
        if report_type == 'weekly_summary':
            content['sections'] = self._generate_weekly_summary()
        elif report_type == 'monthly_finance':
            content['sections'] = self._generate_monthly_finance()
        elif report_type == 'kpi_dashboard':
            content['sections'] = self._generate_kpi_dashboard()
        elif report_type == 'anomaly_alert':
            content['sections'] = self._generate_anomaly_alert()
        elif report_type == 'custom':
            content['sections'] = self._generate_custom_report(config)

        return content

    def _generate_weekly_summary(self) -> List[Dict]:
        """Genera resumen semanal de operaciones"""

        sections = [
            {
                'title': '📊 Resumen Ejecutivo',
                'type': 'metrics_summary',
                'data': {
                    'revenue_week': self.mdh.calculate_metric_value('revenue_total'),
                    'new_clients': {'value': 8, 'target': 10},  # Simulado
                    'conversion_rate': self.mdh.calculate_metric_value('conversion_rate'),
                    'satisfaction': self.mdh.calculate_metric_value('customer_satisfaction')
                }
            },
            {
                'title': '🎯 KPIs Principales',
                'type': 'kpi_list',
                'data': [
                    {'name': 'Ingresos Totales', 'value': '$12.5M', 'change': '+8.2%'},
                    {'name': 'Clientes Activos', 'value': '125', 'change': '+12'},
                    {'name': 'Tasa Conversión', 'value': '68.5%', 'change': '+2.1%'}
                ]
            }
        ]

        return sections

    def _generate_monthly_finance(self) -> List[Dict]:
        """Genera reporte mensual financiero"""

        sections = [
            {
                'title': '💰 Situación Financiera',
                'type': 'financial_summary',
                'data': {
                    'total_revenue': '$25.8M',
                    'total_expenses': '$18.2M',
                    'net_profit': '$7.6M',
                    'margin': '29.5%'
                }
            },
            {
                'title': '📊 Estado de Cobranzas',
                'type': 'payment_status',
                'data': {
                    'paid_invoices': 142,
                    'pending_invoices': 23,
                    'overdue_invoices': 8,
                    'payment_rate': '94.2%'
                }
            }
        ]

        return sections

    def _generate_kpi_dashboard(self) -> List[Dict]:
        """Genera dashboard completo de KPIs"""

        # Obtener múltiples métricas del MDH
        all_metrics = self.mdh.get_all_metrics()

        sections = [
            {
                'title': '🎯 KPIs de Ventas',
                'type': 'kpi_grid',
                'data': self._get_metrics_by_category('ventas')
            },
            {
                'title': '📈 KPIs de Marketing',
                'type': 'kpi_grid',
                'data': self._get_metrics_by_category('marketing')
            },
            {
                'title': '💪 KPIs de Operaciones',
                'type': 'kpi_grid',
                'data': self._get_metrics_by_category('operaciones')
            }
        ]

        return sections

    def _generate_anomaly_alert(self) -> List[Dict]:
        """Genera alerta de anomalías detectadas"""

        sections = [
            {
                'title': '🚨 Anomalías Detectadas',
                'type': 'anomaly_list',
                'data': {
                    'critical': [
                        {'metric': 'Ingresos Diarios', 'value': '$85K', 'expected': '$120K', 'deviation': '-29%'}
                    ],
                    'high': [
                        {'metric': 'Clientes Nuevos', 'value': '3', 'expected': '8', 'deviation': '-62%'}
                    ],
                    'medium': []
                }
            },
            {
                'title': '🎯 Recomendaciones',
                'type': 'recommendations',
                'data': [
                    'Revisar campañas de marketing activas',
                    'Contactar a clientes de alto valor con retraso',
                    'Verificar integridad de datos de ingreso'
                ]
            }
        ]

        return sections

    def _generate_custom_report(self, config: Dict) -> List[Dict]:
        """Genera reporte personalizado basado en configuración"""

        sections = []

        if 'custom_metrics' in config:
            sections.append({
                'title': '📊 Métricas Personalizadas',
                'type': 'custom_metrics',
                'data': self._calculate_custom_metrics(config['custom_metrics'])
            })

        if config.get('include_charts', False):
            sections.append({
                'title': '📈 Visualizaciones',
                'type': 'charts',
                'data': ['revenue_trend.png', 'customer_growth.png']
            })

        return sections

    def _calculate_custom_metrics(self, metric_ids: List[str]) -> Dict:
        """Calcula métricas personalizadas especificadas"""

        results = {}
        for metric_id in metric_ids:
            result = self.mdh.calculate_metric_value(metric_id)
            if result['success']:
                results[metric_id] = result['value']

        return results

    def _get_metrics_by_category(self, category: str) -> Dict:
        """Obtiene métricas por categoría del MDH"""

        metrics = self.mdh.get_all_metrics(category=category)

        # Calcular valores actuales
        metric_data = {}
        for metric in metrics[:6]:  # Máximo 6 métricas por sección
            result = self.mdh.calculate_metric_value(metric['id'])
            if result['success']:
                metric_data[metric['name']] = {
                    'value': result['value'],
                    'unit': result.get('unit', ''),
                    'data_type': result.get('data_type', 'number')
                }

        return metric_data

    def _format_report(self, config: Dict, report_data: Dict) -> Dict:
        """Formatea el reporte en diferentes formatos soportados"""

        report_format = config.get('format', 'pdf')

        if report_format == 'pdf':
            return self._format_as_pdf(config, report_data)
        elif report_format == 'excel':
            return self._format_as_excel(config, report_data)
        elif report_format == 'html':
            return self._format_as_html(config, report_data)
        else:  # json por defecto
            return self._format_as_json(config, report_data)

    def _format_as_pdf(self, config: Dict, report_data: Dict) -> Dict:
        """Formatea reporte como PDF"""

        # Esta implementación requeriría reportlab o similar
        # Por ahora, simular generación
        pdf_content = f"""
        <html>
        <head><title>{report_data['title']}</title></head>
        <body>
        <h1>{report_data['title']}</h1>
        <p>Generado: {report_data['generated_at']}</p>
        <h2>Contenido del Reporte</h2>
        <pre>{json.dumps(report_data, indent=2)}</pre>
        </body>
        </html>
        """

        # En implementación real, convertiría HTML a PDF
        return {
            'format': 'pdf',
            'content': base64.b64encode(pdf_content.encode()).decode(),
            'mime_type': 'application/pdf',
            'extension': 'pdf'
        }

    def _format_as_excel(self, config: Dict, report_data: Dict) -> Dict:
        """Formatea reporte como Excel"""

        # Simulación de contenido Excel
        excel_data = {
            'summary_sheet': {
                'title': report_data.get('title', 'Reporte'),
                'generated_at': report_data.get('generated_at'),
                'sections': len(report_data.get('sections', []))
            },
            'data_sheets': report_data.get('sections', [])
        }

        return {
            'format': 'excel',
            'content': base64.b64encode(json.dumps(excel_data).encode()).decode(),
            'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'extension': 'xlsx'
        }

    def _format_as_html(self, config: Dict, report_data: Dict) -> Dict:
        """Formatea reporte como HTML completo"""

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report_data['title']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #f0f2f6; padding: 20px; border-radius: 8px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: white; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report_data['title']}</h1>
                <p>Reporte generado automáticamente - {report_data['generated_at']}</p>
            </div>

            {self._generate_html_sections(report_data.get('sections', []))}

            <div class="footer" style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 5px;">
                <p>Reporte generado por OAPCE BI - Sistema de Inteligencia Artificial</p>
            </div>
        </body>
        </html>
        """

        return {
            'format': 'html',
            'content': base64.b64encode(html_content.encode()).decode(),
            'mime_type': 'text/html',
            'extension': 'html'
        }

    def _generate_html_sections(self, sections: List[Dict]) -> str:
        """Genera HTML para las secciones del reporte"""

        html = ""
        for section in sections:
            section_html = f"""
            <div class="section">
                <h2>{section['title']}</h2>
                <div>
            """

            # Generar contenido específico por tipo
            if section['type'] == 'metrics_summary':
                for key, value in section['data'].items():
                    if isinstance(value, dict):
                        section_html += f'<div class="metric"><strong>{key}:</strong> {value.get("value", "N/A")}</div>'
                    else:
                        section_html += f'<div class="metric"><strong>{key}:</strong> {value}</div>'

            elif section['type'] == 'kpi_list':
                section_html += '<ul>'
                for kpi in section['data']:
                    section_html += '<li class="metric">'
                    section_html += f'<strong>{kpi["name"]}:</strong> {kpi["value"]} ({kpi["change"]})'
                    section_html += '</li>'
                section_html += '</ul>'

            elif section['type'] == 'anomaly_list':
                for severity, anomalies in section['data'].items():
                    if anomalies:
                        section_html += f'<h3>{severity.title()}</h3><ul>'
                        for anomaly in anomalies:
                            section_html += f'<li>{anomaly["metric"]}: {anomaly["value"]} (esperado: {anomaly["expected"]}, desviación: {anomaly["deviation"]})</li>'
                        section_html += '</ul>'

            section_html += "</div></div>"
            html += section_html

        return html

    def _format_as_json(self, config: Dict, report_data: Dict) -> Dict:
        """Formatea reporte como JSON estructurado"""

        return {
            'format': 'json',
            'content': base64.b64encode(json.dumps(report_data, indent=2).encode()).decode(),
            'mime_type': 'application/json',
            'extension': 'json'
        }

    def _save_report_to_file(self, formatted_report: Dict, config: Dict) -> str:
        """Guarda el reporte en un archivo"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{config['type']}_{timestamp}.{formatted_report['extension']}"
        filepath = os.path.join(self.output_dir, filename)

        # Guardar contenido basado en formato
        content_data = base64.b64decode(formatted_report['content'])
        with open(filepath, 'wb') as f:
            f.write(content_data)

        return filepath

    def _distribute_report(self, formatted_report: Dict, config: Dict) -> Dict:
        """Distribuye el reporte a los destinatarios configurados"""

        results = {'email': [], 'slack': []}

        recipients = config.get('recipients', [])
        # Si no hay destinatarios, enviar al usuario actual si existe
        if not recipients and self.user and 'email' in self.user:
            recipients = [self.user['email']]

        # Enviar por email si está configurado
        if recipients and self._is_email_configured():
            email_results = self._send_emails(formatted_report, config, recipients)
            results['email'] = email_results

        # Enviar por Slack si está configurado
        if config.get('slack_notification', False) and self.default_config['webhook_slack']:
            slack_result = self._send_slack_notification(formatted_report, config)
            results['slack'] = slack_result

        return results

    def _send_emails(self, formatted_report: Dict, config: Dict, recipients: List[str]) -> List[Dict]:
        """Envía el reporte por email a múltiples destinatarios"""

        results = []

        # Esta implementación requeriría smtplib
        # Por ahora, simular envíos exitosos
        for recipient in recipients:
            results.append({
                'recipient': recipient,
                'status': 'sent',
                'subject': config.get('title', f'Reporte {config["type"]}')
            })

        return results

    def _send_slack_notification(self, formatted_report: Dict, config: Dict) -> Dict:
        """Envía notificación por Slack"""

        # Simulación de envío a Slack
        return {
            'status': 'sent',
            'channel': '#reportes',
            'message': f'Nuevo reporte generado: {config.get("title", "Reporte Automático")}'
        }

    def _is_email_configured(self) -> bool:
        """Verifica si el envío de emails está configurado"""
        return bool(
            self.default_config['sender_email'] and
            self.default_config['sender_password']
        )

    def _log_report_generation(self, config: Dict, processing_time: float):
        """Registra la generación del reporte"""

        try:
            unified_logger.log_agent_activity(
                agent="ard",
                action="report_generated",
                status="success",
                duration=processing_time,
                details={
                    "report_type": config['type'],
                    "format": config.get('format', 'pdf'),
                    "recipients_count": len(config.get('recipients', [])),
                    "user_role": self.user.get('rol') if self.user else 'anonymous'
                }
            )
        except Exception as e:
            logger.error(f"Error registrando generación de reporte: {str(e)}")

    def schedule_report(self, report_config: Dict, schedule_config: Dict) -> Dict:
        """Programa un reporte para ejecución automática"""

        # Esta implementación requeriría celery o similar
        # Por ahora, simular scheduling
        return {
            'success': True,
            'schedule_id': f"scheduled_{datetime.now().timestamp()}",
            'next_run': schedule_config.get('next_run', 'daily_9am'),
            'frequency': schedule_config.get('frequency', 'daily')
        }

    def get_scheduled_reports(self) -> List[Dict]:
        """Obtiene lista de reportes programados"""

        # Simulación de reportes programados
        return [
            {
                'id': 'weekly_kpi',
                'name': 'KPIs Semanales',
                'type': 'weekly_summary',
                'schedule': 'monday_9am',
                'recipients': ['gerencia@empresa.cl', 'ventas@empresa.cl'],
                'active': True
            },
            {
                'id': 'monthly_finance',
                'name': 'Finanzas Mensuales',
                'type': 'monthly_finance',
                'schedule': 'month_first_8am',
                'recipients': ['contabilidad@empresa.cl'],
                'active': True
            }
        ]

    def close(self):
        """Cierra conexiones"""
        self.db.close()
        self.mdh.close()


# Ejemplos de uso y configuración
def create_sample_report_configs():
    """Crea configuraciones de reporte de ejemplo"""

    configs = [
        {
            'type': 'weekly_summary',
            'name': 'Resumen Semanal Ejecutivo',
            'title': 'Resumen Ejecutivo - Semana {week_number}',
            'format': 'pdf',
            'recipients': ['ceo@empresa.cl', 'gerentes@empresa.cl'],
            'slack_notification': True
        },
        {
            'type': 'kpi_dashboard',
            'name': 'Dashboard KPIs Mensual',
            'title': 'Tablero de Control - {month_year}',
            'format': 'excel',
            'recipients': ['analistas@empresa.cl'],
            'save_to_file': True
        },
        {
            'type': 'anomaly_alert',
            'name': 'Alerta Anomalías',
            'title': '⚠️ Anomalías Detectadas - Acción Requerida',
            'format': 'html',
            'recipients': ['it@empresa.cl'],
            'slack_notification': True
        }
    ]

    return configs


if __name__ == "__main__":
    # Test básico del ARD
    ard = AutomatedReportingDispatcher()

    # Crear reporte de ejemplo
    config = {
        'type': 'weekly_summary',
        'name': 'Test Report',
        'format': 'html'
    }

    print("Generando reporte de prueba...")
    result = ard.generate_automated_report(config)
    print(f"Resultado: {result}")

    ard.close()
