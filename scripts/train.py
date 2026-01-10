import os
import python_sim.neat_runner as neat_run
import python_sim.simulation as sim

#FIXME train soll nur trainieren(inkl. abspeichern) und simulate soll nur simulieren

"""
wird benötigt weil Windows neue Prozesse/Multiprocessing via Spawn erstellt.
Spawn importiert beim ERSTELLEN des neuen Prozesses alle Module und führt danach das Hauptskript aus.
d.h. dass alles ohne if __name__ == "__main__" doppelt ausgeführt wird. Dadurch wird der pool von Parallel Evaluator fehlerhaft gesetzt => Error
"""
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config")

    winner_genome, winner_nn = neat_run.run_neat(config_path=config_path)

    app = sim(width=30, height=30, num_bushes=200, nn=winner_nn)
    app.run()