import neat
import python_sim.logger_setup as log
from python_sim.environment import Environment
from python_sim.state_builder import StateBuilder
import random

#FIXME Fortplanzen nochmal anschauen, maybe consent
#FIXME schauen wegen Live NN verbesserung
#FIXME fortplanzen um energieverbrauch & Cooldown & Speziation erweitern
#TODO muss ich die Organismen erkennen lassen wie viel Essen pro Bush ist?
#TODO Such/Sortieralgorithmen mit bester Performance raussuchen => o(log(n))
#TODO später JSON LOGS damit ich die Graphen zeichnen kann, pro Gen die Fitness Werte
#TODO maybe wegen Threaded Evaluation schauen, multiprocessing.shared_memory z.B. => Worker Prozesse für Sim
#NOTE maybe Genom für über Wasser gehen, binäres Genom
#NOTE vielleicht eine Object Klasse als Basis für Organismen, Food mit .destroy() und Koordinaten usw.
#NOTE überlegen ob ich alle Attribute private oder so machen soll
#NOTE wie trainiere ich das Programm dann am KI-Server

logger = log.get_logger(__name__)

class NEATSim:
    def __init__(self, neat_config_path, app_config):
        sim_config = app_config["simulation"]

        self.paused = False
        self.tick = 0
        self.tick_rate = sim_config["tick_rate"]
        #TODO das nochmal überdenken, ob das smart ist
        self.ticks_per_snapshot = sim_config["ticks_per_snapshot"]

        self.env = Environment(width=sim_config["width"],
                               height=sim_config["height"],
                               num_bushes=sim_config["num_bushes"],
                               seed=sim_config["seed"])

        #NOTE für Visualisierung ausklammern
        #self.env.WorldGen.visualize() 

        # NEAT Config laden
        self.neat_config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            neat_config_path
        )

        logger.info(
            f"NEAT Config loaded: pop_size={self.neat_config.pop_size}, "
            f"inputs={self.neat_config.genome_config.num_inputs}, "
            f"outputs={self.neat_config.genome_config.num_outputs}"
        )
        self.neat_config.pop_size = sim_config["num_organisms"]
        self.population = neat.Population(self.neat_config)

        self.state_builder = StateBuilder()
        self.deaths_this_tick = []
        self.init_population()

    def init_population(self):
        """Erstelle initiale Organismen passend zur NEAT-Population"""
        self.env.add_organisms(self.neat_config.pop_size)

        #TODO da nachschauen wie das funktioniert und warum das funktioniert?
        #TODO das noch mit mp.worker aufteilen
        for org, genome in zip(self.env.organisms, self.population.population.values()):
            org.net = neat.nn.RecurrentNetwork.create(genome, self.neat_config)
            org.genome = genome
            genome.fitness = 0

        logger.info(f"Initialized Organisms into Environment | {self.neat_config.pop_size} Organisms")

    def update_fitness(self, org):
        """Fitnesskontinuierlich anpassen"""
        f = org.genome.fitness

        # 1. Überleben
        f += 0.1

        # 2. Ressourcenlevel
        f += org.energy / org.max_energy
        f += org.food / org.max_food
        f += org.water / org.max_water

        # 3. Essen/Trinken
        if org.ate_this_tick:
            f += 4.0
        if org.drank_this_tick:
            f += 2.0
        if org.mated_this_tick:
            f += 10.0

        # 4. Sichtbare Ressourcen belohnen
        seen = org.seen_objects()
        if seen["food"]:
            dist_food, _ = org.get_closest(seen["food"])
            f += (org.vision_range - dist_food) / org.vision_range
        if seen["water"]:
            dist_water, _ = org.get_closest(seen["water"])
            f += (org.vision_range - dist_water) / org.vision_range

        org.genome.fitness = f

    def handle_death(self, org):
        """Organismus entfernen und neues Genome spawnen"""
        self.env.remove_organism(org)
    
    def reproduce(self, parents):
        parent1, parent2 = parents

        child = self.neat_config.genome_type(
            random.randint(0, 1_000_000)
        )

        child.configure_crossover(parent1, parent2, self.neat_config.genome_config)

        child.mutate(self.neat_config.genome_config)

        self.population.population[child.key] = child

        logger.info("REPRODUCED LETS GO!")  #BUG da noch einen guten Log rein
        return child

    def process_mating(self):
        pairs = self.env.consume_mating_pairs()

        for parent1, parent2 in pairs:
            child_genome = self.reproduce([parent1.genome, parent2.genome])

            net = neat.nn.RecurrentNetwork.create(child_genome, self.neat_config)
            self.env.add_organisms(1)       # FIXME da noch die Position von den Eltern nehmen

            new_org = self.env.organisms[-1]

            new_org.net = net
            new_org.genome = child_genome

            child_genome.fitness = 0

    def step_simulation(self):
        logger.debug(f"Tick {self.tick} running")
        self.deaths_this_tick = []
        self.env.update()            # Bushes regrown

        for org in list(self.env.organisms):
            inputs = org.get_inputs()
            outputs = org.net.activate(inputs)
            org.update(outputs)

            partner = org.try_find_mate()
            if partner:
                self.env.register_mating_pair(org, partner)

            self.update_fitness(org)

            if org.energy <= 0:
                self.deaths_this_tick.append(org.id)
                self.handle_death(org)

        self.process_mating()
        self.tick += 1

    def should_send_snapshot(self):
        return self.tick % self.ticks_per_snapshot == 0

    def build_snapshot(self):
        self.state_builder.build_organisms(self.env.organisms)
        self.state_builder.build_bushes(self.env.bushes)
        self.state_builder.build_state(self.tick, self.tick_rate, self.deaths_this_tick)

        return self.state_builder.state