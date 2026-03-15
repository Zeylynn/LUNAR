extends Node2D

# --- Referenzen (müssen im Editor zugewiesen oder benannt sein) ---
@onready var tilemap: TileMapLayer = $TileMapLayer
@onready var camera: Camera2D = $Camera2D

#  Szenen vorladen
var monster_scene = preload("res://Game/Monster.tscn")
var hud_scene = preload("res://HUD.tscn") # Stelle sicher, dass der Pfad stimmt!
var hud_instance: CanvasLayer

# Container für Monster, damit wir sie sauber löschen können
var monster_container: Node2D
var selected_monster_id: int = -1
@export var tick_rate: float = 1.0 

var spawned_monsters: Dictionary = {}

# --- Temporäre Busch-Variablen ---
var bush_container: Node2D
var spawned_bushes: Dictionary = {}

# --- Wir merken uns die Map-Grenzen ---
var map_width_tiles: float = 0.0
var map_height_tiles: float = 0.0

# --- Netzwerk Variablen ---
var socket = StreamPeerTCP.new()
var host = "127.0.0.1"
var port = 9001
var config_sent: bool = false 

# --- TileMap Konstanten ---
const TERRAIN_SET := 0
const TERRAIN_WATER := 0 # Entspricht 0 im JSON
const TERRAIN_LAND := 1  # Entspricht 1 im JSON
var TILE_SIZE: float = 32.0

var effective_tile_size: float = 32.0

# --- Globale Statistik-Variablen ---
var current_tick: int = 0
var total_births: int = 0
var total_deaths: int = 0
var current_population: int = 0

# --- Historie für die Graphen (speichert Vector2(tick, wert)) ---
var history_avg_food: Array[Vector2] = []
var history_avg_water: Array[Vector2] = []
var history_avg_speed: Array[Vector2] = []
var history_avg_lifetime: Array[Vector2] = []
var history_avg_energy: Array[Vector2] = []


func _ready():
	print("Starte Client...")
	
	if tilemap.tile_set != null:
		TILE_SIZE = float(tilemap.tile_set.tile_size.x)
		
	# --- IN DER _ready() FUNKTION HINZUFÜGEN ---
	bush_container = Node2D.new()
	add_child(bush_container)
	
	monster_container = Node2D.new()
	add_child(monster_container)
	
	# Sicherheitshalber die lokalen Werte nullen
	monster_container.position = Vector2.ZERO
	monster_container.scale = Vector2(1, 1)
	
	# HUD instanzieren und anzeigen
	hud_instance = hud_scene.instantiate()
	add_child(hud_instance)
	
	# Verbindung aufbauen
	var err = socket.connect_to_host(host, port)
	if err == OK:
		print("Verbinde zu ", host, ":", port)
	else:
		print("Fehler beim Verbinden: ", err)

func _process(_delta):
	socket.poll()
	var status = socket.get_status()
	
	if status == StreamPeerTCP.STATUS_CONNECTED:
		# Config direkt nach erfolgreichem Verbindungsaufbau senden
		if not config_sent:
			print("Verbindung steht! Sende Config...")
			send_command({
				"cmd": "config",
				"data": null
			})
			config_sent = true # Wichtig: Auf true setzen!

		var bytes_available = socket.get_available_bytes()
		if bytes_available > 0:
			var data = socket.get_data(bytes_available)
			
			if data[0] == OK:
				var message_text = data[1].get_string_from_utf8()
				process_message(message_text)
				
	elif status == StreamPeerTCP.STATUS_ERROR or status == StreamPeerTCP.STATUS_NONE:
		config_sent = false # Falls die Verbindung abbricht, setzen wir den Status zurück

# Funktion zum Senden von Befehlen an den Server
func send_command(data: Dictionary):
	# JSON.stringify macht aus einem Dictionary einen validen JSON-String
	var msg = JSON.stringify(data) + "\n"
	
	socket.put_data(msg.to_utf8_buffer())
	print("Server-Kommando gesendet: ", msg.strip_edges())

# Beim Schließen des Godot-Fensters den Server stoppen
func _exit_tree():
	if socket.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		send_command({
			"cmd": "quit"
		})

