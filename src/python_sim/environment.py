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
            max_turn_speed = math.radians(60)       # max. 60° pro Tick
            vision_level = random.uniform(0, 1)

            organism = Organism(x, y, angle, max_speed, max_turn_speed, vision_level, self)
            self.organisms.append(organism)

    def remove_organism(self, organism):
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
        """
        Paare registrieren, ohne Doppelungen.
        (A-B gilt als gleich wie B-A)
        """
        if org1.id < org2.id:
            pair = (org1, org2)
        else:
            pair = (org2, org1)

        if pair not in self.mating_pairs:
            self.mating_pairs.append(pair)

    def consume_mating_pairs(self):
        pairs = self.mating_pairs
        self.mating_pairs = []
        return pairs

    def update(self):
        """
        Iteriert durch jedes
        - Bush-Obj und führt .update() aus => lässt Food nachwachsen
        """
        for bush in self.bushes:
            bush.update()