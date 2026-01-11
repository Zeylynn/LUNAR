import os
import python_sim.neat_runner as neat_run
import python_sim.simulation as sim
from python_sim.config_loader import load_config

#TODO eigene TODO liste mit Folder oder so
#TODO die World Gen Parameter in die config packen
#TODO die Organism/Bush Max Werte in die config packen

app_config = load_config()

def main():
    neat_conf_file = "../config/neat-config"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    neat_conf_file = os.path.join(base_dir, neat_conf_file)

    winner_genome, winner_nn = neat_run.run_neat(neat_config_path=neat_conf_file,
                                                 app_config=app_config)

    app = sim.Simulation(config=app_config, nn=winner_nn)
    app.run()

"""
wird benötigt weil Windows neue Prozesse/Multiprocessing via Spawn erstellt.
Spawn importiert beim ERSTELLEN des neuen Prozesses alle Module und führt danach das Hauptskript aus.
d.h. dass alles ohne if __name__ == "__main__" doppelt ausgeführt wird. Dadurch wird der pool von Parallel Evaluator fehlerhaft gesetzt => Error
"""
if __name__ == "__main__":
    main()