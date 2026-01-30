extends Node2D

# --- Referenzen (müssen im Editor zugewiesen oder benannt sein) ---
@onready var tilemap: TileMapLayer = $TileMapLayer
@onready var camera: Camera2D = $Camera2D

# Monster Scene vorladen
var monster_scene = preload("res://ZweitesMonster.tscn")

# Container für Monster, damit wir sie sauber löschen können
var monster_container: Node2D

# --- Netzwerk Variablen ---
var socket = StreamPeerTCP.new()
var host = "127.0.0.1"
var port = 9001

# --- TileMap Konstanten ---
const TERRAIN_SET := 0
const TERRAIN_WATER := 0 # Entspricht 0 im JSON
const TERRAIN_LAND := 1  # Entspricht 1 im JSON
const TILE_SIZE := 32    # Anpassung an deine Pixel-Größe (z.B. 16, 32, 64)

func _ready():
	print("Starte Client...")
	
	# Container für Monster erstellen
	monster_container = Node2D.new()
	add_child(monster_container)
	
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
		var bytes_available = socket.get_available_bytes()
		if bytes_available > 0:
			var data = socket.get_data(bytes_available)
			if data[0] == OK:
				var message_text = data[1].get_string_from_utf8()
				process_message(message_text)
				
	elif status == StreamPeerTCP.STATUS_ERROR or status == StreamPeerTCP.STATUS_NONE:
		print("Verbindung verloren oder Fehler.")

func process_message(json_string: String):
	# 1. Wir reparieren "aneinanderklebende" JSON-Objekte
	var clean_string = json_string.replace("}{", "}|{")
	
	# 2. Wir splitten den String in einzelne Pakete
	var packets = clean_string.split("|")
	
	for packet in packets:
		var json = JSON.new()
		var error = json.parse(packet.strip_edges())
		
		if error == OK:
			var data = json.data
			
			# Fall A: Es ist ein Dictionary (z.B. Map oder einzelnes Monster)
			if typeof(data) == TYPE_DICTIONARY:
				if "terrain" in data:
					print("Empfange Karte...")
					update_map(data["terrain"], data["size"])
				elif data.get("type") == "Organism":
					spawn_or_update_monster(data)
			
			# Fall B: Es ist eine Liste von Monstern (falls der Server das mal ändert)
			elif typeof(data) == TYPE_ARRAY:
				for item in data:
					if typeof(item) == TYPE_DICTIONARY and item.get("type") == "Organism":
						spawn_or_update_monster(item)
		else:
			print("JSON Fehler im Paket: ", json.get_error_message())
			# Optional: print("Kaputtes Paket war: ", packet)

func update_map(terrain_grid: Array, size: Dictionary):
	print("Zeichne Map neu...")
	tilemap.clear()
	
	var width = size["width"]
	var height = size["height"]
	
	var SOURCE_ID = 0 
	
	# Hier musst du evtl. schauen, wo deine Tiles im Bild liegen:
	var COORD_WATER = Vector2i(0, 0) # Nimm das Tile oben links für Wasser
	var COORD_LAND = Vector2i(1, 0)  # Nimm das Tile daneben für Land
	
	for y in range(height):
		for x in range(width):
			if y < terrain_grid.size() and x < terrain_grid[y].size():
				var cell_type = terrain_grid[y][x]
				var grid_pos = Vector2i(x, y)
				
		
				if cell_type == 0: # Wasser
					tilemap.set_cell(grid_pos, SOURCE_ID, COORD_WATER)
				elif cell_type == 1: # Land
					tilemap.set_cell(grid_pos, SOURCE_ID, COORD_LAND)

	# --- Kamera fixen (Verschiebung lösen) ---
	var map_center_x = (width * TILE_SIZE) / 2
	var map_center_y = (height * TILE_SIZE) / 2
	
	# Bewege die Kamera dorthin
	camera.position = Vector2(map_center_x, map_center_y)
	
	# Optional: Zoom etwas raus, damit man alles sieht (z.B. 0.5 für rauszoomen, 2.0 für rein)
	camera.zoom = Vector2(0.25, 0.25)

func spawn_or_update_monster(info: Dictionary):
	var monster = monster_scene.instantiate()
	monster_container.add_child(monster)
	
	# Position berechnen (Grid-Koordinaten * Tile-Größe + halbe Tile für Mitte)
	var grid_x = info["x"]
	var grid_y = info["y"]
	monster.position = Vector2(grid_x * TILE_SIZE, grid_y * TILE_SIZE) + Vector2(TILE_SIZE/2, TILE_SIZE/2)
	
	# Rotation setzen (Godot nutzt Radians, dein JSON scheint auch Radians zu sein -> angle: 3.02...)
	monster.rotation = info["angle"]
	

	if "energy" in info:

		# monster.energy = info["energy"]["current"]
		pass
