extends Node2D

@onready var tilemap: TileMapLayer = $TileMapLayer
@onready var camera: Camera2D = $Camera2D

# Terrain IDs (müssen zu deinem TileSet passen)
const TERRAIN_SET := 0
const TERRAIN_WATER := 0
const TERRAIN_LAND := 1

func _ready():
	print("WORLD READY")

	tilemap.clear()

	var width := 20
	var height := 15

	var water := []
	var land := []

	for y in range(height):
		for x in range(width):
			if x < 5 or y < 4:
				water.append(Vector2i(x, y))
			else:
				land.append(Vector2i(x, y))

	# WICHTIG: gesammelt setzen
	tilemap.set_cells_terrain_connect(water, TERRAIN_SET, TERRAIN_WATER)
	tilemap.set_cells_terrain_connect(land, TERRAIN_SET, TERRAIN_LAND)

	# Kamera zentrieren
	camera.enabled = true
	camera.zoom = Vector2(1, 1)
	camera.position = tilemap.map_to_local(Vector2i(width / 2, height / 2))

	print("MAP GENERATED")
