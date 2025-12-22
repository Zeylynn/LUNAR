extends Node

var socket = StreamPeerTCP.new()
var host = "127.0.0.1"
var port = 9001

func _ready():
	# Verbindung zum Server starten
	var err = socket.connect_to_host(host, port)
	if err == OK:
		print("Verbindungsversuch zu ", host, ":", port)
	else:
		print("Fehler beim Starten der Verbindung: ", err)

func _process(_delta):
	# Status des Sockets aktualisieren
	socket.poll()
	
	var status = socket.get_status()
	
	if status == StreamPeerTCP.STATUS_CONNECTED:
		# Prüfen, ob Daten empfangen wurden
		var bytes_available = socket.get_available_bytes()
		if bytes_available > 0:
			# Daten abholen
			var data = socket.get_data(bytes_available)
			if data[0] == OK:
				# Byte-Array in String umwandeln und ausgeben
				var message = data[1].get_string_from_utf8()
				print("Empfangen: ", message.strip_edges())
				
	elif status == StreamPeerTCP.STATUS_ERROR or status == StreamPeerTCP.STATUS_NONE:
		# Optional: Logik für Verbindungsabbruch
		pass
