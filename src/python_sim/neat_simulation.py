import neat
import python_sim.logger_setup as log
from python_sim.environment import Environment
from python_sim.state_builder import StateBuilder
import random

#TODO Evolution einbauen, also Attribute bei Fortpflanzung leicht ändern
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
    def __init__(self, neat_config_path, app_config, pretrained_genomes=None):
        sim_config = app_config["simulation"]
        my_neat_config = app_config["neat"]

        self.paused = False
        self.tick = 0
        self.tick_rate = sim_config["tick_rate"]
        self.ticks_per_snapshot = sim_config["ticks_per_snapshot"]

        # RT-NEAT spezifische Parameter
        self.fitness_dropoff = my_neat_config["fitness_dropoff"]
        self.eval_interval = my_neat_config["eval_interval"]                    # wie oft live-update läuft
        self.live_mutation_strength = my_neat_config["live_mutation_strength"]  #BUG das noch nachschauen
        self.live_weight_perturb = my_neat_config["live_weight_perturb"]        # max Änderungsbetrag
        self.live_structural_prob = my_neat_config["live_structural_prob"]      # Chance neue Conn
        self.live_add_node_prob = my_neat_config["live_add_node_prob"]          # Chance neuen Node

        self.env = Environment(width=sim_config["width"],
                               height=sim_config["height"],
                               num_bushes=sim_config["num_bushes"],
                               seed=sim_config["seed"],
                               org_config=app_config["organism"]) 

        # NEAT Config laden
        self.neat_config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            neat_config_path
        )
        self.pretrained_genomes = pretrained_genomes

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
        """Erstellt initiale Organismen Bevölkerung"""
        pop_size = self.neat_config.pop_size
        self.env.add_organisms(pop_size)

        all_genomes = []

        if self.pretrained_genomes:
            logger.info(f"Using {len(self.pretrained_genomes)} pretrained genomes")

            # pretrained zuerst rein
            all_genomes.extend(self.pretrained_genomes)

            # dann auffüllen durch RECYCLING (Option 2)
            while len(all_genomes) < pop_size:
                g = random.choice(self.pretrained_genomes)

                # WICHTIG: COPY machen → sonst teilen sich mehrere Orgs das gleiche Genome!
                new_g = self.neat_config.genome_type(random.randint(0, 10**9))
                new_g.configure_crossover(g, g, self.neat_config.genome_config)  # Clone
                new_g.mutate(self.neat_config.genome_config)  # kleine Variation

                all_genomes.append(new_g)

        else:
            all_genomes = list(self.population.population.values())

        # Safety (falls zu viele pretrained)
        all_genomes = all_genomes[:pop_size]

        for org, genome in zip(self.env.organisms, all_genomes):
            org.genome = genome
            org.net = neat.nn.RecurrentNetwork.create(genome, self.neat_config)
            genome.fitness = 0.0

        logger.info(f"Initialized {len(self.env.organisms)} Organisms into Environment")

    def live_mutate(self, org):
        genome = org.genome

        for cg in genome.connections.values():
            cg.weight += random.uniform(
                -self.live_mutation_strength,
                self.live_mutation_strength
            )

        # selten Strukturmutation
        if random.random() < 0.01:
            genome.mutate(self.neat_config.genome_config)

        # Netzwerk neu bauen
        org.net = neat.nn.RecurrentNetwork.create(genome, self.neat_config)

    def handle_death(self, org):
        """Organismus entfernen und neues Genome spawnen"""
        self.env.remove_organism(org)
    
    def reproduce(self, g1, g2):
        child = self.neat_config.genome_type(random.randint(0, 10e6))

        child.configure_crossover(g1, g2, self.neat_config.genome_config)
        child.mutate(self.neat_config.genome_config)

        self.population.population[child.key] = child
        return child

    def process_mating(self):
        pairs = self.env.consume_mating_pairs()

        for parent1, parent2 in pairs:
            child_genome = self.reproduce(parent1.genome, parent2.genome)

            net = neat.nn.RecurrentNetwork.create(child_genome, self.neat_config)
            self.env.add_organisms(1)

            new_org = self.env.organisms[-1]
            new_org.x = (parent1.x + parent2.x) / 2.0 + random.uniform(-0.5, 0.5)
            new_org.y = (parent1.y + parent2.y) / 2.0 + random.uniform(-0.5, 0.5)

            new_org.net = net
            new_org.genome = child_genome
            new_org.parentID_1 = parent1.id
            new_org.parentID_2 = parent2.id

            child_genome.fitness = 0    #BUG maybe is das ein Fehler

            parent1.energy -= parent1.reproduction_cost
            parent1.mate_cooldown = parent1.mate_cooldown_max
            parent1.genome.fitness += 15.0

            parent2.energy -= parent2.reproduction_cost
            parent2.mate_cooldown = parent2.mate_cooldown_max
            parent2.genome.fitness += 15.0

            logger.info(
                f"Reproduction | tick={self.tick} | "
                f"parents=({parent1.id},{parent2.id}) | "
                f"child={new_org.id}"
            )

    def step_simulation(self):
        logger.debug(f"Tick {self.tick} running")
        self.deaths_this_tick = []
        self.env.update()            # Bushes regrown

        for org in list(self.env.organisms):
            inputs = org.get_inputs()
            outputs = org.net.activate(inputs)

            reward = org.apply_nn_output(outputs)
            org.genome.fitness += reward

            org.fitness_signal = org.genome.fitness

            partner = org.try_find_mate()
            if partner:
                self.env.register_mating_pair(org, partner)

            if org.energy <= 0:
                self.deaths_this_tick.append(org.id)
                self.handle_death(org)

            org.genome.fitness = org.genome.fitness * (1 - self.fitness_dropoff) 

        self.process_mating()

        if self.tick % self.eval_interval == 0:
            for org in self.env.organisms:
                self.live_mutate(org)

        if self.tick % 50 == 0:
            self.log_population_stats()
            self.log_top_organism()

        self.tick += 1

    def log_population_stats(self):
        genomes = [org.genome for org in self.env.organisms if hasattr(org, "genome")]

        if not genomes:
            return

        fitness_values = [g.fitness for g in genomes]

        avg = sum(fitness_values) / len(fitness_values)
        best = max(fitness_values)
        worst = min(fitness_values)

        logger.info(
            f"[STATS] Tick={self.tick} | "
            f"Pop={len(genomes)} | "
            f"AvgFit={avg:.2f} | "
            f"BestFit={best:.2f} | "
            f"WorstFit={worst:.2f}"
        )

    def log_top_organism(self):
        if not self.env.organisms:
            return  

        best = max(self.env.organisms, key=lambda o: o.genome.fitness)

        logger.info(
            f"[TOP] ID={best.id} | "
            f"Fitness={best.genome.fitness:.2f} | "
            f"Energy={best.energy:.1f} | "
            f"Food={best.food:.1f} | "
            f"Water={best.water:.1f}"
        )

    def should_send_snapshot(self):
        return self.tick % self.ticks_per_snapshot == 0

    def build_snapshot(self):
        self.state_builder.build_organisms(self.env.organisms)
        self.state_builder.build_bushes(self.env.bushes)
        self.state_builder.build_state(self.tick, self.tick_rate, self.deaths_this_tick)

        return self.state_builder.state