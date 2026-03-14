extends CanvasLayer

# --- UI Elemente referenzieren ---
@onready var lbl_pop = $SidebarPanel/VBoxContainer/LblPop
@onready var lbl_births = $SidebarPanel/VBoxContainer/LblBirths
@onready var lbl_deaths = $SidebarPanel/VBoxContainer/LblDeaths
@onready var lbl_selected_stats = $SidebarPanel/VBoxContainer/LblSelectedStats

@onready var graph_energy = $SidebarPanel/VBoxContainer/GraphEnergy
@onready var graph_food = $SidebarPanel/VBoxContainer/GraphFood
@onready var graph_water = $SidebarPanel/VBoxContainer/GraphWater


# --- Variablen für die Linien (Plots) ---
var plot_energy
var plot_food
var plot_water

func _ready():
	# 1. Graphen mit unserer Hilfsfunktion optisch einrichten
	_setup_graph(graph_energy, "Avg Energy (%)")
	_setup_graph(graph_food, "Avg Food (%)")
	_setup_graph(graph_water, "Avg Water (%)")
	
	# 2. Die Linien in den jeweiligen Graphen anlegen
	plot_energy = graph_energy.add_plot_item("Energy", Color.YELLOW, 2.0)
	plot_food = graph_food.add_plot_item("Food", Color.GREEN, 2.0)
	plot_water = graph_water.add_plot_item("Water", Color.CYAN, 2.0)

# Hilfsfunktion, um Code-Wiederholungen zu vermeiden
func _setup_graph(g: Graph2D, title: String):
	g.x_min = 0.0
	g.x_max = 100.0  # Start-Skalierung der X-Achse (0 bis 100 Ticks)
	g.y_min = 0.0
	g.y_max = 100.0  # Y-Achse geht von 0 bis 100 (Prozent)
	
	g.x_label = "Ticks"
	g.y_label = title
	g.background_color = Color(0.1, 0.1, 0.12, 0.95) # Dunkles Panel
	g.grid_horizontal_visible = true
	g.grid_vertical_visible = true

# Diese Funktion wird von test.gd jeden Tick aufgerufen!
func update_dashboard(tick: int, pop: int, births: int, deaths: int, avg_energy: float, avg_food: float, avg_water: float):
	
	# 1. Labels aktualisieren
	lbl_pop.text = "Aktuelle Population: " + str(pop)
	lbl_births.text = "Gesamte Geburten: " + str(births)
	lbl_deaths.text = "Gesamte Tode: " + str(deaths)
	
	# 2. X-Achse (Ticks) scrollen lassen, wenn wir über den Rand (x_max) kommen
	if float(tick) > graph_energy.x_max:
		# Erweitert die Achse um 100 weitere Ticks für ALLE Graphen
		graph_energy.x_max += 100.0
		graph_food.x_max += 100.0
		graph_water.x_max += 100.0
		
	# 3. Den neuen Datenpunkt in die Kurven eintragen
	if plot_energy: plot_energy.add_point(Vector2(tick, avg_energy))
	if plot_food: plot_food.add_point(Vector2(tick, avg_food))
	if plot_water: plot_water.add_point(Vector2(tick, avg_water))
	
	# Wird jeden Tick aufgerufen, um das individuelle Monster zu zeigen
func update_selected_monster(is_selected: bool, id: int = -1, x: float = 0.0, y: float = 0.0, energy: float = 0.0, food: float = 0.0, water: float = 0.0):
	if not is_selected:
		lbl_selected_stats.text = "Kein Organismus ausgewählt."
		return
		
	# %d ist für ganze Zahlen (IDs), %.1f rundet Kommazahlen auf 1 Nachkommastelle
	var stats_text = "ID: %d\n" % id
	stats_text += "Position: (%.1f, %.1f)\n" % [x, y]
	stats_text += "Energy: %.1f %%\n" % energy
	stats_text += "Food: %.1f %%\n" % food
	stats_text += "Water: %.1f %%" % water
	
	lbl_selected_stats.text = stats_text
