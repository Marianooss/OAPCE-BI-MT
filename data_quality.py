"""
Data Quality Guardian (DQG) - Agente 9
Módulo para monitorear y garantizar la calidad de los datos
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import get_db
from models import Cliente, Factura, Vendedor, ActividadVenta, DataQualityLog
import logging
import pandas as pd

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidadorCalidadDatos:
    """
    Guardián de calidad de datos para el sistema OAPCE
    """

    def __init__(self, config_path='config/calidad.yaml'):
        self.db = get_db()
        self.config = self._cargar_configuracion_default()
        self.metricas_calidad = {}

    def _cargar_configuracion_default(self) -> dict:
        """Carga configuración por defecto de calidad de datos"""
        return {
            'datasets': [
                {'id': 'clientes', 'nombre': 'Clientes'},
                {'id': 'facturas', 'nombre': 'Facturas'},
                {'id': 'vendedores', 'nombre': 'Vendedores'},
                {'id': 'actividades_venta', 'nombre': 'Actividades de Venta'}
            ],
            'reglas': [
                {
                    'id': 'completitud_campos_obligatorios',
                    'nombre': 'Campos obligatorios completos',
                    'tipo': 'completitud',
                    'severidad': 'alta',
                    'activa': True,
                    'parametros': {
                        'campos_obligatorios': {
                            'clientes': ['nombre', 'rut', 'email'],
                            'facturas': ['numero_factura', 'cliente_id', 'monto_total', 'fecha_emision'],
                            'vendedores': ['nombre', 'email'],
                            'actividades_venta': ['vendedor_id', 'tipo_actividad', 'fecha']
                        }
                    }
                },
                {
                    'id': 'rango_valores',
                    'nombre': 'Valores dentro de rangos aceptables',
                    'tipo': 'rango',
                    'severidad': 'media',
                    'activa': True,
                    'parametros': {
                        'rangos': {
                            'clientes': {
                                'valor_estimado': {'min': 0, 'max': 100000000}  # Hasta 100M
                            },
                            'facturas': {
                                'monto_total': {'min': 0, 'max': 10000000}  # Hasta 10M
                            },
                            'vendedores': {
                                'meta_mensual': {'min': 0, 'max': 10000000},
                                'comision_porcentaje': {'min': 0, 'max': 50}  # Máximo 50%
                            }
                        }
                    }
                },
                {
                    'id': 'consistencia_relacional',
                    'nombre': 'Consistencia en relaciones de datos',
                    'tipo': 'consistencia',
                    'severidad': 'media',
                    'activa': True
                },
                {
                    'id': 'unicidad_registros',
                    'nombre': 'Ausencia de duplicados',
                    'tipo': 'unicidad',
                    'severidad': 'alta',
                    'activa': True,
                    'parametros': {
                        'campos_unicos': {
                            'clientes': ['rut'],
                            'facturas': ['numero_factura'],
                            'vendedores': ['email']
                        }
                    }
                }
            ],
            'intervalo_monitoreo': 3600,  # 1 hora en segundos
            'umbral_alerta_critica': 80,
            'umbral_alerta_advertencia': 95
        }

    def ejecutar_validaciones(self, dataset_id: str) -> dict:
        """
        Ejecuta todas las validaciones configuradas para un conjunto de datos
        """
        logger.info(f"Ejecutando validaciones de calidad para {dataset_id}")

        start_time = time.time()

        try:
            # Obtener datos del dataset
            datos = self._obtener_datos_dataset(dataset_id)
            if not datos:
                return {
                    'success': False,
                    'dataset_id': dataset_id,
                    'error': f'No se pudieron obtener datos para {dataset_id}'
                }

            resultados = {
                'dataset_id': dataset_id,
                'timestamp': datetime.now(),
                'metricas': {},
                'problemas': [],
                'puntuacion_general': 0.0
            }

            # Ejecutar cada regla de validación
            for regla in self.config['reglas']:
                if regla['activa']:
                    logger.info(f"Validando regla: {regla['id']}")
                    resultado_regla = self._aplicar_regla(regla, datos, dataset_id)
                    resultados['metricas'][regla['id']] = resultado_regla

                    # Agregar problemas encontrados
                    if resultado_regla.get('problemas'):
                        for problema in resultado_regla['problemas']:
                            resultados['problemas'].append({
                                'regla_id': regla['id'],
                                'tipo': regla['tipo'],
                                'severidad': regla['severidad'],
                                **problema
                            })

            # Calcular puntuación general
            resultados['puntuacion_general'] = self._calcular_puntuacion_general(resultados)

            # Guardar resultados en base de datos
            self._guardar_resultados_calidad(resultados)

            execution_time = time.time() - start_time


            return {
                'success': True,
                'dataset_id': dataset_id,
                'puntuacion_general': resultados['puntuacion_general'],
                'total_problemas': len(resultados['problemas']),
                'metricas': resultados['metricas'],
                'execution_time': execution_time,
                'timestamp': resultados['timestamp']
            }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error ejecutando validaciones para {dataset_id}: {str(e)}")
            return {
                'success': False,
                'dataset_id': dataset_id,
                'error': str(e),
                'execution_time': execution_time
            }

    def _obtener_datos_dataset(self, dataset_id: str) -> List[Dict]:
        """
        Obtiene los datos de un dataset específico
        """
        try:
            if dataset_id == 'clientes':
                clientes = self.db.query(Cliente).all()
                return [{
                    'id': c.id,
                    'nombre': c.nombre,
                    'rut': c.rut,
                    'email': c.email,
                    'telefono': c.telefono,
                    'estado_funnel': str(c.estado_funnel),
                    'valor_estimado': c.valor_estimado,
                    'fecha_ingreso': c.fecha_ingreso,
                    'vendedor_id': c.vendedor_id
                } for c in clientes]

            elif dataset_id == 'facturas':
                facturas = self.db.query(Factura).all()
                return [{
                    'id': f.id,
                    'numero_factura': f.numero_factura,
                    'cliente_id': f.cliente_id,
                    'fecha_emision': f.fecha_emision,
                    'fecha_vencimiento': f.fecha_vencimiento,
                    'monto_total': f.monto_total,
                    'monto_pagado': f.monto_pagado,
                    'estado': str(f.estado)
                } for f in facturas]

            elif dataset_id == 'vendedores':
                vendedores = self.db.query(Vendedor).all()
                return [{
                    'id': v.id,
                    'nombre': v.nombre,
                    'email': v.email,
                    'telefono': v.telefono,
                    'meta_mensual': v.meta_mensual,
                    'comision_porcentaje': v.comision_porcentaje,
                    'activo': v.activo
                } for v in vendedores]

            elif dataset_id == 'actividades_venta':
                actividades = self.db.query(ActividadVenta).all()
                return [{
                    'id': a.id,
                    'vendedor_id': a.vendedor_id,
                    'fecha': a.fecha,
                    'tipo_actividad': a.tipo_actividad,
                    'monto_estimado': a.monto_estimado
                } for a in actividades]

            else:
                logger.warning(f"Dataset no reconocido: {dataset_id}")
                return []

        except Exception as e:
            logger.error(f"Error obteniendo datos de {dataset_id}: {str(e)}")
            return []

    def _aplicar_regla(self, regla: dict, datos: List[Dict], dataset_id: str) -> dict:
        """
        Aplica una regla de validación específica a los datos
        """
        try:
            regla['dataset_id'] = dataset_id # Add dataset_id to rule for sub-functions

            if regla['id'] == 'completitud_campos_obligatorios':
                return self._validar_completitud(regla, datos)
            elif regla['id'] == 'rango_valores':
                return self._validar_rangos(regla, datos)
            elif regla['id'] == 'consistencia_relacional':
                return self._validar_consistencia_relacional(regla, datos)
            elif regla['id'] == 'unicidad_registros':
                return self._validar_unicidad(regla, datos)
            else:
                return {'success': False, 'error': f'Regla no implementada: {regla["id"]}'}

        except Exception as e:
            logger.error(f"Error aplicando regla {regla['id']}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _validar_completitud(self, regla: dict, datos: List[Dict]) -> dict:
        """
        Valida completitud de campos obligatorios
        """
        dataset_id = regla.get('dataset_id', 'unknown')
        campos_obligatorios = regla['parametros']['campos_obligatorios'].get(dataset_id, [])

        if not campos_obligatorios:
            return {'success': False, 'error': f'No hay campos obligatorios definidos para {dataset_id}'}

        total_registros = len(datos)
        problemas = []

        for i, registro in enumerate(datos):
            for campo in campos_obligatorios:
                valor = registro.get(campo)
                if valor is None or (isinstance(valor, str) and valor.strip() == ''):
                    problemas.append({
                        'registro_id': registro.get('id', i),
                        'campo': campo,
                        'tipo_problema': 'campo_obligatorio_vacio',
                        'descripcion': f'Campo obligatorio vacío: {campo}'
                    })

        completitud = ((total_registros - len(problemas)) / total_registros * 100) if total_registros > 0 else 0

        return {
            'success': True,
            'tipo_validacion': 'completitud',
            'total_registros': total_registros,
            'registros_completos': total_registros - len(problemas),
            'registros_incompletos': len(problemas),
            'puntuacion': completitud,
            'problemas': problemas
        }

    def _validar_rangos(self, regla: dict, datos: List[Dict]) -> dict:
        """
        Valida que los valores estén dentro de rangos aceptables
        """
        dataset_id = regla.get('dataset_id', 'unknown')
        rangos = regla['parametros']['rangos'].get(dataset_id, {})

        total_registros = len(datos)
        problemas = []

        for registro in datos:
            for campo, limites in rangos.items():
                valor = registro.get(campo)
                if valor is not None:
                    if valor < limites['min'] or valor > limites['max']:
                        problemas.append({
                            'registro_id': registro.get('id'),
                            'campo': campo,
                            'valor': valor,
                            'tipo_problema': 'fuera_de_rango',
                            'descripcion': f'Valor fuera de rango [{limites["min"]}, {limites["max"]}]: {valor}'
                        })

        puntuacion = ((total_registros - len(problemas)) / total_registros * 100) if total_registros > 0 else 0

        return {
            'success': True,
            'tipo_validacion': 'rango',
            'total_registros': total_registros,
            'registros_validos': total_registros - len(problemas),
            'registros_invalidos': len(problemas),
            'puntuacion': puntuacion,
            'problemas': problemas
        }

    def _validar_consistencia_relacional(self, regla: dict, datos: List[Dict]) -> dict:
        """
        Valida consistencia en relaciones entre tablas
        """
        dataset_id = regla.get('dataset_id', 'unknown')
        problemas = []

        if dataset_id == 'clientes':
            # Verificar que los vendedores referenciados existen
            vendedores_ids = {v['id'] for v in self._obtener_datos_dataset('vendedores')}
            for cliente in datos:
                if cliente.get('vendedor_id') and cliente['vendedor_id'] not in vendedores_ids:
                    problemas.append({
                        'registro_id': cliente.get('id'),
                        'tipo_problema': 'referencia_invalida',
                        'descripcion': f'Vendedor ID {cliente["vendedor_id"]} no existe'
                    })

        elif dataset_id == 'facturas':
            # Verificar que los clientes referenciados existen
            clientes_ids = {c['id'] for c in self._obtener_datos_dataset('clientes')}
            for factura in datos:
                if factura.get('cliente_id') and factura['cliente_id'] not in clientes_ids:
                    problemas.append({
                        'registro_id': factura.get('id'),
                        'tipo_problema': 'referencia_invalida',
                        'descripcion': f'Cliente ID {factura["cliente_id"]} no existe'
                    })

        total_registros = len(datos)
        puntuacion = ((total_registros - len(problemas)) / total_registros * 100) if total_registros > 0 else 0

        return {
            'success': True,
            'tipo_validacion': 'consistencia',
            'total_registros': total_registros,
            'registros_consistentes': total_registros - len(problemas),
            'registros_inconsistentes': len(problemas),
            'puntuacion': puntuacion,
            'problemas': problemas
        }

    def _validar_unicidad(self, regla: dict, datos: List[Dict]) -> dict:
        """
        Valida ausencia de duplicados
        """
        dataset_id = regla.get('dataset_id', 'unknown')
        campos_unicos = regla['parametros']['campos_unicos'].get(dataset_id, [])

        if not campos_unicos:
            return {
                'success': False,
                'error': f'No hay campos únicos definidos para {dataset_id}'
            }

        total_registros = len(datos)
        problemas = []

        for campo in campos_unicos:
            valores_vistos = {}
            for registro in datos:
                valor = registro.get(campo)
                if valor is not None:
                    registro_id = registro.get('id')
                    if valor in valores_vistos:
                        problemas.append({
                            'registro_id': registro_id,
                            'campo': campo,
                            'valor': valor,
                            'tipo_problema': 'duplicado',
                            'descripcion': f'Valor duplicado en campo único {campo}: {valor}'
                        })
                    else:
                        valores_vistos[valor] = registro_id

        puntuacion = ((total_registros - len(problemas)) / total_registros * 100) if total_registros > 0 else 0

        return {
            'success': True,
            'tipo_validacion': 'unicidad',
            'total_registros': total_registros,
            'registros_unicos': total_registros - len(problemas),
            'registros_duplicados': len(problemas),
            'puntuacion': puntuacion,
            'problemas': problemas
        }

    def _calcular_puntuacion_general(self, resultados: dict) -> float:
        """
        Calcula puntuación general de calidad (0-100)
        """
        try:
            metricas = resultados.get('metricas', {})
            if not metricas:
                return 0.0

            # Pesos por tipo de métrica (priorizando calidad crítica)
            pesos = {
                'completitud_campos_obligatorios': 0.4,  # Más importante
                'unicidad_registros': 0.3,
                'rango_valores': 0.2,
                'consistencia_relacional': 0.1
            }

            puntuacion_total = 0.0
            peso_total = 0.0

            for regla_id, metrica in metricas.items():
                if metrica.get('success') and 'puntuacion' in metrica:
                    peso = pesos.get(regla_id, 0.1)
                    puntuacion_total += metrica['puntuacion'] * peso
                    peso_total += peso

            return puntuacion_total / peso_total if peso_total > 0 else 0.0

        except Exception as e:
            logger.error(f"Error calculando puntuación general: {str(e)}")
            return 0.0

    def _guardar_resultados_calidad(self, resultados: dict):
        """
        Guarda resultados de calidad en la base de datos
        """
        try:
            # Guardar métricas principales
            calidad_log = DataQualityLog(
                table_name=resultados['dataset_id'],
                operation='quality_check',
                records_processed=len(self._obtener_datos_dataset(resultados['dataset_id'])),
                records_successful=len(self._obtener_datos_dataset(resultados['dataset_id'])),
                quality_score=resultados['puntuacion_general'],
                details=json.dumps({
                    'metricas': resultados['metricas'],
                    'problemas': resultados['problemas'],
                    'puntuacion_general': resultados['puntuacion_general']
                })
            )
            self.db.add(calidad_log)
            self.db.commit()

        except Exception as e:
            logger.error(f"Error guardando resultados de calidad: {str(e)}")
            self.db.rollback()

    def obtener_estado_calidad(self, dataset_id: str) -> dict:
        """
        Obtiene el estado actual de calidad para un dataset
        """
        try:
            # Ejecutar validaciones actuales
            resultado = self.ejecutar_validaciones(dataset_id)
            if not resultado['success']:
                return resultado

            # Obtener historial de calidad
            historial = self.db.query(DataQualityLog).filter(
                DataQualityLog.table_name == dataset_id,
                DataQualityLog.operation == 'quality_check'
            ).order_by(DataQualityLog.timestamp.desc()).limit(10).all()

            historial_data = [{
                'timestamp': str(log.timestamp),
                'quality_score': log.quality_score,
                'total_problemas': len(json.loads(log.details).get('problemas', []))
            } for log in historial]

            return {
                'success': True,
                'dataset_id': dataset_id,
                'estado_actual': {
                    'puntuacion_general': resultado['puntuacion_general'],
                    'total_problemas': resultado['total_problemas'],
                    'timestamp': str(resultado['timestamp'])
                },
                'historial': historial_data,
                'alertas': self._generar_alertas(resultado)
            }

        except Exception as e:
            logger.error(f"Error obteniendo estado de calidad para {dataset_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _generar_alertas(self, resultado: dict) -> List[Dict]:
        """
        Genera alertas basadas en resultados de calidad
        """
        alertas = []
        puntuacion = resultado.get('puntuacion_general', 0)

        if puntuacion < self.config['umbral_alerta_critica']:
            alertas.append({
                'tipo': 'critica',
                'mensaje': f'Calidad crítica: {puntuacion:.1f}% - Se requieren acciones inmediatas',
                'recomendaciones': [
                    'Revisar y corregir problemas de calidad',
                    'Implementar validaciones en origen',
                    'Notificar a equipos responsables'
                ]
            })
        elif puntuacion < self.config['umbral_alerta_advertencia']:
            alertas.append({
                'tipo': 'advertencia',
                'mensaje': f'Calidad baja: {puntuacion:.1f}% - Monitoreo recomendado',
                'recomendaciones': [
                    'Revisar tendencias de calidad',
                    'Corregir problemas identificados',
                    'Mejorar procesos de captura'
                ]
            })

        return alertas

    def obtener_problemas(self, severidad: str = None) -> List[Dict]:
        """
        Obtiene problemas de calidad encontrados
        """
        try:
            # Obtener del historial más reciente
            problemas = []
            logs = self.db.query(DataQualityLog).filter(
                DataQualityLog.operation == 'quality_check'
            ).order_by(DataQualityLog.timestamp.desc()).limit(50).all()

            for log in logs:
                if log.details:
                    detalles = json.loads(log.details)
                    for problema in detalles.get('problemas', []):
                        if severidad and problema.get('severidad') != severidad:
                            continue
                        problemas.append({
                            'dataset_id': log.table_name,
                            'timestamp': str(log.timestamp),
                            **problema
                        })

            return problemas

        except Exception as e:
            logger.error(f"Error obteniendo problemas: {str(e)}")
            return []

    def monitorear_continuo(self):
        """
        Monitoreo continuo de calidad de datos (ejecutar como demonio)
        """
        logger.info("Iniciando monitoreo continuo de calidad de datos")

        while True:
            try:
                for dataset in self.config['datasets']:
                    logger.info(f"Verificando calidad de {dataset['id']}")
                    resultado = self.ejecutar_validaciones(dataset['id'])

                    if resultado['success']:
                        alertas = self._generar_alertas(resultado)
                        if alertas:
                            logger.warning(f"Alertas para {dataset['id']}: {[a['mensaje'] for a in alertas]}")

                time.sleep(self.config['intervalo_monitoreo'])

            except Exception as e:
                logger.error(f"Error en monitoreo continuo: {str(e)}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar

    def close(self):
        """Cierra la sesión de base de datos"""
        self.db.close()
