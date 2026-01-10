from python_sim.world_generator import WorldGenerator
from python_sim.json_builder import JSONBuilder
import random

#TODO Unittests mit pytest

seed = random.randint(-9999, 500)

world = WorldGenerator(world_width=10, world_height=10, seed=seed, num_bushes=10)
world.init_world()
terrain = world.get_terrain()

builder = JSONBuilder()
builder.build_terrain(terrain=terrain)

print(builder.json_terrain)