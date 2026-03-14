extends Camera2D

@export var zoom_speed := 0.1
@export var min_zoom := 0.05
@export var max_zoom := 30.0

var dragging := false

func _unhandled_input(event):

	# Mausrad Zoom
	if event is InputEventMouseButton and event.is_pressed():
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			# Plus = Reinzoomen (Werte werden größer)
			zoom *= (1.0 + zoom_speed) 
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			# Minus = Rauszoomen (Werte werden kleiner)
			zoom *= (1.0 - zoom_speed)

		zoom.x = clamp(zoom.x, min_zoom, max_zoom)
		zoom.y = clamp(zoom.y, min_zoom, max_zoom)

	# Drag mit mittlerer Maustaste
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_MIDDLE:
		dragging = event.pressed

	if event is InputEventMouseMotion and dragging:
		# WICHTIG: Hier muss geteilt werden, damit die Maus exakt am Punkt bleibt!
		position -= event.relative / zoom
