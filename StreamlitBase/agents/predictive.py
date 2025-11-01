from .base import BaseAgent
from ..db_utils import execute_query, execute_write_query
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

class PredictiveModelEngine(BaseAgent):
    def __init__(self):
        super().__init__("PredictiveModelEngine")
        
    def predict_sales(self, days_ahead=30):
        """Predice ventas futuras usando regresión lineal simple"""
        try:
            # Obtener datos históricos
            df = execute_query("""
                SELECT fecha as ds, monto as y 
                FROM ventas_diarias 
                ORDER BY fecha
            """)
            
            if df.empty:
                self.log("error", "No hay datos históricos disponibles", "error")
                return False
                
            # Preparar datos para regresión
            df['days_from_start'] = (pd.to_datetime(df['ds']) - pd.to_datetime(df['ds']).min()).dt.days
            X = df[['days_from_start']].values
            y = df['y'].values
            
            # Entrenar modelo
            model = LinearRegression()
            model.fit(X, y)
            
            # Generar predicciones
            last_day = df['days_from_start'].max()
            future_days = np.array(range(last_day + 1, last_day + days_ahead + 1)).reshape(-1, 1)
            predictions = model.predict(future_days)
            
            # Calcular fechas futuras
            last_date = pd.to_datetime(df['ds'].max())
            future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
            
            # Guardar predicciones
            for date, pred in zip(future_dates, predictions):
                confidence = np.std(y) * 2  # Intervalo de confianza simple
                query = """
                INSERT INTO model_predictions 
                (model_name, prediction_date, target_date, metric_name, 
                predicted_value, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                params = (
                    'linear_regression',
                    datetime.now(),
                    date,
                    'daily_sales',
                    float(pred),
                    float(confidence)
                )
                execute_write_query(query, params)
                
            self.log("predict", f"Predicción completada para {days_ahead} días usando regresión lineal")
            return True
            
        except Exception as e:
            self.log("error", f"Error en predicción: {str(e)}", "error")
            return False
            
    def run(self):
        """Ejecuta todas las predicciones configuradas"""
        return self.predict_sales()
