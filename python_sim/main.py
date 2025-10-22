from environment import Environment
import logger_setup as log

#TODO config File auf Evolutionssimulator anpassen
#TODO Multithreading/auslagern auf verschieden Cores/GPU
#NOTE maybe Genom für über Wasser gehen, binäres Genom
#NOTE vielleicht eine Object Klasse als Basis für Organismen, Food mit .destroy() und Koordinaten usw.
#NOTE überlegen ob ich alle Attribute private oder so machen soll
#NOTE wie trainiere ich das Programm dann am KI-Server

logger = log.get_logger(__name__)

class Simulation:
    def __init__(self, width=100, height=100, num_organisms=2, num_bushes=5, max_ticks=100, seed=None):
        self.max_ticks = max_ticks
        self.current_tick = 0

        self.env = Environment(width=width, height=height, num_organisms=num_organisms, num_bushes=num_bushes, seed=seed)
        self.env.WorldGen.visualize()   #NOTE Remove Later

        logger.info("Simulation initialized")

    def run_tick(self):
        """
        Führt 1en Tick aus, beinhaltet
        - env.update()
        - printet jedes Organismus
        - printet jeden Busch
        """
        self.env.update()
        logger.debug(f"Tick {self.current_tick} is currently running")

        # Organismen anzeigen
        for org in self.env.organisms:
            print(org)

        # Ressourcen anzeigen
        for bush in self.env.bushes:
            print(bush)

        self.current_tick += 1

    def run(self):
        """Lässt {self.max_ticks} viele Ticks laufen"""
        logger.info("Simulation is running")
        while self.current_tick < self.max_ticks:
            self.run_tick()
            input("Press <SOMETHING> to continue")

sim = Simulation()
sim.run()