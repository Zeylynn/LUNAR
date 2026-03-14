@tool extends EditorPlugin
## Plugin
##
## Sets up the plugin and autoload.
##
## @since: 1.0.0

## Setup our autoload
##
## @since: 1.0.0
func _enter_tree() -> void:
	add_autoload_singleton("SimpleSettings", "res://addons/simple-settings/simple-settings.gd")


## Cleanup our autoload
##
## @since: 1.0.0
func _exit_tree() -> void:
	remove_autoload_singleton("SimpleSettings")
