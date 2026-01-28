import os
import python_sim.neat_runner as neat_run
import python_sim.simulation as sim
from python_sim.config_loader import load_config
import asyncio
import multiprocessing as mp

#TODO eigene TODO liste mit Folder oder so
#TODO die World Gen Parameter in die config packen
#TODO die Organism/Bush Max Werte in die config packen
#TODO wenn ich das Readme schreibe, erwähnen dass wir die MIT Lizenz haben
#TODO maybe solche Icons wie im neat-python GitHub Readme

app_config = load_config()

async def main():
    # Priority
    mp.set_start_method('spawn')
    loop = asyncio.get_running_loop()
    
    # Paths
    neat_conf_file = "../config/neat-config"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    neat_conf_file = os.path.join(base_dir, neat_conf_file)

    # Process
    neat_con_proc = mp.Process(target=neat_run.run_neat, args=(neat_conf_file, app_config), name="NEATController")
    num_cores = mp.cpu_count()
    event = mp.Event()
    con1, con2 = mp.Pipe()
    job_queue = mp.Queue()
    result_queue = mp.Queue()

    # Simulation
    neat_con_proc.start()
    app = sim.Simulation(config=app_config, nn=winner_nn)   # Nur das winner_nn ist noch ein Problem
    await app.run()

"""
wird benötigt weil Windows neue Prozesse/Multiprocessing via Spawn erstellt.
Spawn importiert beim ERSTELLEN des neuen Prozesses alle Module und führt danach das Hauptskript aus.
d.h. dass alles ohne if __name__ == "__main__" doppelt ausgeführt wird. Dadurch wird der pool von Parallel Evaluator fehlerhaft gesetzt => Error
"""
if __name__ == "__main__":
    asyncio.run(main())