func process_message(json_string: String):
	var clean_string = json_string.replace("}{", "}|{")
	
	log_raw(json_string)  
	
	# Wir splitten den String in einzelne Pakete
	var packets = clean_string.split("|")
	#testes
	for packet in packets:
		if packet.strip_edges() == "":
			continue
			
		var json = JSON.new()
		var error = json.parse(packet.strip_edges())
		
		if error == OK:
			var data = json.data
			if typeof(data) == TYPE_DICTIONARY:
				
				# Fall A: Es ist die Map (Terrain)
				if "terrain" in data:
					print("Empfange Karte...")
					update_map(data["terrain"], data["size"])
					
					# START-Befehl an Python senden, sobald die Map gezeichnet ist!
					send_command({"cmd": "start"})
					
				# Fall B: Es ist ein Status-Update der Simulation ("type": "state") 
				# Fall B: Es ist ein Status-Update der Simulation ("type": "state") 
				elif data.get("type") == "state":
					
					# 1. Metadaten auslesen & Tick-Rate updaten
					var metadata = data.get("metadata", {})
					
					if metadata.has("tick"): # NEU: Aktuellen Tick speichern
						current_tick = int(metadata["tick"])
						
					if metadata.has("tick_rate"):
						tick_rate = float(metadata["tick_rate"])
						
					# 2. Das große Sterben (Tote aus der Welt und dem Dictionary entfernen)
					var deaths = metadata.get("deaths", [])
					total_deaths += deaths.size() # NEU: Tode zur Gesamtstatistik addieren
					
					
					
					for dead_id in deaths:
						var id = int(dead_id)
						
						if id == selected_monster_id:
								selected_monster_id = -1
						
						if spawned_monsters.has(id):
							var dead_monster = spawned_monsters[id]
							dead_monster.queue_free() # Sicher aus der Szene löschen
							spawned_monsters.erase(id) # Aus dem Dictionary entfernen
							
					# 3. Die Überlebenden und Neugeborenen verarbeiten
					var entities = data.get("entities", {})
					var organisms = entities.get("organisms", [])
					
					
					# --- NEU: Büsche verarbeiten (4 feste Farben) ---
					var bushes = entities.get("bushes", [])
					
					for bush_info in bushes:
						var b_id = int(bush_info["id"])
						var b_x = float(bush_info["x"])
						var b_y = float(bush_info["y"])
						
						# Food als Integer auslesen (0, 1, 2 oder 3)
						var food_current = int(bush_info.get("food", 0))
						
						# Farbe anhand des exakten Wertes bestimmen
						var bush_color: Color
						match food_current:
							3:
								bush_color = Color(0.0, 0.3, 0.0, 0.85) # Sehr dunkles Grün (85% deckend)
							2:
								bush_color = Color(1.0, 1.0, 0.0, 0.85) # Gelb
							1:
								bush_color = Color(1.0, 0.5, 0.0, 0.85) # Orange
							0:
								bush_color = Color(1.0, 0.0, 0.0, 0.85) # Rot
							_:
								bush_color = Color(1.0, 0.0, 0.0, 0.85) # Fallback (Rot), falls was schiefgeht
								
						if not spawned_bushes.has(b_id):
							# Neuen "Busch" (Quadrat) erstellen
							var rect = ColorRect.new()
							rect.size = Vector2(effective_tile_size, effective_tile_size)
							rect.position = Vector2(b_x * effective_tile_size, b_y * effective_tile_size)
							
							# Harte Farbe setzen
							rect.color = bush_color 
							
							bush_container.add_child(rect)
							spawned_bushes[b_id] = rect
						else:
							# Busch existiert schon? Dann nur die Farbe aktualisieren!
							var existing_rect = spawned_bushes[b_id]
							existing_rect.color = bush_color
					
					# NEU: Hilfsvariablen für die Durchschnitte in diesem Tick
					var sum_food: float = 0.0
					var sum_water: float = 0.0
					var sum_speed: float = 0.0
					var sum_energy: float = 0.0 # <--- NEU
					#var sum_age: float = 0.0 
					var pop_count: int = 0
					
					# --- NEU: Variablen für das ausgewählte Monster ---
					var selected_found: bool = false
					var sel_x: float = 0.0
					var sel_y: float = 0.0
					var sel_energy: float = 0.0
					var sel_food: float = 0.0
					var sel_water: float = 0.0
					
					for org in organisms:
						# NEU: Wir holen erst das Dictionary und dann den "current"-Wert
						
						var food_data = org.get("food", {})
						sum_food += float(food_data.get("current", 0.0))
						
						var water_data = org.get("water", {})
						sum_water += float(water_data.get("current", 0.0))
						
						var speed_data = org.get("speed", {})
						sum_speed += float(speed_data.get("current", 0.0))
						
						# NEU: Energie auslesen!
						var energy_data = org.get("energy", {})
						sum_energy += float(energy_data.get("current", 0.0))
						
						# Lebenszeit: In deinem JSON-Ausschnitt sehe ich kein "age" oder "lifetime".
						# Falls das ein flacher Wert ist, bleibt es so:
						#sum_age += float(org.get("age", 0.0)) 
						
						pop_count += 1
						
						# Aufruf deiner bestehenden Funktion
						spawn_or_update_monster(org)
						
						# --- NEU: Ist das unser ausgewähltes Monster? Dann schnapp dir die Daten! ---
						if int(org.get("id")) == selected_monster_id:
							selected_found = true
							sel_x = float(org.get("x", 0.0))
							sel_y = float(org.get("y", 0.0))
							# Wir nutzen hier gleich die Werte, die du oben eh schon ausgelesen hast:
							sel_energy = float(energy_data.get("current", 0.0))
							sel_food = float(food_data.get("current", 0.0))
							sel_water = float(water_data.get("current", 0.0))
						
					# 4. NEU: Statistiken finalisieren und in die Historie pushen
					current_population = pop_count
					#print("DEBUG -> Pop: ", current_population, " | HUD da?: ", hud_instance != null)
					
					if current_population > 0:
						var avg_food = sum_food / current_population
						var avg_water = sum_water / current_population
						var avg_speed = sum_speed / current_population
						var avg_energy = sum_energy / current_population # <--- NEU
						#var avg_age = sum_age / current_population
						
						# Vector2 für den Graphen erstellen: (X = Tick, Y = Durchschnittswert)
						history_avg_food.append(Vector2(current_tick, avg_food))
						history_avg_water.append(Vector2(current_tick, avg_water))
						history_avg_speed.append(Vector2(current_tick, avg_speed))
						history_avg_energy.append(Vector2(current_tick, avg_energy)) # <--- NEU
						#history_avg_lifetime.append(Vector2(current_tick, avg_age))
						
						# NEU: Wir senden alle gesammelten Werte an das HUD!
						if hud_instance != null:
							hud_instance.update_dashboard(
								current_tick,
								current_population,
								total_births,
								total_deaths,
								avg_energy,
								avg_food,
								avg_water
							)
							hud_instance.update_selected_monster(
								selected_found, 
								selected_monster_id,
								sel_x,
								sel_y,
								sel_energy,
								sel_food, 
								sel_water
							)
							
						# Debug: Alle 10 Ticks Werte in die Konsole drucken
						if current_tick % 10 == 0:
							print("Tick: ", current_tick, " | Pop: ", current_population, " | Geburten: ", total_births, " | Avg Food: ", avg_food, " | Energy: ", avg_energy)
		else:
			print("JSON Fehler im Paket: ", json.get_error_message())

