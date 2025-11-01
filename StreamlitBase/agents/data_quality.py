from .base import BaseAgent
from ..db_utils import execute_query, execute_write_query
import pandas as pd

class DataQualityGuardian(BaseAgent):
    def __init__(self):
        super().__init__("DataQualityGuardian")
        
    def run(self):
        self.log("start", "Iniciando verificación de calidad")
        try:
            issues = self.check_data_quality()
            self.log("complete", f"Verificación completada. {len(issues)} problemas encontrados")
            return True
        except Exception as e:
            self.log("error", str(e), "error")
            return False
            
    def check_data_quality(self):
        issues = []
        for table in self._get_monitored_tables():
            df = execute_query(f"SELECT * FROM {table}")
            if df.empty:
                continue
                
            # Verificar completitud
            null_counts = df.isnull().sum()
            for column, nulls in null_counts.items():
                if nulls > 0:
                    issues.append({
                        'dataset_name': table,
                        'issue_type': 'completeness',
                        'severity': 'alta' if nulls/len(df) > 0.1 else 'media',
                        'description': f"Columna {column} tiene {nulls} valores nulos",
                        'affected_rows': int(nulls)
                    })
        return issues
        
    def _get_monitored_tables(self):
        return ['ventas_diarias', 'dataset_catalog', 'quality_metrics']
