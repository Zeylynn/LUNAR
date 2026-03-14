extends CharacterBody2D

@export var speed: float = 190.0
@export var change_dir_time: float = 3.0

# Größe der Spielfläche (Viewport oder Map)
@export var area_size: Vector2 = Vector2(1560, 940)

var direction: Vector2 = Vector2.ZERO
var timer: float = 0.0

func _physics_process(delta: float) -> void:
	timer -= delta

	# Zufällige neue Richtung alle X Sekunden
	if timer <= 0.0:
		direction = _random_direction()
		timer = change_dir_time

	# Bewegung
	velocity = direction * speed
	move_and_slide()

	# An den Rändern Richtung wechseln
	_check_bounds()
	

func _random_direction() -> Vector2:
	return Vector2(
		randf() * 2 - 1,
		randf() * 2 - 1
	).normalized()


func _check_bounds() -> void:
	var pos = global_position

	var hit_border := false

	# Linke Wand
	if pos.x < 0:
		pos.x = 0
		hit_border = true

	# Rechte Wand
	if pos.x > area_size.x:
		pos.x = area_size.x
		hit_border = true

	# Oben
	if pos.y < 0:
		pos.y = 0
		hit_border = true

	# Unten
	if pos.y > area_size.y:
		pos.y = area_size.y
		hit_border = true

	global_position = pos

	# Wenn Rand getroffen → neue zufällige Richtung
	if hit_border:
		direction = _random_direction()
