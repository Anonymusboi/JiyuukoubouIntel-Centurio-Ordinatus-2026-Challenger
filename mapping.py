import math
import cameraVision
from cameraVision import RawBall

cameraWidth = cameraVision.cameraWidth
cameraFOV = cameraVision.cameraFOV
class Robot():
    #heading of 0 degrees will be FULL NORTH ^
    def __init__(self, coordinates, width, height, heading):
        self.transform = self.Transform(coordinates, width, height, heading)

    class Transform():
        def __init__(self, coordinates, width, height, heading):
            self.x, self.y = coordinates
            self.width = width
            self.height = height
            self.headingD = heading
            self.headingR = math.radians(heading)
            #COORDINATES FOR MAKING THE BOX
            self.__topLeft = (self.x - width/2, self.y + height/2)
            self.__topRight = (self.x + width/2, self.y + height/2)
            self.__bottomRight = (self.x + width/2, self.y - height/2)
            self.__bottomLeft = (self.x - width/2, self.y - height/2)

            self.__localBoxCoords = [((self.__topLeft), (self.__topRight)), 
                                    ((self.__topRight), (self.__bottomRight)),
                                    ((self.__bottomRight), (self.__bottomLeft)),
                                    ((self.__bottomLeft), (self.__topLeft))]
            
            self.worldBoxCoords = self.__localBoxCoords
            
        def rotate(self, angle):
            radians = math.radians(angle)
            self.headingD += angle
            self.headingR += radians
            
            newCoords = []
            
            for coord1, coord2 in self.worldBoxCoords:
                x1, y1 = coord1
                x1 -= self.x
                y1 -= self.y
                rotatedCoords_x1 = x1*math.cos(radians) - y1*math.sin(radians) + self.x
                rotatedCoords_y1 = x1*math.sin(radians) + y1*math.cos(radians) + self.y
                x2, y2 = coord2
                x2 -= self.x
                y2 -= self.y
                rotatedCoords_x2 = x2*math.cos(radians) - y2*math.sin(radians) + self.x
                rotatedCoords_y2 = x2*math.sin(radians) + y2*math.cos(radians) + self.y
                newCoords.append(((rotatedCoords_x1, rotatedCoords_y1), (rotatedCoords_x2, rotatedCoords_y2)))
            
            self.worldBoxCoords = newCoords
            return newCoords
        
        
class Ball():
    def __init__(self, diameter, colour):
        self.transform = self.Transform()
        self.diameter = diameter
        self.colour = colour
        self.collected = False
        
    def markCollected(self):
        self.collected = True
    class Transform:
        def __init__(self):
            self.localx = 0
            self.localy = 0
            self.worldx = 0
            self.worldy = 0
            
<<<<<<< HEAD
        def updateLocation(self, origin : Robot, x, y):
            self.x = x
            self.y = y
            self.worldx, self.worldy = self.localToWorldCoords(origin)
            
        def calculateLocalCoords(self,x,y,r,distance, cameraFOV, cameraResolution):
            cameraWidth, cameraHeight = cameraResolution
            offset_x = x - cameraWidth/2
            angle = (offset_x/(cameraWidth/2))*(cameraFOV/2)
            radians = math.radians(angle)
            localx = distance * math.cos(radians) 
            localy = distance * math.sin(radians)
            return (localx, localy)
            
        def localToWorldCoords(self, origin : Robot):
            targetCoords_x = self.x
            targetCoords_y = self.y
=======
        def updateLocal(self, offset_x, distance):
            viewAngle = (offset_x/(cameraWidth/2)) * (cameraFOV/2)
            viewRadians = math.radians(viewAngle)
            
            self.localx = distance/10 * math.sin(viewRadians)
            self.localy = distance/10 * math.cos(viewRadians)
            
        def updateWorldCoords(self, origin : Robot):
            targetCoords_x = self.localx
            targetCoords_y = self.localy
>>>>>>> renderer-rollback
            
            #rotation translation
            rotatedCoords_x = targetCoords_x*math.cos(origin.transform.headingR) - targetCoords_y*math.sin(origin.transform.headingR)
            rotatedCoords_y = targetCoords_x*math.sin(origin.transform.headingR) + targetCoords_y*math.cos(origin.transform.headingR)
            
            #displacement translation
            finalCoords_x = rotatedCoords_x + origin.transform.x
            finalCoords_y = rotatedCoords_y + origin.transform.y
            
            worldCoords = (finalCoords_x, finalCoords_y)
            
<<<<<<< HEAD
            return worldCoords
=======
            self.worldx = finalCoords_x
            self.worldy = finalCoords_y
            
            return worldCoords
        
def createBall(ball : RawBall, diameter):
    if ball is None:
        return None
    x, y, r, distance, colour = ball.getData()
    offset_x = x - cameraWidth / 2
    digitalBall = Ball(diameter, colour)
    digitalBall.transform.updateLocal(offset_x, distance)
    return digitalBall
>>>>>>> renderer-rollback
