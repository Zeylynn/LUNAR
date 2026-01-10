import neat
from python_sim.environment import Environment
import python_sim.logger_setup as log
import multiprocessing
import pickle
from functools import partial

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

    net = neat.nn.FeedForwardNetwork.create(genome, config)             #TODO Später maybe ein RNN statt FFW für Memory

    org = env.add_organisms(1)[0]       # Output: [Organism]
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
        inputs = env.get_inputs(org)
        outputs = net.activate(inputs)
        org.update(outputs)
        env.update()

        # Wenn Org ist tot => abbrechen
        if org.energy <= 0:
            fitness -= 50
            break

        # 1. Überleben
        fitness += 0.1

        # 2. Ressourcen
        fitness += org.energy / org.max_energy
        fitness += org.food / org.max_food
        fitness += org.water / org.max_water

        #3. Essen/Trinken belohnen
        if org.ate_this_tick:
            fitness += 4.0
        if org.drank_this_tick:
            fitness += 2.0

        # 4. Ressourcen in Sicht belohnen
        seen = org.seen_objects()
        if seen["food"]:
            dist_food, _ = org.get_closest(seen["food"])
            fitness += (org.vision_range - dist_food) / org.vision_range
        if seen["water"]:
            dist_water, _ = org.get_closest(seen["water"])
            fitness += (org.vision_range - dist_water) / org.vision_range
        
    genome.fitness = fitness    # Die eigentliche Fitness
    return fitness              # Optional, setzt interne ParallelEvaluator Werte

def run_neat(neat_config_path, app_config):
    NUM_GENS = app_config["neat"]["num_gens"]       # max. Anzahl an Generationen, wenn nicht vorher via. fitness_threshold terminiert
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
    master_config = app_config["master_env"]
    master_env = Environment(width=master_config["width"],
                             height=master_config["height"],
                             num_organisms=0,
                             num_bushes=master_config["num_bushes"],
                             seed=master_config["seed"])
    logger.info("Master environment generated")
    pickled_master_env = pickle.dumps(master_env)   # Speichert im RAM, dazu da dass jeder Prozess eine Kopie anstatt einen Verweis bekommt

    eval_func = partial(eval_genome, sim_ticks=app_config["neat"]["sim_ticks"], pickled_master_env=pickled_master_env)

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
    winner_nn = neat.nn.FeedForwardNetwork.create(winner, neat_config)

    logger.info(f"NEAT evolution completed. Winner genome ID: {winner}")
    logger.info(f"Winner Fitness: {winner.fitness:.4f}")
    logger.info(f"Total Generations: {len(stats.most_fit_genomes)}")

    # Log per-generation best fitness (if available)
    for gen_idx, g in enumerate(stats.most_fit_genomes):
        fit = getattr(g, "fitness", None)
        logger.info(f"Gen {gen_idx}: best_fitness={fit}")

    # Save winner genome to file for later reuse
    """
    #FIXME das beste NN speichern => pickle, das winner obj speichern und dann das NN für die Outputs usen, VERIFIEN
    out_path = "winner_genome.pkl"
    with open(out_path, "wb") as f:
        pickle.dump(winner, f)
    logger.info(f"Saved winner genome to {out_path}")
    """

    return winner, winner_nn