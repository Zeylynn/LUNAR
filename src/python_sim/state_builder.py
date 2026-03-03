from python_sim.resources import Bush

#BUG alive in den Snapshot machen

class StateBuilder:
    def __init__(self):
        self.state = None
        self.terrain = None
        self.organisms = None
        self.bushes = None

    def build_organisms(self, organisms):
        """Konvertiert Organismen in State-Struktur"""
        result = []
        for org in organisms:
            result.append(org.to_dict())

        self.organisms = result

    def build_bushes(self, bushes):
        """Konvertiert Bushes in State-Struktur"""
        result = []
        for bush in bushes:
            result.append(bush.to_dict())

        self.bushes = result

    def build_state(self, tick, tick_rate):
        result = {
            "type": "state",
            "entities": {
                "organisms": self.organisms,
                "bushes": self.bushes
            },
            "metadata": {
                "tick": tick,
                "tick_rate": tick_rate
            }
        }
        self.state = result

    def build_terrain(self, terrain):
        """Exportiert terrain in Godot-freundlichem State"""
        height = len(terrain)
        width = len(terrain[0])

        terrain_out = []
        objects = []

        for y in range(len(terrain)):
            terrain_row = []
            for x in range(len(terrain[y])):
                tile = terrain[y][x]
                terrain_row.append(int(tile["terrain"]))

                obj = tile.get("object")
                if isinstance(obj, Bush):
                    objects.append(obj.to_dict())

            terrain_out.append(terrain_row)

        result = {
            "type": "terrain",
            "size": {"width": width, "height": height},
            "terrain": terrain_out,
            "bushes": objects
        }
        self.terrain = result