import random
from environment import Environment
import logger_setup as log

#TODO config File auf Evolutionssimulator anpassen
#TODO Multithreading/auslagern auf verschieden Cores/GPU
#TODO maybe Genom für über Wasser gehen, binäres Genom

logger = log.get_logger(__name__)

class Simulation:
    def __init__(self, width=100, height=100, num_resources=4, num_organisms=2, max_ticks=100, seed=None):
        self.max_ticks = max_ticks
        self.current_tick = 0
        self.set_seed(seed)

        self.env = Environment(width=width, height=height, num_resources=num_resources, num_organisms=num_organisms, seed=seed)
        self.env.NoiseGen.visualize()   #TODO Remove Later

        logger.info("Simulation initialized")

    def set_seed(self, seed):
        """
        Verhindert dass ein nicht nutzbarer Seed eingegeben wird,
        da die Funktion pnoise2 keine Fehlermeldung ausgibt wenn sie abstürzt
        Wenn kein Seed eingeben ist wird ein zufälliger generiert
        """
        if seed == None:
            self.seed = random.randint(-9999, 500)
        elif seed < 500 and seed > -9999:
            self.seed = seed
        else:
            raise ValueError('seed ist out of usable range! Usable range is -9999 to 500!')
        logger.debug(f"Seed set as: {seed}")

    def run_tick(self):
        """Führt einen einzigen Tick aus"""
        self.env.update()
        logger.debug(f"Tick {self.current_tick} is currently running")

        # Organismen anzeigen
        for org in self.env.organisms:
            print(org)

        # Ressourcen anzeigen
        for res in self.env.resources:
            print(res)

        self.current_tick += 1

    def run(self):
        """Lässt soviele Ticks laufen wie self.max_ticks groß ist"""
        logger.info("Simulation is running")
        while self.current_tick < self.max_ticks:
            self.run_tick()
            input("Press <SOMETHING> to continue")

sim = Simulation(width=100, height=100, num_resources=2, num_organisms=1, max_ticks=100, seed=-100)
sim.run()