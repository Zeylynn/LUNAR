import logging
from datetime import datetime
import os

# GENERELL zu imports: Python, wenn man importiert NUR beim ersten Import egal in welchem File den Code ausführt, weil es danach das File das importiert wird zwischenspeichert.

#TODO Verschiedene Logs für Organismen / Simulation maybe?
#TODO Jeder Log in einem eigenen File, alte Logs archivieren

"""
Logging sind prinzipiell nur für Informative Sachen z.B. für Fehler die zwar passieren aber nicht schlimm genug sind die Anwendung zu unterbrechen
oder für Fehler die umgangen werden, Für Kritische Fehler einfach => raise Error()
---
CRITICAL - 50
ERROR - 40
WARNING - 30
INFO - 20
DEBUG - 10

Logger:
Prinzipiell kann ich unendlich viele Logger machen, sie müssen nur einen eigenen Namen haben. getLogger(name) => gibt mir den Logger zurück, wenn
es de Logger mit diesem Namen schon gibt
Jeder Logger kann auch Prinzipiell undendlich viele Handler haben.
"""
# def get_logger(name = __name__) geht nicht, WEIL die Default-Argumente beim definieren der Funktion ausgewertet werden, NICHT bei jedem Aufruf
# => d.h. so würde jedes File sich als logger_Setup loggen, deswegen muss jedem logger __name__ bzw- __file__ übergeben werden
def get_logger(name):
    """
    Gibt einen Logger zurück, der automatisch in eine Datei schreibt.
    - name: Name des Loggers (typischerweise __name__ des aufrufenden Moduls) => steht dann im Log File
    """
    """
    !!WICHTIG!! VSCodes Ausführpfad ist weiß Gott wo => deswegen keine relativen Pfade benutzen
        => wenn man einen relativen Pfad benutzt wie z.B. ../logs wird ein logs Ordner dort angelegt wo VSCodes Standardordner liegt,
        der kann auch außerhalb der virtullen Umgebung liegen, es sieht dann so aus als wäre nicht gelogged worden aber der Ordner ist einfach im Nirvana
    Deswegen funktionieren relative Pfade beim logging wenn man sie im selben Verzeichniss mit Python ausführt und mit VSCode dann nicht
    logging.basicConfig ist in VSCode auch nicht zu empfehlen weil es NUR dann läuft wenn der Root-Logger noch keine Handler hat
        => wenn VSCode automatisch schon Handler einsetzt dann lädt die basic.Config nicht => bei mir würde es aber Funktionieren
    !!WICHTIG!! Absolute Pfade benutzen
    """
    # Baut den Pfad zum Log-Ordner auf und stellt sicher dass es existiert
    log_dir = "../logs"                                     # Relativ gesehen von logger_setup.py
    base_dir = os.path.dirname(os.path.abspath(__file__))   # Absoluter Pfad von logger_setup.py
    log_dir = os.path.join(base_dir, log_dir)               # absoluter Pfad zu logs => .join() berücksichtigt ../ etc.
    os.makedirs(log_dir, exist_ok=True)

    datum = datetime.now().strftime("%Y-%m-%d")
    log_name = os.path.join(log_dir, f"simulation_{datum}.log") # Erstellt den Log-File Namen

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Welche Messages die mind. ist die im Logging eingetragen wird

    # Falls diese Methode 2x mit demselben Logger-Namen aufgerufen wird, wird nicht noch ein FileHandler hinzugefügt
    if not logger.handlers:
        file_handler = logging.FileHandler(log_name, mode="a", encoding="utf-8")                              # Handeled wo das File hingespeichert wird, etc.
        formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')   # Handeled welche Formatierung die Log-Einträge haben soll, etc.
        file_handler.setFormatter(formatter)        # => %Filename => Immer der Name des Files, %name => im Endeffekt __name__
        logger.addHandler(file_handler)
    
    logger.propagate = True # verhindert doppeltes Logging an den root-Logger
    return logger

"""
Wenn man ein File mit Python ausführt ist __name__ vom ausgeführten File automatisch "__main__" auch wenn das File anders heißt
Wenn man ein Modul aber importiert ist __name__ vom importierten Modul der Name des Files, deswegen läuft der Code nur wenn DIESES File direkt ausgeführt wird
__file__ ist IMMER der absolute Pfad der Datei wo der Code AUSGEFÜHRT WIRD
    => d.h. wenn ich dieses File importiere und in der Funktion get_logger() __file__ ausgeführt wird ist das der abolute Pfad von logger_setup.py
"""
if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.debug("This message should go to the log file")
    logger.info("So should this")
    logger.warning("And this, too")
    logger.error("And non-ASCII stuff, too, like Øresund and Malmö")
    logger.critical("Oh no :(, Error!")