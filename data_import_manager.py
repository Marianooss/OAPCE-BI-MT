"""
Data Import Manager (DIM) - Agente 10
Sistema de importación y migración de datos para producción
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from database import get_db, init_db_real_data
from models import Cliente, Factura, Vendedor, ActividadVenta
from unified_logger import unified_logger
from metrics_hub import MetricsDefinitionHub
import logging
from sqlalchemy import Table, MetaData, DateTime, Date, select
from sqlalchemy.sql import text
from datetime import datetime, date

logger = logging.getLogger(__name__)

class DataImportManager:
    """
    Gestiona la importación, validación y migración de datos reales del cliente
    """

    def __init__(self):
        self.db = get_db()
        self.templates_dir = 'data_templates/'
        self.import_dir = 'import_data/'
        self.backup_dir = 'backups/'

        # Crear directorios necesarios
        for dir_path in [self.templates_dir, self.import_dir, self.backup_dir]:
            os.makedirs(dir_path, exist_ok=True)

        # Configuraciones de mapeo (ahora dinámicas)
        self.field_mappings = {}

    def _infer_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Infiere los tipos de datos de las columnas de un DataFrame de forma más robusta.
        """
        inferred_types = {}
        for col in df.columns:
            # Intentar inferir tipos más específicos
            # Primero, intentar numéricos
            if pd.api.types.is_numeric_dtype(df[col]):
                if pd.api.types.is_integer_dtype(df[col]):
                    inferred_types[col] = 'integer'
                elif pd.api.types.is_float_dtype(df[col]):
                    inferred_types[col] = 'float'
                else:
                    inferred_types[col] = 'numeric' # Catch-all for other numeric
            # Luego, intentar fechas
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                inferred_types[col] = 'datetime'
            else:
                # Intentar convertir a fecha si es un string
                try:
                    # Usar infer_datetime_format=True para mejor detección
                    temp_series = pd.to_datetime(df[col], errors='coerce')
                    if not temp_series.isnull().all(): # Si al menos algunos valores se pudieron convertir
                        inferred_types[col] = 'datetime'
                    else:
                        inferred_types[col] = 'string'
                except Exception:
                    # Intentar booleano
                    if df[col].astype(str).str.lower().isin(['true', 'false', '1', '0', 'yes', 'no']).any():
                        inferred_types[col] = 'boolean'
                    else:
                        inferred_types[col] = 'string' # Por defecto, string

        return inferred_types

    _SQL_TYPE_MAP = {
        'string': 'TEXT',
        'integer': 'INTEGER',
        'float': 'REAL',
        'datetime': 'DATETIME',
        'boolean': 'BOOLEAN',
        'numeric': 'REAL' # Fallback for generic numeric
    }

    def _alter_table_add_column(self, table_name: str, column_name: str, inferred_type: str) -> bool:
        """
        Añade dinámicamente una columna a una tabla de la base de datos.
        """
        sql_type = self._SQL_TYPE_MAP.get(inferred_type, 'TEXT') # Default to TEXT if type not found
        try:
            # Usar la conexión de la base de datos para ejecutar SQL crudo
            with self.db.begin() as conn:
                conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_type}'))
            unified_logger.info("dim", f"Columna {column_name} ({sql_type}) añadida a la tabla {table_name}.")
            return True
        except Exception as e:
            unified_logger.error("dim", f"Error al añadir columna {column_name} a la tabla {table_name}: {e}")
            return False

    def _get_db_model_schema(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene dinámicamente el esquema (columnas y tipos) de los modelos de la base de datos.
        """
        schema = {}
        # Importar los modelos para poder introspeccionarlos
        from models import Cliente, Factura, Vendedor, ActividadVenta

        model_map = {
            'clientes': Cliente,
            'facturas': Factura,
            'vendedores': Vendedor,
            'actividades_venta': ActividadVenta
        }

        for table_name, model in model_map.items():
            table_schema = {}
            for col in model.__table__.columns:
                table_schema[col.name] = str(col.type) # Guardar el tipo como string
            schema[table_name] = table_schema
        return schema

    def validate_import_file(self, file_path: str, table_name: str) -> Dict:
        """
        Valida un archivo para importación

        Args:
            file_path: Ruta del archivo a validar
            table_name: Nombre de la tabla destino

        Returns:
            Dict con resultado de validación
        """
        try:
            # Leer archivo según extensión
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8', sep=';')
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    df = pd.DataFrame(data)
            else:
                return {'success': False, 'error': 'Formato no soportado'}

            # Obtener esquema dinámico de la BD para validación
            db_schema = self._get_db_model_schema()
            target_table_cols = db_schema.get(table_name, {})

            if not target_table_cols:
                return {'success': False, 'error': f'Tabla {table_name} no encontrada en el esquema de la BD'}

            # Identificar campos requeridos dinámicamente (columnas no nulas)
            # Esto es una heurística; en un sistema real, se usarían metadatos más ricos
            required_fields = []
            engine = self.db.get_bind()
            metadata = MetaData()
            metadata.reflect(bind=engine)
            table = Table(table_name, metadata, autoload_with=engine)

            for col in table.columns:
                if not col.nullable:
                    required_fields.append(col.name)

            # Verificar campos requeridos
            missing_required = []
            for field in required_fields:
                if field not in df.columns:
                    missing_required.append(field)

            if missing_required:
                return {
                    'success': False,
                    'error': f'Campos requeridos faltantes: {", ".join(missing_required)}',
                    'missing_fields': missing_required
                }

            # Análisis de calidad
            quality_analysis = self._analyze_data_quality(df, table_name)

            return {
                'success': True,
                'file_info': {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'size_mb': os.path.getsize(file_path) / (1024 * 1024)
                },
                'field_mapping': self._generate_field_mapping(df, table_name),
                'quality_analysis': quality_analysis,
                'inferred_column_types': self._infer_column_types(df),
                'preview': df.head(5).to_dict('records')
            }

        except Exception as e:
            logger.error(f"Error validando archivo {file_path}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _analyze_data_quality(self, df: pd.DataFrame, table_name: str) -> Dict:
        """Analiza calidad de los datos"""

        analysis = {
            'total_rows': len(df),
            'null_analysis': {},
            'data_types': {},
            'duplicate_analysis': None,
            'issues': []
        }

        # Análisis de nulos
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_percentage = (null_count / len(df)) * 100
            analysis['null_analysis'][col] = {
                'null_count': int(null_count),
                'null_percentage': round(null_percentage, 2)
            }

        # Tipos de datos
        analysis['data_types'] = self._infer_column_types(df)

        # Análisis de duplicados
        duplicate_rows = df.duplicated().sum()
        analysis['duplicate_analysis'] = {
            'duplicate_rows': int(duplicate_rows),
            'duplicate_percentage': round((duplicate_rows / len(df)) * 100, 2)
        }

        # Detectar problemas
        if duplicate_rows > 0:
            analysis['issues'].append(f"{duplicate_rows} filas duplicadas ({analysis['duplicate_analysis']['duplicate_percentage']}%)")

        for col, null_info in analysis['null_analysis'].items():
            if null_info['null_percentage'] > 50:
                analysis['issues'].append(f"{col}: {null_info['null_percentage']}% nulos (muy alto)")

        return analysis

    def _generate_field_mapping(self, df: pd.DataFrame, table_name: str) -> Dict:
        """
        Genera mapeo automático de campos entre las columnas del archivo y las de la BD.
        Prioriza coincidencias exactas y luego flexibles. Retorna candidatos si no hay match directo.
        """

        db_schema = self._get_db_model_schema()
        target_table_cols = db_schema.get(table_name, {})

        mapping = {'mapped': {}, 'unmapped_file_cols': [], 'suggested': {}}
        mapped_db_cols = set()

        # Paso 1: Coincidencia exacta y flexible
        for file_col in df.columns:
            file_col_cleaned = file_col.lower().replace('_', '').replace(' ', '')
            found_match = False

            for db_col in target_table_cols.keys():
                db_col_cleaned = db_col.lower().replace('_', '').replace(' ', '')

                # Coincidencia exacta o muy cercana
                if file_col == db_col: # Exact match (case sensitive)
                    mapping['mapped'][file_col] = db_col
                    mapped_db_cols.add(db_col)
                    found_match = True
                    break
                elif file_col.lower() == db_col.lower(): # Case-insensitive match
                    mapping['mapped'][file_col] = db_col
                    mapped_db_cols.add(db_col)
                    found_match = True
                    break
                elif file_col_cleaned == db_col_cleaned: # Cleaned match
                    mapping['mapped'][file_col] = db_col
                    mapped_db_cols.add(db_col)
                    found_match = True
                    break

            if not found_match:
                mapping['unmapped_file_cols'].append(file_col)

        # Paso 2: Sugerir mapeos para columnas de DB no mapeadas (basado en análisis de nombres)
        # Esto es un paso intermedio. Idealmente, las sugerencias vendrían de un análisis más profundo.
        # La configuración hardcodeada de field_mappings ya no se usa aquí.

        # Identificar columnas de la BD que no fueron mapeadas
        unmapped_db_cols = [col for col in target_table_cols.keys() if col not in mapped_db_cols]

        for unmapped_db_col in unmapped_db_cols:
            # Intentar encontrar una columna del archivo no mapeada que sea una buena sugerencia
            for unmapped_file_col in mapping['unmapped_file_cols']:
                if unmapped_db_col.lower() in unmapped_file_col.lower() or unmapped_file_col.lower() in unmapped_db_col.lower():
                    mapping['suggested'][unmapped_file_col] = unmapped_db_col
                    break

        return mapping

    def import_data(self, file_path: str, table_name: str, field_mapping: Dict,
                   inferred_column_types: Dict[str, str], add_new_columns: List[str] = None,
                   transformation_rules: Optional[Dict] = None, dry_run: bool = True) -> Dict:
        """
        Importa datos desde archivo con mapeo de campos

        Args:
            file_path: Ruta del archivo
            table_name: Tabla destino
            field_mapping: Mapeo de campos origen -> destino
            transformation_rules: Reglas de transformación adicionales
            dry_run: Si True, solo simular sin modificar BD

        Returns:
            Dict con resultado de importación
        """
        try:
            start_time = datetime.now()

            # 1. Añadir nuevas columnas si se solicitan
            if add_new_columns and not dry_run:
                for col_name in add_new_columns:
                    inferred_type = inferred_column_types.get(col_name, 'string') # Default a string si no se infiere
                    if not self._alter_table_add_column(table_name, col_name, inferred_type):
                        return {'success': False, 'error': f'Fallo al añadir columna {col_name}'}

            # Leer archivo
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8', sep=';')
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    df = pd.DataFrame(data)

            # Aplicar mapeo de campos
            # Asegurarse de que field_mapping sea el diccionario 'mapped' si viene en la nueva estructura
            actual_mapping = field_mapping.get('mapped', field_mapping) if isinstance(field_mapping, dict) else field_mapping
            df_mapped = df.rename(columns=actual_mapping)

            # Aplicar transformaciones
            df_transformed = self._apply_transformations(df_mapped, table_name, transformation_rules)

            # Backup si no es dry run
            if not dry_run:
                backup_result = self._create_backup(table_name)
                if not backup_result['success']:
                    return {'success': False, 'error': 'Error creando backup'}

            # Importar datos
            import_result = self._execute_import(df_transformed, table_name, dry_run)

            duration = (datetime.now() - start_time).total_seconds()

            # Logging
            unified_logger.log_agent_activity(
                agent="dim",
                action="data_import",
                status="completed" if import_result['success'] else "failed",
                duration=duration,
                details={
                    "table": table_name,
                    "rows_imported": import_result.get('rows_imported', 0),
                    "dry_run": dry_run
                }
            )

            return {
                'success': import_result['success'],
                'dry_run': dry_run,
                'table': table_name,
                'rows_processed': len(df_transformed),
                'rows_imported': import_result.get('rows_imported', 0),
                'duration_seconds': round(duration, 2),
                'data_preview': df_transformed.head(3).to_dict('records') if import_result['success'] else None,
                'errors': import_result.get('errors', [])
            }

        except Exception as e:
            logger.error(f"Error importando datos: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _apply_transformations(self, df: pd.DataFrame, table_name: str,
                             transformation_rules: Optional[Dict] = None) -> pd.DataFrame:
        """Aplica transformaciones a los datos"""

        df_transformed = df.copy()
        config = self.field_mappings.get(table_name, {})

        # Transformaciones automáticas
        for col, transformation in config.get('transformations', {}).items():
            if col in df_transformed.columns:
                if transformation == 'date':
                    df_transformed[col] = pd.to_datetime(df_transformed[col], errors='coerce')
                elif transformation == 'currency':
                    # Limpiar caracteres monetarios y convertir a float
                    df_transformed[col] = df_transformed[col].astype(str).str.replace(r'[$,]', '', regex=True).astype(float)
                elif transformation == 'phone':
                    # Limpiar teléfonos
                    df_transformed[col] = df_transformed[col].astype(str).str.replace(r'[^\d+]', '', regex=True)
                elif transformation == 'boolean':
                    # Convertir a boolean
                    df_transformed[col] = df_transformed[col].astype(bool)

        # Transformaciones personalizadas
        if transformation_rules:
            for col, rule in transformation_rules.items():
                if col in df_transformed.columns:
                    if rule.get('type') == 'map_values':
                        mapping = rule.get('mapping', {})
                        df_transformed[col] = df_transformed[col].map(mapping)
                    elif rule.get('type') == 'fill_null':
                        df_transformed[col] = df_transformed[col].fillna(rule.get('value'))

        return df_transformed

    def _generic_import_to_db(self, df: pd.DataFrame, table_name: str, dry_run: bool) -> Dict:
        """
        Importa datos de un DataFrame a una tabla de la base de datos de forma genérica.
        """
        rows_imported = 0
        errors = []

        if dry_run:
            return {'success': True, 'rows_imported': len(df), 'errors': []}

        try:
            # Usar la conexión de la base de datos para obtener el motor
            engine = self.db.get_bind()
            metadata = MetaData()
            metadata.reflect(bind=engine)
            table = Table(table_name, metadata, autoload_with=engine)

            with self.db.begin() as conn:
                for idx, row in df.iterrows():
                    try:
                        # Filtrar columnas que no existen en la tabla de destino
                        insert_data = {col: row[col] for col in row.index if col in table.columns.keys()}

                        # Convertir NaT a None para columnas de fecha/hora
                        for col, value in insert_data.items():
                            if pd.isna(value) and isinstance(table.columns[col].type, (DateTime, Date)):
                                insert_data[col] = None

                        conn.execute(table.insert(), insert_data)
                        rows_imported += 1
                    except Exception as e:
                        errors.append(f"Fila {idx+1}: {str(e)}")
                self.db.commit()

            return {'success': True, 'rows_imported': rows_imported, 'errors': errors}

        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}

    def _execute_import(self, df: pd.DataFrame, table_name: str, dry_run: bool) -> Dict:
        """Ejecuta la importación física en la base de datos"""

        try:
            return self._generic_import_to_db(df, table_name, dry_run)

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _create_backup(self, table_name: str) -> Dict:
        """
        Crea backup antes de importar, exportando datos de la tabla de forma genérica.
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_dir, f'backup_{table_name}_{timestamp}.json')

            engine = self.db.get_bind()
            metadata = MetaData()
            metadata.reflect(bind=engine)
            table = Table(table_name, metadata, autoload_with=engine)

            # Seleccionar todos los registros de la tabla
            s = select(table)
            result = self.db.execute(s).fetchall()

            # Convertir a lista de diccionarios
            data = []
            for row in result:
                clean_record = {}
                for col_name, value in row._asdict().items():
                    # Convertir objetos no serializables a string (ej. datetime)
                    if isinstance(value, (datetime, date)):
                        clean_record[col_name] = value.isoformat()
                    else:
                        clean_record[col_name] = value
                data.append(clean_record)

            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'backup_date': timestamp,
                    'table': table_name,
                    'record_count': len(data),
                    'data': data
                }, f, indent=2, ensure_ascii=False, default=str)

            unified_logger.info("dim", f"Backup de tabla {table_name} creado en {backup_file}")
            return {'success': True, 'backup_file': backup_file}

        except Exception as e:
            unified_logger.error("dim", f"Error creando backup para tabla {table_name}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def migrate_from_demo_to_production(self) -> Dict:
        """
        Migra el sistema de datos de demostración a producción
        """
        try:
            # 1. Backup completo de datos de demo
            logger.info("Creando backup completo de datos de demostración...")
            full_backup_result = self._create_full_backup()
            if not full_backup_result['success']:
                return full_backup_result

            # 2. Limpiar datos de demostración
            logger.info("Limpiando datos de demostración...")
            clean_result = self._clean_demo_data()
            if not clean_result['success']:
                return clean_result

            # 3. Reinicializar base de datos para producción
            logger.info("Inicializando base de datos para producción...")
            init_db_real_data()

            # 4. Actualizar estado del sistema
            unified_logger.log_agent_activity(
                agent="dim",
                action="migration_to_production",
                status="completed",
                details={"full_backup_created": full_backup_result['success']}
            )

            return {
                'success': True,
                'message': 'Migración a producción completada exitosamente',
                'backup_info': full_backup_result,
                'migration_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error en migración a producción: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _create_full_backup(self) -> Dict:
        """
        Crea backup completo de todos los datos de forma genérica.
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_dir, f'full_backup_{timestamp}.json')

            full_data = {
                'backup_date': timestamp,
                'migration_purpose': 'demo_to_production',
                'tables': {}
            }

            engine = self.db.get_bind()
            metadata = MetaData()
            metadata.reflect(bind=engine)

            # Backup de cada tabla reflejada
            for table_name, table in metadata.tables.items():
                s = select(table)
                result = self.db.execute(s).fetchall()

                data = []
                for row in result:
                    clean_record = {}
                    for col_name, value in row._asdict().items():
                        if isinstance(value, (datetime, date)):
                            clean_record[col_name] = value.isoformat()
                        else:
                            clean_record[col_name] = value
                    data.append(clean_record)

                full_data['tables'][table_name] = {
                    'record_count': len(data),
                    'data': data
                }

            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(full_data, f, indent=2, ensure_ascii=False, default=str)

            unified_logger.info("dim", f"Backup completo creado en {backup_file}")
            return {
                'success': True,
                'backup_file': backup_file,
                'total_records': sum(t['record_count'] for t in full_data['tables'].values())
            }

        except Exception as e:
            unified_logger.error("dim", f"Error creando backup completo: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _clean_demo_data(self) -> Dict:
        """
        Limpia datos de demostración de todas las tablas de forma genérica.
        """
        try:
            engine = self.db.get_bind()
            metadata = MetaData()
            metadata.reflect(bind=engine)

            with self.db.begin() as conn:
                for table_name, table in metadata.tables.items():
                    # Evitar eliminar tablas del sistema si es necesario
                    if not table_name.startswith('sqlite_'): # Ejemplo para SQLite
                        conn.execute(table.delete())
            self.db.commit()
            unified_logger.info("dim", "Datos de demostración limpiados de todas las tablas.")
            return {'success': True}

        except Exception as e:
            self.db.rollback()
            unified_logger.error("dim", f"Error limpiando datos de demostración: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_import_templates(self) -> Dict:
        """
        Obtiene plantillas de importación para ayudar a los usuarios, generadas dinámicamente.
        """
        templates = {}
        db_schema = self._get_db_model_schema()

        for table_name, columns_info in db_schema.items():
            required_fields = []
            all_fields = []
            for col_name, col_type in columns_info.items():
                all_fields.append(col_name)
                # Asumimos que si no es nullable, es requerido para la plantilla
                # Esto es una simplificación; en un sistema real, se usarían metadatos más ricos
                # Para este ejemplo, si el tipo es 'INTEGER' o 'TEXT' y no es 'id', lo consideramos requerido
                # Esto es una heurística, no una regla estricta de DB
                if col_name != 'id' and ('INTEGER' in col_type or 'TEXT' in col_type or 'DATETIME' in col_type):
                    required_fields.append(col_name)

            templates[table_name] = {
                'required_fields': required_fields,
                'all_fields': all_fields,
                'example_data': self._generate_example_data(table_name, columns_info),
                'field_descriptions': self._get_field_descriptions(table_name, columns_info)
            }

        return templates

    def _generate_example_data(self, table_name: str, columns_info: Dict[str, str]) -> List[Dict]:
        """
        Genera datos de ejemplo genéricos para cada tabla basados en el esquema dinámico.
        """
        example_row = {}
        for col_name, col_type in columns_info.items():
            if col_name == 'id':
                example_row[col_name] = f'{table_name.upper()}_001'
            elif 'INTEGER' in col_type:
                example_row[col_name] = 123
            elif 'REAL' in col_type:
                example_row[col_name] = 123.45
            elif 'DATETIME' in col_type:
                example_row[col_name] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            elif 'BOOLEAN' in col_type:
                example_row[col_name] = True
            else: # Default a string
                example_row[col_name] = f'Ejemplo de {col_name}'
        return [example_row]

    def _get_field_descriptions(self, table_name: str, columns_info: Dict[str, str]) -> Dict:
        """
        Obtiene descripciones de campos genéricas basadas en el esquema dinámico.
        """
        descriptions = {}
        for col_name, col_type in columns_info.items():
            descriptions[col_name] = f'Campo {col_name} de tipo {col_type}.'
            if col_name == 'id':
                descriptions[col_name] = 'Identificador único para el registro.'
            elif 'fecha' in col_name.lower() or 'date' in col_name.lower():
                descriptions[col_name] = 'Fecha en formato YYYY-MM-DD o YYYY-MM-DD HH:MM:SS.'
            elif 'monto' in col_name.lower() or 'valor' in col_name.lower():
                descriptions[col_name] = 'Valor monetario o numérico.'
            elif 'email' in col_name.lower():
                descriptions[col_name] = 'Dirección de correo electrónico.'
            elif 'telefono' in col_name.lower():
                descriptions[col_name] = 'Número de teléfono.'
        return descriptions

    def export_template_file(self, table_name: str, format: str = 'csv') -> Dict:
        """Exporta archivo de plantilla para una tabla específica"""
        try:
            template_data = self.get_import_templates()
            if table_name not in template_data:
                return {'success': False, 'error': f'Tabla {table_name} no encontrada'}

            example_data = template_data[table_name]['example_data']
            if not example_data:
                return {'success': False, 'error': 'No hay datos de ejemplo disponibles'}

            # Crear DataFrame con datos de ejemplo
            df = pd.DataFrame(example_data)

            # Crear archivo de plantilla
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'template_{table_name}_{timestamp}.{format}'
            filepath = os.path.join(self.templates_dir, filename)

            if format == 'csv':
                df.to_csv(filepath, index=False, encoding='utf-8', sep=';')
            elif format == 'xlsx':
                df.to_excel(filepath, index=False, engine='openpyxl')
            elif format == 'json':
                df.to_json(filepath, orient='records', indent=2, date_format='iso', force_ascii=False)

            return {
                'success': True,
                'file_path': filepath,
                'filename': filename,
                'format': format,
                'columns': list(df.columns)
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def close(self):
        """Cierra conexiones del gestor de datos"""
        try:
            if hasattr(self, 'db'):
                self.db.close()
        except Exception as e:
            logger.error(f"Error cerrando conexiones: {str(e)}")


# Funciones de utilidad globales
def get_import_manager() -> DataImportManager:
    """Obtiene instancia del gestor de importación"""
    return DataImportManager()

def validate_import_file(file_path: str, table_name: str) -> Dict:
    """Función de conveniencia para validar archivos"""
    manager = DataImportManager()
    try:
        return manager.validate_import_file(file_path, table_name)
    finally:
        manager.close()

def migrate_to_production() -> Dict:
    """Función de conveniencia para migrar a producción"""
    manager = DataImportManager()
    try:
        return manager.migrate_from_demo_to_production()
    finally:
        manager.close()
