from resources import Bush
import json
import copy

#TODO maybe logger einbauen

class JSONBuilder:
    def __init__(self):
        self.json_terrain = None
        self.json_organisms = None
        self.json_bushes = None

    def build_organisms(self, organisms):
        """Konvertiert Organismen in JSON-Struktur"""
        result = []
        for org in organisms:
            result.append(org.to_dict())

        #NOTE wenn man mehr als 1 Objekt sendet muss man vielleicht mit kompatibilität schauen, z.B. \n am Ende anfügen fpr Trennung
        self.json_organisms = json.dumps(result)

    def build_bushes(self, bushes):
        """Konvertiert Bushes in JSON-Struktur"""
        result = []
        for bush in bushes:
            result.append(bush.to_dict())

        #NOTE wenn man mehr als 1 Objekt sendet muss man vielleicht mit kompatibilität schauen, z.B. \n am Ende anfügen fpr Trennung
        self.json_bushes = json.dumps(result)

    def build_terrain(self, terrain):
        """Exportiert terrain in Godot-freundliches JSON"""
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
            "size": {"width": width, "height": height},
            "terrain": terrain_out,
            "objects": objects
        }

        self.json_terrain = json.dumps(result)

if __name__ == "__main__":
    from world_generator import WorldGenerator

    world = WorldGenerator(10, 10, seed=999, num_bushes=10)
    world.init_world()
    terrain = world.get_terrain()

    print(terrain)
    builder = JSONBuilder()
    builder.build_terrain(terrain=terrain)

    print(builder.json_terrain)