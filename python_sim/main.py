#TODO merge beide .gitignores(maybe)?
#TODO config File auf Evolutionssimulator anpassen

from environment import Environment

def main():
    env = Environment(width=500, height=500, num_resources=50, num_organisms=10)
    for tick in range(10):
        env.update()
        print(f"Tick {tick} has passed!")

