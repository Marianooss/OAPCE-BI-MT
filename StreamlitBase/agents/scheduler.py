from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import streamlit as st
from datetime import datetime

class AgentScheduler:
    """Planificador central para todos los agentes"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._init_schedules()
    
    def _init_schedules(self):
        """Inicializa los jobs programados"""
        # Data Quality Guardian - cada 6 horas
        self.scheduler.add_job(
            func=lambda: st.session_state.get('dq_agent').run(),
            trigger=CronTrigger(hour='*/6'),
            id='dq_check',
            name='Data Quality Check'
        )
        
        # Predictive Model Engine - diario a las 2 AM
        self.scheduler.add_job(
            func=lambda: st.session_state.get('pm_agent').run(),
            trigger=CronTrigger(hour=2),
            id='predictions',
            name='Daily Predictions'
        )
        
        # Anomaly Detector - cada hora
        self.scheduler.add_job(
            func=lambda: st.session_state.get('ad_agent').run(),
            trigger=CronTrigger(minute=0),
            id='anomaly_check',
            name='Hourly Anomaly Check'
        )
    
    def start(self):
        """Inicia el planificador"""
        if not self.scheduler.running:
            self.scheduler.start()
            
    def stop(self):
        """Detiene el planificador"""
        self.scheduler.shutdown()
