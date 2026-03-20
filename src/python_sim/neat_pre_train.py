import neat
from python_sim.environment import Environment
import python_sim.logger_setup as log
import multiprocessing
import pickle
from functools import partial
import random

#TODO später JSON LOGS damit ich die Graphen zeichnen kann, pro Gen die Fitness Werte
#TODO Multi Agent NEAT, mehrere Genomes in einem Environment
#TODO maybe wegen Threaded Evaluation schauen, multiprocessing.shared_memory z.B.
#NOTE man kann die Loops abbrechen wenn ein NN mit hoch genuger Fitness gefunden ist
#NOTE die alten Environments löschen wenn es vom Speicher her Problematisch wird => Python hat aber eh Garbage Collection

logger = log.get_logger(__name__)

def eval_genome(genome, config, sim_ticks, pickled_master_env):
    """
    Bewertet ein einzelnes Genom in einer eigenen Kopie des Master-Environments.
    """
    env = pickle.loads(pickled_master_env)      # Lädt vom RAM

    net = neat.nn.RecurrentNetwork.create(genome, config)

    env.add_organisms(1)
    org = env.organisms[0]

    org.net = net
    org.genome = genome

    genome.fitness = 0
    fitness = genome.fitness
    """
    #NOTE Später bei RT-NEAT wird das ganz dann kontinuierlich anstatt von Gen zu Gen
    Für jedes Genom/NN wird eine mini-Simulation simuliert um die Fitness UNABHÄNGIG von den anderen Organismen zu ermitteln
    NEAT erstelle dann anhand der Basis von den Fitness Werten neue Generationen
    """
    for _ in range(sim_ticks):
        env.update()

        inputs = org.get_inputs()
        outputs = org.net.activate(inputs)
        reward = org.apply_nn_output(outputs)

        # Wenn Org ist tot => abbrechen
        if org.energy <= 0:
            fitness -= 20
            break

        fitness += reward

    genome.fitness = fitness    # Die eigentliche Fitness
    return fitness              # Optional, setzt interne ParallelEvaluator Werte

def run_neat(neat_config_path, app_config):
    NUM_GENS = app_config["neat"]["pre_train"]["num_gens"]       # max. Anzahl an Generationen, wenn nicht vorher via. fitness_threshold terminiert
    logger.info("Starting NEAT run")

    neat_config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        neat_config_path
    )

    logger.info(
        f"NEAT Config loaded: pop_size={neat_config.pop_size}, "
        f"inputs={neat_config.genome_config.num_inputs}, "
        f"outputs={neat_config.genome_config.num_outputs}"
    )

    population = neat.Population(neat_config)

    # Gibt Konsolenoutput um Fortschritt zu sehen
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    #TODO jetzt ist immer dasselbe Environment für alle 100Gens, das sollt ned sein
    master_config = app_config["simulation"]
    master_env = Environment(width=master_config["width"],
                             height=master_config["height"],
                             num_bushes=master_config["num_bushes"],
                             seed=master_config["seed"],
                             org_config=app_config["organism"])
    logger.info("Master environment generated")
    pickled_master_env = pickle.dumps(master_env)   # Speichert im RAM, dazu da dass jeder Prozess eine Kopie anstatt einen Verweis bekommt

    eval_func = partial(eval_genome, sim_ticks=app_config["neat"]["pre_train"]["gen_ticks"], pickled_master_env=pickled_master_env)

    """
    Use CPU count + 1 workers
    => worker != Kern, ein Worker ist ein Prozess der eine Aufgabe ausführt.
    Dieser Worker wird dann vom Scheduler Kernen zugeteilt.
    + 1 damit während Idle Times der Scheduler sofort den nächsten Worker zuteilen kann
    """
    num_workers = 1 + multiprocessing.cpu_count()
    logger.info(f"Starting ParallelEvaluator with {num_workers} workers")
    pe = neat.ParallelEvaluator(
        num_workers=num_workers,
        eval_function=eval_func
    )

    logger.info(f"Starting evolution loop (max {NUM_GENS} generations).")
    winner = population.run(pe.evaluate, n=NUM_GENS)

    # VIBECODE start
    # Top + Random mischen
    all_genomes = list(population.population.values())

    # sortieren nach fitness
    all_genomes.sort(key=lambda g: g.fitness, reverse=True)

    top_k = int(len(all_genomes) * 0.7)
    top_genomes = all_genomes[:top_k]
    random_genomes = random.sample(all_genomes[top_k:], len(all_genomes) - top_k)

    final_genomes = top_genomes + random_genomes

    for g in final_genomes:
        g.fitness = 0.0
    # VIBECODE END

    winner_nn = neat.nn.FeedForwardNetwork.create(winner, neat_config)

    logger.info(f"NEAT evolution completed. Winner genome ID: {winner}")
    logger.info(f"Winner Fitness: {winner.fitness:.4f}")
    logger.info(f"Total Generations: {len(stats.most_fit_genomes)}")

    # Log per-generation best fitness (if available)
    for gen_idx, g in enumerate(stats.most_fit_genomes):
        fit = getattr(g, "fitness", None)
        logger.info(f"Gen {gen_idx}: best_fitness={fit}")

    return winner, winner_nn, population