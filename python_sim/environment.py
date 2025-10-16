from organism import Organism
from resources import Food
from noise_runner import NoiseGenerator
import random
import math

#TODO maybe Threshold einstellbar machen idk

class Environment:
    def __init__(self, width, height, num_resources, num_organisms, seed):
        self.width = width
        self.height = height
        self.resources = None
        self.organisms = None

        self.seed = seed
        self.NoiseGen = NoiseGenerator(world_width=self.width, world_height=self.height, seed=self.seed, threshold=-0.15)
        self.terrain = self.NoiseGen.generate_terrain()

        self.init_resources(num_resources)
        self.init_organisms(num_organisms)

        print("Initialisation complete!")

    def init_resources(self, num_resources):
        self.resources = []
        for _ in range(num_resources):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            food = Food(x, y)
            self.resources.append(food)

    def init_organisms(self, num_organisms):
        self.organisms = []
        for _ in range(num_organisms):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(5, 15)
            organism = Organism(x, y, angle, speed)
            self.organisms.append(organism)

    def update(self):
        """Iterates through every Organism and runs .move() for every iteration"""
        for org in self.organisms:
            org.move(self.width, self.height)
            #org.consume_energy()