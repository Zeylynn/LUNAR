class Bush:
    def __init__(self, x, y, max_food=5, regen_rate=0.01):
        # float damit man u.a. mit Organismus Koordinaten vergleichen kann
        self.x = float(x)
        self.y = float(y)
        self.food = max_food
        self.max_food = max_food
        self.regen_rate = regen_rate

    def update(self):
        """aktualisiert self.food um die self.regen_rate, bis zu einem maximum von self.max_food"""
        self.food = min(self.max_food, self.food + self.regen_rate)

    def harvest(self):
        pass
        #TODO implementieren dass Organismen Food essen können

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

class Food:
    def __init__(self, x, y):
        # float weil sie mit INT zufällige Positionen bekommen, ich aber alle x,y Werte in float haben will
        #TODO Food implementieren/removen => in der Nähe von Bäumen wachsen
        self.x = float(x)
        self.y = float(y)

        self.size = 1

    def __str__(self):
        return f"""Food(
            Pos X: {self.x},
            Pos Y: {self.y})"""