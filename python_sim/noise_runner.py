import numpy as np
import matplotlib.pyplot as plt
from noise import pnoise2
import logger_setup as log

#TODO Random Buschgeneration einbauen

logger = log.get_logger(__name__)

class NoiseGenerator:
    def __init__(self, world_width, world_height, seed, scale=10.0, octaves=4, persistence=0.5, lacunarity=2.0, threshold=0.0):
        self.world_width = world_width
        self.world_height = world_height

        # Noise Attributes
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.threshold = threshold
        self.seed = seed

        # Das Enviroment als Array
        self.world = np.zeros((self.world_height, self.world_width))
        self.terrain = None
        self.generate_noise_world()

    def generate_noise_world(self):
        """
        Erstellt einen Array in der Größe der World width/height,
        ist gefüllt mit Werten von -1 bis 1 basierend auf PearlNoise
        """
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
        logger.debug(f"Noise World generated with size: ({actual_height}, {actual_width})")

    def generate_terrain(self):
        """Wandel die NoiseMap in einen Array mit 0=Wasser und 1=Land um"""
        # np.where liefert entweder x oder y, je nachdem ob condition True/False ist und das für jedes Element im Array
        self.terrain = np.where(self.world < self.threshold, float(0), float(1))    # ohne float kann es nicht mit float threshholds verglichen werden
        return self.terrain

    def visualize(self):
        plt.imshow(self.terrain, cmap='terrain')
        plt.title("2D World - Land & Water via Perlin Noise")
        plt.colorbar()
        plt.show()