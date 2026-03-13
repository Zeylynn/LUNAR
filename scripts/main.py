import os
import asyncio
import time
import json
import multiprocessing as mp
from python_sim.config_manager import load_config, merge_configs
from python_sim.neat_simulation import NEATSim
from python_sim.server_handler import ServerHandler
import python_sim.logger_setup as log
from python_sim.state_builder import StateBuilder

#BUG schauen welche Graphen wir alle machen weil Clemens faul ist
#BUG Spezies inklv. Einfärbung => nach welchen Kategorien färbe ich ein
#TODO eigene ToDo liste mit Folder oder so
#TODO die World Gen Parameter in die config packen
#TODO die Organism/Bush Max Werte in die config packen, wenns Sinn macht
#TODO wenn ich das Readme schreibe, erwähnen dass wir die MIT Lizenz haben
#TODO maybe solche Icons wie im neat-python GitHub Readme
#TODO beim anklicken NN mit JSON Export machen
#TODO auf Race Conditions checken
#TODO ich habe jetzt halt keine std.out reporter mehr...
#NOTE ich könnte noch cleaner beenden mit shutdown_event = asyncio.Event()
"""
population.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
population.add_reporter(stats)
"""

logger = log.get_logger(__name__)

# Evaluator Prozess
def evaluator_process(command_queue, snapshot_queue, config):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    neat_conf_file = os.path.join(base_dir, "../config/neat-config")

    rt_sim = NEATSim(
        neat_config_path=neat_conf_file,
        app_config=config,
    )

    running = True                      # Solange der Prozess läuft
    started = False                     # Sim startet erst nach GoDot start Command
    tick_rate = rt_sim.tick_rate        # FPS / TPS
    tick_duration = 1.0 / tick_rate

    logger.info("rt-neat-simulation Process started, waiting for 'start' command...")

    while running:
        start_time = time.time()
        while not command_queue.empty():
            cmd = command_queue.get()

            if cmd["cmd"] == "quit":
                running = False
                logger.info("Received quit command. Exiting rt-neat-simulation.")
                break

            elif cmd["cmd"] == "get_terrain":
                builder = StateBuilder()
                builder.build_terrain(rt_sim.env.terrain)
                snapshot_queue.put(builder.terrain)
                logger.info("Terrain snapshot requested and put into snapshot_queue")

            elif cmd["cmd"] == "start":
                started = True
                rt_sim.paused = False
                logger.info("Received 'start' command. Simulation begins.")

                #snapshot_queue.put({"type": "ready_ack"}) Optional idk ob nötig, so wie ich Froggy kenne eher ned

            elif cmd["cmd"] == "pause":
                rt_sim.paused = True
                logger.info("Simulation paused")

            elif cmd["cmd"] == "resume":
                rt_sim.paused = False
                logger.info("Simulation resumed")

            elif cmd["cmd"] == "set_tick_rate":
                rt_sim.tick_rate = cmd["tick_rate"]
                tick_duration = 1.0 / rt_sim.tick_rate
                logger.info(f"Simulation tick_rate set to {rt_sim.tick_rate} | tick_duration={tick_duration:.4f}s")

        if started and not rt_sim.paused:
            rt_sim.step_simulation()

            if rt_sim.should_send_snapshot():
                snapshot = rt_sim.build_snapshot()
                snapshot_queue.put(snapshot)

        elapsed = time.time() - start_time
        sleep_time = max(0.0, tick_duration - elapsed)

        if started and not rt_sim.paused:
            actual_fps = 1.0 / elapsed
            logger.debug(f"Tick {rt_sim.tick - 1} finished | duration={elapsed:.4f}s | effective FPS={actual_fps:.2f}")

        if sleep_time > 0.0:
            time.sleep(sleep_time)      #NOTE time.sleep() nicht ganz optimal, im Rahmen dieses Projektes ausreichend
        else:
            logger.warning(f"Tick {rt_sim.tick - 1} took longer ({elapsed:.4f}s) than expected tick duration ({tick_duration:.4f}s)")

    snapshot_queue.put({"type": "shutdown_ack"})
    logger.info("rt-neat-simulation terminated")

# Asyncio Main Process - Event Loop
async def main():
    mp.set_start_method("spawn")
    loop = asyncio.get_running_loop()

    base_config = load_config()
    command_queue = mp.Queue()
    snapshot_queue = mp.Queue()

    server = ServerHandler(base_config["server"])
    server.create_socket()
    await server.wait_for_client()      #NOTE Falls Error, maybe delay dazwischen

    logger.info("Client connected")

    # Erster Handshake - recv config
    data = await server.recv_json()
    cmd = json.loads(data)

    if cmd["cmd"] != "config":
        raise RuntimeError("First command must be 'config'")
    
    client_config = cmd["data"]
    config = merge_configs(base_config, client_config)
    logger.info(f"Merged Simulation config: {config}")

    evaluator = mp.Process(
        target=evaluator_process,
        args=(command_queue, snapshot_queue, config),
        name="rt-neat-simulation"
    )
    evaluator.start()

    # Zweiter Handshake - send terrain
    command_queue.put({"cmd": "get_terrain"})

    # SENDEN
    async def send_snapshots():
        first_snapshot = await loop.run_in_executor(None, snapshot_queue.get)
        if first_snapshot["type"] == "terrain":
            await server.send_json(first_snapshot)
            logger.info("Terrain snapshot sent")

        while True:
            snapshot = await loop.run_in_executor(None, snapshot_queue.get) # None = ThreadPoolExecutor
            await server.send_json(snapshot)

            if snapshot["type"] == "shutdown_ack":
                logger.info("Received shutdown_ack. Exiting send_snapshots()")
                break

            logger.debug(f"Snapshot sent | Tick {snapshot['metadata']['tick'] - 1}")

    # EMPFANGEN
    async def receive_commands():
        while True:
            data = await server.recv_json()

            # Falls Disconnect
            if data == "DISCONNECT":
                command_queue.put({"cmd": "quit"})
                logger.warning("Client Disconnected, starting 'quit' sequence, Exiting receive_commands()")
                break

            # Falls leere Nachricht
            if not data:
                continue

            cmd = json.loads(data)
            logger.info(f"Received from Client: {cmd}")
            command_queue.put(cmd)

            if cmd.get("cmd") == "quit":
                logger.info("Received quit command. Exiting receive_commands()")
                break

    # Beide Tasks parallel laufen lassen im Event Loop
    await asyncio.gather(
        send_snapshots(),
        receive_commands()
    )

    # Clean schließen
    evaluator.join()
    server.close()

"""
wird benötigt weil Windows neue Prozesse/Multiprocessing via Spawn erstellt.
Spawn importiert beim ERSTELLEN des neuen Prozesses alle Module und führt danach das Hauptskript aus.
d.h. dass alles ohne if __name__ == "__main__" doppelt ausgeführt wird. Dadurch wird der pool von Parallel Evaluator fehlerhaft gesetzt => Error
"""
if __name__ == "__main__":
    asyncio.run(main())
    logger.info("Program Terminated!")

"""
cmd queue:
- {"cmd":"config, "data": {"seed": 42, ...}}\n
- {"cmd":"start"}\n
- {"cmd":"pause"}\n
- {"cmd":"resume"}\n
- {"cmd":"set_tick_rate", "tick_rate":40}\n
- {"cmd":"quit"}\n

snapshot queue:
- {"type":"ready_ack"}\n
- {"type":"terrain", ...}\n
- {"type":"state", ...}\n
- {"type":"quit_ack"}\n
"""