from abc import ABC, abstractmethod
from ..db_utils import log_agent_event

class BaseAgent(ABC):
    def __init__(self, name):
        self.name = name
        
    def log(self, event_type, message, status="info"):
        return log_agent_event(self.name, event_type, message, status)
        
    @abstractmethod
    def run(self):
        pass

    def health_check(self):
        try:
            self.log("health_check", "Iniciando verificación de salud")
            return True
        except Exception as e:
            self.log("error", f"Error en health check: {str(e)}", "error")
            return False
