import socket
import logger_setup as log

#NOTE für max. throughput normale Sockets besser, allerdings benutzen die Byte-Streams, kein JSON
#NOTE das File nicht Socket nennen, weil es sonst gleich heißt wie das Python-Modul => Fehler

logger = log.get_logger(__name__)

class ServerHandler:
    def __init__(self, host="127.0.0.1", port=9001):
        """
        host: IP-Adresse (localhost)
        port: 9001 = freier Port vom OS
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_addr = None

    def create_socket(self):
        """Erstellt ein TCP-Server-Socket"""
        self.server_socket = socket.socket(
            socket.AF_INET,             # IPv4
            socket.SOCK_STREAM)         # TCP-Socket
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)    # max. 1 Client

        logger.info(f"Server listening on {self.host}:{self.port}")
        print(f"Server listening on {self.host}:{self.port}")

    def wait_for_client(self):
        """Warte auf Client-Verbindung"""
        print("Waiting for client...")
        self.client_socket, self.client_addr = self.server_socket.accept()

        logger.info(f"Client connected: {self.client_addr}")
        print(f"Client connected: {self.client_addr}")

    def send_json(self, data):
        """Sendet ein JSON-Objekt an den Client"""
        self.client_socket.sendall(data.encode("utf-8"))

    def close(self):
        """Schließt Socket(s)"""
        #TODO Das in die SIM-Schließfunktion einbauen
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        logger.info("Python-Server closed.")
        print("Python-Server closed.")