import math
class Ball():
    #Ball uses diameter, so only 1 size is used.
    def __init__(self, x, y, diameter, colour):
        self.x = x
        self.y = y
        self.diameter = diameter
        self.colour = colour
        self.collected = False
        
    def markCollected(self):
        self.collected = True
        
class Robot():
    #heading of 0 degrees will be FULL NORTH ^
    def __init__(self, coordinates, width, height, heading):
        self.transform = self.Transform(coordinates, width, height)
        #HEADING IS IN ANGLES, NOT RADIANS YET
        self.headingD = heading
        self.headingR = math.radians(heading)

    class Transform():
        def __init__(self, coordinates, width, height):
            self.x, self.y = coordinates
            self.width = width
            self.height = height
            #COORDINATES FOR MAKING THE BOX
            self.topLeft = (self.x - width/2, self.y + height/2)
            self.topRight = (self.x + width/2, self.y + height/2)
            self.bottomRight = (self.x + width/2, self.y - height/2)
            self.bottomLeft = (self.x - width/2, self.y - height/2)

            self.boxCoords = (self.topLeft, self.topRight, self.bottomRight, self.bottomLeft)
            
        def rotate(self, angle):
            finalCoords = []
            for x, y in self.boxCoords:
                x -= self.x
                y -= self.y
                rotatedCoords_x = x*math.cos(angle) - y*math.sin(angle) + self.x
                rotatedCoords_y = x*math.sin(angle) + y*math.cos(angle) + self.y
                finalCoords.append((rotatedCoords_x, rotatedCoords_y))
        
            
            self.boxCoords = [((finalCoords[0]), (finalCoords[1])), 
                              ((finalCoords[1]),(finalCoords[2])), 
                              ((finalCoords[2]),(finalCoords[3])), 
                              ((finalCoords[3]),(finalCoords[0]))]
            return self.boxCoords
        
def calculateLocalCoords(distance, offset_x):
    targetCoords = (offset_x, distance)
    return targetCoords

def localToWorldCoords(origin : Robot, target):
    targetCoords_x, targetCoords_y = target
    
    #rotation translation
    rotatedCoords_x = targetCoords_x*math.cos(origin.headingR) - targetCoords_y*math.sin(origin.headingR)
    rotatedCoords_y = targetCoords_x*math.sin(origin.headingR) + targetCoords_y*math.cos(origin.headingR)
    
    #displacement translation
    finalCoords_x = rotatedCoords_x + origin.transform.x
    finalCoords_y = rotatedCoords_y + origin.transform.y
    
    worldCoords = (finalCoords_x, finalCoords_y)
    
    return worldCoords