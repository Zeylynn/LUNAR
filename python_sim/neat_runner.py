import neat
from environment import Environment
from organism import Organism

def eval_genomes(genomes, config):
    """
    Bewertet jedes Genom in der Population anhand seiner Performance im Environment.
    """
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        env = Environment(width=100, height=100, num_resources=10, num_organisms=0)
        organism = Organism(
            x=50, y=50, angle=0, speed=5, vision_level=0.5, terrain=env.terrain
        )

        fitness = 0
        for _ in range(500):  # Simulationsschritte
            inputs = env.get_inputs(organism)
            outputs = net.activate(inputs)
            organism.apply_nn_output(outputs, env)
            env.update()

            # Wenn tot → abbrechen
            if organism.energy <= 0:
                break

            # Fitness = Energie + Entfernung zu Food
            seen = organism.seen_resources()
            fitness += organism.energy * 0.01 + len(seen["food"]) * 0.1

        genome.fitness = fitness

def run_neat(config_path):
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(eval_genomes, n=50)

    print("\n🏆 Beste Fitness:", winner.fitness)
    print("Simulation abgeschlossen!")