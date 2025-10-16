#TODO Food generiert in der Nähe von "Bäumen" anstatt einfach so

class Food:
    def __init__(self, x, y):
        # float weil sie mit INT zufällige Positionen bekommen, ich aber alle x,y Werte in float haben will
        self.x = float(x)
        self.y = float(y)

        self.size = 1

    def __str__(self):
        return f'Food(Pos X: {self.x}, Pos Y: {self.y})'