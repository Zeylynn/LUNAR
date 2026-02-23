from python_sim.world_generator import WorldGenerator
from python_sim.state_builder import StateBuilder
import random
import json

#TODO Unittests mit pytest

seed = random.randint(-9999, 500)

world = WorldGenerator(world_width=10, world_height=10, seed=seed, num_bushes=10)
world.init_world()
terrain = world.get_terrain()

builder = StateBuilder()
builder.build_terrain(terrain=terrain)

print(json.dumps(builder.terrain))