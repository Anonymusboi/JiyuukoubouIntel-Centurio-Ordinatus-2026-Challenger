

class CommonObject:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

class Ball(CommonObject):
    def __init__(self, x, y, size, colour):
        super().__init__(x, y, size)
        self.colour = colour
        self.collected = False
        
    def markCollected(self):
        self.collected = True
        
class Robot(CommonObject):
    def __init__(self, x, y, size):
        super().__init__(x, y, size) 