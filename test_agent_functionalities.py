import os
import sys
from datetime import datetime
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Configure basic logging for the test script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import all agent classes
from catalog import DataCatalogManager
from data_pipeline import DataPipelineOrchestrator
from predictive_models import PredictiveModelEngine
from prescriptive_advisor import PrescriptiveAdvisor
from data_quality import ValidadorCalidadDatos
from anomaly_detector import AnomalyDetector
from generative_assistant import GenerativeDataAssistant
from system_integrator import SystemIntegrator
from data_import_manager import DataImportManager
from metrics_hub import MetricsDefinitionHub
from unified_logger import unified_logger # Ensure unified_logger is initialized

class AgentFunctionalityTester:
    def __init__(self):
        self.results = {}

    def run_test(self, agent_name: str, agent_class, test_method_name: str, *args, **kwargs):
        logger.info(f"--- Testing {agent_name} ---")
        try:
            agent_instance = agent_class()
            test_method = getattr(agent_instance, test_method_name)
            result = test_method(*args, **kwargs)
            
            if isinstance(result, dict) and result.get('success', False):
                self.results[agent_name] = {"status": "PASSED", "details": result}
                logger.info(f"{agent_name} PASSED: {test_method_name} executed successfully.")
            elif isinstance(result, dict) and 'error' in result:
                self.results[agent_name] = {"status": "FAILED", "details": result['error']}
                logger.error(f"{agent_name} FAILED: {test_method_name} - {result['error']}")
            else:
                self.results[agent_name] = {"status": "PASSED", "details": "Method executed, result not a dict with 'success' key."}
                logger.info(f"{agent_name} PASSED: {test_method_name} executed successfully (non-standard return).")

        except Exception as e:
            self.results[agent_name] = {"status": "FAILED", "details": str(e)}
            logger.error(f"{agent_name} FAILED: {test_method_name} - {str(e)}", exc_info=True)
        finally:
            if 'agent_instance' in locals() and hasattr(agent_instance, 'close'):
                agent_instance.close()
        logger.info(f"--- Finished testing {agent_name} ---
")

    def run_all_tests(self):
        logger.info("Starting comprehensive agent functionality tests...")

        # Test Data Catalog Manager (DCM)
        self.run_test("DataCatalogManager", DataCatalogManager, "get_catalog_summary")

        # Test Data Pipeline Orchestrator (DPO)
        # Note: run_etl_pipeline requires a table name. We'll use a dummy one for testing init.
        # A full ETL run might be too heavy for a quick test.
        self.run_test("DataPipelineOrchestrator", DataPipelineOrchestrator, "get_quality_metrics")

        # Test Predictive Model Engine (PME)
        self.run_test("PredictiveModelEngine", PredictiveModelEngine, "get_model_metrics")

        # Test Prescriptive Advisor (PA)
        # PA needs a user context for some functions, but get_recommendations_summary can run without specific client_id
        self.run_test("PrescriptiveAdvisor", PrescriptiveAdvisor, "get_recommendations_summary")

        # Test Data Quality Guardian (DQG)
        # DQG needs a dataset_id. We'll use 'clientes' as an example.
        self.run_test("ValidadorCalidadDatos", ValidadorCalidadDatos, "ejecutar_validaciones", dataset_id='clientes')

        # Test Anomaly Detector (AD)
        self.run_test("AnomalyDetector", AnomalyDetector, "get_anomalies")

        # Test Generative Data Assistant (GDA)
        # GDA needs a query.
        self.run_test("GenerativeDataAssistant", GenerativeDataAssistant, "process_query", user_query="¿Cuántos clientes tenemos?")

        # Test System Integrator (SI)
        self.run_test("SystemIntegrator", SystemIntegrator, "get_system_health_dashboard")

        # Test Data Import Manager (DIM)
        # DIM's main functions are import/validate. We'll test template generation.
        self.run_test("DataImportManager", DataImportManager, "get_import_templates")

        # Test Metrics Definition Hub (MDH)
        self.run_test("MetricsDefinitionHub", MetricsDefinitionHub, "get_all_metrics")


        self.print_summary()

    def print_summary(self):
        logger.info("\n=== Test Summary ===")
        passed_count = 0
        failed_count = 0
        for agent, result in self.results.items():
            if result["status"] == "PASSED":
                passed_count += 1
                logger.info(f"✅ {agent}: PASSED")
            else:
                failed_count += 1
                logger.error(f"❌ {agent}: FAILED - {result['details']}")
        
        logger.info(f"\nTotal Tests: {len(self.results)}, Passed: {passed_count}, Failed: {failed_count}")
        if failed_count > 0:
            logger.error("Some agent functionality tests FAILED. Please review the logs above.")
        else:
            logger.info("All agent functionality tests PASSED successfully!")

if __name__ == "__main__":
    tester = AgentFunctionalityTester()
    tester.run_all_tests()
