import math
import random

#TODO maybe Wasser / Food Threshold einbauen
#TODO bei Life = 0 sterben sie, Life einbauen
#NOTE maybe isWater ist ein Attirbut was automatisch gesetzt wird?
#NOTE maybe eigene Funktion für Energieverbrauch

class Organism:
    def __init__(self, x, y, angle, speed, vision_level, terrain):
        # ATTRIBUTE
        self.x = x
        self.y = y
        self.angle = angle  # in radiant weil die meisten Mathematischen Funktionen radiant erwarten
        self.speed = speed
        self.vision_level = vision_level

        self.energy = 100
        self.max_energy = 100

        self.food = 100
        self.max_food = 100

        self.water = 100
        self.max_water = 100

        self.terrain = terrain
        self.update_vision()

        # ATTRIBUTES - UNUSED
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

    def normalize_angle(self, angle):
        """
        Normalisiert einen Winkel auf den Bereich [-pi, +pi].
        z.B. ein Winkel von 9rad ~ 3pi wird zu 3rad ~ pi, ich bekomme immer die kleinste Rotation
        """
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

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
        """
        Findet alle Tiles im Sichtfeld des Organismus.
        Erkennt 'Bush' (Food) und Wasser anhand des Terrains.
        Gibt ein Dict mit 'food' und 'water' zurück.
        """
        #NOTE maybe visible_water, etc. als Attribut machen
        visible_food = []
        visible_water = []
        #visible_tiles = []         wäre zur Visualisierung von dem Sichtfeld
        half_fov = self.fov / 2  # halber Sichtwinkel

        height = len(self.terrain)
        width = len(self.terrain[0])

        # Suchbereich auf Sichtreichweite beschränken => 10x so wenig Tiles zum Scannen
        # z.b. bei range=10, ein Quadrat von 21x21 Felder
        for y in range(max(0, int(self.y - self.range)), min(int(self.y + self.range) + 1, height)):    # => +1 weil b bei range(a, b) NICHT inklusive ist
            for x in range(max(0, int(self.x - self.range)), min(int(self.x + self.range) + 1, width)):
                tile = self.terrain[y][x]

                # Distanz vom Tile zur Kreatur ausrechnen
                dx = (x + 0.5) - self.x   # +0.5 => Tile-Mitte
                dy = (y + 0.5) - self.y
                distance = math.hypot(dx, dy)

                # Nur Tiles in Reichweite berücksichtigen, präziser Kreis von z.B. range=10
                if distance > self.range:
                    continue

                # Winkel zwischen Blickrichtung und Tile
                angle_to_tile = math.atan2(dy, dx)
                raw_diff = angle_to_tile - self.angle

                # Normalisiert => kürzeste Drehung
                angle_diff = self.normalize_angle(raw_diff)

                # Prüfen, ob innerhalb Sichtfeld, abs() entfernt Vorzeichen
                if abs(angle_diff) <= half_fov:
                    # Wasser oder Food erkennen
                    if tile["terrain"] == 0:
                        visible_water.append((x, y))
                    elif tile["object"] == "Bush":
                        visible_food.append((x, y))
                    #visible_tiles.append((x, y))               wäre zur Visualisierung von dem Sichtfeld

        return {
            "food": visible_food,
            "water": visible_water
        }

    
    def is_on_water(self):
        """prüft über das Terrain ob Wasser auf (x, y) ist oder nicht"""
        # Int besser als round wegen der Indexierung von Tiles, so wird 99.5 auf Tile 99 abgerundet, anstatt auf Tile 100(nicht existent) aufgerundet
        grid_x = int(self.x)
        grid_y = int(self.y)

        # TRUE wenn Wasser, FALSE wenn kein Wasser
        if self.terrain[grid_y][grid_x]["terrain"] == 0:
            return True
        else:
            return False    

    def drink(self):
        """Trinkt Wasser, wenn der Organismus auf einem Wasser-Tile steht."""
        if self.is_on_water():
            self.water = min(self.max_water, self.water)

    def eat(self, bush, amount):
        """Organismus zieht amount von bush.food ab und erhöht seine eigene Energie um amount * bush.nutrition"""
        harvested = bush.harvest(amount)
        self.energy = min(self.max_energy, self.energy + (harvested * bush.nutrition / 100))

    def metabolism(self):
        """
        Standard Wasser | Food | Energie Kosten pro Tick.
        - Wenn Food und Wasser über 20% ihrer Maximalwerte liegen, bekommt der Organismus Energie.
        - Wenn eines unter 20% liegt, bekommt er keine Energie.
        - Zusätzlich werden Food und Wasser leicht reduziert, um Verbrauch zu simulieren.
        """
        # Verbrauch pro Tick
        food_consumption = 1
        water_consumption = 1

        # Ressourcen reduzieren
        self.food = max(0.0, self.food - food_consumption)
        self.water = max(0.0, self.water - water_consumption)

        # Prüfen, ob genug Ressourcen vorhanden sind (>20% des Max)
        food_ok = self.food > 0.2 * self.max_food
        water_ok = self.water > 0.2 * self.max_water

        if food_ok and water_ok:
            energy_gain = 2  # Menge pro Tick, kann angepasst werden
            self.energy = min(self.max_energy, self.energy + energy_gain)
        else:
            pass
        

    def move(self, width, height):
        """
        Organismus bewegt sich um zufällige x, y Koordinaten und verliert Energie
        """
        # Zurzeit einfach random Movement
        self.angle += random.uniform(-0.5, 0.5)

        self.angle = self.normalize_angle(self.angle)

        old_x = self.x
        old_y = self.y
        
        # Neue Position berechnen
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # der Organismus muss innerhalb 0 und width - 1e-6 bleiben
        self.x = max(0, min(self.x, width - 1e-6))  # Gültiger Bereich zum Moven 0-99.999...
        self.y = max(0, min(self.y, height - 1e-6))

        # Getravelte Distanz berechnen
        distance = math.hypot(self.x - old_x, self.y - old_y)
        
        # Energieverbrauch: proportional zur Distanz und Geschwindigkeit
        energy_cost = distance * self.speed * 0.5
        self.energy = max(0.0, self.energy - energy_cost)

    def apply_nn_output(self, output, environment):
        """
        Nimmt die Ausgabe des neuronalen Netzes und führt entsprechende Aktionen aus.
        Output ist ein Array wie [turn_left, turn_right, move_forward, interact].
        """
        turn_left, turn_right, move_forward, interact = output

        # Bewegung / Drehung
        if turn_left > 0.5:
            self.angle -= 0.2
        if turn_right > 0.5:
            self.angle += 0.2
        if move_forward > 0.5:
            self.move(environment.width, environment.height)

        # Interaktion mit Umgebung
        if interact > 0.5:
            if self.is_on_water(environment.terrain):
                self.drink()
            else:
                for bush in environment.bushes:
                    if abs(bush.x - self.x) < 1 and abs(bush.y - self.y) < 1:
                        bush.harvest(self)
                        break

        # Metabolismus
        self.metabolism()

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