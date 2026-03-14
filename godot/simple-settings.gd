extends Node
## Simple Settings
##
## A simple plugin allowing developers to implement a flexible settings system.
##
## @since: 1.0.0


## Emitted when any value changes.
##
## @since: 1.0.0
signal key_changed(file: String, key: String, value: Variant, old_value: Variant)


## Emitted when a settings file is saved.
##
## @since: 1.0.0
signal file_saved(file: String)


## Emitted when a settings file is loaded.
##
## @since: 1.0.0
signal file_loaded(file: String)


## Setup autosave.
##
## Define the interval between autosaves in seconds.
## Values less than or equal to 0 will disable autosave.
##
## @since: 1.0.0
var autosave_interval: int = 1


## The config files to handle.
##
## @since: 1.0.0
var config_files: Dictionary = {}


## Setup debugging.
##
## 0 - Errors only
## 1 - Errors and important messages
## 2 - Errors and all messages
##
## @since: 1.0.0
var debug_level: int = 1


## Should we save automatically when quitting?
##
## @since: 1.0.0
var save_on_quit: bool = true


## Whether or not settings are loaded.
##
## @since: 1.0.0
var _loaded: bool = false


## The autosave timer.
##
## @since: 1.0.0
var _save_timer: Timer


## Get things ready
##
## @since: 1.0.0
func _ready() -> void:
	# Create the autosave timer.
	_create_autosave_timer()


## Load the settings files
##
## @since: 1.0.0
func load() -> void:
	if config_files.is_empty():
		push_error(tr("No config files defined!"))
		return

	for key in config_files:
		var config_file: Dictionary = config_files[key]
		config_file.config = ConfigFile.new()
		config_file.config.load(config_file.path)

		file_loaded.emit(key)

		if debug_level >= 2:
			print(tr("Loading settings file \"{file}\"").format({
				file = key,
			}))

	_loaded = true


## Delete a section from a config file
##
## @since: 1.0.0
func erase_section(file: String, section: String) -> void:
	if _loaded:
		config_files[file].config.erase_section(section)


## Return an array of keys in the specified section
##
## @since: 1.0.0
func get_section_keys(file: String, section: String) -> PackedStringArray:
	var keys = []

	if _loaded:
		keys = config_files[file].config.get_section_keys(section)

	return keys


## Return an array of all defined section identifiers in a config file
##
## @since 1.0.0
func get_sections(file: String) -> PackedStringArray:
	var sections = []

	if _loaded:
		sections = config_files[file].config.get_sections()

	return sections


## Return a value from the given file.
## If no default value is specified, it looks in the
## Project Settings for the key (prefixed by "defaults/").
##
## @since: 1.0.0
func get_value(file: String, key: String, default = null) -> Variant:
	var value = null

	if _loaded:
		var section_key := _split_section_key(key)

		if default == null:
			default = ProjectSettings.get_setting("defaults/" + key)

		value = config_files[file].config.get_value(
			section_key.section,
			section_key.key,
			default
		)

	return value


## Returns true if the section exists in the given file
##
## @since: 1.0.0
func has_section(file: String, section: String) -> bool:
	var exists = false

	if _loaded:
		exists = config_files[file].config.has_section(section)

	return exists


## Returns true if the key exists in the given file
##
## @since: 1.0.0
func has_section_key(file: String, key: String) -> bool:
	var exists = false

	if _loaded:
		var section_key := _split_section_key(key)

		exists = config_files[file].config.has_section_key(
			section_key.section,
			section_key.key
		)

	return exists


## Sets a value in the given configuration file.
##
## @since: 1.0.0
func set_value(file: String, key: String, value: Variant) -> void:
	if _loaded:
		var section_key := _split_section_key(key)
		var old_value: Variant = config_files[file].config.get_value(file, key, false)

		config_files[file].config.set_value(
			section_key.section,
			section_key.key,
			value
		)

		key_changed.emit(file, key, value, old_value)

		if debug_level >= 2:
			print(tr("Setting {key} to {value} in {file}").format({
				key = key,
				value = value,
				file = file,
			}))


## Save the managed settings files.
##
## @since: 1.0.0
func save() -> void:
	if _loaded:
		for key in config_files:
			var config_file: Dictionary = config_files[key]
			config_file.config.save(config_file.path)


## Create the autosave timer
##
## @since: 1.0.0
func _create_autosave_timer() -> void:
	_save_timer = Timer.new()
	add_child(_save_timer)

	if autosave_interval > 0:
		_save_timer.start(autosave_interval)
	else:
		_save_timer.start(60)

	_save_timer.one_shot = true

	_save_timer.timeout.connect(func _on_autosave_timer_timeout() -> void:
		if autosave_interval > 0:
			save()

			# Restart timer
			_save_timer.start(autosave_interval)
		else:
			_save_timer.start(60)
	)


## Split a key string into a section and key
##
## @since: 1.0.0
func _split_section_key(key: String) -> Dictionary:
	var section_key := key.split("/", true, 1)

	if section_key.size() != 2:
		push_error(tr("The key must be prefixed with a section!"))
		assert(false)

	return {
		section = section_key[0],
		key = section_key[1],
	}


## Save on exit
##
## @since: 1.0.0
func _exit_tree() -> void:
	if save_on_quit:
		save()
