#TODO config File auf Evolutionssimulator anpassen
#TODO Multithreading/auslagern auf verschieden Cores/GPU
#TODO implement Logger
#TODO maybe Genom für über Wasser gehen, binäres Genom

import random
from environment import Environment

class Simulation:
    def __init__(self, width=100, height=100, num_resources=4, num_organisms=2, max_ticks=100, seed=None):
        self.max_ticks = max_ticks
        self.current_tick = 0
        self.set_seed(seed)

        self.env = Environment(width=width, height=height, num_resources=num_resources, num_organisms=num_organisms, seed=seed)
        self.env.NoiseGen.visualize()   #TODO Remove Later

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

    def run_tick(self):
        """Führt einen einzigen Tick aus"""
        self.env.update()
        print(f"Tick {self.current_tick} has passed!")

        # Organismen anzeigen
        for org in self.env.organisms:
            print(org)
            print(f"Organismus ist auf Wasser: {org.is_on_water(self.env.terrain)}")

        # Ressourcen anzeigen
        for res in self.env.resources:
            print(res)

        self.current_tick += 1

    def run(self):
        """Lässt soviele Ticks laufen wie self.max_ticks groß ist"""
        print("Simulation Runs!")
        while self.current_tick < self.max_ticks:
            self.run_tick()
            input("Press <SOMETHING> to continue")

sim = Simulation(width=100, height=100, num_resources=2, num_organisms=1, max_ticks=100, seed=-100)
sim.run()