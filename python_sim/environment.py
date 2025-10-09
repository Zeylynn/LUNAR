from organism import Organism
from resources import Food
import random
import math

#TODO Water Generation via Noise

class Environment:
    def __init__(self, width, height, num_resources, num_organisms):
        self.width = width
        self.height = height
        self.init_resources(num_resources)
        self.init_organisms(num_organisms)

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
            organism = Organism(x, y, angle)
            self.organisms.append(organism)

    def update(self):
        for org in self.organisms:
            org.move(self.width, self.height)
            org.consume_energy()
