import math
import random

#TODO Wasser / Food einen Sinn geben
#TODO Attribtue zufällig initialisieren / Sinnvolle Werte geben
#TODO eigene Funktion für Energieverbrauch
#TODO bei Energy = 0 sterben sie
#TODO Angle muss zischen 2Pi und 0 bleiben => zurzeit bleibt der Angle immer ca. gleich vielleicht Rotation reinmachen
#TODO maybe isWater ist ein Attirbut was automatisch gesetzt wird?

class Organism:
    def __init__(self, x, y, angle, speed, vision_level, terrain):
        # float weil sie mit INT zufällige Positionen bekommen, ich aber alle x,y Werte in float haben will
        self.x = float(x)
        self.y = float(y)
        self.angle = angle  # in radiant weil die meisten Mathematischen Funktionen radiant erwarten
        self.speed = speed
        self.vision_level = vision_level
        self.terrain = terrain

        self.update_vision()

        # ATTRIBUTES
        self.energy = 100
        self.food = 100
        self.water = 100
        self.life = 100
        self.size = 1

        # Maybe
        self.age = None
        self.turnSpeed = None
        self.agingSpeed = None
        self.mutationRate = None
        self.layTime = None
        self.hatchTime = None

    def lerp(self, a, b, t):
        """Lineare Interpolation, z.B. für die Vision"""
        return a + (b - a) * t

    def update_vision(self):
        """
        setzt von vision_level abhängig die fov und range
        - 0 = 360 Grad FOV, 1 Tile Range
        - 1 = 10 Grad FOV, 20 Tile Range
        """
        # Werte in Radiant
        max_fov = math.radians(360)
        min_fov = math.radians(10)

        # Berechnung
        self.vision_fov = self.lerp(max_fov, min_fov, self.vision_level)
        self.vision_range = self.lerp(1.0, 20.0, self.vision_level)

    def seen_resources(self):
        visible = []
        #TODO implementieren, zuerst aber Busch/Food generation
    
    def is_on_water(self):
        """prüft über das Terrain ob Wasser auf (x, y) ist oder nicht"""
        # Int besser als round wegen der Indexierung von Tiles, so wird 99.5 auf Tile 99 abgerundet, anstatt auf Tile 100(nicht existent) aufgerundet
        grid_x = int(self.x)
        grid_y = int(self.y)

        # TRUE wenn Wasser, FALSE wenn kein Wasser
        if self.terrain[grid_y][grid_x] == 0:
            return True
        else:
            return False    

    def move(self, width, height):
        # Zurzeit einfach random Movement
        self.angle += random.uniform(-0.5, 0.5)
        
        #TODO Die Mathematik nachprüfen
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # checkt ob der Organismus an der Border ist
        self.x = max(0, min(self.x, width - 1e-6))  # Gültiger Bereich zum Moven 0-99.999...
        self.y = max(0, min(self.y, height - 1e-6))

        self.energy -= self.speed * 0.5

    def __str__(self):
        return f"""Organism(
            Pos X: {self.x},
            Pos Y: {self.y},
            Angle: {self.angle},
            Energy: {self.energy},
            Speed: {self.speed},
            FOV: {math.degrees(self.vision_fov)},
            Range: {self.vision_range},
            onWater: {self.is_on_water()})"""