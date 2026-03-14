extends CharacterBody2D

# Unser neues Signal
signal clicked(id: int)

# Hier speichern wir die ID
var org_id: int = -1

# Da du das Signal _input_event schon verbunden hast, nutzen wir genau diese Funktion!
func _input_event(_viewport, event, _shape_idx):
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		# Wenn wir angeklickt werden, schießen wir unsere ID an test.gd
		clicked.emit(org_id)
