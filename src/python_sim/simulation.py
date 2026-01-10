from python_sim.environment import Environment
from python_sim.server_handler import ServerHandler
from python_sim.json_builder import JSONBuilder
import time
import python_sim.logger_setup as log

#TODO muss ich die Organismen erkennen lassen wie viel Essen pro Bush ist?
#TODO brauchen wir eine Lizenz?
#TODO Training läuft auf allen Kernen, Simulation nicht...
#TODO RNNs für Memeory => wo war Wasser, wo war Food
#TODO Such/Sortieralgorithmen mit bester Performance raussuchen => o(log(n))
#TODO funktion für cleanes beenden einbauen
#NOTE ich hab eine Framerate von 20, GoDot muss das dann auf 60 FPS interpolieren, die Framerate irgendwie anzeigen
#NOTE maybe Genom für über Wasser gehen, binäres Genom
#NOTE vielleicht eine Object Klasse als Basis für Organismen, Food mit .destroy() und Koordinaten usw.
#NOTE überlegen ob ich alle Attribute private oder so machen soll
#NOTE wie trainiere ich das Programm dann am KI-Server

logger = log.get_logger(__name__)

class Simulation:
    def __init__(self, config, nn=None):
        sim_config = config["simulation"]
        self.tick_rate = sim_config["tick_rate"]        # FPS
        self.tick_duration = 1 / self.tick_rate
        self.max_ticks = sim_config["max_ticks"]

        self.env = Environment(width=sim_config["width"],
                               height=sim_config["height"],
                               num_organisms=sim_config["num_organisms"],
                               num_bushes=sim_config["num_bushes"],
                               seed=sim_config["seed"])
        self.env.WorldGen.visualize()   #NOTE Remove Later

        self.nn = nn
        self.current_tick = 0

        self.builder = JSONBuilder()
        self.builder.build_terrain(self.env.terrain)

        self.server = ServerHandler(config["server"])
        self.server.create_socket()
        self.server.wait_for_client()                           #NOTE potentieller delay
        self.server.send_json(self.builder.json_terrain)        # Sendet das Terrain nur einmal, da es sich nie verändert

        logger.info("Simulation initialized")

    def run_tick(self):
        """
        Führt 1en Tick aus, beinhaltet
        - env.update()
        - printet jedes Organismus
        - printet jeden Busch
        """
        logger.debug(f"Tick {self.current_tick} running")
        self.env.update()

        # Organismen anzeigen
        for org in self.env.organisms:
            #logger.debug(org)
            print(org)

        # Ressourcen anzeigen
        for bush in self.env.bushes:
            #logger.debug(bush)
            print(bush)

        #NOTE Ist zwar ein NN für alle Organismen aber darüber muss ich mir später Gedanken machen
        if self.nn:
            for org in self.env.organisms:
                inputs = self.env.get_inputs(org)
                outputs = self.nn.activate(inputs)
                org.apply_nn_output(outputs)

        self.current_tick += 1

    def run(self):
        """Lässt {self.max_ticks} viele Ticks laufen mit fixer Tickrate"""
        logger.info(f"Simulation started | Max ticks: {self.max_ticks}")

        while self.current_tick < self.max_ticks:
            start_time = time.time()

            # GANZE SIMULATION IN DIESEM CODEBEREICH
            self.run_tick()

            # VERBINDUGN ZU GODOT
            self.builder.build_bushes(self.env.bushes)
            self.server.send_json(self.builder.json_bushes)

            self.builder.build_organisms(self.env.organisms)
            self.server.send_json(self.builder.json_organisms)
            #TODO maybe Schlusszeichen senden damit GoDot weiß wann Schluss ist
            
            # BERECHNUNG PERFORMANCE - FPS
            elapsed_time = time.time() - start_time
            sleep_time = max(0.0, self.tick_duration - elapsed_time)

            actual_fps = 1.0 / elapsed_time
            logger.debug(f"Tick {self.current_tick - 1} finished | duration={elapsed_time:.4f}s | effective FPS={actual_fps:.2f}")

            if sleep_time > 0.0:
                time.sleep(sleep_time)      #NOTE time.sleep() nicht ganz optimal, im Rahmen dieses Projektes ausreichend
            else:
                logger.warning(f"Tick {self.current_tick - 1} took longer ({elapsed_time:.4f}s) than expected tick duration ({self.tick_duration:.4f}s)")

        logger.info("Simulation finished")