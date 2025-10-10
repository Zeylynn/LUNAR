#TODO merge beide .gitignores(maybe)?
#TODO config File auf Evolutionssimulator anpassen
#TODO maybe Klasse für main Loop machen
#TODO nicht im ersten Tick schon moven. Im ersten Tick alles initen, im 2. dann "simulieren" => Init und update methoden
#TODO maybe Log File statt Debug Prints

from environment import Environment

def main():
    env = Environment(width=100, height=100, num_resources=4, num_organisms=2)
    for tick in range(100):
        env.update()

        for org in env.organisms:
            print(org)

        for res in env.resources:
            print(res)

        print(f"Tick {tick} has passed!")
        input("Press <SOMETHING> to continue")

main()