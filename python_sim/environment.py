from organism import Organism
from python_sim.world_generator import WorldGenerator
import random
import math
import logger_setup as log
from resources import Bush

#TODO maybe eigene Logs für Organismen

logger = log.get_logger(__name__)

class Environment:
    def __init__(self, width, height, num_organisms, num_bushes, seed):
        # ATTRIBUTE
        self.width = width
        self.height = height
        self.set_seed(seed)

        self.organisms = None
        self.bushes = None

        #TODO maybe Threshold einstellbar machen idk
        self.WorldGen = WorldGenerator(world_width=self.width, world_height=self.height, seed=self.seed, num_bushes=num_bushes, threshold=-0.15)
        self.WorldGen.init_world()
        self.terrain = self.WorldGen.get_terrain()

        self.bushes = self.WorldGen.get_bushes()
        self.organisms = self.init_organisms(num_organisms)
        
        logger.info("Environment initialized")

    def init_organisms(self, num_organisms):
        """
        Erstellt {num_organisms} viele Organismen
        - Jedes Attribut wird zufällig zugewiesen
        - gibt eine Liste an Organismen zurück
        """
        #TODO so machen dass Lebewesen nicht auf Wasser generieren können
        organisms = []
        for _ in range(num_organisms):
            x = random.uniform(0, self.width)   # Exkludiert self.width deswegen ist die Spawnrange 0-99.999...
            y = random.uniform(0, self.height)
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(5, 15)
            vision_level = random.uniform(0, 1)

            organism = Organism(x, y, angle, speed, vision_level, self.terrain)
            organisms.append(organism)

        logger.info("Organisms initialized")
        return organisms

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
        logger.debug(f"Seed set as: {seed}")

    def update(self):
        """
        Iteriert durch jedes
        - Organism-Obj und führt .move() aus
        - Bush-Obj und führt .update() aus
        """
        # Bewegt alle Organismen
        for org in self.organisms:
            org.move(self.width, self.height)
            #org.consume_energy()

        # Updated alle Büsche
        for row in self.terrain:
            for tile in row:
                obj = tile["object"]
                if isinstance(obj, Bush):       # Prüft ob der Eintrag "object" vom Typ Bush ist
                    obj.update()                # Food wächst 