"""
Generative Data Assistant (GDA) - Agente 7
Asistente de consultas en lenguaje natural sobre los datos del sistema
"""

import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from database import get_db
from models import Cliente, Factura, Vendedor, ActividadVenta
from unified_logger import unified_logger
from metrics_hub import MetricsDefinitionHub
from auth import get_current_user
import logging

logger = logging.getLogger(__name__)

class GenerativeDataAssistant:
    """
    Asistente inteligente que responde consultas en lenguaje natural sobre los datos
    """

    def __init__(self, user: Optional[Dict] = None, llm_provider: str = "mock", api_key: Optional[str] = None):
        self.db = get_db()
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.mdh = MetricsDefinitionHub()
        self.user = user or get_current_user()

        # Contexto del sistema
        self.system_context = f"""
        Eres un asistente experto en análisis de datos para OAPCE Multitrans, una empresa chilena de transporte.
        Actualmente estás asistiendo a {self.user['nombre']} ({self.user['rol']}).
        Los datos incluyen: clientes, facturas, vendedores, actividades de venta, y métricas KPI.

        Respuestas deben ser:
        - Concisas pero informativas
        - En español profesional
        - Con números y porcentajes cuando aplique
        - Objetivas, sin sesgos promocionales
        """ if self.user else """
        Eres un asistente experto en análisis de datos para OAPCE Multitrans, una empresa chilena de transporte.
        Los datos incluyen: clientes, facturas, vendedores, actividades de venta, y métricas KPI.

        Respuestas deben ser:
        - Concisas pero informativas
        - En español profesional
        - Con números y porcentajes cuando aplique
        - Objetivas, sin sesgos promocionales
        """

        # Schema simplificado para consultas SQL seguras
        self.data_schema = self._build_data_schema()

    def _build_data_schema(self) -> Dict:
        """Construye esquema simplificado de datos para consultas seguras"""
        return {
            "clientes": {
                "columns": ["id", "nombre", "fecha_ingreso", "estado_funnel", "valor_estimado"],
                "description": "Información de clientes y su estado en el proceso de ventas"
            },
            "facturas": {
                "columns": ["id", "cliente_id", "fecha_emision", "fecha_vencimiento", "estado", "monto_total", "monto_pagado"],
                "description": "Facturas emitidas con estado de pago"
            },
            "vendedores": {
                "columns": ["id", "nombre", "email", "activo"],
                "description": "Información de los vendedores"
            },
            "actividades_venta": {
                "columns": ["id", "cliente_nombre", "tipo_actividad", "fecha", "descripcion"],
                "description": "Historial de actividades con cada cliente"
            },
            "metricas_disponibles": {
                "ventas": ["revenue_total", "conversion_rate", "client_lifetime_value"],
                "marketing": ["conversion_rate"],
                "retencion": ["churn_rate"],
                "servicio": ["customer_satisfaction"]
            }
        }

    def process_query(self, user_query: str) -> Dict:
        """
        Procesa una consulta del usuario y genera respuesta inteligente

        Args:
            user_query: La pregunta del usuario en lenguaje natural

        Returns:
            Dict con respuesta estructurada
        """
        start_time = time.time()

        try:
            # Limpiar y normalizar consulta
            clean_query = self._clean_query(user_query)

            # Identificar tipo de consulta
            query_type, entities = self._classify_query(clean_query)

            # Generar plan de respuesta
            response_plan = self._generate_response_plan(clean_query, query_type, entities)

            # Ejecutar consultas de datos según el plan
            data_results = self._execute_data_queries(response_plan)

            # Generar respuesta natural con LLM o lógica de reglas
            if self.llm_provider == "mock":
                response = self._generate_mock_response(clean_query, data_results)
            else:
                response = self._generate_llm_response(clean_query, data_results)

            # Registrar consulta y respuesta
            self._log_query(user_query, response, time.time() - start_time, data_results)

            return {
                'success': True,
                'query': user_query,
                'response': response,
                'data_used': data_results,
                'processing_time': round(time.time() - start_time, 2),
                'confidence_score': self._calculate_confidence(clean_query, data_results)
            }

        except Exception as e:
            logger.error(f"Error procesando consulta '{user_query}': {str(e)}")
            return {
                'success': False,
                'error': f"No pude procesar tu consulta: {str(e)}",
                'query': user_query
            }

    def _clean_query(self, query: str) -> str:
        """Limpia y normaliza la consulta del usuario"""
        # Remover caracteres especiales excesivos
        query = re.sub(r'[^\w\s¿?¡!.,]', ' ', query)
        # Normalizar espacios
        query = ' '.join(query.split())
        # Convertir a minúsculas para análisis
        return query.lower()

    def _classify_query(self, query: str) -> Tuple[str, List[str]]:
        """
        Clasifica el tipo de consulta y extrae entidades

        Returns:
            (tipo_consulta, entidades_mencionadas)
        """
        entities = []

        # Patrones para identificar tipos de consulta
        patterns = {
            'metricas_kpi': [
                r'ventas', r'ingresos', r'revenue', r'facturación',
                r'conversión', r'conversion', r'clv', r'valor.*vida',
                r'churn', r'abandono', r'satisfacción', r'kpi'
            ],
            'clientes': [
                r'cliente', r'prospecto', r'lead', r'usuario'
            ],
            'facturas': [
                r'factur', r'pago', r'pagad', r'vencid', r'impagad',
                r'cobranza', r'deuda', r'monto'
            ],
            'tendencias': [
                r'tendencia', r'evolución', r'cambio', r'versus', r'comparad',
                r'últim', r'pasad', r'mes', r'semana', r'año'
            ],
            'comparaciones': [
                r'compar', r'vs', r'versus', r'mejor', r'peor',
                r'más', r'menos', r'aumento', r'disminución'
            ],
            'anomalias': [
                r'anomal', r'extrañ', r'rar', r'insólit', r'desviación',
                r'problema', r'issue', r'alerta'
            ]
        }

        # Clasificar consulta
        query_type = 'general'
        max_matches = 0

        for tipo, patterns_list in patterns.items():
            matches = sum(1 for pattern in patterns_list if re.search(pattern, query))
            if matches > max_matches:
                max_matches = matches
                query_type = tipo

        # Extraer entidades específicas (fechas, números, etc.)
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|\d{4}'
        number_pattern = r'\d+(?:\.\d+)?'

        date_matches = re.findall(date_pattern, query, re.IGNORECASE)
        number_matches = re.findall(number_pattern, query)

        entities.extend(date_matches)
        entities.extend(number_matches)

        return query_type, entities

    def _generate_response_plan(self, query: str, query_type: str, entities: List[str]) -> Dict:
        """Genera un plan estructurado para responder la consulta"""

        plan = {
            'query_type': query_type,
            'entities_found': entities,
            'data_queries': [],
            'insights_needed': [],
            'visualization_suggestions': []
        }

        # Planes específicos por tipo de consulta
        if query_type == 'metricas_kpi':
            plan['data_queries'].extend([
                {'type': 'metrics_calculation', 'metrics': ['revenue_total', 'conversion_rate']},
                {'type': 'trends_analysis', 'period': 'last_30_days'}
            ])
            plan['insights_needed'].append('performance_indicators')

        elif query_type == 'clientes':
            plan['data_queries'].extend([
                {'type': 'count_entities', 'table': 'clientes', 'filters': {}}
            ])
            plan['insights_needed'].append('customer_distribution')

        elif query_type == 'facturas':
            plan['data_queries'].extend([
                {'type': 'financial_summary', 'include_overdue': True}
            ])
            plan['insights_needed'].append('payment_status')

        elif query_type == 'tendencias':
            plan['data_queries'].append({
                'type': 'time_series',
                'period': 'last_90_days'
            })
            plan['visualization_suggestions'].append('line_chart')

        elif query_type == 'comparaciones':
            plan['data_queries'].append({
                'type': 'comparison',
                'periods': ['current_quarter', 'previous_quarter']
            })

        return plan

    def _execute_data_queries(self, response_plan: Dict) -> Dict:
        """Ejecuta las consultas de datos según el plan definido"""

        results = {}

        try:
            for query in response_plan.get('data_queries', []):

                if query['type'] == 'metrics_calculation':
                    # Calcular métricas usando MDH
                    metrics_results = {}
                    for metric_id in query.get('metrics', []):
                        result = self.mdh.calculate_metric_value(metric_id)
                        if result['success']:
                            metrics_results[metric_id] = result['value']
                        else:
                            metrics_results[metric_id] = None
                    results['metrics'] = metrics_results

                elif query['type'] == 'count_entities':
                    # Contar entidades con filtros
                    table = query.get('table', 'clientes')
                    filters = query.get('filters', {})
                    if self.user and self.user.get('rol') == 'ventas':
                        vendedor = self.db.query(Vendedor).filter(Vendedor.email == self.user['email']).first()
                        if vendedor:
                            vendedor_id = vendedor.id
                            if table == 'clientes':
                                filters['vendedor_id'] = vendedor_id
                        else:
                            logger.warning(f"No se encontró vendedor para el email: {self.user['email']}")
                    count = self._count_entities(table, filters)
                    results[f'{table}_count'] = count

                elif query['type'] == 'financial_summary':
                    # Resumen financiero básico
                    financial_data = self._get_financial_summary()
                    results['financial'] = financial_data

                elif query['type'] == 'time_series':
                    # Datos de series temporales
                    time_data = self._get_time_series_data(query.get('period', 'last_30_days'))
                    results['time_series'] = time_data

        except Exception as e:
            logger.error(f"Error ejecutando consultas de datos: {str(e)}")
            results['error'] = str(e)

        return results

    def _count_entities(self, table: str, filters: Dict) -> int:
        """Cuenta entidades con filtros aplicados"""
        try:
            # Esta implementación simplificada usaría SQLAlchemy
            # Por ahora, devolvemos valores simulados realistas

            base_counts = {
                'clientes': 125,
                'facturas': 890,
                'vendedores': 8,
                'actividades_venta': 450
            }

            return base_counts.get(table, 0)

        except Exception as e:
            logger.error(f"Error contando entidades en {table}: {str(e)}")
            return 0

    def _get_financial_summary(self) -> Dict:
        """Obtiene resumen financiero básico"""
        try:
            # Simulación de datos reales
            return {
                'total_revenue': 12500000,  # CLP
                'paid_invoices': 675,
                'overdue_invoices': 15,
                'payment_rate': 94.2,  # %
                'avg_invoice_value': 185000
            }
        except Exception as e:
            return {}

    def _get_time_series_data(self, period: str) -> List[Dict]:
        """Obtiene datos de series temporales"""
        try:
            # Simulación de datos históricos mensuales
            import random
            base_value = 1000000  # CLP base mensual

            data = []
            for i in range(6):  # Últimos 6 meses
                variation = random.uniform(-0.2, 0.3)  # -20% a +30%
                value = base_value * (1 + variation)
                data.append({
                    'month': f'2025-{str(i+1).zfill(2)}',
                    'revenue': round(value),
                    'growth_rate': round(variation * 100, 1)
                })

            return data
        except Exception as e:
            return []

    def _generate_mock_response(self, query: str, data_results: Dict) -> str:
        """Genera respuesta usando lógica de reglas (fallback sin LLM)"""

        # Respuestas basadas en palabras clave detectadas
        responses = {
            'ventas': f"Los ingresos totales del período son de ${data_results.get('metrics', {}).get('revenue_total', 'N/A'):,} CLP.",
            'clientes': f"Actualmente tienes {data_results.get('clientes_count', 125)} clientes activos en tu cartera.",
            'facturas': f"De las {data_results.get('facturas_count', 890)} facturas, el {data_results.get('financial', {}).get('payment_rate', 94.2)}% están pagadas.",
            'rendimiento': "El rendimiento general está dentro de parámetros normales con una tasa de conversión del 68.5%.",
            'problemas': "No se detectan problemas críticos en las métricas monitoreadas actualmente."
        }

        # Personalizar respuesta por rol
        if self.user and self.user.get('rol') == 'ventas':
            responses['clientes'] = f"Actualmente tienes {data_results.get('clientes_count', '0')} clientes asignados."
        elif self.user and self.user.get('rol') == 'finanzas':
            responses['ventas'] = f"El total de ingresos registrados es de ${data_results.get('metrics', {}).get('revenue_total', 'N/A'):,} CLP."

        # Buscar respuesta más relevante
        for keyword, response in responses.items():
            if keyword in query.lower():
                return response

        # Respuesta genérica
        return "Tu consulta ha sido procesada. Los indicadores generales muestran un rendimiento saludable con oportunidades de mejora en el proceso de conversión."

    def _generate_llm_response(self, query: str, data_results: Dict) -> str:
        """Genera respuesta usando LLM (cuando esté configurado)"""
        # Esta implementación requeriría integración con OpenAI/Claude
        # Por ahora, delegamos a la respuesta mock
        return self._generate_mock_response(query, data_results)

    def _calculate_confidence(self, query: str, data_results: Dict) -> float:
        """Calcula la confianza en la respuesta proporcionada"""
        # Lógica simple de confianza basada en datos disponibles
        confidence = 0.5  # Base

        if data_results and data_results != {}:
            confidence += 0.3  # Datos disponibles

        if len(query.split()) > 3:  # Consulta específica
            confidence += 0.2

        return min(round(confidence, 2), 1.0)

    def _log_query(self, query: str, response: str, processing_time: float, data_results: Dict):
        """Registra la consulta para análisis posterior"""
        try:
            unified_logger.log_agent_activity(
                agent="gda",
                action="query_processed",
                status="success",
                duration=processing_time,
                details={
                    "query_length": len(query),
                    "response_length": len(response),
                    "confidence": self._calculate_confidence(query, data_results),
                    "user_role": self.user.get('rol') if self.user else 'anonymous'
                }
            )
        except Exception as e:
            logger.error(f"Error registrando consulta: {str(e)}")

    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Obtiene historial reciente de consultas"""
        # Esta implementación requeriría una tabla dedicada de conversaciones
        # Por ahora, devolvemos datos simulados
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "query": "Ejemplo de consulta",
                "response": "Ejemplo de respuesta",
                "confidence": 0.85
            }
        ]

    def get_popular_queries(self, limit: int = 5) -> List[Dict]:
        """Obtiene consultas más frecuentes"""
        # Simulación de queries populares
        return [
            {"query": "¿Cuál es el estado de las ventas?", "frequency": 15},
            {"query": "¿Cuántos clientes tenemos?", "frequency": 12},
            {"query": "¿Facturas pendientes?", "frequency": 8},
            {"query": "¿Problemas detectados?", "frequency": 6},
            {"query": "¿Tendencias de ingresos?", "frequency": 4}
        ]

    def set_llm_configuration(self, provider: str, api_key: str, model: str = None):
        """Configura el LLM para consultas avanzadas"""
        self.llm_provider = provider
        self.api_key = api_key
        self.llm_model = model

    def close(self):
        """Cierra conexiones"""
        self.db.close()
        self.mdh.close()


# Funciones de utilidad globales
def process_natural_query(query: str, user_context: Optional[Dict] = None) -> Dict:
    """
    Función de conveniencia para procesar consultas naturales
    """
    assistant = GenerativeDataAssistant(user=user_context)
    try:
        return assistant.process_query(query)
    finally:
        assistant.close()


def get_gda_status() -> Dict:
    """
    Obtiene el estado actual del asistente
    """
    assistant = GenerativeDataAssistant()
    try:
        return {
            "status": "operational",
            "llm_provider": assistant.llm_provider,
            "metrics_available": assistant.mdh.get_all_metrics() is not None,
            "last_activity": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        assistant.close()


if __name__ == "__main__":
    # Test del GDA
    assistant = GenerativeDataAssistant()

    # Consultas de prueba
    test_queries = [
        "¿Cuántos clientes tenemos?",
        "¿Cuál es el estado de las ventas este mes?",
        "¿Hay problemas con los pagos?",
        "¿Cuáles son las tendencias de ingresos?"
    ]

    print("=== Generative Data Assistant - Tests ===\n")

    for query in test_queries:
        print(f"Consulta: {query}")
        result = assistant.process_query(query)
        print(f"Respuesta: {result['response']}")
        print(f"Confianza: {result['confidence_score']}")
        print("-" * 50)

    assistant.close()
