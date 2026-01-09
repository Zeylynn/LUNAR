import numpy as np
import matplotlib.pyplot as plt
from noise import pnoise2
import python_sim.logger_setup as log
import random
from python_sim.resources import Bush

logger = log.get_logger(__name__)

class WorldGenerator:
    def __init__(self, world_width, world_height, seed, num_bushes, threshold=0.0,
                 scale=10.0, octaves=4, persistence=0.5, lacunarity=2.0):
        self.world_width = world_width
        self.world_height = world_height

        # Noise Attributes
        self.threshold = threshold
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity

        self.seed = seed
        self.num_bushes = num_bushes

        # Enviroment initialisieren
        self.world = np.zeros((self.world_height, self.world_width))    # => ein Array gefüllt mit [[0, 0], [0, 0], ...]
        self.terrain = None                                             # => die fertige Map mit allem

    def init_world(self):
        """führt alle Methoden aus, die self.terrain, also die Welt 'zusammenbauen'"""
        self.generate_noise_world()
        self.generate_terrain_array()
        self.generate_terrain()
        self.generate_bushes()
        logger.info(f"Terrain fully generated")

    def generate_noise_world(self):
        """überschreibt den Array self.world mit Perl Noise Werten von -1 bis 1"""
        for y in range(self.world_height):
            for x in range(self.world_width):
                nx = x / self.scale
                ny = y / self.scale
                noise_val = pnoise2(nx, ny,
                                    octaves=self.octaves,
                                    persistence=self.persistence,
                                    lacunarity=self.lacunarity,
                                    repeatx=1024,
                                    repeaty=1024,
                                    base=self.seed)     # Dieser Paramater ist kaum definiert, jeder Seed außerhalb des Bereichs -9999 bis +500 ist unbrauchbar, theoretisch ist es ein signed int
                self.world[y][x] = noise_val
        
        actual_height = len(self.world)
        actual_width = len(self.world[0])

        # Fehlermeldung weil die Funktion Standardmäßig keine Fehler meldet
        if actual_height != self.world_height or actual_width != self.world_width:
            raise ValueError(
                f"Falsche Weltgröße: erwartet ({self.world_height}x{self.world_width}), "
                f"aber erhalten ({actual_height}x{actual_width})."
            )
        logger.debug(f"Noise world generated with size: ({self.world.shape})")

    def generate_terrain_array(self):
        """
        Setzt den Array self.terrain mit:
        - Array[x][y] < self.threshold = 0
        - Array[x][y] > self.threshold = 1
        """
        # np.where liefert entweder x oder y, je nachdem ob condition True/False ist und das für jedes Element im Array
        self.terrain = np.where(self.world < self.threshold, float(0), float(1))    # ohne float kann es nicht mit float threshholds verglichen werden
        logger.debug(f"Array based on noise world generated: (0=Water, 1=Terrain)")

    def generate_terrain(self):
        """
        überschreibt den Array self.terrain mit folgender Dictionary Struktur:
        -  {"terrain": 0 or 1, "object": None}
        """
        terrain_grid = []

        height, width = self.terrain.shape
        for y in range(height):
            row = []
            for x in range(width):
                # Füllt den Array neu auf
                row.append({
                    "terrain": self.terrain[y][x],
                    "object": None
                })
            terrain_grid.append(row)

        self.terrain = terrain_grid
        logger.debug("Generated terrain grid with structure: {'terrain': 0 or 1, 'object': None or Bush}")

    def generate_bushes(self):
        """
        Setzt 'object' im self.terrain array auf Bush und generiert so zufällig Büsche mit folgenden Kriterien
        - sie können nicht in Wasser generieren
        """
        height = len(self.terrain)
        width = len(self.terrain[0])
        bushes = 0

        while bushes < self.num_bushes:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)

            # Tile darf kein Wasser haben
            if self.terrain[y][x]["terrain"] == 0:
                continue

            #NOTE maybe implementieren dass ein gewisser Abstand zwischen den Büschen sein muss

            # Wenn frei => Busch platzieren
            self.terrain[y][x]["object"] = Bush(x, y)
            bushes += 1
        logger.debug(f"Added {bushes} bushes into terrain grid")

    def get_terrain(self):
        """gibt self.terrain zurück"""
        return self.terrain
    
    def get_bushes(self):
        """
        Durchsucht self.terrain und gibt eine Liste von allen Bush-Objekten zurück
        """
        bushes = []
        for row in self.terrain:
            for tile in row:
                obj = tile.get("object")
                if isinstance(obj, Bush):
                    bushes.append(obj)
        return bushes

    def visualize(self):
        #NOTE Remove Later
        height = len(self.terrain)
        width = len(self.terrain[0])
        terrain_array = np.zeros((height, width))

        for y in range(height):
            for x in range(width):
                terrain_array[y, x] = self.terrain[y][x]["terrain"]

        plt.imshow(terrain_array, cmap="terrain")
        plt.title("2D World - Land & Water via Perlin Noise")
        plt.colorbar()
        plt.show()