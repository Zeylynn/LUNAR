import math
import random

#TODO Wasser / Food einen Sinn geben
#TODO Attribtue zufällig initialisieren / Sinnvolle Werte geben
#TODO eigene Funktion für Energieverbrauch
#TODO bei Energy = 0 sterben sie
#TODO Angle muss zischen 2Pi und 0 bleiben => zurzeit bleibt der Angle immer ca. gleich vielleicht Rotation reinmachen

class Organism:
    def __init__(self, x, y, angle, speed):
        # float weil sie mit INT zufällige Positionen bekommen, ich aber alle x,y Werte in float haben will
        self.x = float(x)
        self.y = float(y)
        self.angle = angle  # in radiant weil die meisten Mathematischen Funktionen radiant erwarten
        self.speed = speed

        # ATTRIBUTES
        self.energy = 100
        self.food = 100
        self.water = 100
        self.life = 100
        self.sightRange = 100
        self.sightArch = 90
        self.size = 1

        # Maybe
        self.age = None
        self.turnSpeed = None
        self.agingSpeed = None
        self.mutationRate = None
        self.layTime = None
        self.hatchTime = None
    
    def is_on_water(self, terrain):
        """prüft über das Terrain ob Wasser auf (x, y) ist oder nicht"""
        #TODO ist es performant jedes mal das terrain zu übergeben, geht maybe anders
        grid_x = round(self.x)
        grid_y = round(self.y)

        return terrain[grid_y][grid_x] == 0    # TRUE wenn Wasser, FALSE wenn kein Wasser

    def move(self, width, height):
        # Zurzeit einfach random Movement
        self.angle += random.uniform(-0.5, 0.5)
        
        #TODO Die Mathematik nachprüfen
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # checkt ob der Organismus an der Border ist
        self.x = max(0, min(width, self.x))
        self.y = max(0, min(height, self.y))

        self.energy -= self.speed * 0.5

    def __str__(self):
        return f'Organism(Pos X: {self.x}, Pos Y: {self.y}, Angle: {self.angle}, Energy: {self.energy}, Speed: {self.speed})'