"""
Metrics Definition Hub (MDH) - Agente 6
Módulo para centralizar y versionar definiciones de métricas clave
"""

import yaml
import json
import os
import time
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
from database import get_db
from models import PredefinedMetric

import logging

logger = logging.getLogger(__name__)

class MetricsDefinitionHub:
    """
    Hub centralizado para definición, versionamiento y gestión de métricas
    """

    def __init__(self, metrics_dir: str = 'metrics/'):
        self.db = get_db()
        self.metrics_dir = metrics_dir
        self.loaded_metrics = {}

        # Crear directorio si no existe
        os.makedirs(self.metrics_dir, exist_ok=True)

        # Cargar métricas al inicializar
        self._load_all_metrics()

    def _load_all_metrics(self) -> None:
        """Carga todas las métricas desde archivos YAML/JSON"""
        try:
            self.loaded_metrics = {}

            if os.path.exists(self.metrics_dir):
                for filename in os.listdir(self.metrics_dir):
                    if filename.endswith(('.yaml', '.yml', '.json')):
                        self._load_metric_file(filename)

            logger.info(f"Cargadas {len(self.loaded_metrics)} métricas desde definiciones")
        except Exception as e:
            logger.error(f"Error cargando métricas: {str(e)}")

    def _load_metric_file(self, filename: str) -> None:
        """Carga una definición de métricas desde archivo"""
        try:
            filepath = os.path.join(self.metrics_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                if filename.endswith('.json'):
                    data = json.load(f)
                else:  # YAML
                    data = yaml.safe_load(f)

            # Procesar todas las métricas en el archivo
            for metric_def in data.get('metrics', []):
                metric_id = metric_def['id']
                self.loaded_metrics[metric_id] = metric_def

        except Exception as e:
            logger.error(f"Error cargando archivo {filename}: {str(e)}")

    def get_metric_definition(self, metric_id: str) -> Optional[Dict]:
        """Obtiene la definición de una métrica por ID"""
        return self.loaded_metrics.get(metric_id)

    def get_all_metrics(self, category: Optional[str] = None) -> List[Dict]:
        """Obtiene todas las métricas, opcionalmente filtradas por categoría"""
        metrics = list(self.loaded_metrics.values())

        if category:
            metrics = [m for m in metrics if m.get('category') == category]

        return sorted(metrics, key=lambda x: x.get('name', ''))

    def validate_metric_definition(self, metric_def: Dict) -> Dict:
        """Valida que una definición de métrica sea correcta"""
        required_fields = ['id', 'name', 'description', 'formula']
        errors = []

        for field in required_fields:
            if field not in metric_def:
                errors.append(f"Campo requerido faltante: {field}")

        # Validar tipos de campos
        if 'data_type' in metric_def:
            valid_types = ['percentage', 'currency', 'number', 'ratio', 'count']
            if metric_def['data_type'] not in valid_types:
                errors.append(f"Tipo de dato inválido: {metric_def['data_type']}. Debe ser uno de {valid_types}")

        if 'aggregation' in metric_def:
            valid_aggs = ['sum', 'avg', 'count', 'min', 'max']
            if metric_def['aggregation'] not in valid_aggs:
                errors.append(f"Agregación inválida: {metric_def['aggregation']}")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def save_metric_definition(self, metric_def: Dict, filename: Optional[str] = None) -> Dict:
        """Guarda una nueva definición de métrica"""
        try:
            # Validar definición
            validation = self.validate_metric_definition(metric_def)
            if not validation['valid']:
                return {
                    'success': False,
                    'errors': validation['errors']
                }

            # Generar nombre de archivo si no proporcionado
            if not filename:
                filename = f"{metric_def['id']}.yaml"

            # Agregar metadata de versioning
            metric_def['created_at'] = datetime.now().isoformat()
            metric_def['version'] = metric_def.get('version', '1.0')

            # Crear archivo
            filepath = os.path.join(self.metrics_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump({'metrics': [metric_def]}, f, default_flow_style=False, allow_unicode=True)

            # Recargar métricas
            self._load_all_metrics()

            return {
                'success': True,
                'metric_id': metric_def['id']
            }

        except Exception as e:
            logger.error(f"Error guardando métrica: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def calculate_metric_value(self, metric_id: str, filters: Optional[Dict] = None) -> Dict:
        """Calcula el valor de una métrica basada en su definición"""
        try:
            metric_def = self.get_metric_definition(metric_id)
            if not metric_def:
                return {'success': False, 'error': f"Métrica no encontrada: {metric_id}"}

            # Obtener fórmula de cálculo
            formula = metric_def['formula']

            # Aquí iría la lógica para ejecutar la fórmula contra la base de datos
            # Por ahora, devolver un valor simulado basado en el tipo
            value = self._execute_formula_simulation(formula, metric_def.get('data_type'))

            return {
                'success': True,
                'metric_id': metric_id,
                'value': value,
                'data_type': metric_def.get('data_type'),
                'unit': metric_def.get('unit', ''),
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error calculando métrica {metric_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _execute_formula_simulation(self, formula: str, data_type: str) -> float:
        """Simula la ejecución de una fórmula (mock temporal)"""
        # Esto sería reemplazado por ejecución real de SQL contra la base de datos

        # Simulaciones basadas en tipo de dato
        if data_type == 'percentage':
            return round(np.random.uniform(85, 98), 1)  # 85-98%
        elif data_type == 'currency':
            return round(np.random.uniform(500000, 2000000), 0)  # CLP
        elif data_type == 'ratio':
            return round(np.random.uniform(0.1, 5.0), 2)  # Tasa
        elif data_type == 'count':
            return int(np.random.uniform(10, 500))
        else:  # number
            return round(np.random.uniform(100, 10000), 2)

    def get_metrics_by_category(self) -> Dict[str, List[Dict]]:
        """Agrupa métricas por categoría"""
        categories = {}
        for metric in self.loaded_metrics.values():
            category = metric.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(metric)

        return categories

    def get_metric_dependencies(self, metric_id: str) -> List[str]:
        """Obtiene métricas dependientes de una métrica específica"""
        dependencies = []
        metric_def = self.get_metric_definition(metric_id)

        if metric_def and 'depends_on' in metric_def:
            dependencies.extend(metric_def['depends_on'])

        return dependencies

    def validate_metric_dependencies(self, metric_def: Dict) -> List[str]:
        """Valida que todas las dependencias de una métrica existan"""
        errors = []

        if 'depends_on' in metric_def:
            for dep_id in metric_def['depends_on']:
                if dep_id not in self.loaded_metrics:
                    errors.append(f"Dependencia no encontrada: {dep_id}")

        return errors

    def sync_to_database(self) -> Dict:
        """Sincroniza definiciones de métricas con la base de datos"""
        try:
            synced_total = 0
            errors_total = 0

            for metric_def in self.loaded_metrics.values():
                try:
                    # Verificar si ya existe
                    existing = self.db.query(PredefinedMetric).filter(
                        PredefinedMetric.id == metric_def['id']
                    ).first()

                    if not existing:
                        # Crear nueva métrica en BD
                        metric_db = PredefinedMetric(
                            id=metric_def['id'],
                            name=metric_def['name'],
                            display_name=metric_def.get('display_name', metric_def['name']),
                            description=metric_def['description'],
                            category=metric_def.get('category', 'general'),
                            data_type=metric_def.get('data_type', 'number'),
                            unit=metric_def.get('unit', ''),
                            formula=json.dumps(metric_def.get('formula', {})),
                            aggregation=metric_def.get('aggregation'),
                            created_at=datetime.now()
                        )
                        self.db.add(metric_db)
                        synced_total += 1

                except Exception as e:
                    logger.error(f"Error sincronizando métrica {metric_def['id']}: {str(e)}")
                    errors_total += 1

            self.db.commit()

            return {
                'success': True,
                'synced': synced_total,
                'errors': errors_total
            }

        except Exception as e:
            logger.error(f"Error en sincronización: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def close(self):
        """Cierra la sesión de base de datos"""
        self.db.close()


# Funciones de utilidad globales
def create_sample_metrics():
    """Crea métricas de ejemplo para demostrar funcionalidad"""
    sample_metrics = [
        {
            'id': 'revenue_total',
            'name': 'Ingresos Totales',
            'display_name': 'Ingresos Totales',
            'description': 'Suma total de todos los ingresos facturados',
            'category': 'ventas',
            'data_type': 'currency',
            'unit': 'CLP',
            'formula': 'SUM(facturas.monto_total) WHERE estado = "Pagada"',
            'aggregation': 'sum'
        },
        {
            'id': 'conversion_rate',
            'name': 'Tasa de Conversión',
            'display_name': 'Tasa de Conversión de Clientes',
            'description': 'Porcentaje de prospectos que se convierten en clientes',
            'category': 'marketing',
            'data_type': 'percentage',
            'unit': '%',
            'formula': '(COUNT(clientes WHERE estado_funnel = "Ganado") / COUNT(clientes WHERE estado_funnel IN ("Contactado", "Calificado", "Propuesta", "Negociación"))) * 100',
            'aggregation': 'ratio',
            'depends_on': ['clientes_activos']
        },
        {
            'id': 'client_lifetime_value',
            'name': 'Valor de Vida del Cliente',
            'display_name': 'CLV - Valor de Vida del Cliente',
            'description': 'Valor promedio de ingresos por cliente a lo largo de su vida',
            'category': 'ventas',
            'data_type': 'currency',
            'unit': 'CLP',
            'formula': 'AVG(clientes.valor_estimado) WHERE active = true',
            'aggregation': 'avg'
        },
        {
            'id': 'customer_satisfaction',
            'name': 'Satisfacción del Cliente',
            'display_name': 'CSAT - Satisfacción del Cliente',
            'description': 'Puntuación promedio de satisfacción en encuestas',
            'category': 'servicio',
            'data_type': 'number',
            'unit': 'puntos',
            'formula': 'AVG(encuestas.score) WHERE tipo = "satisfaccion"',
            'aggregation': 'avg',
            'range_min': 1,
            'range_max': 5
        },
        {
            'id': 'churn_rate',
            'name': 'Tasa de Abandono',
            'display_name': 'Churn Rate - Tasa de Abandono',
            'description': 'Porcentaje de clientes perdidos en los últimos 30 días',
            'category': 'retencion',
            'data_type': 'percentage',
            'unit': '%',
            'formula': '(COUNT(clientes WHERE estado_funnel = "Perdido" AND updated_at >= DATE_SUB(NOW(), 30)) / COUNT(clientes_activos)) * 100',
            'aggregation': 'ratio',
            'depends_on': ['clientes_activos']
        }
    ]

    return sample_metrics


if __name__ == "__main__":
    # Test básico del MDH
    mdh = MetricsDefinitionHub()
    print(f"Métricas cargadas: {len(mdh.loaded_metrics)}")

    # Crear métricas de ejemplo
    metrics_dir = 'metrics/'
    os.makedirs(metrics_dir, exist_ok=True)

    samples = create_sample_metrics()
    with open(os.path.join(metrics_dir, 'sample_metrics.yaml'), 'w', encoding='utf-8') as f:
        yaml.dump({'version': '1.0', 'metrics': samples}, f, default_flow_style=False, allow_unicode=True)

    print(f"Creadas {len(samples)} métricas de ejemplo")
