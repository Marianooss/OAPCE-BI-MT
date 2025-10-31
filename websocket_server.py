"""
WebSocket Server - Comunicación en tiempo real para agentes
Cumple con Agents.md: "Detección en tiempo real mediante WebSockets"
"""

import asyncio
import json
import redis
import logging
from datetime import datetime
from typing import Dict, Set, List
import websockets
from websockets.exceptions import ConnectionClosedError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentWebSocketServer:
    """
    Servidor WebSocket para comunicación en tiempo real entre agentes y UI
    Cumple con especificaciones de Agents.md para AD y notificaciones realtime
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
        self.connected_clients: Dict[str, Set[websockets.WebSocketServerProtocol]] = {
            'ui_clients': set(),  # Dashboards y UI
            'agent_clients': set()  # Agentes que envían notificaciones
        }
        self.server = None
        self.redis_pubsub = None

    async def start_server(self):
        """Inicia el servidor WebSocket y Redis pubsub"""
        try:
            # Iniciar servidor WebSocket
            self.server = await websockets.serve(
                self.handle_connection,
                self.host,
                self.port,
                ping_interval=30,
                ping_timeout=10
            )

            logger.info(f"🚀 WebSocket Server iniciado en ws://{self.host}:{self.port}")

            # Iniciar listener de Redis en segundo plano
            asyncio.create_task(self.redis_listener())

            # Mantener servidor activo
            await self.server.wait_closed()

        except Exception as e:
            logger.error(f"Error iniciando WebSocket server: {e}")
            raise

    async def handle_connection(self, websocket, path):
        """
        Maneja nuevas conexiones WebSocket
        """
        try:
            # Identificar tipo de cliente (primer mensaje)
            client_type = await asyncio.wait_for(websocket.recv(), timeout=10.0)

            try:
                client_info = json.loads(client_type)
                ws_type = client_info.get('type', 'ui_clients')
            except (json.JSONDecodeError, KeyError):
                ws_type = 'ui_clients'  # Default

            # Agregar a grupo correspondiente
            if ws_type in self.connected_clients:
                self.connected_clients[ws_type].add(websocket)
                logger.info(f"Cliente {ws_type} conectado. Total {ws_type}: {len(self.connected_clients[ws_type])}")

            try:
                # Mantener conexión activa
                async for message in websocket:
                    await self.handle_message(websocket, message)

            except ConnectionClosedError:
                pass
            finally:
                # Limpiar conexión cerrada
                for client_group in self.connected_clients.values():
                    client_group.discard(websocket)
                logger.info(f"Cliente {ws_type} desconectado")

        except asyncio.TimeoutError:
            logger.warning("Timeout esperando identificación de cliente")
            await websocket.close(1008, "Timeout esperando identificación")

    async def handle_message(self, websocket, message):
        """
        Procesa mensajes entrantes del cliente WebSocket
        """
        try:
            data = json.loads(message)
            message_type = data.get('type')

            if message_type == 'subscribe':
                # Cliente se suscribe a canales específicos
                channels = data.get('channels', [])
                # Futuro: Lógica para gestionar suscripciones específicas

            elif message_type == 'ping':
                # Responder a pings para mantener conexión viva
                await websocket.send(json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))

        except json.JSONDecodeError:
            logger.warning("Mensaje JSON inválido recibido")

    async def redis_listener(self):
        """
        Escucha mensajes de Redis para retransmitir vía WebSocket
        Cumple con Agents.md: detección realtime mediante WebSockets
        """
        try:
            self.redis_pubsub = self.redis_client.pubsub()
            channels = [
                'dpo_update',
                'pme_retraining_complete',
                'critical_anomalies_detected',
                'data_quality_alert',
                'new_recommendations_available'
            ]

            await self.redis_pubsub.subscribe(*channels)
            logger.info("📡 Redis listener suscrito a canales de agentes")

            while True:
                try:
                    # Esperar mensaje de Redis
                    message = await self.redis_pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

                    if message:
                        channel = message['channel']
                        data = json.loads(message['data'])

                        # Retransmitir a clientes WebSocket
                        await self.broadcast_to_ui(channel, data)

                except Exception as e:
                    logger.error(f"Error procesando mensaje Redis: {e}")
                    await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error en Redis listener: {e}")

    async def broadcast_to_ui(self, channel: str, data: Dict):
        """
        Retransmite mensajes de agentes a clientes UI en tiempo real
        """
        if not self.connected_clients['ui_clients']:
            return

        message = {
            'type': 'agent_notification',
            'channel': channel,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }

        # Filtrar clientes desconectados
        disconnected = set()

        for websocket in self.connected_clients['ui_clients']:
            try:
                await websocket.send(json.dumps(message))
            except ConnectionClosedError:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error enviando a cliente UI: {e}")
                disconnected.add(websocket)

        # Limpiar conexiones rotas
        self.connected_clients['ui_clients'] -= disconnected

        if disconnected:
            logger.info(f"Removidos {len(disconnected)} clientes UI desconectados")

    async def shutdown(self):
        """Cierra el servidor WebSocket correctamente"""
        logger.info("🛑 Cerrando WebSocket Server...")

        if self.server:
            self.server.close()
            await self.server.wait_closed()

        if self.redis_pubsub:
            await self.redis_pubsub.unsubscribe()
            self.redis_pubsub.close()

    def send_realtime_notification(self, channel: str, message: Dict):
        """
        API sincrónica para enviar notificaciones desde agentes
        """
        try:
            notification = {
                'channel': channel,
                'timestamp': datetime.now().isoformat(),
                'data': message
            }

            # Publicar en Redis (que será capturado por redis_listener)
            self.redis_client.publish(channel, json.dumps(notification))

            logger.info(f"📤 Notificación realtime enviada: {channel}")

        except Exception as e:
            logger.error(f"Error enviando notificación realtime: {e}")

    def get_connection_stats(self) -> Dict:
        """Retorna estadísticas de conexiones activas"""
        return {
            'ui_clients_connected': len(self.connected_clients.get('ui_clients', set())),
            'agent_clients_connected': len(self.connected_clients.get('agent_clients', set())),
            'total_connections': sum(len(clients) for clients in self.connected_clients.values()),
            'server_running': self.server is not None,
            'redis_connected': self.redis_client.ping() if self.redis_client else False
        }


# Instancia global del servidor
websocket_server = AgentWebSocketServer()


async def main():
    """Función principal para ejecutar el servidor"""
    logger.info("🐍 Iniciando WebSocket Server para agentes OAPCE...")

    # Verificar conexión Redis antes de iniciar
    try:
        websocket_server.redis_client.ping()
        logger.info("✅ Redis disponible para comunicación realtime")
    except:
        logger.warning("⚠️  Redis no disponible - notificaciones realtime limitadas")

    try:
        await websocket_server.start_server()
    except KeyboardInterrupt:
        await websocket_server.shutdown()
    except Exception as e:
        logger.error(f"Fatal error en WebSocket server: {e}")
        await websocket_server.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
