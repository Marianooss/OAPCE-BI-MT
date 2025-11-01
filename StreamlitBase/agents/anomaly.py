from .base import BaseAgent
from ..db_utils import execute_query, execute_write_query
import numpy as np
from datetime import datetime

class AnomalyDetector(BaseAgent):
    def __init__(self):
        super().__init__("AnomalyDetector")
        
    def run(self):
        self.log("start", "Iniciando detección de anomalías")
        try:
            self.detect_sales_anomalies()
            self.log("complete", "Detección completada")
            return True
        except Exception as e:
            self.log("error", str(e), "error")
            return False
            
    def detect_sales_anomalies(self):
        df = execute_query("SELECT fecha, monto FROM ventas_diarias ORDER BY fecha DESC LIMIT 30")
        if df.empty:
            return
            
        mean = df['monto'].mean()
        std = df['monto'].std()
        threshold = 3
        
        for _, row in df.iterrows():
            z_score = abs(row['monto'] - mean) / std
            if z_score > threshold:
                execute_write_query("""
                    INSERT INTO anomalies (detected_date, description, status)
                    VALUES (?, ?, ?)
                """, (row['fecha'], f"Venta anómala detectada: ${row['monto']:,.2f}", 'Abierta'))
