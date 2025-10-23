from organism import Organism
from world_generator import WorldGenerator
import random
import math
import logger_setup as log

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

        #NOTE maybe Threshold einstellbar machen idk
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
        - Organismen können nicht auf Wasser generieren
        """
        organisms = []
        for _ in range(num_organisms):
            while True:
                x = random.uniform(0, self.width)   # Exkludiert self.width deswegen ist die Spawnrange 0-99.999...
                y = random.uniform(0, self.height)

                grid_x = int(x)
                grid_y = int(y)

                # Bricht die Schleife ab wenn auf Land gespawnt ist
                if self.terrain[grid_y][grid_x]["terrain"] == 1:
                    break
            
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
        logger.debug(f"Seed set as: {self.seed}")

    def update(self):
        """
        Iteriert durch jedes
        - Organism-Obj und führt .move() & .metabolism() aus
        - Bush-Obj und führt .update() aus
        """
        for org in self.organisms:
            org.move(self.width, self.height)
            org.metabolism()

        for bush in self.bushes:
            bush.update()