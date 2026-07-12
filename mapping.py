import math
class CommonObject:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class Ball(CommonObject):
    #Ball uses diameter, so only 1 size is used.
    def __init__(self, x, y, diameter, colour):
        super().__init__(x, y, diameter, 0)
        self.diameter = diameter
        self.colour = colour
        self.collected = False
        
    def markCollected(self):
        self.collected = True
        
class Robot(CommonObject):
    #heading of 0 degrees will be FULL NORTH ^
    def __init__(self, x, y, width, height, heading):
        super().__init__(x, y, width, height) 
        #HEADING IS IN ANGLES, NOT RADIANS YET
        self.headingD = heading
        self.headingR = math.radians(heading)
        
def calculateLocalCoords(origin, distance, offset_x):
    originCoords_x = origin.x
    originCoords_y = origin.y
    targetCoords = (originCoords_x + offset_x, originCoords_y + distance)
    return targetCoords

def localToWorldCoords(origin : Robot, target):
    targetCoords_x, targetCoords_y = target
    
    #rotation translation
    rotatedCoords_x = targetCoords_x*math.cos(origin.headingR) - targetCoords_y*math.sin(origin.headingR)
    rotatedCoords_y = targetCoords_x*math.sin(origin.headingR) + targetCoords_y*math.cos(origin.headingR)
    
    #displacement translation
    finalCoords_x = rotatedCoords_x + origin.x
    finalCoords_y = rotatedCoords_y + origin.y
    
    worldCoords = (finalCoords_x, finalCoords_y)
    
    return worldCoords