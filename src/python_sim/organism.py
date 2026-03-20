import math
from python_sim.resources import Bush
import itertools
import random

#BUG muss ich die erkennen lassen wo die Border ist?
#TODO NN Daten(net, genome) via JSON an Clemens schicken => für Visualisierung der "Brains"
#TODO maybe Wasser / Food Threshold einbauen als Variable/Mutation
#NOTE maybe isWater ist ein Attirbut was automatisch gesetzt wird?

class Organism:
    # Threadsafe d.h. wenn Instanzen in mehreren Threads erstellt werden bekommen sie trotzdem einzigartige IDs, bei Prozessen nicht
    _id_counter = itertools.count(start=1)

    def __init__(self, x, y, angle, environment, org_config):
        self.id = next(Organism._id_counter)
        # Position
        self.x = x
        self.y = y
        self.prev_x = self.x
        self.prev_y = self.y

        # Stats
        self.max_energy = org_config["org_stats"]["max_energy"]
        self.energy = self.max_energy / 2
        self.max_food = org_config["org_stats"]["max_food"]
        self.food = self.max_food / 2
        self.max_water = org_config["org_stats"]["max_water"]
        self.water = self.max_water / 2

        # Movement
        self.angle = angle          # in radiant weil die meisten Mathematischen Funktionen radiant erwarten
        self.max_speed = org_config["org_stats"]["max_speed"]
        self.speed = 0.0
        self.max_turn_speed = math.radians(org_config["org_stats"]["max_turn_speed"])
        self.turn_speed = 0.0

        # Vision
        self.vision_level = org_config["org_stats"]["vision_level"]
        self.set_vision()

        # Terrain
        self.environment = environment
        self.terrain = environment.terrain
        self.bushes = self.get_bushes()

        # NEAT
        self.net = None
        self.genome = None
        self.mate_range = org_config["org_stats"]["mate_range"]
        self.parentID_1 = None
        self.parentID_2 = None
        self.mate_cooldown_max = org_config["org_stats"]["mate_cooldown_max"]
        self.mate_cooldown = 0
        self.reproduction_cost = org_config["org_stats"]["reproduction_cost"]
        self.fitness_signal = 0.0

        # Metabolism
        self.food_consumption = org_config["sim_stats"]["food_consumption"]
        self.water_consumption = org_config["sim_stats"]["water_consumption"]
        self.food_ok = org_config["sim_stats"]["food_threshold"]
        self.water_ok = org_config["sim_stats"]["water_threshold"]
        self.energy_gain = org_config["sim_stats"]["energy"]["std_gain"]
        self.energy_loss = org_config["sim_stats"]["energy"]["std_loss"]
        self.movement_loss_factor = org_config["sim_stats"]["energy"]["movement_loss_factor"]

        # Maybe
        self.size = 1
        self.age = None
        self.agingSpeed = None
        self.mutationRate = None
        self.layTime = None
        self.hatchTime = None
        self.acceleration = 0.2

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
        max_fov = math.radians(300)
        min_fov = math.radians(60)

        max_range = 30.0
        min_range = 10.0

        # Berechnung
        self.vision_fov = self.lerp(max_fov, min_fov, self.vision_level)
        self.vision_range = self.lerp(min_range, max_range, self.vision_level)
        self.vision_area = 0.5 * (self.vision_range ** 2) * self.vision_fov     #BUG schauen wegen der Formel

    def seen_objects(self):
        """
        Findet alle Objekte(Wasser, Food) im Sichtfeld des Organismus.
        Gibt ein Dict mit 'food', 'water' zurück.
        """
        #NOTE maybe visible_water, etc. als Attribut machen
        visible_food = []
        visible_water = []
        #visible_tiles = []         wäre zur Visualisierung von dem Sichtfeld
        half_fov = self.vision_fov / 2  # halber Sichtwinkel

        height = len(self.terrain)
        width = len(self.terrain[0])

        # --< FOOD + WATER >--
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
                    elif isinstance(tile["object"], Bush) == True:
                        visible_food.append((x, y))
                    #visible_tiles.append((x, y))               wäre zur Visualisierung von dem Sichtfeld

        visible_organisms = []
        # --< ORGANISMS >--
        for other in self.environment.organisms:
            if other is self:
                continue  # sich selbst ignorieren

            dx = other.x - self.x
            dy = other.y - self.y
            distance = math.hypot(dx, dy)

            if distance > self.vision_range:
                continue

            angle_to_other = math.atan2(dy, dx)
            angle_diff = self.normalize_angle(angle_to_other - self.angle)

            if abs(angle_diff) <= half_fov:
                visible_organisms.append((other.x, other.y, other))

        return {
            "food": visible_food,
            "water": visible_water,
            "organisms": visible_organisms
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

    def metabolism(self):
        """
        Standard Wasser | Food | Energie Kosten pro Tick.
        - Wenn Food und Wasser über 20% ihrer Maximalwerte liegen, bekommt der Organismus Energie.
        - Wenn eines unter 20% liegt, bekommt er keine Energie.
        - Zusätzlich werden Food und Wasser leicht reduziert, um Verbrauch zu simulieren.
        """
        # Ressourcen reduzieren
        self.food = max(0.0, self.food - self.food_consumption)
        self.water = max(0.0, self.water - self.water_consumption)

        if self.food > self.food_ok and self.water > self.water_ok:
            self.energy = min(self.max_energy, self.energy + self.energy_gain)
        else:
            pass

        # Fixer verbrauch
        self.energy = max(0, self.energy - self.energy_loss)

    def move(self):
        """
        turn + throttle werden angewandt
        """
        self.prev_x = self.x
        self.prev_y = self.y
        height = len(self.terrain)
        width = len(self.terrain[0])

        # Bewegungsvektor
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # der Organismus muss innerhalb 0 und width - 1e-6 bleiben
        self.x = max(0, min(self.x, width - 1e-6))  # Gültiger Bereich zum Moven 0-99.999...
        self.y = max(0, min(self.y, height - 1e-6))

        # Getravelte Distanz berechnen
        distance = math.hypot(self.x - self.prev_x, self.y - self.prev_y)

        # Energieverlust proportional zur tatsächlichen Distanz
        self.energy -= distance * self.movement_loss_factor

    def apply_nn_output(self, output):
        """
        turn[-1...1]
        throttle[0...1]
        eat_signal[0 | 1]       True > 0
        drink_signal[0 | 1]     True > 0
        mate_signal[0 | 1]      True > 0
        """
        #TODO negatives Reward wenn der Organismus signale auf 1 stellt die nicht gehen
        turn, throttle, eat_signal, drink_signal, mate_signal = output
        reward = 0.0

        # Normalisierung, da alle Outputs tanh sind, muss ich manuell Normalisieren
        throttle = (throttle + 1) / 2       # Normalisiert auf [0...1]
        self.speed = throttle * self.max_speed

        # Winkelsteuerung
        self.angle += turn * self.max_turn_speed
        self.angle = self.normalize_angle(self.angle)

        self.move()

        # Trinken
        if drink_signal > 0.5:
            if self.is_on_water():
                self.water = min(self.max_water, self.water + 50)
                reward += 4.0
            else:
                reward -= 1.0

        # Essen
        if eat_signal > 0.5:
            eaten = False
            # Wenn in der Nähe, Esse
            for bush in self.bushes:
                if abs(bush.x - self.x) < 1 and abs(bush.y - self.y) < 1:
                    harvested = bush.harvest()
                    self.food = min(self.max_food, self.food + (harvested * bush.nutrition))
                    eaten = True
                    reward += 5.0
                    break

            if not eaten:
                reward -= 1.0

        if mate_signal > 0.5:
            self.energy -= 0.5      #BUG da noch konkrete Werte finden, wenn maten was kostet dann lernen sies besser

            if self.org_can_mate():
                self.want_mate = True
                reward += 1.0
            else:
                self.want_mate = False
                reward -= 1.0
        else:
            self.want_mate = False

        # Metabolismus
        self.metabolism()

        # 1. Überleben
        reward += 0.1

        # 2. Ressourcenlevel
        reward += 0.5 * (self.energy / self.max_energy)
        reward += 0.3 * (self.food / self.max_food)
        reward += 0.3 * (self.water / self.max_water)

        # 4. Sichtbare Ressourcen belohnen
        seen = self.seen_objects()

        #BUG wie viel bekomt man da ungefähr...?, ergänzen um Orgs. maybe wegmachen
        if seen["food"]:
            dist_food, _ = self.get_closest(seen["food"])
            reward += (self.vision_range - dist_food) / self.vision_range
        if seen["water"]:
            dist_water, _ = self.get_closest(seen["water"])
            reward += (self.vision_range - dist_water) / self.vision_range

        return reward

    def get_inputs(self):
        """
        Liefert eine normalisierte Liste an Sensorwerten für das neuronale Netz
        - Hungriness[0...1]                 =>  food / max_food
        - Thirstiness[0...1]                =>  water / max_water
        - Energiness[0...1]                 =>  energy / max_energy
        - curr_Speediness[0...1]            =>  speed / max_speed
        - abs_angle[-1...1]                 =>  angle / pi
        - turn_Speed[0...1]                 =>  turn_speed / max_turn_speed
        - can_mate[0 | 1]                   =>  can_mate
        --------------------------
        - Distance to closest Bush[0...1]   =>  distance / range
        - Angle to closest Bush[-1...1]     =>  angle / pi
        - Amount of seen Bushes[0...1]      =>  seen_bushes / range
        - Distance to closest Water[0...1]  =>  distance / range
        - Angle to closest Water[-1...1]    =>  angle / pi
        - Amount of seen Water[0...1]       =>  seen_water / range
        - Distance to closest Org[0...1]    =>  org / range
        - Angle to closest Org[-1...1]      =>  angle / pi
        - Amount of seen Orgs[0...1]        =>  seen_org / range
        """
        #NOTE maybe besserer Name für Energiness
        #NOTE Amount seen vielleicht logarithmisch machen damit 30 oder 31 wasser egal ist idk
        seen = self.seen_objects()

        # Stats
        hungry = self.food / self.max_food
        thirsty = self.water / self.max_water
        energy = self.energy / self.max_energy
        speed_input = self.speed / self.max_speed
        #angle_input = self.angle / math.pi                     kann entfallen weil schon werte für Resourcen
        turn_input = self.turn_speed / self.max_turn_speed

        # Nähestes Food suchen
        if seen["food"]:
            dist_food, angle_food = self.get_closest(seen["food"])
            #dist_food_norm = dist_food / self.vision_range
            dist_food_norm = min(math.log1p(dist_food) / math.log1p(self.vision_range), 1.0)    # Log für weniger Unterschied auf große Distanzen
            angle_food_norm = angle_food / math.pi
        else:
            dist_food_norm = 1.0  # nichts gesehen => maximale Distanz
            angle_food_norm = 0.0

        # Nähestes Wasser suchen
        if seen["water"]:
            dist_water, angle_water = self.get_closest(seen["water"])
            #dist_water_norm = dist_water / self.vision_range
            dist_water_norm = min(math.log1p(dist_water) / math.log1p(self.vision_range), 1.0)
            angle_water_norm = angle_water / math.pi
        else:
            dist_water_norm = 1.0
            angle_water_norm = 0.0

        # Näheste Orgs suchen
        if seen["organisms"]:
            dist_org, angle_org = self.get_closest([(x, y) for x, y, _ in seen["organisms"]])
            #dist_org_norm = dist_org / self.vision_range
            dist_org_norm = min(math.log1p(dist_org) / math.log1p(self.vision_range), 1.0)
            angle_org_norm = angle_org / math.pi
        else:
            dist_org_norm = 1.0
            angle_org_norm = 0.0

        if self.org_can_mate():
            can_mate = 1.0
        else:
            can_mate = 0.0

        return [
            # Generell
            hungry,
            thirsty,
            energy,
            speed_input,
            #angle_input,
            turn_input,
            can_mate,
            # Food
            dist_food_norm,
            angle_food_norm,
            # Water
            dist_water_norm,
            angle_water_norm,
            # Orgs
            dist_org_norm,
            angle_org_norm
        ]

    def org_can_mate(self):
        """
        Prüft ob Organismus bereit zur Fortpflanzung ist
        """
        #NOTE Maten braucht irgendeinen Cooldown hätt ich gesagt
        return (
            self.energy >= 0.3 * self.max_energy and
            self.mate_cooldown == 0
        )

    def try_mate(self, partner):
        """
        Versucht sich mit einem Partner zu paaren.
        Gibt True zurück wenn Bedingungen erfüllt sind.
        """
        if partner is self: #prob. redundant
            return False

        if not self.org_can_mate() or not partner.org_can_mate():
            return False

        """
        #TODO Später Speziation beachten
        if self.species_id != partner.species_id:
            return False
        """

        # Distanz prüfen
        dx = partner.x - self.x
        dy = partner.y - self.y
        dist = math.hypot(dx, dy)

        if dist > self.mate_range:
            return False

        """
        # probability für Selektion
        f1 = max(0.0, self.genome.fitness)
        f2 = max(0.0, partner.genome.fitness)

        mating_prob = math.log1p(f1 + f2) / 5.0  # Skalierung anpassen
        mating_prob = min(1.0, mating_prob)

        # 0.0 -> 1.0
        if random.random() > mating_prob:
            return False
        """

        return True

    def try_find_mate(self):
        if not self.want_mate:
            return None

        seen = self.seen_objects()

        for x, y, partner in seen["organisms"]:
            if self.try_mate(partner):
                return partner

        return None

    def to_dict(self):
        """Return JSON-serializable dictionary of the organism"""
        return {
            "id": self.id,
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "prev_x": round(self.prev_x, 2),
            "prev_y": round(self.prev_y, 2),
            "angle": round(self.angle, 2),
            "energy": {"current": round(self.energy, 2), "max": self.max_energy},
            "water": {"current": round(self.water, 2), "max": self.max_water},
            "food": {"current": round(self.food, 2), "max": self.max_food},
            "speed": {"current": round(self.speed, 2), "max": round(self.max_speed, 2)},
            "turn_speed": {"current": round(self.turn_speed, 2), "max": round(self.max_turn_speed)},
            "vision_range": round(self.vision_range, 2),
            "vision_fov": round(self.vision_fov, 2),
        }

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