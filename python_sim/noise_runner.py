import numpy as np
import matplotlib.pyplot as plt
from noise import pnoise2

#TODO Sichtbar machen wenn Fehler bei generate_world auftauchen

class NoiseGenerator:
    def __init__(self, world_width, world_height, seed, scale=10.0, octaves=4, persistence=0.5, lacunarity=2.0, threshold=0.0):
        # +1 damit der Array gleich groß ist wie die Welt
        self.world_width = world_width + 1
        self.world_height = world_height + 1 

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
        (Generiert keine Fehlermdlung wenn sie abstürzt)
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