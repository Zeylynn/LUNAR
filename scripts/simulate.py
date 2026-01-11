import os
import python_sim.simulation as sim
from python_sim.config_loader import load_config
import pickle
import python_sim.logger_setup as log
import neat

logger = log.get_logger(__name__)
app_config = load_config()

def simulate():
    neat_conf_file = "../config/neat-config"
    genome_file = "../genomes/genome.pkl"
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    neat_conf_file = os.path.join(base_dir, neat_conf_file)
    genome_file = os.path.join(base_dir, genome_file)

    neat_config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        neat_conf_file
    )

    with open(genome_file, 'rb') as f:
        winner = pickle.load(f)
        logger.info(f"Loaded winner genome from {genome_file}")

        winner_nn = neat.nn.FeedForwardNetwork.create(winner, neat_config)

    app = sim.Simulation(config=app_config, nn=winner_nn)
    app.run()

"""
wird benötigt weil Windows neue Prozesse/Multiprocessing via Spawn erstellt.
Spawn importiert beim ERSTELLEN des neuen Prozesses alle Module und führt danach das Hauptskript aus.
d.h. dass alles ohne if __name__ == "__main__" doppelt ausgeführt wird. Dadurch wird der pool von Parallel Evaluator fehlerhaft gesetzt => Error
"""
if __name__ == "__main__":
    simulate()