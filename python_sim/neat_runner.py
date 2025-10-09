# neat_runner.py
import neat
import random
from environment import Environment
from organism import Organism

WIDTH, HEIGHT = 500, 500

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        env = Environment(WIDTH, HEIGHT)
        org = Organism(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        fitness = 0

        for _ in range(50):  # simulation steps
            food = env.get_closest_food(org)
            # Normalize inputs to 0..1
            inputs = [
                (food[0] - org.x)/WIDTH,
                (food[1] - org.y)/HEIGHT,
                org.energy/100
            ]
            output = net.activate(inputs)
            # output[0] -> dx, output[1] -> dy
            org.move(output[0]*5, output[1]*5, WIDTH, HEIGHT)

            # Simple fitness: closer to food is better
            dist = org.distance_to_food(food)
            fitness += max(0, 10 - dist)  # the closer, the higher

        genome.fitness = fitness

def run(config_file):
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file
    )

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    winner = p.run(eval_genomes, 10)  # run 10 generations
    print("Best genome:", winner)

if __name__ == "__main__":
    run("config-feedforward.txt")
