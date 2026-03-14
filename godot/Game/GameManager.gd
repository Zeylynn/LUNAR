extends Node

var selected_monster: Node = null

func select_monster(monster: Node) -> void:
	if selected_monster != null:
		selected_monster.hide_stats()

	selected_monster = monster
	selected_monster.show_stats()