func update_map(terrain_grid: Array, size: Dictionary):
	effective_tile_size = TILE_SIZE 
	
	var width = int(size["width"])
	var height = int(size["height"])
	
	# Map-Größe speichern
	map_width_tiles = float(width)
	map_height_tiles = float(height)
	
	print("Zeichne Map neu (", width, "x", height, ")...")
	tilemap.clear()
	
	var SOURCE_ID = 0 
	var COORD_WATER = Vector2i(0, 0)
	var COORD_LAND = Vector2i(1, 0)
	
	for y in range(height):
		for x in range(width):
			if y < terrain_grid.size() and x < terrain_grid[y].size():
				var cell_type = terrain_grid[y][x]
				var grid_pos = Vector2i(x, y)
				
				if cell_type == 0:
					tilemap.set_cell(grid_pos, SOURCE_ID, COORD_WATER)
				elif cell_type == 1:
					tilemap.set_cell(grid_pos, SOURCE_ID, COORD_LAND)

	# Kamera auf die tatsächliche Mitte zentrieren
	camera.position = Vector2(width * TILE_SIZE, height * TILE_SIZE) / 2.0
	camera.zoom = Vector2(0.25, 0.25)

func spawn_or_update_monster(info: Dictionary):
	# 1. Sicheres Auslesen und Casten der Daten
	var org_id = int(info["id"]) 
	var grid_x = float(info["x"])
	var grid_y = float(info["y"])
	var angle = float(info.get("angle", 0.0)) 

	var target_pos = Vector2(grid_x * effective_tile_size, grid_y * effective_tile_size)
	
	# 2. Tween-Dauer berechnen inkl. Sicherheits-Check gegen Division durch Null
	var tween_duration = 0.2
	if tick_rate > 0:
		tween_duration = 1.0 / tick_rate 
	
	# 3. Prüfen: Existiert das Monster schon?
	if spawned_monsters.has(org_id):
		# --- UPDATE (Flüssige Bewegung) ---
		var monster = spawned_monsters[org_id]
		var tween = create_tween()
		
		# Setze die Position flüssig um
		tween.tween_property(monster, "position", target_pos, tween_duration)
		
		# Setze auch die Rotation flüssig um
		# NEU: Den kürzesten Drehwinkel über die Pi-Grenze berechnen
		var current_angle = monster.rotation
		# Berechnet die Differenz und zwingt sie in den Bereich von -PI bis +PI
		var angle_diff = wrapf(angle - current_angle, -PI, PI) 
		
		# Dem Tween sagen, er soll genau von da, wo er ist, dieses kleine Stück weitergehen
		tween.parallel().tween_property(monster, "rotation", current_angle + angle_diff, tween_duration)
		
	else:
		# --- SPAWN (Neugeborene) ---
		total_births += 1
		print("Neues Monster gespawnt: ID ", org_id) 
		var monster = monster_scene.instantiate()
		monster.position = target_pos
		monster.rotation = angle
		
		# --- NEU: ID übergeben und Signal verbinden ---
		monster.org_id = org_id
		monster.clicked.connect(_on_monster_clicked)
		
		# 1. Startfarbe festlegen (z.B. leuchtendes Gelb/Gold)
		monster.modulate = Color(2, 2, 0) # Werte > 1 erzeugen einen Glow-Effekt (HDR)
		
		# 2. Einen Tween erstellen, der die Farbe zurück auf Weiß (normal) setzt
		var birth_tween = create_tween()
		# Wir faden die Farbe in 1.5 Sekunden zurück auf Standard (1, 1, 1)
		birth_tween.tween_property(monster, "modulate", Color(1, 1, 1), 7)
		
		monster_container.add_child(monster)
		spawned_monsters[org_id] = monster

func log_raw(data: String):
	var file = FileAccess.open("C:/Users/Admin/Desktop/HTL/5chel/Neuer Ordner/raw_log.txt", FileAccess.READ_WRITE)
	if not file:
		file = FileAccess.open("C:/Users/Admin/Desktop/HTL/5chel/Neuer Ordner/raw_log.txt", FileAccess.WRITE)
	file.seek_end()
	file.store_string(data + "\n")
	file.close()

func _on_monster_clicked(clicked_id: int):
	print("Monster ausgewählt! ID: ", clicked_id)
	
	# Altes Monster wieder auf normale Farbe setzen (Weiß)
	if selected_monster_id != -1 and spawned_monsters.has(selected_monster_id):
		spawned_monsters[selected_monster_id].modulate = Color(1, 1, 1) 
		
	# Neue ID merken
	selected_monster_id = clicked_id
	
	# Das neu angeklickte Monster farblich hervorheben (z.B. leuchtendes Cyan)
	if spawned_monsters.has(selected_monster_id):
		spawned_monsters[selected_monster_id].modulate = Color(0, 2, 2)
