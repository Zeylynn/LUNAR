import multiprocessing as mp
import time

#NOTE was ist ein Global Interpreter Lock(GIL)?
#NOTE jedes Python Programm ist ein Prozess mit einem Thread(main thread)

# Neue Prozesse erstellen mit fork/spawn => Win => spawn(neuer Python Interpreter, neu importieren, Nur explizit übergebene Sachen sind enthalten, keine Speicher teilung)
    # Deswegen if __nam__ == "__main__" Guard
# Der Prozess KANN NUR DANN terminieren wenn alle non-daemon Threads im Prozess terminiert sind, und all non-daemon Kind Prozesse terminiert sind
# Child Process = ist von einem anderen Process erstellt
# Daemon ist ein Background Process
"""
Tipps:
1) Contextmanager = with usen
2) Timeouts beim warten benutzen
3) entry points securen
4) beim sharen von Daten wenns einfach geht
- mp.Value
- mp.Array
hernehmen
5) bei komplexeren Sachen Pipes(Verbindung zwischen 2 Prozessen), schickt pickable Python Objekte
- con1, con2 = mp.Pipe()
- con2.send("Hi :3 Nya")    => pickled
- con3.recv()               => automatisch unpickled
-- Queues --
Datenstruktur wo man Daten hinzufügen und entnehmen kann. First-in First-Out
- queue = mp.Queue()
- queue.put(item)
- item = queue.get()

# Das würde auf alle Prozesse warten
for process in processes:
    process.join()

"""

def task(sleep, msg, lock):
    # with released Lock automatisch, sonst muss man manuell releasen
    with lock:
        time.sleep(sleep)
        print(f"This is from another Process: {msg}")

if __name__ == "__main__":
    mp.set_start_method('spawn')    # Vor allem anderen setzen, nur 1x pro Programm
    lock = mp.Lock()                # verhindern dass mehrere gleichzeitig auf kritische Teile Zugreifen, es gibt einen Lock auf alle Processes
    num_cores = mp.cpu_count()
    event = mp.Event()              # Basically ein shared bool über alle Prozesse. "set" = True, "not set" = False
    if event.is_set():
        print("Do smth")
        event.set()
        event.clear()
        event.wait(timeout=10)
    process = mp.Process(target=task, args=(1.5, "Das Crazy!"), name="NEATController")
    process.start()     # Startet den Prozess, startet main Thread. Runnt .run() intern
    print("Waiting for Process")
    process.join()  # Wartet bis der Kind Prozess fertig ist

"""
class CustomProcess(mp.Process):
    def __init__(self, group = None, target = None, name = None, args = ..., kwargs = ..., *, daemon = None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)

    def run():
        time.sleep(1)
        print("Einfach überschrieben lol")
"""