extends Control

# Referenzen auf die Nodes (Namen ggf. anpassen!)
@onready var video_player = $Video
@onready var file_dialog = $MeinFileDialog

func _ready():
	# Optional: Fenstergröße beim Start festlegen
	# DisplayServer.window_set_size(Vector2i(1280, 720))
	pass

# BUTTON 1: Website öffnen
func _on_button_1_pressed():
	print("DEBUG: Button 1 wurde wirklich ausgelöst!")
	var err = OS.shell_open("https://www.youtube.com/watch?v=BwHw4pDcGns")
	if err != OK:
		print("Fehler-Code vom System: ", err)

# BUTTON 2: Dateimanager öffnen
func _on_button_2_pressed():
	file_dialog.popup_centered()

# Signal vom FileDialog (muss im Editor verbunden werden!)
func _on_mein_file_dialog_file_selected(path):
	print("Datei ausgewählt: ", path)

# BUTTON 3: Video abspielen
func _on_button_3_pressed():
	# Falls das Video über dem Button liegt, machen wir es erst jetzt sichtbar
	video_player.show() 
	video_player.play()

func _on_button_pressed() -> void:
	pass # Replace with function body.
