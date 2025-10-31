"""
Predictive Model Engine (PME) - Agente 3
Módulo para entrenar, evaluar y servir modelos predictivos
"""

import json
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import get_db
from models import ModelPrediction, ModelMetric, Cliente, Factura, Vendedor, ActividadVenta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictiveModelEngine:
    """
    Motor de modelos predictivos para el sistema OAPCE
    """

    def __init__(self):
        self.db = get_db()
        self.models = {}

    def train_sales_forecast_model(self, forecast_horizon_days: int = 30) -> Dict:
        """
        Entrena modelo de predicción de ventas usando Prophet
        """
        try:
            start_time = time.time()

            # Obtener datos históricos de ventas (últimos 6 meses)
            cutoff_date = datetime.now() - timedelta(days=180)

            # Agregar datos de facturas pagadas
            sales_data = self.db.query(
                Factura.fecha_emision,
                Factura.monto_total
            ).filter(
                Factura.estado == "Pagada",
                Factura.fecha_emision >= cutoff_date
            ).order_by(Factura.fecha_emision).all()

            if len(sales_data) < 10:
                logger.warning(f"Solo {len(sales_data)} puntos de venta disponibles, usando fallback simple")
                # Usar datos de ejemplo para hacer funcionar la demo
                return self._generate_demo_sales_forecast(forecast_horizon_days)

            # Crear DataFrame para Prophet
            df = pd.DataFrame(sales_data, columns=['ds', 'y'])
            df['ds'] = pd.to_datetime(df['ds'])

            # Agregar datos faltantes (rellenar con 0)
            date_range = pd.date_range(start=df['ds'].min(), end=df['ds'].max(), freq='D')
            df = df.set_index('ds').reindex(date_range, fill_value=0).reset_index()
            df.columns = ['ds', 'y']

            # Entrenar modelo Prophet
            try:
                from prophet import Prophet
                model = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=True,
                    daily_seasonality=False
                )
                model.fit(df)

                # Generar predicciones
                future_dates = model.make_future_dataframe(periods=forecast_horizon_days)
                forecast = model.predict(future_dates)

                # Guardar predicciones en BD
                predictions_saved = 0
                for _, row in forecast.tail(forecast_horizon_days).iterrows():
                    prediction = ModelPrediction(
                        model_name="sales_prophet",
                        prediction_type="sales_forecast",
                        target_date=row['ds'].date(),
                        predicted_value=float(row['yhat']),
                        confidence_interval_lower=float(row['yhat_lower']),
                        confidence_interval_upper=float(row['yhat_upper']),
                        input_features=json.dumps({
                            "historical_data_points": len(df),
                            "training_period_days": 180
                        })
                    )
                    self.db.add(prediction)
                    predictions_saved += 1

                self.db.commit()

                # Calcular métricas del modelo
                training_time = time.time() - start_time
                self._save_model_metrics("sales_prophet", df, training_time)

                return {
                    "success": True,
                    "model_name": "sales_prophet",
                    "predictions_saved": predictions_saved,
                    "training_time": training_time,
                    "historical_data_points": len(df)
                }

            except ImportError:
                # Fallback sin Prophet - usar media móvil simple
                logger.warning("Prophet no disponible, usando modelo simple")
                return self._train_simple_sales_forecast(df, forecast_horizon_days)

        except Exception as e:
            logger.error(f"Error entrenando modelo de ventas: {str(e)}")
            return {"success": False, "error": str(e)}

    def _train_simple_sales_forecast(self, df: pd.DataFrame, horizon: int) -> Dict:
        """
        Modelo simple de predicción de ventas usando media móvil
        """
        try:
            start_time = time.time()

            # Calcular media móvil de 30 días
            df['ma_30'] = df['y'].rolling(window=30, min_periods=1).mean()

            # Predecir usando la media reciente
            recent_avg = df['ma_30'].tail(30).mean()

            predictions_saved = 0
            for i in range(1, horizon + 1):
                target_date = df['ds'].max() + timedelta(days=i)

                prediction = ModelPrediction(
                    model_name="sales_simple_ma",
                    prediction_type="sales_forecast",
                    target_date=target_date.date(),
                    predicted_value=float(recent_avg),
                    input_features=json.dumps({
                        "method": "moving_average_30d",
                        "historical_data_points": len(df)
                    })
                )
                self.db.add(prediction)
                predictions_saved += 1

            self.db.commit()

            training_time = time.time() - start_time
            self._save_model_metrics("sales_simple_ma", df, training_time)

            return {
                "success": True,
                "model_name": "sales_simple_ma",
                "predictions_saved": predictions_saved,
                "training_time": training_time
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def train_risk_assessment_model(self) -> Dict:
        """
        Entrena modelo de evaluación de riesgo de morosidad usando XGBoost
        """
        try:
            start_time = time.time()

            # Obtener datos de clientes con historial de pagos
            clients_data = self.db.query(
                Cliente.id,
                Cliente.fecha_ingreso,
                Cliente.valor_estimado
            ).all()

            # Crear features para cada cliente
            X = []
            y = []

            for client in clients_data:
                client_id, fecha_ingreso, valor_estimado = client

                # Calcular features de riesgo
                features = self._calculate_risk_features(client_id)
                X.append(features)

                # Determinar si es de alto riesgo (facturas vencidas > 30 días)
                risk_label = self._calculate_risk_label(client_id)
                y.append(risk_label)

            if len(X) < 10:
                logger.warning(f"Solo {len(X)} puntos de datos de clientes disponibles, usando fallback demo")
                return self._generate_demo_risk_predictions(clients_data)

            X = np.array(X)
            y = np.array(y)

            # Entrenar modelo XGBoost con fallback robusto
            try:
                from xgboost import XGBClassifier
                from sklearn.model_selection import train_test_split
                from sklearn.metrics import accuracy_score, precision_score, recall_score

                # Check if we have both classes - if not, use simple fallback
                if sum(y) == 0:
                    logger.warning("Todos los clientes son de bajo riesgo, usando modelo simple")
                    return self._generate_simple_risk_predictions(clients_data)

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                model = XGBClassifier(
                    n_estimators=50,  # Reducido para ser más robusto
                    max_depth=3,
                    learning_rate=0.1,
                    random_state=42,
                    objective='binary:logistic',
                    eval_metric='logloss',
                    booster='gbtree'
                )
                model.fit(X_train, y_train)

                # Evaluar modelo
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, zero_division=0)
                recall = recall_score(y_test, y_pred, zero_division=0)

                # Guardar métricas
                training_time = time.time() - start_time
                self._save_model_metrics("risk_xgboost", pd.DataFrame(X), training_time, {
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "test_size": len(X_test)
                })

                # Generar predicciones para todos los clientes
                predictions_saved = 0
                risk_probs = model.predict_proba(X)[:, 1]  # Probabilidad de riesgo

                for i, client in enumerate(clients_data):
                    prediction = ModelPrediction(
                        model_name="risk_xgboost",
                        prediction_type="risk_assessment",
                        target_date=datetime.now().date(),
                        predicted_value=float(risk_probs[i]),
                        entity_id=client[0],
                        entity_type="cliente",
                        input_features=json.dumps({
                            "features_used": list(range(len(features))),
                            "model_accuracy": accuracy
                        })
                    )
                    self.db.add(prediction)
                    predictions_saved += 1

                self.db.commit()

                return {
                    "success": True,
                    "model_name": "risk_xgboost",
                    "predictions_saved": predictions_saved,
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "training_time": training_time,
                    "predictions": self.get_predictions(prediction_type="risk_assessment", limit=predictions_saved)['predictions']
                }

            except (ImportError, Exception) as e:
                logger.warning(f"Error con XGBoost: {str(e)}, usando fallback simple")
                return self._generate_simple_risk_predictions(clients_data)

        except Exception as e:
            logger.error(f"Error entrenando modelo de riesgo: {str(e)}")
            return {"success": False, "error": str(e)}

    def _calculate_risk_features(self, client_id: int) -> List[float]:
        """
        Calcula features para evaluación de riesgo de un cliente
        """
        # Días desde ingreso
        client = self.db.query(Cliente).filter(Cliente.id == client_id).first()

        days_since_entry = 0
        if client and client.fecha_ingreso:
            days_since_entry = (datetime.now().date() - client.fecha_ingreso).days

        # Estadísticas de facturas
        invoices = self.db.query(Factura).filter(Factura.cliente_id == client_id).all()

        total_invoices = len(invoices)
        paid_invoices = len([i for i in invoices if i.estado == "Pagada"])
        overdue_invoices = len([i for i in invoices if i.estado == "Vencida"])

        total_amount = sum(i.monto_total for i in invoices)
        paid_amount = sum(i.monto_pagado for i in invoices if i.estado == "Pagada")

        # Payment ratio
        payment_ratio = paid_amount / total_amount if total_amount > 0 else 0

        # Days overdue average
        overdue_days = []
        for invoice in invoices:
            if invoice.estado == "Vencida":
                days_overdue = (datetime.now().date() - invoice.fecha_vencimiento).days
                overdue_days.append(max(0, days_overdue))

        avg_overdue_days = np.mean(overdue_days) if overdue_days else 0

        return [
            float(days_since_entry),
            float(total_invoices),
            float(paid_invoices),
            float(overdue_invoices),
            float(total_amount),
            float(payment_ratio),
            float(avg_overdue_days)
        ]

    def _calculate_risk_label(self, client_id: int) -> int:
        """
        Determina si un cliente es de alto riesgo (1) o bajo riesgo (0)
        """
        invoices = self.db.query(Factura).filter(Factura.cliente_id == client_id).all()

        high_risk_count = 0
        for invoice in invoices:
            if invoice.estado == "Vencida":
                days_overdue = (datetime.now().date() - invoice.fecha_vencimiento).days
                if days_overdue > 30:  # Más de 30 días vencido
                    high_risk_count += 1

        # Alto riesgo si tiene más de 2 facturas vencidas > 30 días
        return 1 if high_risk_count >= 2 else 0

    def train_conversion_probability_model(self) -> Dict:
        """
        Entrena modelo de probabilidad de cierre de oportunidades usando LightGBM
        """
        try:
            start_time = time.time()

            # Obtener datos de clientes con estado de funnel
            clients_data = self.db.query(
                Cliente.id,
                Cliente.estado_funnel,
                Cliente.fecha_ingreso,
                Cliente.valor_estimado
            ).all()

            if len(clients_data) < 10:
                logger.warning(f"Solo {len(clients_data)} puntos de datos de clientes disponibles, usando fallback demo")
                return self._generate_demo_conversion_predictions(clients_data)

            # Crear features
            X = []
            y = []

            for client in clients_data:
                client_id, estado_funnel, fecha_ingreso, valor_estimado = client

                # Get client name for activity matching
                cliente_obj = self.db.query(Cliente).filter(Cliente.id == client_id).first()
                client_name = cliente_obj.nombre if cliente_obj else ""

                # Count activities by matching client name (since ActividadVenta doesn't have cliente_id)
                activities_count = self.db.query(ActividadVenta).filter(
                    ActividadVenta.cliente_nombre.ilike(f"%{client_name}%")
                ).count()

                features = [
                    float((datetime.now().date() - fecha_ingreso).days),  # Días en funnel
                    float(valor_estimado or 0),  # Valor estimado
                    float(activities_count),  # Número de actividades
                ]

                # Estado actual del funnel (convertido a numérico)
                funnel_states = {
                    "Prospecto": 0,
                    "Contactado": 1,
                    "Calificado": 2,
                    "Propuesta": 3,
                    "Negociación": 4,
                    "Ganado": 5,
                    "Perdido": 6
                }

                current_stage = funnel_states.get(estado_funnel.value, 0)
                features.append(float(current_stage))

                X.append(features)

                # Target: 1 si ganado, 0 si perdido o en proceso
                target = 1 if estado_funnel.value == "Ganado" else 0
                y.append(target)

            X = np.array(X)
            y = np.array(y)

            # Entrenar modelo
            try:
                from lightgbm import LGBMClassifier
                from sklearn.model_selection import train_test_split
                from sklearn.metrics import roc_auc_score

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                model = LGBMClassifier(
                    n_estimators=100,
                    max_depth=3,
                    learning_rate=0.1,
                    random_state=42
                )
                model.fit(X_train, y_train)

                # Evaluar modelo
                y_pred_proba = model.predict_proba(X_test)[:, 1]
                auc_score = roc_auc_score(y_test, y_pred_proba)

                # Generar predicciones de probabilidad de conversión
                predictions_saved = 0
                conversion_probs = model.predict_proba(X)[:, 1]

                for i, client in enumerate(clients_data):
                    prediction = ModelPrediction(
                        model_name="conversion_lgbm",
                        prediction_type="conversion_probability",
                        target_date=datetime.now().date(),
                        predicted_value=float(conversion_probs[i]),
                        entity_id=client[0],
                        entity_type="cliente",
                        input_features=json.dumps({
                            "auc_score": auc_score,
                            "features_used": ["dias_en_funnel", "valor_estimado", "num_actividades", "estado_actual"]
                        })
                    )
                    self.db.add(prediction)
                    predictions_saved += 1

                self.db.commit()

                # Guardar métricas
                training_time = time.time() - start_time
                self._save_model_metrics("conversion_lgbm", pd.DataFrame(X), training_time, {
                    "auc": auc_score,
                    "test_size": len(X_test)
                })

                return {
                    "success": True,
                    "model_name": "conversion_lgbm",
                    "predictions_saved": predictions_saved,
                    "auc_score": auc_score,
                    "training_time": training_time,
                    "predictions": self.get_predictions(prediction_type="conversion_probability", limit=predictions_saved)['predictions']
                }

            except ImportError:
                return {"success": False, "error": "LightGBM no disponible. Instalar con: pip install lightgbm"}

        except Exception as e:
            logger.error(f"Error entrenando modelo de conversión: {str(e)}")
            return {"success": False, "error": str(e)}

    def _save_model_metrics(self, model_name: str, data: pd.DataFrame, training_time: float,
                           additional_metrics: Dict = None):
        """
        Guarda métricas del modelo en la base de datos
        """
        try:
            metrics_to_save = [
                ("training_time", training_time, {"unit": "seconds"}),
                ("dataset_size", len(data), {"description": "training_samples"})
            ]

            if additional_metrics:
                for metric_name, value in additional_metrics.items():
                    metrics_to_save.append((metric_name, value, {}))

            for metric_type, value, info in metrics_to_save:
                metric = ModelMetric(
                    model_name=model_name,
                    metric_date=datetime.now().date(),
                    metric_type=metric_type,
                    metric_value=float(value),
                    dataset_size=len(data),
                    training_time_seconds=training_time,
                    additional_info=json.dumps(info)
                )
                self.db.add(metric)

            self.db.commit()

        except Exception as e:
            logger.error(f"Error guardando métricas del modelo {model_name}: {str(e)}")

    def get_predictions(self, prediction_type: str = None, entity_type: str = None,
                       entity_id: int = None, limit: int = 50) -> Dict:
        """
        Obtiene predicciones almacenadas
        """
        try:
            query = self.db.query(ModelPrediction)

            if prediction_type:
                query = query.filter(ModelPrediction.prediction_type == prediction_type)
            if entity_type:
                query = query.filter(ModelPrediction.entity_type == entity_type)
            if entity_id:
                query = query.filter(ModelPrediction.entity_id == entity_id)

            predictions = query.order_by(
                ModelPrediction.created_at.desc()
            ).limit(limit).all()

            results = []
            for pred in predictions:
                results.append({
                    "id": pred.id,
                    "model_name": pred.model_name,
                    "prediction_type": pred.prediction_type,
                    "target_date": str(pred.target_date),
                    "predicted_value": pred.predicted_value,
                    "confidence_lower": pred.confidence_interval_lower,
                    "confidence_upper": pred.confidence_interval_upper,
                    "entity_id": pred.entity_id,
                    "entity_type": pred.entity_type,
                    "created_at": str(pred.created_at)
                })

            return {
                "success": True,
                "predictions": results,
                "count": len(results)
            }

        except Exception as e:
            logger.error(f"Error obteniendo predicciones: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_model_metrics(self, model_name: str = None, days: int = 30) -> Dict:
        """
        Obtiene métricas de modelos
        """
        try:
            query = self.db.query(ModelMetric)

            if model_name:
                query = query.filter(ModelMetric.model_name == model_name)

            # Filtrar por días recientes
            cutoff_date = datetime.now() - timedelta(days=days)
            query = query.filter(ModelMetric.created_at >= cutoff_date)

            metrics = query.order_by(ModelMetric.created_at.desc()).all()

            results = []
            for metric in metrics:
                results.append({
                    "model_name": metric.model_name,
                    "metric_date": str(metric.metric_date),
                    "metric_type": metric.metric_type,
                    "metric_value": metric.metric_value,
                    "dataset_size": metric.dataset_size,
                    "training_time": metric.training_time_seconds,
                    "additional_info": json.loads(metric.additional_info) if metric.additional_info else {}
                })

            return {
                "success": True,
                "metrics": results,
                "count": len(results)
            }

        except Exception as e:
            logger.error(f"Error obteniendo métricas: {str(e)}")
            return {"success": False, "error": str(e)}

    def _generate_simple_risk_predictions(self, clients_data):
        """
        Genera predicciones de riesgo simples para cuando XGBoost falla
        """
        try:
            start_time = time.time()

            predictions_saved = 0
            for client in clients_data:
                client_id = client[0]

                # Calcular riesgo basado en reglas simples
                features = self._calculate_risk_features(client_id)
                risk_label = self._calculate_risk_label(client_id)

                # Convertir a probabilidad: altos riesgo = 0.8+, medio riesgo = 0.4-0.8, bajo riesgo = 0.1-0.4
                if risk_label == 1:  # Alto riesgo
                    risk_probability = 0.8 + np.random.random() * 0.15  # 0.8 - 0.95
                elif features[3] > 0:  # Tiene facturas vencidas pero no severas
                    risk_probability = 0.4 + np.random.random() * 0.4  # 0.4 - 0.8
                else:  # Bajo riesgo
                    risk_probability = 0.05 + np.random.random() * 0.35  # 0.05 - 0.4

                prediction = ModelPrediction(
                    model_name="risk_simple",
                    prediction_type="risk_assessment",
                    target_date=datetime.now().date(),
                    predicted_value=float(risk_probability),
                    entity_id=client_id,
                    entity_type="cliente",
                    input_features=json.dumps({
                        "method": "rule_based_fallback",
                        "features_evaluated": len(features)
                    })
                )
                self.db.add(prediction)
                predictions_saved += 1

            self.db.commit()

            training_time = time.time() - start_time

            return {
                "success": True,
                "model_name": "risk_simple",
                "predictions_saved": predictions_saved,
                "training_time": training_time,
                "rule_based": True,
                "predictions": self.get_predictions(prediction_type="risk_assessment", limit=predictions_saved)['predictions']
            }

        except Exception as e:
            logger.error(f"Error generando predicciones de riesgo simples: {str(e)}")
            return {"success": False, "error": str(e)}

    def _generate_demo_risk_predictions(self, clients_data: List[Tuple]) -> Dict:
        """
        Genera predicciones de riesgo demo sintéticas para la funcionalidad del agente
        cuando no hay suficientes datos para entrenar un modelo real.
        """
        try:
            start_time = time.time()
            predictions_saved = 0

            for client in clients_data:
                client_id = client[0]
                
                # Simular una probabilidad de riesgo aleatoria
                risk_probability = np.random.uniform(0.05, 0.95) # Entre 5% y 95%

                prediction = ModelPrediction(
                    model_name="risk_demo",
                    prediction_type="risk_assessment",
                    target_date=datetime.now().date(),
                    predicted_value=float(risk_probability),
                    entity_id=client_id,
                    entity_type="cliente",
                    input_features=json.dumps({
                        "method": "demo_synthetic_data",
                        "simulated_range": "0.05-0.95"
                    })
                )
                self.db.add(prediction)
                predictions_saved += 1

            self.db.commit()

            training_time = time.time() - start_time

            return {
                "success": True,
                "model_name": "risk_demo",
                "predictions_saved": predictions_saved,
                "training_time": training_time,
                "demo_data": True,
                "predictions": self.get_predictions(prediction_type="risk_assessment", limit=predictions_saved)['predictions']
            }

        except Exception as e:
            logger.error(f"Error generando predicciones de riesgo demo: {str(e)}")
            return {"success": False, "error": str(e)}

    def _generate_demo_conversion_predictions(self, clients_data: List[Tuple]) -> Dict:
        """
        Genera predicciones de probabilidad de conversión demo sintéticas para la funcionalidad del agente
        cuando no hay suficientes datos para entrenar un modelo real.
        """
        try:
            start_time = time.time()
            predictions_saved = 0

            for client in clients_data:
                client_id = client[0]
                
                # Simular una probabilidad de conversión aleatoria
                conversion_probability = np.random.uniform(0.1, 0.9) # Entre 10% y 90%

                prediction = ModelPrediction(
                    model_name="conversion_demo",
                    prediction_type="conversion_probability",
                    target_date=datetime.now().date(),
                    predicted_value=float(conversion_probability),
                    entity_id=client_id,
                    entity_type="cliente",
                    input_features=json.dumps({
                        "method": "demo_synthetic_data",
                        "simulated_range": "0.1-0.9"
                    })
                )
                self.db.add(prediction)
                predictions_saved += 1

            self.db.commit()

            training_time = time.time() - start_time

            return {
                "success": True,
                "model_name": "conversion_demo",
                "predictions_saved": predictions_saved,
                "training_time": training_time,
                "demo_data": True,
                "predictions": self.get_predictions(prediction_type="conversion_probability", limit=predictions_saved)['predictions']
            }

        except Exception as e:
            logger.error(f"Error generando predicciones de conversión demo: {str(e)}")
            return {"success": False, "error": str(e)}

    def _generate_demo_sales_forecast(self, horizon: int) -> Dict:
        """
        Genera predicciones de ventas usando datos demo sintéticos para la funcionalidad del agente
        """
        try:
            start_time = time.time()

            # Generar datos demo sintéticos
            base_revenue = 5000000  # Base de 5M CLP
            predictions_saved = 0

            for i in range(1, horizon + 1):
                target_date = datetime.now().date() + timedelta(days=i)

                # Agregar variación aleatoria para simular fluctuaciones
                variation = np.random.normal(0, 0.1)  # 10% de variación estándar
                predicted_amount = base_revenue * (1 + variation)

                prediction = ModelPrediction(
                    model_name="sales_demo",
                    prediction_type="sales_forecast",
                    target_date=target_date,
                    predicted_value=float(max(0, predicted_amount)),  # No valores negativos
                    input_features=json.dumps({
                        "method": "demo_synthetic_data",
                        "base_revenue": base_revenue,
                        "variation": 0.1
                    })
                )
                self.db.add(prediction)
                predictions_saved += 1

            self.db.commit()

            training_time = time.time() - start_time

            return {
                "success": True,
                "model_name": "sales_demo",
                "predictions_saved": predictions_saved,
                "training_time": training_time,
                "demo_data": True
            }

        except Exception as e:
            logger.error(f"Error generando predicciones demo: {str(e)}")
            return {"success": False, "error": str(e)}

    def close(self):
        """Cierra la sesión de base de datos"""
        self.db.close()
