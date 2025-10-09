import math
import random

#TODO Wasser / Food einen Sinn geben
#TODO Attribtue zufällig initialisieren / Sinnvolle Werte geben
#TODO eigene Funktion für Energieverbrauch

class Organism:
    def __init__(self, x, y, angle):
        # Zufällige Startposition
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)  # in radiant weil die meisten Mathematischen Funktionen radiant erwarten

        # ATTRIBUTES
        self.energy = 100
        self.food = 100
        self.water = 100
        self.life = 100
        self.sightRange = 100
        self.sightArch = 90
        self.size = 1
        self.speed = 1

        # Maybe
        self.age = None
        self.turnSpeed = None
        self.agingSpeed = None
        self.mutationRate = None
        self.layTime = None
        self.hatchTime = None
        
    def move(self, width, height):
        # Zurzeit einfach random Movement
        self.angle += random.uniform(-0.2, 0.2)
        
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # checkt ob der Organismus an der Border ist
        self.x = max(0, min(width, self.x))
        self.y = max(0, min(height, self.y))

        self.energy -= self.speed * 0.1