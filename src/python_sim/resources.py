class Bush:
    def __init__(self, x, y, max_food=3, regen_rate=0.05):
        # float damit man u.a. mit Organismus Koordinaten vergleichen kann
        self.x = float(x)
        self.y = float(y)
        self.food = max_food
        self.max_food = max_food
        self.regen_rate = regen_rate
        self.nutrition = 1                    # Wie viel Energie ein "Apfel" auffüllt, Faktor

    def update(self):
        """aktualisiert self.food um die self.regen_rate, bis zu einem maximum von self.max_food"""
        self.food = min(self.max_food, self.food + self.regen_rate)

    def harvest(self):
        """Entfernt 1 von self.food, gibt zurück wie viel entnommen wurde"""
        harvested = min(int(self.food), 1)      # Falls Food < 1, wird nichts geerntet
        self.food -= harvested
        return harvested

    def is_empty(self):
        """
        Gibt zurück:
        - TRUE wenn self.food < 1
        - FALSE wenn self.food > 1
        """
        if self.food < 1:
            return True
        else:
            return False
    
    def to_dict(self):
        """Return JSON-serializable dictionary of the bush"""
        return {
            "type": "Bush",
            "x": int(self.x),
            "y": int(self.y),
            "max_food": self.max_food,
            "food": self.food,
            "regen_rate": self.regen_rate,
            "nutrition": self.nutrition
        }

    def __str__(self):
        return f"""Bush(
            Pos X: {self.x},
            Pos Y: {self.y},
            MaxFood: {self.max_food},
            Food: {self.food},
            RegenRate {self.regen_rate},
            Nutrition {self.nutrition})"""