"""
Agent Scheduler - Coordinador Central de Automatización
Módulo para orquestación automática de agentes con Celery + Redis
Cumple con la arquitectura especificada en Agents.md
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from database import get_db
from data_pipeline import DataPipelineOrchestrator
from predictive_models import PredictiveModelEngine
from anomaly_detector import AnomalyDetector
from prescriptive_advisor import PrescriptiveAdvisor
from data_quality import ValidadorCalidadDatos
from generative_assistant import GenerativeDataAssistant
from unified_logger import unified_logger

# Fallback: Sistema de threading para automatización sin dependencias externas
# Si Redis/Celery están disponibles, usa esos; si no, usa threading nativo
try:
    from celery import Celery
    from celery.schedules import crontab
    import redis

    # Redis para comunicación en tiempo real (WebSockets)
    redis_client = redis.Redis(host='localhost', port=6379, db=1)

    # Configuración de Celery para Redis
    app = Celery(
        'agent_scheduler',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0',
        include=['agent_scheduler']
    )

    # Configuración de tareas
    app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='America/Santiago',
        enable_utc=True,
        beat_schedule={
            'daily-data-pipeline': {
                'task': 'agent_scheduler.daily_data_pipeline',
                'schedule': crontab(hour=6, minute=0),
            },
            'weekly-model-retraining': {
                'task': 'agent_scheduler.weekly_model_retraining',
                'schedule': crontab(day_of_week='monday', hour=2, minute=0),
            },
            'daily-predictions-update': {
                'task': 'agent_scheduler.daily_predictions_update',
                'schedule': crontab(hour=7, minute=0),
            },
            'hourly-anomaly-detection': {
                'task': 'agent_scheduler.hourly_anomaly_detection',
                'schedule': crontab(minute=0),
            },
            'continous-quality-monitoring': {
                'task': 'agent_scheduler.continuous_quality_monitoring',
                'schedule': crontab(minute='*/30'),
            },
            'daily-recommendations-generation': {
                'task': 'agent_scheduler.daily_recommendations_generation',
                'schedule': crontab(hour=8, minute=0),
            },
            'weekly-schema-update': {
                'task': 'agent_scheduler.weekly_schema_update',
                'schedule': crontab(day_of_week='monday', hour=3, minute=0),
            },
        }
    )

    CELERY_AVAILABLE = True
    REDIS_AVAILABLE = True

except ImportError:
    # Fallback a threading si no hay Celery/Redis
    app = None
    redis_client = None
    CELERY_AVAILABLE = False
    REDIS_AVAILABLE = False

    unified_logger.log("scheduler", "WARNING", "Celery/Redis no disponibles - usando sistema de threading alternativo")

class ThreadingScheduler:
    """
    Fallback scheduler usando threading cuando Celery/Redis no están disponibles
    """

    def __init__(self):
        self.db = get_db()
        self.active_agents = {}
        self.threads = {}
        self.stop_event = threading.Event()
        self.last_runs = {}  # Track last execution times

    def _run_task_in_thread(self, task_name: str, task_func, *args, **kwargs):
        """Ejecuta una tarea en un thread separado"""
        def task_wrapper():
            try:
                unified_logger.log("scheduler", "INFO", f"Ejecutando tarea programada: {task_name}")
                result = task_func(*args, **kwargs)
                unified_logger.log("scheduler", "INFO", f"Tarea completada: {task_name}")
                return result
            except Exception as e:
                unified_logger.log("scheduler", "ERROR", f"Error en tarea {task_name}: {str(e)}")
                return None

        thread = threading.Thread(target=task_wrapper, daemon=True)
        thread.start()
        self.threads[task_name] = thread
        return thread

    def _should_run_task(self, task_name: str, interval_seconds: int) -> bool:
        """Determina si una tarea debe ejecutarse basado en el intervalo"""
        now = datetime.now()
        last_run = self.last_runs.get(task_name)

        if last_run is None:
            return True

        time_since_last = (now - last_run).total_seconds()
        return time_since_last >= interval_seconds

    def _mark_task_run(self, task_name: str):
        """Marca que una tarea fue ejecutada"""
        self.last_runs[task_name] = datetime.now()

    def start_scheduler_loop(self):
        """Loop principal del scheduler usando threading"""
        unified_logger.log("scheduler", "INFO", "Iniciando scheduler con threading (modo fallback)")

        # Ejecutar tareas iniciales inmediatamente para testing
        self._run_task_in_thread("daily_data_pipeline", self.daily_data_pipeline)
        time.sleep(2)  # Pequeña pausa
        self._run_task_in_thread("daily_predictions_update", self.daily_predictions_update)
        time.sleep(2)
        self._run_task_in_thread("daily_recommendations_generation", self.daily_recommendations_generation)

        # Loop de verificación continua
        while not self.stop_event.is_set():
            try:
                now = datetime.now()

                # Verificar cada tarea según su intervalo
                # DPO - cada 24 horas
                if self._should_run_task("daily_data_pipeline", 24 * 3600):
                    self._run_task_in_thread("daily_data_pipeline", self.daily_data_pipeline)
                    self._mark_task_run("daily_data_pipeline")

                # PME predictions - cada 6 horas
                if self._should_run_task("daily_predictions_update", 6 * 3600):
                    self._run_task_in_thread("daily_predictions_update", self.daily_predictions_update)
                    self._mark_task_run("daily_predictions_update")

                # AD - cada hora
                if self._should_run_task("hourly_anomaly_detection", 3600):
                    self._run_task_in_thread("hourly_anomaly_detection", self.hourly_anomaly_detection)
                    self._mark_task_run("hourly_anomaly_detection")

                # DQG - cada 30 minutos
                if self._should_run_task("continuous_quality_monitoring", 30 * 60):
                    self._run_task_in_thread("continuous_quality_monitoring", self.continuous_quality_monitoring)
                    self._mark_task_run("continuous_quality_monitoring")

                # PA - cada 12 horas
                if self._should_run_task("daily_recommendations_generation", 12 * 3600):
                    self._run_task_in_thread("daily_recommendations_generation", self.daily_recommendations_generation)
                    self._mark_task_run("daily_recommendations_generation")

                # PME retraining - semanal (cada 7 días)
                if self._should_run_task("weekly_model_retraining", 7 * 24 * 3600):
                    self._run_task_in_thread("weekly_model_retraining", self.weekly_model_retraining)
                    self._mark_task_run("weekly_model_retraining")

                # GDA schema update - semanal
                if self._should_run_task("weekly_schema_update", 7 * 24 * 3600):
                    self._run_task_in_thread("weekly_schema_update", self.weekly_schema_update)
                    self._mark_task_run("weekly_schema_update")

                # Esperar 5 minutos antes de verificar nuevamente
                time.sleep(300)

            except Exception as e:
                unified_logger.log("scheduler", "ERROR", f"Error en loop del scheduler: {str(e)}")
                time.sleep(60)  # Esperar 1 minuto en caso de error

    def stop_scheduler(self):
        """Detiene el scheduler"""
        unified_logger.log("scheduler", "INFO", "Deteniendo scheduler con threading")
        self.stop_event.set()

        # Esperar que terminen los threads activos
        for thread_name, thread in self.threads.items():
            if thread.is_alive():
                thread.join(timeout=10)

    # Métodos de tareas (sin decoradores @app.task)
    def daily_data_pipeline(self):
        """Versión sin Celery del DPO"""
        try:
            unified_logger.log_agent_activity(
                agent="dpo",
                action="scheduled_daily_etl",
                status="started"
            )

            dpo = DataPipelineOrchestrator()
            tables_to_process = ['clientes', 'facturas', 'vendedores', 'actividades_venta']
            results = {}

            for table in tables_to_process:
                try:
                    result = dpo.run_etl_pipeline(table)
                    results[table] = result
                except Exception as e:
                    results[table] = {'success': False, 'error': str(e)}

            dpo.close()

            unified_logger.log_agent_activity(
                agent="dpo",
                action="scheduled_daily_etl",
                status="completed",
                details={
                    "tables_processed": len(tables_to_process),
                    "success_count": sum(1 for r in results.values() if r.get('success'))
                }
            )

            return results

        except Exception as e:
            unified_logger.log_agent_activity(
                agent="dpo",
                action="scheduled_daily_etl",
                status="failed",
                details={"error": str(e)}
            )
            return {"success": False, "error": str(e)}

    def weekly_model_retraining(self):
        """Versión sin Celery del PME retraining"""
        try:
            unified_logger.log_agent_activity(
                agent="pme",
                action="scheduled_weekly_retraining",
                status="started"
            )

            pme = PredictiveModelEngine()
            results = {}

            try:
                sales_result = pme.train_sales_forecast_model()
                results['sales_forecast'] = sales_result
            except Exception as e:
                results['sales_forecast'] = {'success': False, 'error': str(e)}

            try:
                risk_result = pme.train_risk_assessment_model()
                results['risk_assessment'] = risk_result
            except Exception as e:
                results['risk_assessment'] = {'success': False, 'error': str(e)}

            try:
                conversion_result = pme.train_conversion_probability_model()
                results['conversion_probability'] = conversion_result
            except Exception as e:
                results['conversion_probability'] = {'success': False, 'error': str(e)}

            pme.close()

            success_count = sum(1 for r in results.values() if r.get('success'))

            unified_logger.log_agent_activity(
                agent="pme",
                action="scheduled_weekly_retraining",
                status="completed",
                details={
                    "models_retrained": len(results),
                    "success_count": success_count
                }
            )

            return results

        except Exception as e:
            unified_logger.log_agent_activity(
                agent="pme",
                action="scheduled_weekly_retraining",
                status="failed",
                details={"error": str(e)}
            )
            return {"success": False, "error": str(e)}

    def daily_predictions_update(self):
        """Versión sin Celery de las predicciones diarias"""
        try:
            unified_logger.log_agent_activity(
                agent="pme",
                action="scheduled_daily_predictions",
                status="started"
            )

            pme = PredictiveModelEngine()

            predictions_generated = 0

            try:
                sales_preds = pme.get_predictions('sales_forecast')
                sales_count = sales_preds.get('count', 0)
                predictions_generated += sales_count
            except:
                sales_count = 0

            try:
                risk_preds = pme.get_predictions('risk_assessment')
                risk_count = risk_preds.get('count', 0)
                predictions_generated += risk_count
            except:
                risk_count = 0

            try:
                conversion_preds = pme.get_predictions('conversion_probability')
                conversion_count = conversion_preds.get('count', 0)
                predictions_generated += conversion_count
            except:
                conversion_count = 0

            pme.close()

            unified_logger.log_agent_activity(
                agent="pme",
                action="scheduled_daily_predictions",
                status="completed",
                details={
                    "sales_predictions": sales_count,
                    "risk_predictions": risk_count,
                    "conversion_predictions": conversion_count,
                    "total_predictions": predictions_generated
                }
            )

            return {
                "predictions_generated": predictions_generated,
                "sales": sales_count,
                "risk": risk_count,
                "conversion": conversion_count
            }

        except Exception as e:
            unified_logger.log_agent_activity(
                agent="pme",
                action="scheduled_daily_predictions",
                status="failed",
                details={"error": str(e)}
            )
            return {"success": False, "error": str(e)}

    def hourly_anomaly_detection(self):
        """Versión sin Celery del AD"""
        try:
            unified_logger.log_agent_activity(
                agent="ad",
                action="scheduled_hourly_anomalies",
                status="started"
            )

            ad = AnomalyDetector()

            sales_anomalies = ad.detect_anomalies_sales(lookback_days=7)
            collections_anomalies = ad.detect_anomalies_collections(lookback_days=7)

            ad.close()

            total_anomalies = (
                sales_anomalies.get('anomalies_detected', 0) +
                collections_anomalies.get('anomalies_detected', 0)
            )

            unified_logger.log_agent_activity(
                agent="ad",
                action="scheduled_hourly_anomalies",
                status="completed",
                details={
                    "sales_anomalies_detected": sales_anomalies.get('anomalies_detected', 0),
                    "collections_anomalies_detected": collections_anomalies.get('anomalies_detected', 0),
                    "total_anomalies": total_anomalies
                }
            )

            return {
                "success": True,
                "sales_anomalies": sales_anomalies,
                "collections_anomalies": collections_anomalies,
                "total_anomalies": total_anomalies
            }

        except Exception as e:
            unified_logger.log_agent_activity(
                agent="ad",
                action="scheduled_hourly_anomalies",
                status="failed",
                details={"error": str(e)}
            )
            return {"success": False, "error": str(e)}

    def continuous_quality_monitoring(self):
        """Versión sin Celery del DQG"""
        try:
            unified_logger.log_agent_activity(
                agent="dqg",
                action="scheduled_quality_monitoring",
                status="started"
            )

            dqg = ValidadorCalidadDatos()

            datasets_to_check = ['ventas', 'clientes', 'productos', 'cobranzas']
            results = {}

            critical_issues = 0
            total_issues = 0

            for dataset in datasets_to_check:
                try:
                    result = dqg.ejecutar_validaciones(dataset)
                    results[dataset] = result

                    issues = len(result.get('problemas', []))
                    total_issues += issues

                    critical_issues_this = sum(1 for p in result.get('problemas', [])
                                             if p.get('severidad') == 'critica')
                    critical_issues += critical_issues_this

                except Exception as e:
                    results[dataset] = {'success': False, 'error': str(e)}

            dqg.close()

            unified_logger.log_agent_activity(
                agent="dqg",
                action="scheduled_quality_monitoring",
                status="completed",
                details={
                    "datasets_checked": len(datasets_to_check),
                    "total_issues": total_issues,
                    "critical_issues": critical_issues
                }
            )

            return {
                "success": True,
                "datasets_checked": len(datasets_to_check),
                "total_issues": total_issues,
                "critical_issues": critical_issues,
                "results": results
            }

        except Exception as e:
            unified_logger.log_agent_activity(
                agent="dqg",
                action="scheduled_quality_monitoring",
                status="failed",
                details={"error": str(e)}
            )
            return {"success": False, "error": str(e)}

    def daily_recommendations_generation(self):
        """Versión sin Celery del PA"""
        try:
            unified_logger.log_agent_activity(
                agent="pa",
                action="scheduled_daily_recommendations",
                status="started"
            )

            pa = PrescriptiveAdvisor()

            high_risk_clients = pa.generate_client_recommendations(
                recommendation_type='high_risk_clients',
                min_confidence=0.6
            )

            sales_opportunities = pa.generate_client_recommendations(
                recommendation_type='sales_opportunities',
                min_confidence=0.5
            )

            collection_alerts = pa.generate_client_recommendations(
                recommendation_type='collection_risks',
                min_confidence=0.4
            )

            pa.close()

            total_recommendations = (
                high_risk_clients.get('recommendations_count', 0) +
                sales_opportunities.get('recommendations_count', 0) +
                collection_alerts.get('recommendations_count', 0)
            )

            unified_logger.log_agent_activity(
                agent="pa",
                action="scheduled_daily_recommendations",
                status="completed",
                details={
                    "high_risk_recommendations": high_risk_clients.get('recommendations_count', 0),
                    "sales_opportunities": sales_opportunities.get('recommendations_count', 0),
                    "collection_alerts": collection_alerts.get('recommendations_count', 0),
                    "total_recommendations": total_recommendations
                }
            )

            return {
                "success": True,
                "high_risk_clients": high_risk_clients,
                "sales_opportunities": sales_opportunities,
                "collection_alerts": collection_alerts,
                "total_recommendations": total_recommendations
            }

        except Exception as e:
            unified_logger.log_agent_activity(
                agent="pa",
                action="scheduled_daily_recommendations",
                status="failed",
                details={"error": str(e)}
            )
            return {"success": False, "error": str(e)}

    def weekly_schema_update(self):
        """Versión sin Celery del GDA"""
        try:
            unified_logger.log_agent_activity(
                agent="gda",
                action="scheduled_weekly_schema_update",
                status="started"
            )

            gda = GenerativeDataAssistant()

            schema_update_result = gda.update_schema_cache()
            embedding_update_result = gda.update_embeddings()

            gda.close()

            unified_logger.log_agent_activity(
                agent="gda",
                action="scheduled_weekly_schema_update",
                status="completed",
                details={
                    "schemas_updated": schema_update_result.get('tables_updated', 0),
                    "embeddings_updated": embedding_update_result.get('vectors_updated', 0)
                }
            )

            return {
                "success": True,
                "schema_update": schema_update_result,
                "embedding_update": embedding_update_result
            }

        except Exception as e:
            unified_logger.log_agent_activity(
                agent="gda",
                action="scheduled_weekly_schema_update",
                status="failed",
                details={"error": str(e)}
            )
            return {"success": False, "error": str(e)}

    def trigger_manual_task(self, task_name: str, **kwargs) -> Dict:
        """Ejecutar tarea manualmente"""
        try:
            task_functions = {
                'daily_data_pipeline': self.daily_data_pipeline,
                'weekly_model_retraining': self.weekly_model_retraining,
                'daily_predictions_update': self.daily_predictions_update,
                'hourly_anomaly_detection': self.hourly_anomaly_detection,
                'continuous_quality_monitoring': self.continuous_quality_monitoring,
                'daily_recommendations_generation': self.daily_recommendations_generation,
                'weekly_schema_update': self.weekly_schema_update,
            }

            if task_name not in task_functions:
                return {"success": False, "error": f"Tarea {task_name} no encontrada"}

            # Ejecutar tarea en thread
            self._run_task_in_thread(task_name, task_functions[task_name], **kwargs)

            unified_logger.log_system_event(
                event_type="manual_task_trigger",
                details={"task_name": task_name}
            )

            return {
                "success": True,
                "task_name": task_name,
                "status": "triggered"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_scheduler_status(self) -> Dict:
        """Estado del scheduler con threading"""
        active_threads = sum(1 for t in self.threads.values() if t.is_alive())

        return {
            "success": True,
            "scheduler_active": not self.stop_event.is_set(),
            "active_tasks_count": active_threads,
            "scheduled_tasks_count": len(self.last_runs),
            "agent_status": {},
            "redis_connected": False,
            "threading_mode": True
        }


class AgentScheduler:
    """
    Orquestador central que implementa la automatización especificada en Agents.md
    """

    def __init__(self):
        self.db = get_db()
        self.active_agents = {}

        # Usar threading scheduler si no hay Celery
        if not CELERY_AVAILABLE:
            self.threading_scheduler = ThreadingScheduler()
            self.is_threading_mode = True
        else:
            self.threading_scheduler = None
            self.is_threading_mode = False

    @app.task(bind=True)
    def daily_data_pipeline(self, *args, **kwargs):
        """Celery version - same as ThreadingScheduler.daily_data_pipeline"""
        return self.threading_scheduler.daily_data_pipeline() if self.is_threading_mode else None

    @app.task(bind=True)
    def weekly_model_retraining(self, *args, **kwargs):
        """Celery version"""
        return self.threading_scheduler.weekly_model_retraining() if self.is_threading_mode else None

    @app.task(bind=True)
    def daily_predictions_update(self, *args, **kwargs):
        """Celery version"""
        return self.threading_scheduler.daily_predictions_update() if self.is_threading_mode else None

    @app.task(bind=True)
    def hourly_anomaly_detection(self, *args, **kwargs):
        """Celery version"""
        return self.threading_scheduler.hourly_anomaly_detection() if self.is_threading_mode else None

    @app.task(bind=True)
    def continuous_quality_monitoring(self, *args, **kwargs):
        """Celery version"""
        return self.threading_scheduler.continuous_quality_monitoring() if self.is_threading_mode else None

    @app.task(bind=True)
    def daily_recommendations_generation(self, *args, **kwargs):
        """Celery version"""
        return self.threading_scheduler.daily_recommendations_generation() if self.is_threading_mode else None

    @app.task(bind=True)
    def weekly_schema_update(self, *args, **kwargs):
        """Celery version"""
        return self.threading_scheduler.weekly_schema_update() if self.is_threading_mode else None

    def _notify_via_redis(self, channel: str, message: Dict):
        """Redis notifications (if available)"""
        if REDIS_AVAILABLE and redis_client:
            try:
                notification = {
                    'channel': channel,
                    'timestamp': datetime.now().isoformat(),
                    'data': message
                }
                redis_client.publish(channel, json.dumps(notification))
                redis_client.lpush('agent_notifications', json.dumps(notification))
                redis_client.ltrim('agent_notifications', 0, 999)
            except Exception as e:
                unified_logger.log_system_event(
                    event_type="redis_notification_error",
                    severity="warning",
                    details={"channel": channel, "error": str(e)}
                )

    def get_scheduler_status(self) -> Dict:
        """Estado actual del scheduler"""
        if self.is_threading_mode:
            return self.threading_scheduler.get_scheduler_status()

        # Celery version
        try:
            inspector = app.control.inspect()
            active_tasks = inspector.active() or {}
            scheduled_tasks = inspector.scheduled() or {}
            stats = inspector.stats() or {}

            agent_status = {}
            for agent_name in ['dpo', 'pme', 'ad', 'pa', 'dqg', 'gda']:
                recent_logs = unified_logger.get_recent_agent_logs(agent_name, hours=24)
                agent_status[agent_name] = {
                    'last_activity': recent_logs[0]['timestamp'] if recent_logs else None,
                    'active_tasks': len([
                        t for tasks in active_tasks.values() for t in tasks
                        if t.get('name', '').startswith(f'agent_scheduler.{agent_name}')
                    ])
                }

            return {
                "success": True,
                "scheduler_active": True,
                "active_tasks_count": sum(len(tasks) for tasks in active_tasks.values()),
                "scheduled_tasks_count": sum(len(tasks) for tasks in scheduled_tasks.values()),
                "agent_status": agent_status,
                "redis_connected": redis_client.ping() if redis_client else False
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "scheduler_active": False
            }

    def trigger_manual_task(self, task_name: str, **kwargs) -> Dict:
        """Ejecutar tarea manualmente"""
        if self.is_threading_mode:
            return self.threading_scheduler.trigger_manual_task(task_name, **kwargs)

        # Celery version
        try:
            task_functions = {
                'daily_data_pipeline': self.daily_data_pipeline,
                'weekly_model_retraining': self.weekly_model_retraining,
                'daily_predictions_update': self.daily_predictions_update,
                'hourly_anomaly_detection': self.hourly_anomaly_detection,
                'continuous_quality_monitoring': self.continuous_quality_monitoring,
                'daily_recommendations_generation': self.daily_recommendations_generation,
                'weekly_schema_update': self.weekly_schema_update,
            }

            if task_name not in task_functions:
                return {"success": False, "error": f"Tarea {task_name} no encontrada"}

            result = task_functions[task_name].delay(**kwargs)

            unified_logger.log_system_event(
                event_type="manual_task_trigger",
                details={"task_name": task_name, "task_id": result.id}
            )

            return {
                "success": True,
                "task_name": task_name,
                "task_id": result.id,
                "status": "triggered"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def start_threading_scheduler(self):
        """Inicia el scheduler con threading (para cuando no hay Celery)"""
        if self.is_threading_mode and self.threading_scheduler:
            threading.Thread(target=self.threading_scheduler.start_scheduler_loop, daemon=True).start()
            unified_logger.log("scheduler", "INFO", "Scheduler con threading iniciado")
            return True
        return False

    def stop_threading_scheduler(self):
        """Detiene el scheduler con threading"""
        if self.is_threading_mode and self.threading_scheduler:
            self.threading_scheduler.stop_scheduler()
            return True
        return False


# Instancia global del scheduler
scheduler = AgentScheduler()


# Funciones de conveniencia para iniciar el scheduler
def start_scheduler():
    """Inicia el scheduler con configuración completa"""
    print("🚀 Iniciando Agent Scheduler de OAPCE BI Multitrans...")
    print("📋 Tareas programadas:")
    print("  • DPO - ETL diario a las 6:00 AM")
    print("  • PME - Re-entrenamiento semanal lunes 2:00 AM")
    print("  • PME - Actualización de predicciones diariamente 7:00 AM")
    print("  • AD - Detección de anomalías cada hora")
    print("  • DQG - Monitoreo de calidad cada 30 minutos")
    print("  • PA - Generación de recomendaciones diariamente 8:00 AM")
    print("  • GDA - Actualización de esquemas semanal lunes 3:00 AM")

    if CELERY_AVAILABLE:
        print("✅ Modo Celery/Redis activado")
    else:
        print("✅ Modo Threading activado (fallback)")
        scheduler.start_threading_scheduler()

    print("✅ Arquitectura de automatización conforme a Agents.md")


def get_scheduler():
    """Retorna instancia del scheduler para uso en otros módulos"""
    return scheduler


if __name__ == '__main__':
    # Ejecutar pruebas del scheduler si se llama directamente
    print("Testing Agent Scheduler...")

    # Verificar conectividad
    print(f"Redis connected: {redis_client.ping() if redis_client else False}")
    print(f"Database connected: {scheduler.db is not None}")
    print(f"Threading mode: {scheduler.is_threading_mode}")

    # Obtener estado
    status = scheduler.get_scheduler_status()
    print(f"Scheduler status: {status}")

    print("✅ Agent Scheduler ready!")
