import socket
import json
import time
import threading
from python_sim.config_manager import load_config

server_config = load_config()["server"]

HOST = server_config["host"]
PORT = server_config["port"]

COMMAND_SEQUENCE = [
    {"cmd": "config", "data": None},
    {"cmd": "start"},
    #{"cmd": "set_tick_rate", "tick_rate": 1},
    #{"cmd": "pause"},
    #{"cmd": "resume"},
    #{"cmd": "set_tick_rate", "tick_rate": 10},
    {"cmd": "quit"}
]

def sender(sock):
    index = 0
    time.sleep(2)   # 2s Startup für Terrain load

    while True:
        cmd = COMMAND_SEQUENCE[index]
        message = json.dumps(cmd) + "\n"

        try:
            sock.sendall(message.encode("utf-8"))
            print("Sent:", cmd)
        except Exception as e:
            print("Send error:", e)
            break

        if cmd["cmd"] == "quit":
            print("Sent quit command. Sender exiting.")
            break

        index = (index + 1) % len(COMMAND_SEQUENCE)
        time.sleep(10)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to server {HOST}:{PORT}...")
        s.connect((HOST, PORT))
        print("Connected!")

        # Sender-Thread starten
        send_thread = threading.Thread(target=sender, args=(s,), daemon=True)
        send_thread.start()

        buffer = ""

        try:
            while True:
                data = s.recv(4096)
                if not data:
                    print("Server closed connection")
                    break

                buffer += data.decode("utf-8")      #NOTE der Empfänger darf auf keinen Fall .strip() machen

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)

                    try:
                        obj = json.loads(line)
                        print("Received JSON:", obj)
                    except json.JSONDecodeError:
                        print("Invalid JSON:", line)

        except KeyboardInterrupt:
            print("Client interrupted, closing...")

        finally:
            print("Client shutting down.")


if __name__ == "__main__":
    main()