"""
Data Catalog Manager (DCM) - Agente 2
Módulo para mantener catálogo actualizado de activos de datos del DWH
Cumple con Agents.md para gestión automática de metadatos y esquemas
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import text, inspect
from database import get_db
from models import *
from unified_logger import unified_logger


class DataCatalogManager:
    """
    Mantiene catálogo actualizado de todos los activos de datos del DWH
    Según especificaciones de Agents.md para el agente DCM
    """

    def __init__(self):
        self.db = get_db()
        self.catalog_schema = self._ensure_catalog_schema()

    def _ensure_catalog_schema(self) -> Dict:
        """Asegura que las tablas de catálogo existan"""
        try:
            # Tabla de metadatos de tablas
            catalog_tables = """
            CREATE TABLE IF NOT EXISTS data_catalog_tables (
                table_name TEXT PRIMARY KEY,
                schema_name TEXT,
                description TEXT,
                source_system TEXT,
                refresh_frequency TEXT,
                last_updated TIMESTAMP,
                row_count INTEGER,
                column_count INTEGER,
                data_quality_score REAL,
                sensitivity_level TEXT CHECK (sensitivity_level IN ('public', 'internal', 'sensitive', 'restricted')),
                tags TEXT,  -- JSON array
                metadata_json TEXT,  -- Extended metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """

            # Tabla de metadatos de columnas
            catalog_columns = """
            CREATE TABLE IF NOT EXISTS data_catalog_columns (
                table_name TEXT,
                column_name TEXT,
                data_type TEXT,
                description TEXT,
                nullable BOOLEAN,
                primary_key BOOLEAN DEFAULT FALSE,
                foreign_key BOOLEAN DEFAULT FALSE,
                foreign_key_table TEXT,
                foreign_key_column TEXT,
                sample_values TEXT,  -- JSON array
                data_quality_metrics TEXT,  -- JSON object
                sensitivity_level TEXT CHECK (sensitivity_level IN ('public', 'internal', 'sensitive', 'restricted')),
                tags TEXT,  -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (table_name, column_name)
            )
            """

            # Tabla de relaciones entre tablas
            catalog_relationships = """
            CREATE TABLE IF NOT EXISTS data_catalog_relationships (
                source_table TEXT,
                source_column TEXT,
                target_table TEXT,
                target_column TEXT,
                relationship_type TEXT CHECK (relationship_type IN ('one_to_one', 'one_to_many', 'many_to_many')),
                relationship_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source_table, source_column, target_table, target_column)
            )
            """

            # Tabla de historial de cambios
            catalog_changes = """
            CREATE TABLE IF NOT EXISTS data_catalog_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                change_type TEXT CHECK (change_type IN ('table_added', 'table_removed', 'column_added', 'column_removed', 'column_modified')),
                object_type TEXT CHECK (object_type IN ('table', 'column', 'relationship')),
                object_name TEXT,
                table_name TEXT,
                old_value TEXT,
                new_value TEXT,
                change_reason TEXT,
                changed_by TEXT DEFAULT 'system',
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """

            with self.db.begin():
                self.db.execute(text(catalog_tables))
                self.db.execute(text(catalog_columns))
                self.db.execute(text(catalog_relationships))
                self.db.execute(text(catalog_changes))

            unified_logger.info(
                agent="dcm",
                message="Catalog schema initialized successfully",
                details={"tables_created": ["data_catalog_tables", "data_catalog_columns", "data_catalog_relationships", "data_catalog_changes"]}
            )

        except Exception as e:
            unified_logger.error(
                agent="dcm",
                message="Error initializing catalog schema",
                details={"error": str(e)}
            )
            raise

        return {"initialized": True}

    def scan_database_schema(self) -> Dict:
        """
        Escanea el esquema completo de la base de datos y actualiza el catálogo
        Según Agents.md: "Mantiene un catálogo actualizado de todos los activos de datos del DWH"
        """
        try:
            unified_logger.log_agent_activity(
                agent="dcm",
                action="schema_scan_started",
                status="started"
            )

            inspector = inspect(self.db)
            tables_found = inspector.get_table_names()
            tables_processed = 0
            columns_processed = 0

            for table_name in tables_found:
                try:
                    # Ignorar tablas del sistema y catálogo
                    if table_name.startswith('sqlite_') or table_name.startswith('data_catalog_'):
                        continue

                    # Procesar tabla
                    self._process_table_metadata(table_name, inspector)
                    tables_processed += 1

                    # Procesar columnas
                    columns_in_table = self._process_column_metadata(table_name, inspector)
                    columns_processed += len(columns_in_table)

                except Exception as e:
                    unified_logger.log_agent_activity(
                        agent="dcm",
                        action="schema_scan_error",
                        details={"table_name": table_name, "error": str(e)}
                    )

            # Detectar cambios desde el último scan
            changes_detected = self._detect_schema_changes()

            unified_logger.log_agent_activity(
                agent="dcm",
                action="schema_scan_completed",
                status="completed",
                details={
                    "tables_processed": tables_processed,
                    "columns_processed": columns_processed,
                    "changes_detected": len(changes_detected)
                }
            )

            return {
                "success": True,
                "tables_processed": tables_processed,
                "columns_processed": columns_processed,
                "changes_detected": changes_detected,
                "last_scan": datetime.now().isoformat()
            }

        except Exception as e:
            unified_logger.log_agent_activity(
                agent="dcm",
                action="schema_scan_failed",
                status="failed",
                details={"error": str(e)}
            )
            return {"success": False, "error": str(e)}

    def _process_table_metadata(self, table_name: str, inspector) -> None:
        """Procesa y guarda metadatos de una tabla"""
        try:
            # Obtener información básica de la tabla
            columns = inspector.get_columns(table_name)
            row_count = self._get_table_row_count(table_name)

            # Metadatos básicos
            table_metadata = {
                "table_name": table_name,
                "schema_name": "main",  # SQLite
                "description": self._infer_table_description(table_name),
                "source_system": self._infer_source_system(table_name),
                "refresh_frequency": "daily",  # Por defecto según DPO
                "last_updated": datetime.now(),
                "row_count": row_count,
                "column_count": len(columns),
                "data_quality_score": 95.0,  # Placeholder
                "sensitivity_level": self._infer_sensitivity_level(table_name),
                "tags": json.dumps(self._infer_table_tags(table_name)),
                "metadata_json": json.dumps({
                    "has_primary_key": any(col.get('primary_key') for col in columns),
                    "has_foreign_keys": any(col.get('foreign_key') for col in columns),
                    "estimated_size_mb": (row_count * len(columns) * 50) / (1024 * 1024),  # Estimado
                    "last_accessed": datetime.now().isoformat()
                })
            }

            # Upsert en catálogo
            with self.db.begin():
                # Verificar si existe
                existing = self.db.execute(
                    text("SELECT table_name FROM data_catalog_tables WHERE table_name = :table_name"),
                    {"table_name": table_name}
                ).fetchone()

                if existing:
                    # Update
                    self.db.execute(text("""
                        UPDATE data_catalog_tables
                        SET last_updated = :last_updated,
                            row_count = :row_count,
                            column_count = :column_count,
                            updated_at = :updated_at
                        WHERE table_name = :table_name
                    """), {
                        **table_metadata,
                        "updated_at": datetime.now()
                    })
                else:
                    # Insert
                    self.db.execute(text("""
                        INSERT INTO data_catalog_tables
                        (table_name, schema_name, description, source_system, refresh_frequency,
                         last_updated, row_count, column_count, data_quality_score, sensitivity_level,
                         tags, metadata_json)
                        VALUES (:table_name, :schema_name, :description, :source_system, :refresh_frequency,
                               :last_updated, :row_count, :column_count, :data_quality_score, :sensitivity_level,
                               :tags, :metadata_json)
                    """), table_metadata)

                    # Log cambio
                    self._log_catalog_change('table_added', 'table', table_name, '', '', 'DCM scan')

        except Exception as e:
            unified_logger.error(
                agent="dcm",
                message="Error processing table metadata",
                details={"table_name": table_name, "error": str(e)}
            )

    def _process_column_metadata(self, table_name: str, inspector) -> List[str]:
        """Procesa y guarda metadatos de columnas de una tabla"""
        try:
            columns = inspector.get_columns(table_name)
            processed_columns = []

            for col in columns:
                column_name = col['name']

                # Obtener datos de muestra
                sample_values = self._get_column_samples(table_name, column_name)

                column_metadata = {
                    "table_name": table_name,
                    "column_name": column_name,
                    "data_type": str(col['type']),
                    "description": self._infer_column_description(table_name, column_name),
                    "nullable": col.get('nullable', True),
                    "primary_key": col.get('primary_key', False),
                    "foreign_key": col.get('foreign_key', False),
                    "foreign_key_table": None,  # SQLite no soporta directamente
                    "foreign_key_column": None,  # SQLite no soporta directamente
                    "sample_values": json.dumps(sample_values[:5]),  # Top 5 valores
                    "data_quality_metrics": json.dumps({
                        "null_percentage": self._calculate_null_percentage(table_name, column_name),
                        "unique_values": len(set(sample_values)),
                        "data_type_consistency": 95.0  # Placeholder
                    }),
                    "sensitivity_level": self._infer_column_sensitivity(table_name, column_name),
                    "tags": json.dumps(self._infer_column_tags(table_name, column_name))
                }

                # Upsert columna
                with self.db.begin():
                    self.db.execute(text("""
                        INSERT OR REPLACE INTO data_catalog_columns
                        (table_name, column_name, data_type, description, nullable, primary_key,
                         foreign_key, foreign_key_table, foreign_key_column, sample_values,
                         data_quality_metrics, sensitivity_level, tags)
                        VALUES (:table_name, :column_name, :data_type, :description, :nullable, :primary_key,
                               :foreign_key, :foreign_key_table, :foreign_key_column, :sample_values,
                               :data_quality_metrics, :sensitivity_level, :tags)
                    """), column_metadata)

                processed_columns.append(column_name)

            return processed_columns

        except Exception as e:
            unified_logger.error(
                agent="dcm",
                message="Error processing column metadata",
                details={"table_name": table_name, "error": str(e)}
            )
            return []

    def _detect_schema_changes(self) -> List[Dict]:
        """Detecta cambios en el esquema desde el último scan"""
        try:
            # Esta es una implementación básica
            # En producción, compararía con un snapshot anterior
            changes = []

            # Detectar nuevas tablas
            current_tables = self.db.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            ).fetchall()

            cataloged_tables = self.db.execute(
                text("SELECT table_name FROM data_catalog_tables")
            ).fetchall()

            current_table_names = {t[0] for t in current_tables}
            cataloged_table_names = {t[0] for t in cataloged_tables}

            # Nuevas tablas
            new_tables = current_table_names - cataloged_table_names
            for table_name in new_tables:
                changes.append({
                    "change_type": "table_added",
                    "object_type": "table",
                    "object_name": table_name,
                    "table_name": table_name
                })

            # Tablas removidas
            removed_tables = cataloged_table_names - current_table_names
            for table_name in removed_tables:
                changes.append({
                    "change_type": "table_removed",
                    "object_type": "table",
                    "object_name": table_name,
                    "table_name": table_name
                })

            return changes

        except Exception as e:
            unified_logger.error(
                agent="dcm",
                message="Error detecting schema changes",
                details={"error": str(e)}
            )
            return []

    def _log_catalog_change(self, change_type: str, object_type: str, object_name: str,
                           old_value: str = "", new_value: str = "", reason: str = "") -> None:
        """Registra cambios en el catálogo"""
        try:
            with self.db.begin():
                self.db.execute(text("""
                    INSERT INTO data_catalog_changes
                    (change_type, object_type, object_name, old_value, new_value, change_reason)
                    VALUES (:change_type, :object_type, :object_name, :old_value, :new_value, :change_reason)
                """), {
                    "change_type": change_type,
                    "object_type": object_type,
                    "object_name": object_name,
                    "old_value": old_value,
                    "new_value": new_value,
                    "change_reason": reason
                })
        except Exception as e:
            unified_logger.error(
                agent="dcm",
                message="Error logging catalog change",
                details={"error": str(e)}
            )

    def get_table_metadata(self, table_name: str) -> Optional[Dict]:
        """Obtiene metadatos de una tabla específica"""
        try:
            result = self.db.execute(
                text("SELECT * FROM data_catalog_tables WHERE table_name = :table_name"),
                {"table_name": table_name}
            ).fetchone()

            if result:
                return {
                    "table_name": result[0],
                    "schema_name": result[1],
                    "description": result[2],
                    "source_system": result[3],
                    "refresh_frequency": result[4],
                    "last_updated": str(result[5]),
                    "row_count": result[6],
                    "column_count": result[7],
                    "data_quality_score": result[8],
                    "sensitivity_level": result[9],
                    "tags": json.loads(result[10]) if result[10] else [],
                    "metadata_json": json.loads(result[11]) if result[11] else {}
                }
            return None

        except Exception as e:
            unified_logger.error(
                agent="dcm",
                message="Error getting table metadata",
                details={"table_name": table_name, "error": str(e)}
            )
            return None

    def get_table_columns(self, table_name: str) -> List[Dict]:
        """Obtiene metadatos de columnas de una tabla"""
        try:
            results = self.db.execute(
                text("SELECT * FROM data_catalog_columns WHERE table_name = :table_name ORDER BY column_name"),
                {"table_name": table_name}
            ).fetchall()

            columns = []
            for result in results:
                columns.append({
                    "column_name": result[1],
                    "data_type": result[2],
                    "description": result[3],
                    "nullable": result[4],
                    "primary_key": result[5],
                    "foreign_key": result[6],
                    "sample_values": json.loads(result[9]) if result[9] else [],
                    "sensitivity_level": result[12]
                })

            return columns

        except Exception as e:
            unified_logger.error(
                agent="dcm",
                message="Error getting table columns metadata",
                details={"table_name": table_name, "error": str(e)}
            )
            return []

    def close(self):
        """Cierra la sesión de base de datos"""
        self.db.close()

    # Métodos auxiliares para inferencia
    def _infer_table_description(self, table_name: str) -> str:
        descriptions = {
            'clientes': 'Información de clientes y prospectos',
            'facturas': 'Documentos de facturación y cobros',
            'vendedores': 'Información de equipo de ventas',
            'actividades_venta': 'Registro de actividades comerciales',
            'cobranzas': 'Movimientos de cobros y pagos',
            'movimientos_caja': 'Movimientos de caja y finanzas'
        }
        return descriptions.get(table_name, f'Tabla {table_name}')

    def _infer_source_system(self, table_name: str) -> str:
        return 'Sistema OAPCE Operacional'

    def _infer_sensitivity_level(self, table_name: str) -> str:
        sensitive_tables = ['clientes', 'cobranzas']
        if table_name in sensitive_tables:
            return 'sensitive'
        return 'internal'

    def _infer_table_tags(self, table_name: str) -> List[str]:
        base_tags = ['oapce', 'operational']
        if 'cliente' in table_name or 'venta' in table_name:
            base_tags.append('sales')
        if 'factura' in table_name or 'cobranza' in table_name:
            base_tags.append('finance')
        return base_tags

    def _infer_column_description(self, table_name: str, column_name: str) -> str:
        # Lógica básica de inferencia
        if 'id' in column_name:
            return 'Identificador único'
        elif 'fecha' in column_name or 'date' in column_name:
            return 'Fecha del registro'
        elif 'monto' in column_name or 'valor' in column_name:
            return 'Valor monetario'
        elif 'estado' in column_name:
            return 'Estado del registro'
        elif 'nombre' in column_name or 'name' in column_name:
            return 'Nombre o descripción'
        return f'Campo {column_name}'

    def _infer_column_sensitivity(self, table_name: str, column_name: str) -> str:
        sensitive_columns = ['monto', 'valor_estimado', 'saldo']
        if any(sensitive in column_name for sensitive in sensitive_columns):
            return 'sensitive'
        return 'internal'

    def _infer_column_tags(self, table_name: str, column_name: str) -> List[str]:
        tags = []
        if 'id' in column_name:
            tags.append('primary_key')
        if 'fecha' in column_name:
            tags.append('temporal')
        if 'monto' in column_name or 'valor' in column_name:
            tags.append('metric')
        return tags

    def _get_table_row_count(self, table_name: str) -> int:
        """Obtiene el número de filas en una tabla"""
        try:
            result = self.db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()
        except Exception as e:
            unified_logger.error(
                agent="dcm",
                message=f"Error getting row count for table {table_name}",
                details={"error": str(e)}
            )
            return 0

    def _get_column_samples(self, table_name: str, column_name: str, limit: int = 100) -> List[Any]:
        """Obtiene valores de muestra de una columna"""
        try:
            result = self.db.execute(
                text(f"SELECT DISTINCT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL LIMIT {limit}")
            ).fetchall()
            return [row[0] for row in result]
        except Exception as e:
            unified_logger.error(
                agent="dcm",
                message=f"Error getting sample values for column {table_name}.{column_name}",
                details={"error": str(e)}
            )
            return []

    def _calculate_null_percentage(self, table_name: str, column_name: str) -> float:
        """Calcula el porcentaje de valores nulos en una columna"""
        try:
            total_count = self.db.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            ).fetchone()[0]

            null_count = self.db.execute(
                text(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NULL")
            ).fetchone()[0]

            return round((null_count / total_count * 100), 2) if total_count > 0 else 0
        except Exception as e:
            unified_logger.error(
                agent="dcm",
                message=f"Error calculating null percentage for column {table_name}.{column_name}",
                details={"error": str(e)}
            )
            return 0
