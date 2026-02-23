import socket
import python_sim.logger_setup as log
import asyncio
import json

#NOTE maybe das in normal asyncio usmchreiben, ohne Workaround
#NOTE für max. throughput normale Sockets besser, allerdings benutzen die Byte-Streams, kein JSON
#NOTE das File nicht Socket nennen, weil es sonst gleich heißt wie das Python-Modul => Fehler
#NOTE für max. Performance msgpack benutzen

logger = log.get_logger(__name__)

class ServerHandler:
    def __init__(self, config):
        """
        host: IP-Adresse (localhost)
        port: 9001 = freier Port vom OS
        """
        self.host = config["host"]
        self.port = config["port"]
        self.server_socket = None
        self.client_socket = None
        self.client_addr = None
        self._recv_buffer = ""

    def create_socket(self):
        """Erstellt ein TCP-Server-Socket"""
        self.server_socket = socket.socket(
            socket.AF_INET,             # IPv4
            socket.SOCK_STREAM)         # TCP-Socket
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)    # max. 1 Client
        self.server_socket.setblocking(False)

        logger.info(f"Server listening on {self.host}:{self.port}")
        print(f"Server listening on {self.host}:{self.port}")

    async def wait_for_client(self):
        """Warte auf Client-Verbindung"""
        loop = asyncio.get_running_loop()
        print("Waiting for client...")             # Workaround, weil .accept() blocking ist
        self.client_socket, self.client_addr = await loop.sock_accept(self.server_socket)
        self.client_socket.setblocking(False)

        logger.info(f"Client connected: {self.client_addr}")
        print(f"Client connected: {self.client_addr}")

    async def send_json(self, data):
        """Sendet ein JSON-Objekt an den Client"""
        loop = asyncio.get_running_loop()

        msg = json.dumps(data) + "\n"   #NOTE da ist der ausgemacht Delimiter
        await loop.sock_sendall(self.client_socket, msg.encode("utf-8"))

    async def recv_json(self, buffer_size=1024):
        """Empfängt ein JSON-Objekt vom Client"""
        loop = asyncio.get_running_loop()
        try:
            data = await loop.sock_recv(self.client_socket, (buffer_size))    # 1024 Bytes maximalgröße pro Nachricht
            if not data:
                return None
        
            self._recv_buffer += data.decode("utf-8")       #FIXME das noch fertig machen

            if "\n" in self._recv_buffer:
                line, self._recv_buffer = self._recv_buffer.split("\n", 1)    # er splittet nur 1x, von links nach rechts
                return line  # noch kein json.loads hier

            return None  # noch keine vollständige Nachricht

            return data.decode("utf-8")
        except:
            logger.error(f"Fehler beim Empfangen vom Client")
            return None

    def close(self):
        """Schließt Socket(s)"""
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        logger.info("Python-Server closed.")
        print("Python-Server closed.")