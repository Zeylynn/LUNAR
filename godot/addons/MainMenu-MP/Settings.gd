extends Control

@export var Start_scene: String = "res://addons/MainMenu-MP/Black.tscn"


func _on_back_settings_button_down() -> void:
	# Wechselt zurück zur Hauptmenü-Szene
	get_tree().change_scene_to_file(Start_scene)
