#NOTE temporärer Vibecodeder Dummy Client
import socket
import json
from python_sim.config_loader import load_config

server_config = load_config()["server"]

HOST = server_config["host"]
PORT = server_config["port"]

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to server {HOST}:{PORT}...")
        s.connect((HOST, PORT))
        print("Connected!")

        try:
            while True:
                data = s.recv(4096)  # Puffergröße 4KB
                if not data:
                    print("Server closed connection")
                    break

                # Daten als UTF-8 dekodieren
                text = data.decode("utf-8").strip()

                # Optional: Wenn mehrere JSONs in einem Stream, splitten
                lines = text.splitlines()
                for line in lines:
                    try:
                        obj = json.loads(line)
                        print("Received JSON:", obj)
                    except json.JSONDecodeError:
                        print("Received non-JSON data:", line)

        except KeyboardInterrupt:
            print("Client interrupted, closing...")

if __name__ == "__main__":
    main()
