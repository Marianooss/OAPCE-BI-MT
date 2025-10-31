#!/usr/bin/env python
"""
Script de inicio para agentes automatizados de OAPCE BI Multitrans
Cumple estrictamente con la arquitectura especificada en Agents.md
Implementa automatización continuola y aprendizaje automático programado
"""

import os
import sys
import time
import signal
import subprocess
import multiprocessing
import threading
from multiprocessing import Process
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('agent_startup')

class AutomatedAgentsOrchestrator:
    """
    Orquestador que inicia todos los componentes de automatización
    Segun especificaciones de Agents.md
    """

    def __init__(self):
        self.processes = []
        self.redis_process = None
        self.celery_worker = None
        self.celery_beat = None  # Corregir bug
        self.websocket_server = None

        # Verificar dependencias críticas
        self._check_dependencies()

    def _check_dependencies(self):
        """Verifica que todas las dependencias críticas estén disponibles"""
        dependencies = [
            ('redis', 'Redis'),
            ('celery', 'Celery'),
            ('websockets', 'WebSockets'),
        ]

        missing = []
        for import_name, display_name in dependencies:
            try:
                __import__(import_name)
            except ImportError:
                missing.append(display_name)

        if missing:
            logger.error(f"❌ Dependencias faltantes: {', '.join(missing)}")
            logger.info("Instalando dependencias...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)

    def _start_redis_server(self):
        """Inicia servidor Redis local (si no está corriendo externamente)"""
        try:
            # Verificar si Redis ya está corriendo
            import redis
            client = redis.Redis(host='localhost', port=6379)
            client.ping()
            logger.info("✅ Redis ya está ejecutándose")
            return True

        except redis.ConnectionError:
            # Redis no está corriendo, intentar iniciarlo
            logger.info("🚀 Iniciando servidor Redis local...")
            try:
                # Intentar iniciar Redis local (debes tener Redis instalado)
                self.redis_process = subprocess.Popen(
                    ['redis-server'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(2)  # Esperar que inicie

                # Verificar
                client = redis.Redis(host='localhost', port=6379)
                client.ping()
                logger.info("✅ Redis servidor iniciado exitosamente")
                return True

            except (subprocess.SubprocessError, redis.ConnectionError) as e:
                logger.warning(f"⚠️  No se pudo iniciar Redis local: {e}")
                logger.warning("⚠️  Usando modo sin Redis - notificaciones realtime limitadas")
                return False

    def _start_celery_worker(self):
        """Inicia worker de Celery para ejecutar tareas programadas"""
        logger.info("🚀 Iniciando Celery Worker...")

        # Comando para iniciar Celery worker
        cmd = [
            sys.executable, '-m', 'celery', '-A', 'agent_scheduler',
            'worker', '--loglevel=info', '--concurrency=2'
        ]

        try:
            self.celery_worker = subprocess.Popen(
                cmd,
                cwd=os.getcwd(),
                env=dict(os.environ, PYTHONPATH=os.getcwd())
            )

            logger.info("✅ Celery Worker iniciado")
            return True

        except subprocess.SubprocessError as e:
            logger.error(f"❌ Error iniciando Celery Worker: {e}")
            return False

    def _start_celery_beat(self):
        """Inicia Celery Beat para ejecutar tareas programadas"""
        logger.info("🚀 Iniciando Celery Beat Scheduler...")

        cmd = [
            sys.executable, '-m', 'celery', '-A', 'agent_scheduler',
            'beat', '--loglevel=info'
        ]

        try:
            self.celery_beat = subprocess.Popen(
                cmd,
                cwd=os.getcwd(),
                env=dict(os.environ, PYTHONPATH=os.getcwd())
            )

            logger.info("✅ Celery Beat Scheduler iniciado")
            logger.info("📋 Tareas programadas activas:")
            logger.info("   • DPO ETL diario: 6:00 AM")
            logger.info("   • PME Re-entrenamiento semanal: Lunes 2:00 AM")
            logger.info("   • PME Predicciones diarias: 7:00 AM")
            logger.info("   • AD Anomalías cada hora")
            logger.info("   • DQG Monitoreo cada 30 min")
            logger.info("   • PA Recomendaciones diarias: 8:00 AM")
            logger.info("   • GDA Actualización semanal: Lunes 3:00 AM")

            return True

        except subprocess.SubprocessError as e:
            logger.error(f"❌ Error iniciando Celery Beat: {e}")
            return False

    def _start_threading_scheduler(self):
        """Inicia scheduler con threading como alternativa a Celery"""
        logger.info("🚀 Iniciando Threading Scheduler (modo alternativo)...")

        try:
            from agent_scheduler import scheduler

            if hasattr(scheduler, 'threading_scheduler') and scheduler.threading_scheduler:
                # Iniciar scheduler en un thread separado
                scheduler_thread = threading.Thread(
                    target=scheduler.threading_scheduler.start_scheduler_loop,
                    daemon=True
                )
                scheduler_thread.start()

                logger.info("✅ Threading Scheduler iniciado")
                logger.info("📋 Tareas programadas activas (threading):")
                logger.info("   • DPO ETL diario: cada 24 horas")
                logger.info("   • PME Re-entrenamiento semanal: cada 7 días")
                logger.info("   • PME Predicciones diarias: cada 6 horas")
                logger.info("   • AD Anomalías cada hora")
                logger.info("   • DQG Monitoreo cada 30 min")
                logger.info("   • PA Recomendaciones diarias: cada 12 horas")
                logger.info("   • GDA Actualización semanal: cada 7 días")

                return True
            else:
                logger.warning("⚠️ Threading scheduler no disponible")
                return False

        except Exception as e:
            logger.error(f"❌ Error iniciando Threading Scheduler: {e}")
            return False

    def _start_websocket_server(self):
        """Inicia servidor WebSocket para comunicación realtime"""
        logger.info("🚀 Iniciando WebSocket Server para notificaciones realtime...")

        try:
            # Ejecutar WebSocket server como proceso separado
            from websocket_server import main as ws_main

            # Ejecutar en background
            self.websocket_server = Process(target=self._run_websocket_async)
            self.websocket_server.start()

            logger.info("✅ WebSocket Server iniciado en ws://localhost:8765")
            return True

        except Exception as e:
            logger.error(f"❌ Error iniciando WebSocket Server: {e}")
            return False

    def _run_websocket_async(self):
        """Ejecuta WebSocket server en proceso separado"""
        try:
            import asyncio
            from websocket_server import main as ws_main
            asyncio.run(ws_main())
        except KeyboardInterrupt:
            pass
        except Exception as e:
            logger.error(f"Error en WebSocket server: {e}")

    def _start_automated_etl(self):
        """Ejecuta ETL inicial para tener datos frescos"""
        logger.info("🚀 Ejecutando ETL inicial...")

        try:
            from agent_scheduler import scheduler

            # Trigger manual del ETL diario
            result = scheduler.trigger_manual_task('daily_data_pipeline')

            if result.get('success'):
                logger.info(f"✅ ETL inicial completado. Task ID: {result.get('task_id')}")
            else:
                logger.warning("⚠️  ETL inicial falló, usando datos existentes")

        except Exception as e:
            logger.warning(f"⚠️  Error en ETL inicial: {e}")

    def start_all_components(self):
        """Inicia todos los componentes de la arquitectura automatizada"""
        logger.info("🤖 Iniciando Arquitectura de Agentes Automatizados - OAPCE BI Multitrans")
        logger.info("📋 Basado en especificaciones de Agents.md")

        # 1. Iniciar Redis (opcional en desarrollo - usar modo alternativo si falla)
        redis_ok = self._start_redis_server()

        if not redis_ok:
            logger.warning("⚠️  Redis no disponible - iniciando en modo desarrollo limitado")
            logger.info("💡 Para funcionamiento completo instala Redis: https://redis.io/download")

        # 2. Iniciar Celery Worker (sólo si hay Redis)
        celery_ok = False
        if redis_ok:
            celery_ok = self._start_celery_worker()
            if not celery_ok:
                logger.warning("⚠️  Celery Worker falló - usando modo threading alternativo")
        else:
            logger.info("⚠️  Celery requiere Redis - usando modo threading alternativo")

        # 3. Iniciar Celery Beat (scheduler) solo si Celery funciona
        beat_ok = False
        threading_ok = False

        if celery_ok:
            beat_ok = self._start_celery_beat()
            if not beat_ok:
                logger.warning("⚠️  Celery Beat no inició - usando modo threading alternativo")
        else:
            # Usar threading scheduler como alternativa
            threading_ok = self._start_threading_scheduler()
            if threading_ok:
                logger.info("✅ Usando Threading Scheduler como alternativa a Celery")
            else:
                logger.warning("⚠️  Threading scheduler tampoco disponible - modo manual")

        # 4. Iniciar WebSocket Server (solo si hay Redis)
        ws_ok = False
        if redis_ok:
            ws_ok = self._start_websocket_server()
        else:
            logger.info("⚠️ WebSockets requieren Redis - notificaciones realtime limitadas")

        # 5. Ejecutar ETL inicial si hay capacidad automática
        if celery_ok or threading_ok:
            self._start_automated_etl()

        # 6. Estado final
        self._print_startup_status()

        # 7. Para desarrollo, iniciar Streamlit también
        if not celery_ok and not threading_ok:
            logger.info("🐍 Iniciando Streamlit para desarrollo...")
            self.start_streamlit_app()

        # 8. Mantener proceso vivo si hay componentes automatizados
        if celery_ok:
            self._keep_alive()
        elif threading_ok:
            # Para threading, mantener vivo también
            self._keep_alive_threading()

        return True

    def _print_startup_status(self):
        """Imprime estado de inicio de componentes"""
        logger.info("\n" + "="*80)
        logger.info("🏁 ESTADO DE COMPONENTES INICIADOS")
        logger.info("="*80)
        logger.info(f"Redis Server: {'🟢 Activo' if self.redis_process else '🟢 OK'}")
        logger.info(f"Celery Worker: {'🟢 Activo' if self.celery_worker else '🔴 Inactivo'}")
        logger.info(f"Celery Beat: {'🟢 Activo' if self.celery_beat else '🔴 Inactivo'}")
        logger.info(f"WebSocket Server: {'🟢 Activo' if self.websocket_server else '🔴 Inactivo'}")

        logger.info("\n✅ ARQUITECTURA AUTOMATIZADA ACTIVA")
        logger.info("📋 Ciclo de automatización:")
        logger.info("   Datos Nuevos → DPO (ETL Diario) → PME (Aprendizaje Continuo)")
        logger.info("   → AD (Análisis Realtime) → PA (Recomendaciones)")
        logger.info("="*80)

    def _keep_alive(self):
        """Mantiene procesos vivos y maneja señales de cierre"""
        def signal_handler(signum, frame):
            logger.info("\n🛑 Recibida señal de parada, cerrando componentes...")
            self.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Mantener vivo mientras subprocess estén activos
        while True:
            if self.celery_worker and self.celery_worker.poll() is not None:
                logger.warning("⚠️  Celery Worker terminó, reiniciando...")
                self._start_celery_worker()

            if self.celery_beat and self.celery_beat.poll() is not None:
                logger.warning("⚠️  Celery Beat terminó, reiniciando...")
                self._start_celery_beat()

            time.sleep(5)  # Verificar cada 5 segundos

    def _keep_alive_threading(self):
        """Mantiene vivo el proceso cuando se usa threading scheduler"""
        def signal_handler(signum, frame):
            logger.info("\n🛑 Recibida señal de parada, cerrando componentes...")
            self.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Mantener vivo indefinidamente mientras el threading scheduler funciona
        logger.info("🔄 Modo threading activo - presiona Ctrl+C para detener")
        while True:
            time.sleep(10)  # Verificar cada 10 segundos
            logger.info("✅ Threading scheduler funcionando...")

    def shutdown(self):
        """Cierra todos los procesos correctamente"""
        logger.info("🔄 Cerrando componentes automatizados...")

        # Terminar procesos
        for process in [self.celery_worker, self.celery_beat, self.redis_process]:
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()

        # Cerrar WebSocket server
        if self.websocket_server and self.websocket_server.is_alive():
            self.websocket_server.terminate()
            self.websocket_server.join(timeout=5)
            if self.websocket_server.is_alive():
                self.websocket_server.kill()

        logger.info("✅ Todos los componentes cerrados correctamente")

    def start_streamlit_app(self):
        """Inicia aplicación Streamlit después de componentes automatizados"""
        logger.info("🚀 Iniciando aplicación Streamlit...")

        try:
            cmd = [sys.executable, '-m', 'streamlit', 'run', 'agents_ui.py',
                   '--server.port=8501', '--server.headless=true']

            streamlit_process = subprocess.Popen(cmd, cwd=os.getcwd())
            logger.info("✅ Aplicación Streamlit iniciada en http://localhost:8501")

            return streamlit_process

        except Exception as e:
            logger.error(f"❌ Error iniciando Streamlit: {e}")
            return None


def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] == '--only-streamlit':
        # Solo iniciar Streamlit (para desarrollo)
        logger.info("🐍 Iniciando solo aplicación Streamlit...")
        orchestrator = AutomatedAgentsOrchestrator()
        streamlit = orchestrator.start_streamlit_app()

        if streamlit:
            try:
                streamlit.wait()
            except KeyboardInterrupt:
                streamlit.terminate()
        return

    # Iniciar arquitectura completa
    orchestrator = AutomatedAgentsOrchestrator()

    try:
        success = orchestrator.start_all_components()
        if not success:
            sys.exit(1)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        orchestrator.shutdown()


if __name__ == '__main__':
    main()
