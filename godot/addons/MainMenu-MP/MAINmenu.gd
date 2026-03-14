extends Control

# Pfade zu deinen anderen Szenen (zieh sie einfach aus dem Dateisystem hier rein)
@export var Settings_scene: String = "res://addons/MainMenu-MP/Settings.tscn"
@export var Credits_scene: String = "res://addons/MainMenu-MP/Credits.tscn"
@export var Start_scene: String = "res://addons/MainMenu-MP/Start.tscn"

# Referenz auf ein Panel, falls du Settings nur einblenden willst
@onready var settings_panel = $SettingsPanel 
@onready var file_dialog = $MeinFileDialog
# --- FUNKTIONEN ---



func _on_start_button_down() -> void:
	# Wechselt die komplette Szene zum Spiel
	get_tree().change_scene_to_file(Start_scene)

func _on_quit_button_down() -> void:
	get_tree().quit()


func _on_settings_button_down() -> void:
	# Zeigt das Settings-Panel an (ohne Szenenwechsel)
	get_tree().change_scene_to_file(Settings_scene)


func _on_credits_button_down() -> void:
	# Wechselt zur Credits-Szene
	get_tree().change_scene_to_file(Credits_scene)


func _on_load_button_down() -> void:
	file_dialog.popup_centered()

func _on_secret_btn_button_down() -> void:
	var err = OS.shell_open("https://github.com/Zeylynn/LUNAR")
	if err != OK:
		print("Fehler-Code vom System: ", err)
