"""
Sistema de Logging Unificado - Agente SI (System Integrator)
Módulo para centralizar logs y monitoreo de todos los agentes
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

class UnifiedLogger:
    """
    Logger unificado para todos los agentes del sistema OAPCE
    """

    def __init__(self, log_dir: str = "logs", max_bytes: int = 10*1024*1024, backup_count: int = 5):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Configurar logger principal
        self.logger = logging.getLogger('oapce_unified')
        self.logger.setLevel(logging.DEBUG)

        # Handler para agentes específicos
        self.agent_loggers = {}

        # Métricas de logging
        self.metrics = {
            "total_logs": 0,
            "error_count": 0,
            "warning_count": 0,
            "agents_active": set(),
            "last_activity": datetime.now()
        }

        # Evitar duplicados de handlers
        if self.logger.handlers:
            return

        # Formatter para logs estructurados
        formatter = logging.Formatter(
            '%(asctime)s | %(agent)s | %(levelname)s | %(message)s | %(extra)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler para archivo general
        general_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'oapce_unified.log',
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        general_handler.setLevel(logging.INFO)
        general_handler.setFormatter(formatter)
        self.logger.addHandler(general_handler)

        # Handler para errores
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'oapce_errors.log',
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)

    def get_agent_logger(self, agent_name: str) -> logging.Logger:
        """
        Obtiene o crea un logger específico para un agente
        """
        if agent_name not in self.agent_loggers:
            agent_logger = logging.getLogger(f'oapce_{agent_name}')
            agent_logger.setLevel(logging.DEBUG)

            # Handler específico del agente
            agent_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / f'{agent_name}.log',
                maxBytes=5*1024*1024,  # 5MB por agente
                backupCount=3
            )

            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s | %(extra)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            agent_handler.setFormatter(formatter)
            agent_logger.addHandler(agent_handler)

            # No propagar al logger padre para evitar duplicados
            agent_logger.propagate = False

            self.agent_loggers[agent_name] = agent_logger

        return self.agent_loggers[agent_name]

    def log(self, agent: str, level: str, message: str, extra: Dict = None, **kwargs):
        """
        Registra un mensaje de log con metadatos
        """
        logger = self.get_agent_logger(agent)

        # Preparar datos extra
        extra_data = extra or {}
        extra_data.update(kwargs)
        extra_data['agent'] = agent

        # Convertir objetos no serializables
        for key, value in extra_data.items():
            if not isinstance(value, (str, int, float, bool, type(None))):
                extra_data[key] = str(value)

        # Crear log record con datos extra
        record = logging.LogRecord(
            name=logger.name,
            level=getattr(logging, level.upper()),
            pathname="",
            lineno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        record.extra = json.dumps(extra_data, default=str)
        record.__dict__['agent'] = agent # Add agent to the record's dict

        # Loguear en el agente específico
        logger.handle(record)

        # También en el logger unificado
        unified_record = logging.LogRecord(
            name=self.logger.name,
            level=getattr(logging, level.upper()),
            pathname="",
            lineno=0,
            msg=f"[{agent}] {message}",
            args=(),
            exc_info=None
        )
        unified_record.extra = json.dumps(extra_data, default=str)
        unified_record.__dict__['agent'] = agent # Add agent to the record's dict
        self.logger.handle(unified_record)

        # Actualizar métricas
        self.metrics["total_logs"] += 1
        self.metrics["agents_active"].add(agent)
        self.metrics["last_activity"] = datetime.now()

        if level.upper() == "ERROR":
            self.metrics["error_count"] += 1
        elif level.upper() == "WARNING":
            self.metrics["warning_count"] += 1

    def info(self, agent: str, message: str, **kwargs):
        """Log a nivel INFO"""
        self.log(agent, "INFO", message, **kwargs)

    def warning(self, agent: str, message: str, **kwargs):
        """Log a nivel WARNING"""
        self.log(agent, "WARNING", message, **kwargs)

    def error(self, agent: str, message: str, **kwargs):
        """Log a nivel ERROR"""
        self.log(agent, "ERROR", message, **kwargs)

    def debug(self, agent: str, message: str, **kwargs):
        """Log a nivel DEBUG"""
        self.log(agent, "DEBUG", message, **kwargs)

    def critical(self, agent: str, message: str, **kwargs):
        """Log a nivel CRITICAL"""
        self.log(agent, "CRITICAL", message, **kwargs)

    def log_agent_activity(self, agent: str, action: str, status: str = "success",
                          duration: float = None, details: Dict = None):
        """
        Log estandarizado para actividades de agentes
        """
        message = f"Agent activity: {action}"

        extra = {
            "action": action,
            "status": status,
            "duration_seconds": duration,
            "details": details or {}
        }

        if status == "success":
            self.info(agent, message, **extra)
        elif status == "warning":
            self.warning(agent, message, **extra)
        else:
            self.error(agent, message, **extra)

    def log_model_training(self, agent: str, model_name: str, dataset_size: int,
                          training_time: float, metrics: Dict = None):
        """
        Log estandarizado para entrenamiento de modelos
        """
        message = f"Model training completed: {model_name}"

        self.info(agent, message,
                 model_name=model_name,
                 dataset_size=dataset_size,
                 training_time_seconds=training_time,
                 metrics=metrics or {})

    def log_prediction(self, agent: str, model_name: str, prediction_type: str,
                      entity_count: int, confidence_avg: float = None):
        """
        Log estandarizado para predicciones generadas
        """
        message = f"Predictions generated: {prediction_type}"

        self.info(agent, message,
                 model_name=model_name,
                 prediction_type=prediction_type,
                 entity_count=entity_count,
                 confidence_avg=confidence_avg)

    def log_recommendation(self, agent: str, recommendation_type: str,
                          priority: str, impact_score: float, client_affected: int = None):
        """
        Log estandarizado para recomendaciones generadas
        """
        message = f"Recommendation generated: {recommendation_type}"

        self.info(agent, message,
                 recommendation_type=recommendation_type,
                 priority=priority,
                 impact_score=impact_score,
                 client_affected=client_affected)

    def get_metrics(self) -> Dict:
        """
        Obtiene métricas actuales del sistema de logging
        """
        return {
            "total_logs": self.metrics["total_logs"],
            "error_count": self.metrics["error_count"],
            "warning_count": self.metrics["warning_count"],
            "error_rate": self.metrics["error_count"] / max(self.metrics["total_logs"], 1),
            "agents_active": list(self.metrics["agents_active"]),
            "last_activity": self.metrics["last_activity"].isoformat(),
            "log_files": self._get_log_files_info()
        }

    def _get_log_files_info(self) -> Dict:
        """
        Obtiene información sobre los archivos de log
        """
        info = {}
        try:
            for log_file in self.log_dir.glob("*.log"):
                stat = log_file.stat()
                info[log_file.name] = {
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
        except Exception:
            pass

        return info

    def get_recent_logs(self, agent: str = None, level: str = None,
                       limit: int = 100) -> List[Dict]:
        """
        Obtiene logs recientes con filtros
        """
        # Esta implementación simplificada lee del archivo general
        # En producción, se usaría una BD dedicada para logs
        logs = []

        try:
            log_file = self.log_dir / 'oapce_unified.log'
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-limit:]  # Últimas N líneas

                for line in reversed(lines):  # Más recientes primero
                    try:
                        parts = line.strip().split(' | ', 4)
                        if len(parts) >= 5:
                            timestamp, agent_name, level_name, message, extra = parts

                            # Aplicar filtros
                            if agent and agent != agent_name:
                                continue
                            if level and level.upper() != level_name:
                                continue

                            logs.append({
                                "timestamp": timestamp,
                                "agent": agent_name,
                                "level": level_name,
                                "message": message,
                                "extra": extra
                            })

                            if len(logs) >= limit:
                                break

                    except Exception:
                        continue

        except Exception as e:
            self.error("logger", f"Error reading recent logs: {str(e)}")

        return logs

    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Limpia logs antiguos para ahorrar espacio
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            for log_file in self.log_dir.glob("*.log*"):  # Incluye archivos rotados
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    self.info("logger", f"Deleted old log file: {log_file.name}")

        except Exception as e:
            self.error("logger", f"Error cleaning old logs: {str(e)}")

# Instancia global del logger unificado
unified_logger = UnifiedLogger()

# Funciones de conveniencia para logging rápido
def log_info(agent: str, message: str, **kwargs):
    unified_logger.info(agent, message, **kwargs)

def log_warning(agent: str, message: str, **kwargs):
    unified_logger.warning(agent, message, **kwargs)

def log_error(agent: str, message: str, **kwargs):
    unified_logger.error(agent, message, **kwargs)

def log_debug(agent: str, message: str, **kwargs):
    unified_logger.debug(agent, message, **kwargs)

def log_critical(agent: str, message: str, **kwargs):
    unified_logger.critical(agent, message, **kwargs)
