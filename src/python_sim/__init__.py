"""
-- Generell --
wenn in einem Folder das __init__.py ist kann der Folder als Paket importiert werden
=> PEP 420 lässt es zu das wegzulassen, aber ist gute Praxis das zu lassen
Python kann Module NUR importieren wenn das Parent Verzeichniss in sys.path ist

Ich brauch eig. ned requirements.txt & pyproject.toml
wenn ich mit -m runne ist alles was ich ausfürhe ein Paket und braucht eine __init__.py

-- Ausführen --
root> python scripts\main.py => geht nicht weil Python dann sys.path auf "C:\...\LUNAR\scripts\" setzt, 
dann sucht es bei imports nach "C:\...\LUNAR\scripts\python_sim\"

root> python -m scripts.main => geht
-m      LUNAR ist Projekt root => sys.path = "C:\...\LUNAR\"

Wenn man mit -m runnt müssen alle relativen imports auf absolute geändert werden
import logger as log            => Falsch
import python_sim.logger as log => Richtig

-- Paket Installiert --
root> pip install -e .
-e      installiert mit Verweis auf die Files => gut für Development
.       vom aktuellen Ornder = LUNAR

Nur neu installieren wenn ich pyproject.toml ändere
Installiert den Ordner als Library => kann dann von überall ohne aufgerufen werden ohne frickeleien mit sys.path
Installiert dann via. pyproject.toml => PEP518

Alles vom Paket installieren:
import logger as log            => Falsch
import python_sim.logger as log => Richtig

Für Unittests verwendet man pytest
=> NAMING: root/tests/test_core.py

Mit einer src/-Struktur liegt dein Paketcode in einem Unterordner (src/python_sim oder src/lunar/python_sim), 
getrennt vom Projekt-Root. Dadurch verhindern Editable-Installs, 
dass Python versehentlich alte oder lokale Dateien im Root importiert, 
und garantieren, dass Tests, Skripte und IDEs immer die „richtige“ Package-Version aus dem installierten Pfad sehen
"""