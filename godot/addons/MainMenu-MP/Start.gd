extends Control

@export var Start_scene: String = "res://addons/MainMenu-MP/Black.tscn"


func _on_back_game_button_down() -> void:
	# Wechselt zurück zur Hauptmenü-Szene
	get_tree().change_scene_to_file(Start_scene)


func _on_start_game_pressed() -> void:
	# Hier fügst du den kopierten Pfad ein
	# Verhindert, dass der Fokus "kleben" bleibt
	
	get_tree().change_scene_to_file("res://Game/world.tscn")
	$StartGame.release_focus()
