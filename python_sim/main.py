from environment import Environment
from server_handler import ServerHandler
from json_builder import JSONBuilder
import time
import logger_setup as log
import os
import neat_runner as neat_run
import neat         #TODO das kann ich entfernen wenn ich die config in neat_runner auslagere

#TODO brauchen wir eine Lizenz?
#TODO Training läuft auf allen Kernen, Simulation nicht...
#TODO RNNs für Memeory => wo war Wasser, wo war Food
#TODO Such/Sortieralgorithmen mit bester Performance raussuchen => o(log(n))
#NOTE ich hab eine Framerate von 20, GoDot muss das dann auf 60 FPS interpolieren, die Framerate irgendwie anzeigen
#NOTE maybe Genom für über Wasser gehen, binäres Genom
#NOTE vielleicht eine Object Klasse als Basis für Organismen, Food mit .destroy() und Koordinaten usw.
#NOTE überlegen ob ich alle Attribute private oder so machen soll
#NOTE wie trainiere ich das Programm dann am KI-Server

TICK_RATE = 20                      # FPS
TICK_DURATION = 1 / TICK_RATE

logger = log.get_logger(__name__)

class Simulation:
    def __init__(self, width=100, height=100, num_organisms=50, num_bushes=100, max_ticks=100, seed=None, nn=None):
        self.max_ticks = max_ticks
        self.current_tick = 0
        self.nn = nn                    #NOTE Optional, später dann für Fertigtrainierte Modelle zum übergeben

        self.env = Environment(width=width, height=height, num_organisms=num_organisms, num_bushes=num_bushes, seed=seed)
        self.env.WorldGen.visualize()   #NOTE Remove Later

        self.builder = JSONBuilder()
        self.builder.build_terrain(self.env.terrain)

        self.server = ServerHandler(host="127.0.0.1", port=9001)
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

        #NOTE Wenn trainiertes NN übergeben wurde, anwenden. Ist zwar ein NN für alle Organismen aber darüber muss ich mir später Gedanken machen
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
            sleep_time = max(0.0, TICK_DURATION - elapsed_time)

            actual_fps = 1.0 / elapsed_time
            logger.debug(f"Tick {self.current_tick} finished | duration={elapsed_time:.4f}s | effective FPS={actual_fps:.2f}")

            if sleep_time > 0.0:
                time.sleep(sleep_time)      #NOTE time.sleep() nicht ganz optimal, im Rahmen dieses Projektes ausreichend
            else:
                logger.warning(f"Tick {self.current_tick} took longer ({elapsed_time:.4f}s) than expected tick duration ({TICK_DURATION:.4f}s)")

        logger.info("Simulation finished")

"""
wird benötigt weil Windows neue Prozesse/Multiprocessing via Spawn erstellt.
Spawn importiert beim ERSTELLEN des neuen Prozesses alle Module und führt danach das Hauptskript aus.
d.h. dass alles ohne if __name__ == "__main__" doppelt ausgeführt wird. Dadurch wird der pool von Parallel Evaluator fehlerhaft gesetzt => Error
"""
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config")

    winner_genome = neat_run.run_neat(config_path=config_path)

    #FIXME das via Neat Runner machen
    winner_nn = neat.nn.FeedForwardNetwork.create(winner_genome, neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    ))

    sim = Simulation(nn=winner_nn)
    sim.run()