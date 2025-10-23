class Bush:
    def __init__(self, x, y, max_food=5, regen_rate=0.01):
        # float damit man u.a. mit Organismus Koordinaten vergleichen kann
        self.x = float(x)
        self.y = float(y)
        self.food = max_food
        self.max_food = max_food
        self.regen_rate = regen_rate
        self.nutrition = 100                # Wie viel Energie ein "Apfel" auffüllt

    def update(self):
        """aktualisiert self.food um die self.regen_rate, bis zu einem maximum von self.max_food"""
        self.food = min(self.max_food, self.food + self.regen_rate)

    def harvest(self, amount: int):
        """Entfernt die Menge in amount von self.food, gibt zurück wie viel entnommen wurde"""
        if type(amount) != int:     # Es können nur "ganze" Früchte entfernt werden
            raise ValueError("amount muss vom Typ integer sein, weil nur 'ganze' Früchte geerntet werden können")
        
        harvested = min(int(self.food), amount)     # Damit nicht mehr geerntet wird als verfügbar
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
        
    def __str__(self):
        return f"""Bush(
            Pos X: {self.x},
            Pos Y: {self.y},
            MaxFood: {self.max_food},
            Food: {self.food},
            RegenRate {self.regen_rate})"""