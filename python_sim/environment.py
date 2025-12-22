from organism import Organism
from world_generator import WorldGenerator
import random
import math
import logger_setup as log
import copy

logger = log.get_logger(__name__)

class Environment:
    def __init__(self, width, height, num_organisms, num_bushes, seed):
        # ATTRIBUTE
        self.width = width
        self.height = height
        self.set_seed(seed)
        self.num_bushes = num_bushes

        self.organisms = []
        self.bushes = None

        #NOTE maybe Threshold einstellbar machen idk, für World Gen Relevant
        self.WorldGen = WorldGenerator(world_width=self.width, world_height=self.height, seed=self.seed, num_bushes=num_bushes, threshold=-0.15)
        self.WorldGen.init_world()
        self.terrain = self.WorldGen.get_terrain()

        self.bushes = self.WorldGen.get_bushes()
        self.organisms = self.add_organisms(num_organisms)
        
        logger.info(f"Environment initialized | {num_organisms} Organisms | {num_bushes} Bushes")

    def add_organisms(self, amount):
        """
        Erstellt {amount} viele Organismen, fügt erstellte Organims self.organisms hinzu, gibt erstellte Organisms zurück
        - Jedes Attribut wird zufällig zugewiesen
        - Organismen können nicht auf Wasser generieren
        """
        ret_organisms = []
        for _ in range(amount):
            while True:
                x = random.uniform(0, self.width)   # Exkludiert self.width deswegen ist die Spawnrange 0-99.999...
                y = random.uniform(0, self.height)

                # auf Tiles Runden
                grid_x = int(x)
                grid_y = int(y)

                # Bricht die Schleife ab wenn auf Land gespawnt ist
                if self.terrain[grid_y][grid_x]["terrain"] == 1:
                    break
            
            angle = random.uniform(-math.pi, math.pi)
            max_speed = random.uniform(1, 3)
            max_turn_speed = math.radians(10)       # max. 10° pro Tick
            vision_level = random.uniform(0, 1)

            organism = Organism(x, y, angle, max_speed, max_turn_speed, vision_level, self.terrain)
            self.organisms.append(organism)
            ret_organisms.append(organism)

        return ret_organisms

    def set_seed(self, seed):
        """
        Setzt die variable self.seed
        - Verhindert, dass ein Seed gesetzt wird der außerhalb des nutzbaren Bereichs(-9999, 500) liegt
        - Falls seed=None wird ein zufälliger seed gesetzt
        """
        if seed == None:
            self.seed = random.randint(-9999, 500)
        elif seed < 500 and seed > -9999:
            self.seed = seed
        else:
            raise ValueError("seed ist out of usable range! Usable range is -9999 to 500!")
        logger.debug(f"Seed set as: {self.seed}")

    def get_inputs(self, organism):
        """
        Liefert eine normalisierte Liste an Sensorwerten für das neuronale Netz
        - Hungriness[0...1]                 =>  food / max_food
        - Thirstiness[0...1]                =>  water / max_water
        - Energiness[0...1]                 =>  energy / max_energy
        - curr_Speediness[0...1]            =>  speed / max_speed
        - abs_angle[-1...1]                 =>  angle / pi
        - turn_Speed[0...1]                 =>  turn_speed / max_turn_speed
        --------------------------
        - Distance to closest Bush[0...1]   =>  distance / range
        - Angle to closest Bush[-1...1]     =>  angle / pi
        - Amount of seen Bushes[0...1]      =>  seen_bushes / range
        - Distance to closest Water[0...1]  =>  distance / range
        - Angle to closest Water[-1...1]    =>  angle / pi
        - Amount of seen Water[0...1]       =>  seen_water / range
        """
        #FIXME Healthiness Später implementieren, config File Inputs anpassen           - Healthiness[0...1]        =>  health / max_health
        #NOTE maybe besserer Name für Energiness
        #NOTE Amount seen vielleicht logarithmisch machen damit 30 oder 31 wasser egal ist idk
        seen = organism.seen_objects()

        # Stats
        hungry = organism.food / organism.max_food
        thirsty = organism.water / organism.max_water
        energy = organism.energy / organism.max_energy
        speed_input = organism.speed / organism.max_speed
        angle_input = organism.angle / math.pi
        turn_input = organism.turn_speed / organism.max_turn_speed

        # Nähestes Food suchen
        if seen["food"]:
            dist_food, angle_food = organism.get_closest(seen["food"])
            dist_food_norm = dist_food / organism.vision_range
            angle_food_norm = angle_food / math.pi
            amount_food = min(len(seen["food"]) / organism.vision_area, 1.0)
        else:
            dist_food_norm = 1.0  # nichts gesehen => maximale Distanz
            angle_food_norm = 0.0
            amount_food = 0.0

        # Nähestes Wasser suchen
        if seen["water"]:
            dist_water, angle_water = organism.get_closest(seen["water"])
            dist_water_norm = dist_water / organism.vision_range
            angle_water_norm = angle_water / math.pi
            amount_water = min(len(seen["water"]) / organism.vision_area, 1.0)
        else:
            dist_water_norm = 1.0
            angle_water_norm = 0.0
            amount_water = 0.0

        return [
            hungry,
            thirsty,
            energy,
            speed_input,
            angle_input,
            turn_input,
            dist_food_norm,
            angle_food_norm,
            amount_food,
            dist_water_norm,
            angle_water_norm,
            amount_water
        ]

    def update(self):
        """
        Iteriert durch jedes
        - Bush-Obj und führt .update() aus => lässt Food nachwachsen
        """
        for bush in self.bushes:
            bush.update()

    def create_copy(self):
        """
        Erstellt eine frische Kopie für Simulation eines Genoms
        __new__ ist verantwrotlich eine neue Instanz/Objekt zu erstellen => wird vor __init__ aufgerufen
        __init__ dafür Attribute zu setzen
        Der Vorteil ist dass Python beim erstellen via __new__ NICHT autmoatisch __init__ aufruft
        """
        env_copy = Environment.__new__(Environment)     # bypass __init__
        env_copy.width = self.width
        env_copy.height = self.height
        env_copy.seed = self.seed
        env_copy.terrain = self.terrain.copy()          # array1 = arry2 erstellt keine Kopie sondern eine Referenz, array  = array.copy() schon

        env_copy.bushes = []
        #NOTE wenn du nix anderes zu tun hast, kannst du schauen ob das nicht anders geht
        for bush in self.bushes:
            env_copy.bushes.append(copy.deepcopy(bush))         # obj1 = obj2 erstellt keine Kopie sondern eine Referenz, obj  = obj.copy() schon

        env_copy.organisms = []

        return env_copy