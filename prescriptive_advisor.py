"""
Prescriptive Advisor (PA) - Agente 4
Módulo para generar recomendaciones accionables basadas en predicciones
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database import get_db
from models import Cliente, Factura, Vendedor, ModelPrediction, ActividadVenta, MovimientoCaja, Cobranza
from predictive_models import PredictiveModelEngine
from auth import get_current_user
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PrescriptiveAdvisor:
    """
    Asesor prescriptivo que genera recomendaciones basadas en predicciones
    """

    def __init__(self, user: Optional[Dict] = None):
        self.db = get_db()
        self.pme = PredictiveModelEngine()
        self.user = user or get_current_user()

    def _filter_recommendations_by_role(self, recommendations: List[Dict]) -> List[Dict]:
        """Filtra recomendaciones según el rol del usuario."""
        if not self.user or 'rol' not in self.user:
            return recommendations  # Si no hay usuario o rol, devolver todo

        user_role = self.user['rol']
        
        # Mapeo de roles a categorías permitidas
        role_permissions = {
            'admin': ['ventas', 'finanzas', 'cobranza', 'atención', 'productividad', 'habilidades', 'equipo', 'operaciones', 'costos', 'riesgo'],
            'direccion': ['ventas', 'finanzas', 'cobranza', 'atención', 'productividad', 'habilidades', 'equipo', 'operaciones', 'costos', 'riesgo'],
            'finanzas': ['finanzas', 'cobranza', 'costos', 'riesgo'],
            'ventas': ['ventas', 'atención', 'productividad', 'habilidades', 'equipo'],
            'operaciones': ['operaciones', 'productividad', 'atención']
        }

        allowed_categories = role_permissions.get(user_role, [])
        
        return [rec for rec in recommendations if rec.get('category') in allowed_categories]

    def generate_client_recommendations(self, client_id: int = None, limit: int = 10) -> Dict:
        """
        Genera recomendaciones para clientes específicos o todos
        """
        try:
            if client_id:
                clients = [self.db.query(Cliente).filter(Cliente.id == client_id).first()]
                if not clients[0]:
                    return {"success": False, "error": f"Cliente {client_id} no encontrado"}
            else:
                # Si el rol es ventas, mostrar solo sus clientes
                if self.user and self.user.get('rol') == 'ventas':
                    vendedor = self.db.query(Vendedor).filter(Vendedor.email == self.user['email']).first()
                    if vendedor:
                        vendedor_id = vendedor.id
                        clients = self.db.query(Cliente).filter(Cliente.vendedor_id == vendedor_id).limit(limit).all()
                    else:
                        logger.warning(f"No se encontró vendedor para el email: {self.user['email']}")
                        clients = [] # No clients to recommend if seller not found
                else:
                    clients = self.db.query(Cliente).limit(limit).all()


            recommendations = []

            for client in clients:
                client_recs = self._analyze_client_situation(client)
                recommendations.extend(client_recs)

            # Filtrar por rol
            filtered_recs = self._filter_recommendations_by_role(recommendations)

            # Ordenar por impacto esperado (descendente)
            filtered_recs.sort(key=lambda x: x.get('impact_score', 0), reverse=True)

            return {
                "success": True,
                "recommendations": filtered_recs[:limit],
                "total_generated": len(filtered_recs)
            }

        except Exception as e:
            logger.error(f"Error generando recomendaciones de clientes: {str(e)}")
            return {"success": False, "error": str(e)}

    def _analyze_client_situation(self, client: Cliente) -> List[Dict]:
        """
        Analiza la situación de un cliente y genera recomendaciones
        """
        recommendations = []

        try:
            # Obtener predicciones del cliente
            risk_predictions = self.pme.get_predictions(
                prediction_type="risk_assessment",
                entity_type="cliente",
                entity_id=client.id
            )

            conversion_predictions = self.pme.get_predictions(
                prediction_type="conversion_probability",
                entity_type="cliente",
                entity_id=client.id
            )

            # Analizar riesgo de morosidad (con fallback si no hay predicciones)
            risk_recommendation = None
            if risk_predictions["success"] and risk_predictions["predictions"] and len(risk_predictions["predictions"]) > 0:
                risk_prob = risk_predictions["predictions"][0]["predicted_value"]

                if risk_prob > 0.7:
                    risk_recommendation = {
                        "type": "risk_mitigation",
                        "priority": "high",
                        "client_id": client.id,
                        "client_name": client.nombre,
                        "title": "Alto riesgo de morosidad detectado",
                        "description": f"El cliente {client.nombre} tiene {risk_prob:.1%} de probabilidad de morosidad",
                        "action": "Revisar condiciones de pago y considerar reducción de crédito",
                        "impact_score": 9.0,
                        "category": "finanzas",
                        "suggested_by": "PA"
                    }

                elif risk_prob > 0.4:
                    risk_recommendation = {
                        "type": "risk_monitoring",
                        "priority": "medium",
                        "client_id": client.id,
                        "client_name": client.nombre,
                        "title": "Monitorear riesgo de morosidad",
                        "description": f"Cliente con riesgo moderado ({risk_prob:.1%}) de morosidad",
                        "action": "Programar seguimiento semanal de pagos",
                        "impact_score": 6.0,
                        "category": "finanzas",
                        "suggested_by": "PA"
                    }
            else:
                # Fallback: analizar facturas vencidas directamente
                overdue_invoices = self._get_overdue_invoices(client.id)
                if overdue_invoices and len(overdue_invoices) > 0:
                    risk_recommendation = {
                        "type": "overdue_payments",
                        "priority": "medium",
                        "client_id": client.id,
                        "client_name": client.nombre,
                        "title": f"Facturas pendientes: {len(overdue_invoices)} vencidas",
                        "description": f"El cliente tiene {len(overdue_invoices)} factura(s) vencida(s) sin predicción de riesgo disponible",
                        "action": "Revisar estado de pagos inmediatamente",
                        "impact_score": 7.0,
                        "category": "finanzas",
                        "suggested_by": "PA"
                    }

            if risk_recommendation:
                recommendations.append(risk_recommendation)

            # Analizar probabilidad de conversión
            if conversion_predictions["success"] and conversion_predictions["predictions"] and len(conversion_predictions["predictions"]) > 0:
                conv_prob = conversion_predictions["predictions"][0]["predicted_value"]

                if conv_prob > 0.8 and client.estado_funnel.value != "Ganado":
                    recommendations.append({
                        "type": "conversion_acceleration",
                        "priority": "high",
                        "client_id": client.id,
                        "client_name": client.nombre,
                        "title": "Alta probabilidad de cierre",
                        "description": f"El cliente {client.nombre} tiene {conv_prob:.1%} de probabilidad de conversión",
                        "action": "Priorizar recursos de venta y acelerar proceso de cierre",
                        "impact_score": 8.5,
                        "category": "ventas",
                        "suggested_by": "PA"
                    })

                elif conv_prob < 0.3 and client.estado_funnel.value in ["Propuesta", "Negociación"]:
                    recommendations.append({
                        "type": "conversion_review",
                        "priority": "medium",
                        "client_id": client.id,
                        "client_name": client.nombre,
                        "title": "Revisar estrategia de venta",
                        "description": f"Baja probabilidad de conversión ({conv_prob:.1%}) en estado {client.estado_funnel.value}",
                        "action": "Evaluar cambio de enfoque o reasignación de vendedor",
                        "impact_score": 7.0,
                        "category": "ventas",
                        "suggested_by": "PA"
                    })

            # Analizar facturas vencidas
            overdue_invoices = self._get_overdue_invoices(client.id)
            if overdue_invoices:
                total_overdue = sum(inv["monto_pendiente"] for inv in overdue_invoices)

                recommendations.append({
                    "type": "payment_followup",
                    "priority": "high",
                    "client_id": client.id,
                    "client_name": client.nombre,
                    "title": f"Facturas vencidas: ${total_overdue:,.0f}",
                    "description": f"El cliente tiene {len(overdue_invoices)} factura(s) vencida(s) por un total de ${total_overdue:,.0f}",
                    "action": "Iniciar proceso de cobranza inmediata",
                    "impact_score": 9.5,
                    "category": "cobranza",
                    "suggested_by": "PA",
                    "details": overdue_invoices
                })

            # Analizar valor potencial vs actual
            if client.valor_estimado and client.valor_estimado > 1000000:  # Más de 1M
                recommendations.append({
                    "type": "high_value_client",
                    "priority": "medium",
                    "client_id": client.id,
                    "client_name": client.nombre,
                    "title": "Cliente de alto valor",
                    "description": f"Cliente con valor estimado de ${client.valor_estimado:,.0f}",
                    "action": "Asignar ejecutivo senior y beneficios preferenciales",
                    "impact_score": 7.5,
                    "category": "atención",
                    "suggested_by": "PA"
                })

        except Exception as e:
            logger.error(f"Error analizando cliente {client.id}: {str(e)}")

        return recommendations

    def _get_overdue_invoices(self, client_id: int) -> List[Dict]:
        """
        Obtiene facturas vencidas de un cliente
        """
        try:
            overdue_invoices = self.db.query(Factura).filter(
                Factura.cliente_id == client_id,
                Factura.estado.in_(["Vencida", "Parcial"]),
                Factura.fecha_vencimiento < datetime.now().date()
            ).all()

            result = []
            for invoice in overdue_invoices:
                days_overdue = (datetime.now().date() - invoice.fecha_vencimiento).days
                pendiente = invoice.monto_total - invoice.monto_pagado

                result.append({
                    "numero_factura": invoice.numero_factura,
                    "monto_total": invoice.monto_total,
                    "monto_pendiente": pendiente,
                    "dias_vencida": days_overdue,
                    "fecha_vencimiento": str(invoice.fecha_vencimiento)
                })

            return result

        except Exception as e:
            logger.error(f"Error obteniendo facturas vencidas: {str(e)}")
            return []

    def generate_sales_team_recommendations(self) -> Dict:
        """
        Genera recomendaciones para el equipo de ventas
        """
        try:
            recommendations = []

            # Analizar vendedores con bajo rendimiento
            sellers = self.db.query(Vendedor).filter(Vendedor.activo == 1).all()

            for seller in sellers:
                seller_recs = self._analyze_seller_performance(seller)
                recommendations.extend(seller_recs)

            # Recomendaciones generales del equipo
            team_recs = self._analyze_team_performance()
            recommendations.extend(team_recs)

            # Filtrar por rol
            filtered_recs = self._filter_recommendations_by_role(recommendations)

            # Ordenar por impacto
            filtered_recs.sort(key=lambda x: x.get('impact_score', 0), reverse=True)

            return {
                "success": True,
                "recommendations": filtered_recs,
                "total_generated": len(filtered_recs)
            }

        except Exception as e:
            logger.error(f"Error generando recomendaciones de ventas: {str(e)}")
            return {"success": False, "error": str(e)}

    def _analyze_seller_performance(self, seller: Vendedor) -> List[Dict]:
        """
        Analiza el rendimiento de un vendedor y genera recomendaciones
        """
        recommendations = []

        try:
            # Obtener actividades recientes (último mes)
            cutoff_date = datetime.now() - timedelta(days=30)
            recent_activities = self.db.query(ActividadVenta).filter(
                ActividadVenta.vendedor_id == seller.id,
                ActividadVenta.fecha >= cutoff_date
            ).all()

            # Calcular métricas
            total_activities = len(recent_activities)
            activities_with_value = len([a for a in recent_activities if a.monto_estimado and a.monto_estimado > 0])

            if total_activities < 5:
                recommendations.append({
                    "type": "activity_increase",
                    "priority": "high",
                    "seller_id": seller.id,
                    "seller_name": seller.nombre,
                    "title": "Baja actividad comercial",
                    "description": f"El vendedor {seller.nombre} ha realizado solo {total_activities} actividades en el último mes",
                    "action": "Aumentar frecuencia de contacto con clientes (meta: 15 actividades/mes)",
                    "impact_score": 8.0,
                    "category": "productividad",
                    "suggested_by": "PA"
                })

            # Analizar conversión de oportunidades
            seller_clients = self.db.query(Cliente).filter(Cliente.vendedor_id == seller.id).all()
            won_clients = len([c for c in seller_clients if c.estado_funnel.value == "Ganado"])
            total_opportunities = len(seller_clients)

            if total_opportunities > 0:
                conversion_rate = won_clients / total_opportunities

                if conversion_rate < 0.2:
                    recommendations.append({
                        "type": "conversion_improvement",
                        "priority": "high",
                        "seller_id": seller.id,
                        "seller_name": seller.nombre,
                        "title": "Baja tasa de conversión",
                        "description": f"Tasa de conversión: {conversion_rate:.1%} ({won_clients}/{total_opportunities} oportunidades)",
                        "action": "Capacitación en técnicas de cierre y calificación de prospectos",
                        "impact_score": 8.5,
                        "category": "habilidades",
                        "suggested_by": "PA"
                    })

        except Exception as e:
            logger.error(f"Error analizando vendedor {seller.id}: {str(e)}")

        return recommendations

    def _analyze_team_performance(self) -> List[Dict]:
        """
        Analiza el rendimiento general del equipo de ventas
        """
        recommendations = []

        try:
            # Análisis de ventas mensuales
            current_month = datetime.now().replace(day=1)
            monthly_sales = self.db.query(
                Factura.fecha_emision,
                Factura.monto_total
            ).filter(
                Factura.estado == "Pagada",
                Factura.fecha_emision >= current_month
            ).all()

            total_monthly_sales = sum(sale[1] for sale in monthly_sales)

            # Meta mensual estimada (suma de metas de vendedores activos)
            sellers = self.db.query(Vendedor).filter(Vendedor.activo == 1).all()
            total_team_target = sum(seller.meta_mensual for seller in sellers)

            if total_team_target > 0:
                achievement_rate = total_monthly_sales / total_team_target

                if achievement_rate < 0.7:
                    recommendations.append({
                        "type": "team_motivation",
                        "priority": "high",
                        "title": "Equipo por debajo de meta mensual",
                        "description": f"Logro actual: {achievement_rate:.1%} de la meta mensual (${total_monthly_sales:,.0f} de ${total_team_target:,.0f})",
                        "action": "Implementar programa de motivación y seguimiento diario de KPIs",
                        "impact_score": 9.0,
                        "category": "equipo",
                        "suggested_by": "PA"
                    })

            # Análisis de distribución de carga de trabajo
            client_distribution = {}
            for seller in sellers:
                client_count = self.db.query(Cliente).filter(Cliente.vendedor_id == seller.id).count()
                client_distribution[seller.nombre] = client_count

            if client_distribution:
                avg_clients = sum(client_distribution.values()) / len(client_distribution)
                overloaded_sellers = [name for name, count in client_distribution.items() if count > avg_clients * 1.5]

                if overloaded_sellers:
                    recommendations.append({
                        "type": "workload_balance",
                        "priority": "medium",
                        "title": "Rebalanceo de carga de trabajo",
                        "description": f"Vendedores sobrecargados: {', '.join(overloaded_sellers)}",
                        "action": "Redistribuir clientes entre vendedores para equilibrar carga",
                        "impact_score": 7.0,
                        "category": "operaciones",
                        "suggested_by": "PA"
                    })

        except Exception as e:
            logger.error(f"Error analizando rendimiento del equipo: {str(e)}")

        return recommendations

    def generate_finance_recommendations(self) -> Dict:
        """
        Genera recomendaciones para el área financiera
        """
        try:
            recommendations = []

            # Analizar flujo de caja
            cash_flow_recs = self._analyze_cash_flow()
            recommendations.extend(cash_flow_recs)

            # Analizar cuentas por cobrar
            receivables_recs = self._analyze_accounts_receivable()
            recommendations.extend(receivables_recs)

            # Filtrar por rol
            filtered_recs = self._filter_recommendations_by_role(recommendations)

            return {
                "success": True,
                "recommendations": filtered_recs,
                "total_generated": len(filtered_recs)
            }

        except Exception as e:
            logger.error(f"Error generando recomendaciones financieras: {str(e)}")
            return {"success": False, "error": str(e)}

    def _analyze_cash_flow(self) -> List[Dict]:
        """
        Analiza el flujo de caja y genera recomendaciones
        """
        recommendations = []

        try:
            # Obtener movimientos de caja de los últimos 30 días
            cutoff_date = datetime.now() - timedelta(days=30)
            movements = self.db.query(MovimientoCaja).filter(
                MovimientoCaja.fecha >= cutoff_date
            ).all()

            total_income = sum(m.monto for m in movements if m.tipo == "Ingreso")
            total_expenses = sum(m.monto for m in movements if m.tipo == "Egreso")

            net_flow = total_income - total_expenses

            if net_flow < 0:
                recommendations.append({
                    "type": "cash_flow_negative",
                    "priority": "critical",
                    "title": "Flujo de caja negativo",
                    "description": f"Flujo neto negativo de ${net_flow:,.0f} en los últimos 30 días",
                    "action": "Revisar gastos operativos y acelerar cobros pendientes",
                    "impact_score": 10.0,
                    "category": "finanzas",
                    "suggested_by": "PA"
                })

            # Analizar gastos por categoría
            expenses_by_category = {}
            for movement in movements:
                if movement.tipo == "Egreso":
                    category = movement.categoria or "Sin categorizar"
                    expenses_by_category[category] = expenses_by_category.get(category, 0) + movement.monto

            # Identificar categorías con gastos altos
            for category, amount in expenses_by_category.items():
                if amount > total_expenses * 0.3:  # Más del 30% del total
                    recommendations.append({
                        "type": "expense_optimization",
                        "priority": "medium",
                        "title": f"Gastos elevados en {category}",
                        "description": f"Categoría {category} representa ${amount:,.0f} ({amount/total_expenses:.1%} del total)",
                        "action": "Revisar y optimizar gastos en esta categoría",
                        "impact_score": 6.5,
                        "category": "costos",
                        "suggested_by": "PA"
                    })

        except Exception as e:
            logger.error(f"Error analizando flujo de caja: {str(e)}")

        return recommendations

    def _analyze_accounts_receivable(self) -> List[Dict]:
        """
        Analiza cuentas por cobrar y genera recomendaciones
        """
        recommendations = []

        try:
            # Obtener facturas pendientes
            pending_invoices = self.db.query(Factura).filter(
                Factura.estado.in_(["Pendiente", "Parcial"])
            ).all()

            total_pending = sum(inv.monto_total - inv.monto_pagado for inv in pending_invoices)

            # Facturas por antigüedad
            current = len([inv for inv in pending_invoices if (datetime.now().date() - inv.fecha_vencimiento).days <= 0])
            overdue_1_30 = len([inv for inv in pending_invoices if 0 < (datetime.now().date() - inv.fecha_vencimiento).days <= 30])
            overdue_31_60 = len([inv for inv in pending_invoices if 30 < (datetime.now().date() - inv.fecha_vencimiento).days <= 60])
            overdue_60_plus = len([inv for inv in pending_invoices if (datetime.now().date() - inv.fecha_vencimiento).days > 60])

            if overdue_60_plus > 0:
                recommendations.append({
                    "type": "aging_receivables",
                    "priority": "high",
                    "title": "Cuentas por cobrar antiguas",
                    "description": f"{overdue_60_plus} facturas con más de 60 días de vencimiento",
                    "action": "Iniciar proceso de cobranza intensiva y considerar provisiones",
                    "impact_score": 8.5,
                    "category": "cobranza",
                    "suggested_by": "PA"
                })

            # Análisis de concentración de riesgo
            client_debt = {}
            for invoice in pending_invoices:
                if invoice.cliente:
                    client_name = invoice.cliente.nombre
                    debt = invoice.monto_total - invoice.monto_pagado
                    client_debt[client_name] = client_debt.get(client_name, 0) + debt

            # Clientes con mayor deuda pendiente
            top_debtors = sorted(client_debt.items(), key=lambda x: x[1], reverse=True)[:3]

            if top_debtors and top_debtors[0][1] > total_pending * 0.2:  # Más del 20% del total
                recommendations.append({
                    "type": "concentration_risk",
                    "priority": "medium",
                    "title": "Concentración de riesgo en clientes",
                    "description": f"El cliente {top_debtors[0][0]} representa ${top_debtors[0][1]:,.0f} de deuda pendiente",
                    "action": "Diversificar cartera de clientes y monitorear concentración",
                    "impact_score": 7.0,
                    "category": "riesgo",
                    "suggested_by": "PA"
                })

        except Exception as e:
            logger.error(f"Error analizando cuentas por cobrar: {str(e)}")

        return recommendations

    def get_recommendations_summary(self, category: str = None, priority: str = None) -> Dict:
        """
        Obtiene un resumen de todas las recomendaciones activas
        """
        try:
            # En un sistema real, las recomendaciones se almacenarían en BD
            # Por ahora, generamos recomendaciones frescas

            all_recommendations = []

            # Generar recomendaciones de diferentes áreas
            client_recs = self.generate_client_recommendations(limit=20)
            if client_recs["success"]:
                all_recommendations.extend(client_recs["recommendations"])

            sales_recs = self.generate_sales_team_recommendations()
            if sales_recs["success"]:
                all_recommendations.extend(sales_recs["recommendations"])

            finance_recs = self.generate_finance_recommendations()
            if finance_recs["success"]:
                all_recommendations.extend(finance_recs["recommendations"])

            # Filtrar por categoría y prioridad
            if category:
                all_recommendations = [r for r in all_recommendations if r.get("category") == category]

            if priority:
                all_recommendations = [r for r in all_recommendations if r.get("priority") == priority]

            # Agrupar por tipo
            by_type = {}
            by_priority = {"high": 0, "medium": 0, "low": 0, "critical": 0}

            for rec in all_recommendations:
                rec_type = rec.get("type", "unknown")
                by_type[rec_type] = by_type.get(rec_type, 0) + 1

                priority_level = rec.get("priority", "medium")
                by_priority[priority_level] += 1

            return {
                "success": True,
                "total_recommendations": len(all_recommendations),
                "by_type": by_type,
                "by_priority": by_priority,
                "top_recommendations": all_recommendations[:10]
            }

        except Exception as e:
            logger.error(f"Error obteniendo resumen de recomendaciones: {str(e)}")
            return {"success": False, "error": str(e)}

    def close(self):
        """Cierra las conexiones"""
        self.db.close()
        self.pme.close()
