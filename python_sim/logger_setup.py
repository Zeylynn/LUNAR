import logging
from datetime import datetime
import os

#TODO man kann einen File Handler benutzen um verschiedene Files in verschieden Logs zu leiten, brauch ich prob. nicht
#TODO Alte Logs archivieren maybe

"""
Logging sind prinzipiell nur für Informative Sachen z.B. für Fehler die zwar passieren aber nicht schlimm sind oder umgangen werden
Für Fehler einfach einen Fehler raisen()
CRITICAL - 50
ERROR - 40
WARNING - 30
INFO - 20
DEBUG - 10
"""
def get_logger(name = __name__, log_dir = "../logs"):
    """
    Gibt einen Logger zurück, der automatisch in eine Datei schreibt.
    - name: Name des Loggers (typischerweise __name__ des aufrufenden Moduls) => steht dann im Log File
    - log_dir: Verzeichnis für die Logdatei
    """
    # Sicherstellen, dass das Log-Verzeichnis existiert, wenn es es gibt kommt kein Fehler
    os.makedirs(log_dir, exist_ok=True)

    datum = datetime.now().strftime("%Y-%m-%d")
    log_name = f'{log_dir}/simulation_{datum}.log'  # Baut den Pfad auf

    # Das ist die Basis für alle logs
    logging.basicConfig(level=logging.DEBUG,
                        encoding='utf-8',
                        filename=log_name, # In welche Datei die Logs geschrieben werden
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Das ist der Aufbau im Log File

    logger = logging.getLogger(name)
    return logger

def test():
    logger = get_logger()
    logger.debug('This message should go to the log file')
    logger.info('So should this')
    logger.warning('And this, too')
    logger.error('And non-ASCII stuff, too, like Øresund and Malmö')
    logger.critical("Oh no :(, Error!")

test()