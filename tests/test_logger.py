import python_sim.logger_setup as log

"""
Wenn man ein File mit Python ausführt ist __name__ vom ausgeführten File automatisch "__main__" auch wenn das File anders heißt
Wenn man ein Modul aber importiert ist __name__ vom importierten Modul der Name des Files, deswegen läuft der Code nur wenn DIESES File direkt ausgeführt wird
__file__ ist IMMER der absolute Pfad der Datei wo der Code AUSGEFÜHRT WIRD
    => d.h. wenn ich dieses File importiere und in der Funktion get_logger() __file__ ausgeführt wird ist das der abolute Pfad von logger_setup.py
"""
if __name__ == "__main__":
    logger = log.get_logger(__name__)
    logger.debug("This message should go to the log file")
    logger.info("So should this")
    logger.warning("And this, too")
    logger.error("And non-ASCII stuff, too, like Øresund and Malmö")
    logger.critical("Oh no :(, Error!")