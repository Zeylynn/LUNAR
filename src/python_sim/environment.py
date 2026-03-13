from python_sim.organism import Organism
from python_sim.world_generator import WorldGenerator
import random
import math
import python_sim.logger_setup as log

logger = log.get_logger(__name__)

class Environment:
    def __init__(self, width, height, num_bushes, seed):
        # ATTRIBUTE
        self.width = width
        self.height = height
        self.set_seed(seed)
        self.num_bushes = num_bushes

        self.organisms = []
        self.mating_pairs = []
        self.bushes = None

        #NOTE maybe Threshold einstellbar machen idk, für World Gen Relevant
        self.WorldGen = WorldGenerator(world_width=self.width, world_height=self.height, seed=self.seed, num_bushes=num_bushes, threshold=-0.15)
        self.WorldGen.init_world()
        self.terrain = self.WorldGen.get_terrain()

        self.bushes = self.WorldGen.get_bushes()
        
        logger.info(f"Environment initialized | {num_bushes} Bushes")

    def add_organisms(self, amount):
        """
        Erstellt {amount} viele Organismen, fügt erstellte Organims self.organisms hinzu, gibt erstellte Organisms zurück
        - Jedes Attribut wird zufällig zugewiesen
        - Organismen können nicht auf Wasser generieren
        """
        for _ in range(amount):
            while True:
                x = random.uniform(0, self.width)   # Exkludiert self.width deswegen ist die Spawnrange 0-99.999...
                y = random.uniform(0, self.height)

                # auf Tiles Runden
                grid_x = int(x)
                grid_y = int(y)

                # Bricht die Schleife ab wenn auf Land gespawnt ist
                if self.terrain[grid_y][grid_x]["terrain"] == 1:
                    break
            
            angle = random.uniform(-math.pi, math.pi)
            max_speed = random.uniform(0.25, 0.75)
            max_turn_speed = math.radians(10)       # max. 10° pro Tick
            vision_level = random.uniform(0, 1)

            organism = Organism(x, y, angle, max_speed, max_turn_speed, vision_level, self)
            self.organisms.append(organism)

    def remove_organisms(self, organism):
        if organism in self.organisms:
            self.organisms.remove(organism)

    def set_seed(self, seed):
        """
        Setzt die variable self.seed
        - Verhindert, dass ein Seed gesetzt wird der außerhalb des nutzbaren Bereichs(-9999, 500) liegt
        - Falls seed=None wird ein zufälliger seed gesetzt
        """
        if seed == None:
            self.seed = random.randint(-9999, 500)
        elif seed < 500 and seed > -9999:
            self.seed = seed
        else:
            raise ValueError("seed ist out of usable range! Usable range is -9999 to 500!")
        logger.debug(f"Seed set as: {self.seed}")

    def register_mating_pair(self, org1, org2):
        """Paare registrieren, keine Doppelungen (A-B = B-A)"""
        pair = tuple(sorted((org1, org2), key=lambda o: o.id))
        if pair not in self.mating_pairs:
            self.mating_pairs.append(pair)

    def process_mating(self):
        """Erzeugt Kinder für alle registrierten Paare"""
        for org1, org2 in self.mating_pairs:
            self.create_offspring(org1, org2)
        self.mating_pairs.clear()

    def create_offspring(self, parent1, parent2):
        """Erzeugt Kind mit NEAT-Reproduktion"""
        env_sim = parent1.env_sim  # Referenz auf NEATSim
        child_genome = env_sim.reproduce([parent1.genome, parent2.genome])
        net = neat.nn.RecurrentNetwork.create(child_genome, env_sim.neat_config)
        new_org = self.add_organisms(1)[0]
        new_org.net = net
        new_org.genome = child_genome
        new_org.env_sim = env_sim
        child_genome.fitness = 0
        env_sim.organisms.append(new_org)

    def update(self):
        """
        Iteriert durch jedes
        - Bush-Obj und führt .update() aus => lässt Food nachwachsen
        """
        for bush in self.bushes:
            bush.update()