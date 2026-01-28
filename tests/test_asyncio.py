import time
import asyncio

async def count():          # async macht die Funktion zu einer coroutine function, runnt nur im Event Loop
    print("One")            # await: gibt Kontrolle zurück an event loop bis der Command halt ausgeführt wird
    await asyncio.sleep(1)      # wartet meistens auf Meldung vom OS das der Task weiter gemacht werden kann, wenn die Ressourcen da sind
    print("Two")
    await asyncio.sleep(1)

"""
async def g():
    result = await f()  # Pause and come back to g() when f() returns
    return result
"""

async def main():
    await asyncio.gather(count(), count(), count()) # führt alles was da drin ist concurrently aus

if __name__ == "__main__":
    start = time.perf_counter()
    asyncio.run(main())     # .run launched den event loop, und führt main aus. NUR 1x pro Programm ist empfohlen(in main halt)
    elapsed = time.perf_counter() - start
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")