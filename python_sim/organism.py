import math
import random
from resources import Bush

#TODO maybe Wasser / Food Threshold einbauen
#TODO bei Life = 0 sterben sie, Life einbauen anstatt Energy
#TODO die Organismen sollen sterben können, nicht nur im Training...
#NOTE maybe isWater ist ein Attirbut was automatisch gesetzt wird?

class Organism:
    def __init__(self, x, y, angle, max_speed, max_turn_speed, vision_level, terrain):
        # Position
        self.x = x
        self.y = y

        # Stats
        self.max_energy = 100
        self.energy = self.max_energy
        self.max_food = 100
        self.food = self.max_food
        self.max_water = 100
        self.water = self.max_water

        # Movement
        self.angle = angle          # in radiant weil die meisten Mathematischen Funktionen radiant erwarten
        #NOTE später vielleicht wieder reinmachen als Evolutionierbaren Stat
        #self.acceleration = 0.2

        self.max_speed = max_speed
        self.speed = 0.0
        self.max_turn_speed = max_turn_speed
        self.turn_speed = 0.0

        # Vision
        self.vision_level = vision_level
        self.set_vision()

        # Terrain
        self.terrain = terrain
        self.bushes = self.get_bushes()

        # NEAT
        self.net = None
        self.genome = None

        # ATTRIBUTES - UNUSED
        self.life = 100
        self.size = 1

        # Maybe
        self.age = None
        self.agingSpeed = None
        self.mutationRate = None
        self.layTime = None
        self.hatchTime = None

    def update(self, output):
        """Applied die NN Outputs"""
        self.apply_nn_output(output=output)

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

    def set_vision(self):
        """
        setzt von vision_level abhängig die fov, range und area
        - 0 = 360 Grad FOV, 1 Tile Range
        - 1 = 10 Grad FOV, 20 Tile Range
        """
        # Werte in Radiant
        max_fov = math.radians(360)
        min_fov = math.radians(10)

        # Berechnung
        self.vision_fov = self.lerp(max_fov, min_fov, self.vision_level)
        self.vision_range = self.lerp(1.0, 20.0, self.vision_level)
        self.vision_area = 0.5 * (self.vision_range ** 2) * self.vision_fov

    def seen_objects(self):
        """
        Findet alle Objekte(Wasser, Food) im Sichtfeld des Organismus.
        Gibt ein Dict mit 'food', 'water' zurück.
        """
        #NOTE maybe visible_water, etc. als Attribut machen
        visible_food = []
        visible_water = []
        visible_organisms = []      #TODO Organismen auch ins Sichtfeld aufnehmen, das bei Inputs & Outputs hinzufügen
        #visible_tiles = []         wäre zur Visualisierung von dem Sichtfeld
        half_fov = self.vision_fov / 2  # halber Sichtwinkel

        height = len(self.terrain)
        width = len(self.terrain[0])

        # Suchbereich auf Sichtreichweite beschränken => 10x so wenig Tiles zum Scannen
        # z.b. bei range=10, ein Quadrat von 21x21 Felder
        for y in range(max(0, int(self.y - self.vision_range)), min(int(self.y + self.vision_range) + 1, height)):    # => +1 weil b bei range(a, b) NICHT inklusive ist
            for x in range(max(0, int(self.x - self.vision_range)), min(int(self.x + self.vision_range) + 1, width)):
                tile = self.terrain[y][x]

                # Distanz vom Tile zur Kreatur ausrechnen
                dx = (x + 0.5) - self.x   # +0.5 => Tile-Mitte
                dy = (y + 0.5) - self.y
                distance = math.hypot(dx, dy)

                # Nur Tiles in Reichweite berücksichtigen, präziser Kreis von z.B. range=10
                if distance > self.vision_range:
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

    def get_closest(self, objects):
        """
        Gibt das nächstgelegene Objekt und den Winkel dorthin zurück.
        objects: Liste von (x, y) Tupeln
        Rückgabe: (distance, angle_relative)
        """
        closest_dist = float('inf')     # Unendlich
        closest_angle = 0.0

        for obj in objects:
            # Objekt-Koordinaten extrahieren
            obj_x, obj_y = obj

            dx = obj_x - self.x
            dy = obj_y - self.y
            dist = math.hypot(dx, dy)
            if dist < closest_dist:
                closest_dist = dist
                angle_to_obj = math.atan2(dy, dx)
                # Winkel relativ zur Blickrichtung normalisieren
                closest_angle = self.normalize_angle(angle_to_obj - self.angle)

        return closest_dist, closest_angle

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

    def is_on_bush(self):
        pass

    def drink(self):
        """Trinkt Wasser, wenn der Organismus auf einem Wasser-Tile steht."""
        #TODO kontinuierliches Trinken einbauen
        if self.is_on_water():
            self.water = min(self.max_water, self.water + 100)

    def eat(self, bush):
        """Organismus zieht 1 von bush.food ab und erhöht seine eigene Energie um bush.nutrition"""
        #TODO kontinuierliches Essen einbauen
        harvested = bush.harvest()
        self.energy = min(self.max_energy, self.energy + (harvested * bush.nutrition))

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

    def move(self):
        """
        turn + throttle werden angewandt
        """
        old_x = self.x
        old_y = self.y
        height = len(self.terrain)
        width = len(self.terrain[0])

        # Bewegungsvektor
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # der Organismus muss innerhalb 0 und width - 1e-6 bleiben
        self.x = max(0, min(self.x, width - 1e-6))  # Gültiger Bereich zum Moven 0-99.999...
        self.y = max(0, min(self.y, height - 1e-6))

        # Getravelte Distanz berechnen
        distance = math.hypot(self.x - old_x, self.y - old_y)

        # Energieverlust proportional zur tatsächlichen Distanz
        self.energy -= distance * 0.5

    def apply_nn_output(self, output):
        """
        turn[-1...1]
        throttle[0...1]
        eat_signal[0 | 1]       True > 0
        drink_signal[0 | 1]     True > 0
        """
        turn, throttle, eat_signal, drink_signal = output

        # Normalisierung, da alle Outputs tanh sind, muss ich manuell Normalisieren
        throttle = (throttle + 1) / 2       # Normalisiert auf [0...1]

        # Winkelsteuerung
        turn_strength = turn * self.max_turn_speed
        self.angle += turn_strength
        self.angle = self.normalize_angle(self.angle)

        # Geschwindigkeitssteuerung
        self.speed = throttle * self.max_speed

        # Bewegung
        self.move()

        # Trinken
        if drink_signal > 0:
            self.drink()

        # Essen
        if eat_signal > 0:
            # Wenn in der Nähe, Esse
            for bush in self.bushes:
                if abs(bush.x - self.x) < 1 and abs(bush.y - self.y) < 1:
                    self.eat(bush)
                    break

        # Metabolismus
        self.metabolism()

    def __str__(self):
        return f"""Organism(
            Pos X: {self.x},
            Pos Y: {self.y},
            Angle: {self.angle},
            Energy: {self.energy} von {self.max_energy},
            Water: {self.water} von {self.max_water},
            Food: {self.food} von {self.max_food},
            Speed: {self.speed} von {self.max_speed},
            TurnSpeed: {self.turn_speed} von {self.max_turn_speed}
            Vision: {self.vision_range} Tiles, {math.degrees(self.vision_fov)} Degrees"""