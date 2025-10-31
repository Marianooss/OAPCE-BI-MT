"""
Anomaly Detector (AD) - Agente 8
Módulo para detectar comportamientos atípicos en métricas clave
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import get_db
from models import AnomalyAlert, AnomalyMetric, Factura, Cobranza, MovimientoCaja, Cliente, Vendedor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Detector de anomalías para métricas clave del sistema OAPCE
    """

    def __init__(self):
        self.db = get_db()
        self.model_configs = {
            'isolation_forest': {
                'contamination': 0.1,
                'n_estimators': 100,
                'max_features': 1.0,
                'random_state': 42
            },
            'prophet': {
                'yearly_seasonality': True,
                'weekly_seasonality': True,
                'seasonality_mode': 'additive'
            },
            'zscore': {
                'threshold': 3.0,
                'window_size': 30
            }
        }

    def detect_anomalies_sales(self, lookback_days: int = 90) -> Dict:
        """
        Detecta anomalías en ventas usando múltiples métodos
        """
        logger.info(f"Detectando anomalías en ventas (últimos {lookback_days} días)")

        try:
            # Obtener datos de ventas históricas
            sales_data = self._get_sales_timeseries(lookback_days)
            if len(sales_data) < 10:
                return {"success": False, "error": "Insuficientes datos históricos de ventas"}

            anomalias_totales = []

            # Método 1: Isolation Forest para detección no supervisada
            try:
                anomalias_if = self.detect_with_isolation_forest(sales_data, "sales_total")
                anomalias_totales.extend(anomalias_if)
            except Exception as e:
                logger.warning(f"Error en Isolation Forest: {str(e)}")

            # Método 2: Prophet para series temporales con estacionalidad
            try:
                anomalias_prophet = self.detect_with_prophet(sales_data, "sales_total")
                anomalias_totales.extend(anomalias_prophet)
            except Exception as e:
                logger.warning(f"Error en Prophet: {str(e)}")

            # Método 3: Z-score dinámico
            try:
                anomalias_zscore = self.calculate_dynamic_zscore(sales_data, "sales_total")
                anomalias_totales.extend(anomalias_zscore)
            except Exception as e:
                logger.warning(f"Error en Z-score: {str(e)}")

            # Filtrar y deduplicar anomalías
            anomalias_filtradas = self._filter_anomalies(anomalias_totales)

            # Guardar anomalías en base de datos
            anomalias_guardadas = []
            for anomalia in anomalias_filtradas:
                alert_id = self._save_anomaly_alert(anomalia)
                if alert_id:
                    anomalias_guardadas.append({**anomalia, 'alert_id': alert_id})

            return {
                "success": True,
                "metric_name": "sales_total",
                "data_points": len(sales_data),
                "anomalies_detected": len(anomalias_filtradas),
                "anomalies_saved": len(anomalias_guardadas),
                "methods_used": ["isolation_forest", "prophet", "zscore"],
                "anomalies": anomalias_guardadas
            }

        except Exception as e:
            logger.error(f"Error detectando anomalías en ventas: {str(e)}")
            return {"success": False, "error": str(e)}

    def detect_anomalies_collections(self, lookback_days: int = 90) -> Dict:
        """
        Detecta anomalías en cobros
        """
        logger.info(f"Detectando anomalías en cobros (últimos {lookback_days} días)")

        try:
            collections_data = self._get_collections_timeseries(lookback_days)
            if len(collections_data) < 10:
                return {"success": False, "error": "Insuficientes datos históricos de cobros"}

            anomalias_totales = []

            # Aplicar métodos de detección
            anomalias_if = self.detect_with_isolation_forest(collections_data, "collections_total")
            anomalias_totales.extend(anomalias_if)

            anomalias_zscore = self.calculate_dynamic_zscore(collections_data, "collections_total")
            anomalias_totales.extend(anomalias_zscore)

            # Filtrar anomalías
            anomalias_filtradas = self._filter_anomalies(anomalias_totales)

            # Guardar anomalías
            anomalias_guardadas = []
            for anomalia in anomalias_filtradas:
                alert_id = self._save_anomaly_alert(anomalia)
                if alert_id:
                    anomalias_guardadas.append({**anomalia, 'alert_id': alert_id})

            return {
                "success": True,
                "metric_name": "collections_total",
                "data_points": len(collections_data),
                "anomalies_detected": len(anomalias_filtradas),
                "anomalies_saved": len(anomalias_guardadas),
                "anomalies": anomalias_guardadas
            }

        except Exception as e:
            logger.error(f"Error detectando anomalías en cobros: {str(e)}")
            return {"success": False, "error": str(e)}

    def detect_with_isolation_forest(self, data: pd.DataFrame, metric_name: str) -> List[Dict]:
        """
        Detecta anomalías usando Isolation Forest
        """
        try:
            from sklearn.ensemble import IsolationForest
            from sklearn.preprocessing import StandardScaler

            # Preparar datos
            X = data[['value']].copy()
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Entrenar modelo
            config = self.model_configs['isolation_forest']
            model = IsolationForest(
                contamination=config['contamination'],
                n_estimators=config['n_estimators'],
                max_features=config['max_features'],
                random_state=config['random_state']
            )

            model.fit(X_scaled)

            # Predecir anomalías
            predictions = model.predict(X_scaled)
            scores = model.decision_function(X_scaled)

            anomalias = []
            for i, (idx, row) in enumerate(data.iterrows()):
                if predictions[i] == -1:  # Anomalía
                    anomalias.append({
                        'timestamp': row['date'],
                        'metric_name': metric_name,
                        'metric_value': float(row['value']),
                        'expected_range_min': float(data['value'].quantile(0.05)),
                        'expected_range_max': float(data['value'].quantile(0.95)),
                        'severity': 'high' if abs(scores[i]) > 0.5 else 'medium',
                        'detection_method': 'isolation_forest',
                        'confidence': float(abs(scores[i])),
                        'notes': f'Anomalía detectada por Isolation Forest. Score: {scores[i]:.3f}'
                    })

            # Guardar métricas del modelo
            self._save_anomaly_metrics(
                model_name='isolation_forest',
                parameters=config,
                dataset_size=len(data)
            )

            logger.info(f"Isolation Forest detectó {len(anomalias)} anomalías en {metric_name}")
            return anomalias

        except ImportError:
            logger.warning("scikit-learn no disponible para Isolation Forest")
            return []
        except Exception as e:
            logger.error(f"Error en Isolation Forest: {str(e)}")
            return []

    def detect_with_prophet(self, data: pd.DataFrame, metric_name: str) -> List[Dict]:
        """
        Detecta anomalías usando Prophet para series temporales
        """
        try:
            from prophet import Prophet
            import matplotlib
            matplotlib.use('Agg')  # Para evitar problemas con display

            # Preparar datos para Prophet
            prophet_data = data[['date', 'value']].copy()
            prophet_data.columns = ['ds', 'y']

            # Entrenar modelo
            config = self.model_configs['prophet']
            model = Prophet(
                yearly_seasonality=config['yearly_seasonality'],
                weekly_seasonality=config['weekly_seasonality'],
                seasonality_mode=config['seasonality_mode']
            )

            model.fit(prophet_data)

            # Generar predicciones
            future = model.make_future_dataframe(periods=0)  # Solo datos históricos
            forecast = model.predict(future)

            # Calcular residuos
            prophet_data['yhat'] = forecast['yhat']
            prophet_data['residual'] = prophet_data['y'] - prophet_data['yhat']

            # Calcular límites de anomalía (3 desviaciones estándar)
            residual_std = prophet_data['residual'].std()
            threshold = 3 * residual_std

            anomalias = []
            for _, row in prophet_data.iterrows():
                if abs(row['residual']) > threshold:
                    severity = 'critical' if abs(row['residual']) > 4 * residual_std else 'high'
                    anomalias.append({
                        'timestamp': row['ds'].date(),
                        'metric_name': metric_name,
                        'metric_value': float(row['y']),
                        'expected_range_min': float(row['yhat'] - threshold),
                        'expected_range_max': float(row['yhat'] + threshold),
                        'severity': severity,
                        'detection_method': 'prophet',
                        'confidence': float(abs(row['residual']) / residual_std),
                        'notes': f'Anomalía detectada por Prophet. Residuo: {row["residual"]:.2f} ({abs(row["residual"])/residual_std:.1f}σ)'
                    })

            logger.info(f"Prophet detectó {len(anomalias)} anomalías en {metric_name}")
            return anomalias

        except ImportError:
            logger.warning("Prophet no disponible")
            return []
        except Exception as e:
            logger.error(f"Error en Prophet: {str(e)}")
            return []

    def calculate_dynamic_zscore(self, data: pd.DataFrame, metric_name: str) -> List[Dict]:
        """
        Calcula Z-score dinámico para detección de anomalías
        """
        try:
            config = self.model_configs['zscore']
            window_size = config['window_size']
            threshold = config['threshold']

            # Asegurar que tenemos suficientes datos
            if len(data) < window_size:
                return []

            data = data.sort_values('date').copy()
            data['rolling_mean'] = data['value'].rolling(window=window_size, min_periods=window_size).mean()
            data['rolling_std'] = data['value'].rolling(window=window_size, min_periods=window_size).std()
            data['zscore'] = (data['value'] - data['rolling_mean']) / data['rolling_std']

            anomalias = []
            for _, row in data.iterrows():
                if pd.notna(row['zscore']) and abs(row['zscore']) > threshold:
                    severity = 'high' if abs(row['zscore']) > 4 else 'medium'
                    anomalias.append({
                        'timestamp': row['date'],
                        'metric_name': metric_name,
                        'metric_value': float(row['value']),
                        'expected_range_min': float(row['rolling_mean'] - threshold * row['rolling_std']),
                        'expected_range_max': float(row['rolling_mean'] + threshold * row['rolling_std']),
                        'severity': severity,
                        'detection_method': 'zscore',
                        'confidence': float(abs(row['zscore'])),
                        'notes': f'Z-score dinámico: {row["zscore"]:.2f} (threshold: {threshold})'
                    })

            logger.info(f"Z-score detectó {len(anomalias)} anomalías en {metric_name}")
            return anomalias

        except Exception as e:
            logger.error(f"Error en cálculo de Z-score: {str(e)}")
            return []

    def _get_sales_timeseries(self, days: int) -> pd.DataFrame:
        """
        Obtiene series temporales de ventas
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            sales = self.db.query(
                Factura.fecha_emision.label('date'),
                Factura.monto_total.label('value')
            ).filter(
                Factura.estado == "Pagada",
                Factura.fecha_emision >= cutoff_date
            ).all()

            df = pd.DataFrame(sales)
            if df.empty:
                return pd.DataFrame()

            # Agrupar por día
            df['date'] = pd.to_datetime(df['date'])
            daily_sales = df.groupby('date')['value'].sum().reset_index()
            daily_sales.columns = ['date', 'value']

            # Rellenar días faltantes con 0
            date_range = pd.date_range(start=daily_sales['date'].min(),
                                     end=daily_sales['date'].max(), freq='D')
            daily_sales = daily_sales.set_index('date').reindex(date_range, fill_value=0).reset_index()
            daily_sales.columns = ['date', 'value']

            return daily_sales.sort_values('date')

        except Exception as e:
            logger.error(f"Error obteniendo series de ventas: {str(e)}")
            return pd.DataFrame()

    def _get_collections_timeseries(self, days: int) -> pd.DataFrame:
        """
        Obtiene series temporales de cobros
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            collections = self.db.query(
                Cobranza.fecha_pago.label('date'),
                Cobranza.monto.label('value')
            ).filter(
                Cobranza.fecha_pago >= cutoff_date
            ).all()

            df = pd.DataFrame(collections)
            if df.empty:
                return pd.DataFrame()

            # Agrupar por día
            df['date'] = pd.to_datetime(df['date'])
            daily_collections = df.groupby('date')['value'].sum().reset_index()
            daily_collections.columns = ['date', 'value']

            # Rellenar días faltantes con 0
            date_range = pd.date_range(start=daily_collections['date'].min(),
                                     end=daily_collections['date'].max(), freq='D')
            daily_collections = daily_collections.set_index('date').reindex(date_range, fill_value=0).reset_index()
            daily_collections.columns = ['date', 'value']

            return daily_collections.sort_values('date')

        except Exception as e:
            logger.error(f"Error obteniendo series de cobros: {str(e)}")
            return pd.DataFrame()

    def _filter_anomalies(self, anomalies: List[Dict]) -> List[Dict]:
        """
        Filtra y deduplica anomalías detectadas por múltiples métodos
        """
        try:
            if not anomalies:
                return []

            # Convertir a DataFrame para facilitar el procesamiento
            df = pd.DataFrame(anomalies)

            # Convertir fechas si es necesario
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])

            # Agrupar por fecha y métrica, mantener la anomalía más severa
            severity_order = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}

            df['severity_score'] = df['severity'].map(severity_order).fillna(1)
            df = df.sort_values(['timestamp', 'severity_score'], ascending=[True, False])

            # Eliminar duplicados por fecha y métrica, manteniendo el más severo
            df_filtered = df.drop_duplicates(subset=['timestamp', 'metric_name'], keep='first')

            return df_filtered.to_dict('records')

        except Exception as e:
            logger.error(f"Error filtrando anomalías: {str(e)}")
            return anomalies

    def _save_anomaly_alert(self, anomaly: Dict) -> Optional[int]:
        """
        Guarda una alerta de anomalía en la base de datos
        """
        try:
            # Verificar si ya existe una alerta similar reciente
            recent_alert = self.db.query(AnomalyAlert).filter(
                AnomalyAlert.metric_name == anomaly['metric_name'],
                AnomalyAlert.timestamp >= datetime.now() - timedelta(hours=24)
            ).first()

            if recent_alert:
                # Actualizar alerta existente si es más severa
                severity_order = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
                existing_severity = severity_order.get(recent_alert.severity, 1)
                new_severity = severity_order.get(anomaly['severity'], 1)

                if new_severity > existing_severity:
                    recent_alert.severity = anomaly['severity']
                    recent_alert.notes = anomaly.get('notes', '')
                    recent_alert.timestamp = datetime.now()
                    self.db.commit()
                    return recent_alert.id
                else:
                    return None  # No guardar, ya existe una alerta similar

            # Crear nueva alerta
            alert = AnomalyAlert(
                metric_name=anomaly['metric_name'],
                metric_value=anomaly['metric_value'],
                expected_range_min=anomaly.get('expected_range_min'),
                expected_range_max=anomaly.get('expected_range_max'),
                severity=anomaly['severity'],
                detection_method=anomaly['detection_method'],
                notes=anomaly.get('notes', ''),
                status='open'
            )

            self.db.add(alert)
            self.db.commit()
            return alert.id

        except Exception as e:
            logger.error(f"Error guardando alerta de anomalía: {str(e)}")
            self.db.rollback()
            return None

    def _save_anomaly_metrics(self, model_name: str, parameters: Dict = None,
                            dataset_size: int = None, evaluation_results: Dict = None):
        """
        Guarda métricas de rendimiento del modelo de anomalías
        """
        try:
            metrics = AnomalyMetric(
                model_name=model_name,
                training_date=datetime.now().date(),
                parameters=json.dumps(parameters) if parameters else None,
                dataset_size=dataset_size
            )

            if evaluation_results:
                metrics.precision = evaluation_results.get('precision')
                metrics.recall = evaluation_results.get('recall')
                metrics.f1_score = evaluation_results.get('f1_score')

            self.db.add(metrics)
            self.db.commit()

        except Exception as e:
            logger.error(f"Error guardando métricas de {model_name}: {str(e)}")
            self.db.rollback()

    def get_anomalies(self, metric_name: str = None, status: str = None,
                     days: int = 30) -> Dict:
        """
        Obtiene anomalías detectadas
        """
        try:
            query = self.db.query(AnomalyAlert)

            if metric_name:
                query = query.filter(AnomalyAlert.metric_name == metric_name)

            if status:
                query = query.filter(AnomalyAlert.status == status)

            # Filtrar por días recientes
            cutoff_date = datetime.now() - timedelta(days=days)
            query = query.filter(AnomalyAlert.timestamp >= cutoff_date)

            anomalies = query.order_by(AnomalyAlert.timestamp.desc()).all()

            results = []
            for alert in anomalies:
                results.append({
                    'id': alert.id,
                    'timestamp': str(alert.timestamp),
                    'metric_name': alert.metric_name,
                    'metric_value': alert.metric_value,
                    'expected_range_min': alert.expected_range_min,
                    'expected_range_max': alert.expected_range_max,
                    'severity': alert.severity,
                    'status': alert.status,
                    'detection_method': alert.detection_method,
                    'assigned_to': alert.assigned_to,
                    'notes': alert.notes
                })

            return {
                "success": True,
                "anomalies": results,
                "count": len(results)
            }

        except Exception as e:
            logger.error(f"Error obteniendo anomalías: {str(e)}")
            return {"success": False, "error": str(e)}

    def acknowledge_anomaly(self, anomaly_id: int, assigned_to: str = None,
                          notes: str = None) -> Dict:
        """
        Confirma recepción de una alerta de anomalía
        """
        try:
            anomaly = self.db.query(AnomalyAlert).filter(AnomalyAlert.id == anomaly_id).first()

            if not anomaly:
                return {"success": False, "error": f"Anomalía {anomaly_id} no encontrada"}

            anomaly.status = "acknowledged"
            if assigned_to:
                anomaly.assigned_to = assigned_to
            if notes:
                anomaly.notes = f"{anomaly.notes or ''}\n[{datetime.now()}] Acknowledged: {notes}".strip()

            self.db.commit()

            return {"success": True, "message": f"Anomalía {anomaly_id} confirmada"}

        except Exception as e:
            logger.error(f"Error confirmando anomalía {anomaly_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    def resolve_anomaly(self, anomaly_id: int, resolution: str) -> Dict:
        """
        Marca una anomalía como resuelta
        """
        try:
            anomaly = self.db.query(AnomalyAlert).filter(AnomalyAlert.id == anomaly_id).first()

            if not anomaly:
                return {"success": False, "error": f"Anomalía {anomaly_id} no encontrada"}

            anomaly.status = "resolved"
            anomaly.notes = f"{anomaly.notes or ''}\n[{datetime.now()}] Resolved: {resolution}".strip()

            self.db.commit()

            return {"success": True, "message": f"Anomalía {anomaly_id} resuelta"}

        except Exception as e:
            logger.error(f"Error resolviendo anomalía {anomaly_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_dashboard_summary(self, days: int = 7) -> Dict:
        """
        Obtiene resumen ejecutivo de anomalías para dashboard
        """
        try:
            # Anomalías por severidad
            severity_counts = {}
            result = self.db.query(AnomalyAlert.severity, AnomalyAlert.status).all()

            for severity, status in result:
                if severity not in severity_counts:
                    severity_counts[severity] = {'total': 0, 'open': 0, 'acknowledged': 0, 'resolved': 0}
                severity_counts[severity]['total'] += 1
                severity_counts[severity][status] += 1

            # Anomalías recientes
            cutoff_date = datetime.now() - timedelta(days=days)
            recent = self.db.query(AnomalyAlert).filter(
                AnomalyAlert.timestamp >= cutoff_date
            ).order_by(AnomalyAlert.timestamp.desc()).limit(10).all()

            recent_anomalies = [{
                'id': a.id,
                'timestamp': str(a.timestamp),
                'metric_name': a.metric_name,
                'metric_value': a.metric_value,
                'severity': a.severity,
                'status': a.status,
                'detection_method': a.detection_method
            } for a in recent]

            return {
                "success": True,
                "severity_summary": severity_counts,
                "recent_anomalies": recent_anomalies,
                "total_anomalies": len(result)
            }

        except Exception as e:
            logger.error(f"Error obteniendo resumen del dashboard: {str(e)}")
            return {"success": False, "error": str(e)}

    def close(self):
        """Cierra la sesión de base de datos"""
        self.db.close()
