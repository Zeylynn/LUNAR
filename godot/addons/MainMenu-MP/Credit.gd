extends Control

@export var Start_scene: String = "res://addons/MainMenu-MP/Black.tscn"


func _ready():
	print("Credits Szene aktiv")





func _on_back_credits_pressed() -> void:
	print("Button gedrückt")
	get_tree().change_scene_to_file(Start_scene)
