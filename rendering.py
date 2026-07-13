import math
import pygame
import numpy as np
import mapping

#30 pixel margin
arenaWidth = 180 + 28
arenaHeight = 180 + 50

#Scale window (based on x value) proportional to arena,
margin =  28
windowWidth = 800
scale = (windowWidth - margin*2)/arenaWidth
windowHeight = int(scale*arenaHeight + margin*2 + 1)
screen = None

walls = [
    #Left walls
    ((0,0), (0, 60)),
    ((0,90), (0, 125)),
    ((0,155), (0,190)),
    ((0,220), (0,230)),
    #Top wall
    ((0,230), (180,230)),
    #Right wall
    ((180,230), (180,50)),
    #Bottom Wall
    ((180,50), (50,50)),
    ((50,50), (50,0)),
    ((50,0), (0,0)),
    
    #Island Left Wall
    ((60,90), (60,180)),
    #Top
    ((60,180), (88,180)),
    #Right
    ((88,180), (88,90)),
    #Bottom
    ((88,90), (60,90)),
    
    #Basket Walls
    #red
    ((0,60), (-28,60)),
    ((-28,60), (-28,90)),
    ((-28,90), (0,90)),
    #yellow
    ((0,125), (-28,125)),
    ((-28,125), (-28,155)),
    ((-28,155), (0,155)),
    #blue
    ((0,190), (-28,190)),
    ((-28,190), (-28,220)),
    ((-28,220), (0,220))
]

lines =[
    #Setup Line
    ((0,49), (50,49)),
    #Basket Lines
    ((5,60), (5,90)),
    ((5,125), (5,155)),
    ((5,190), (5,220)),
    #Line Trace Checkpoints
    ((15,75), (45,75)),
    ((15,140), (45,140)),
    ((60,220), (60,190)),
    ((119,180), (149,180)),
    ((119,55), (149,55)),
    #The Line Trace itself (No curves)
    ((30,75), (30,190)),
    ((45,205), (119,205)),
    ((134,190), (134,50)),
    #Line Trace Curves
    #Left
    ((30,190), (31.21,195.74)),
    ((31.21,195.74), (34.477,200.52)),
    ((34.477,200.52),(39.256,203.79)),
    ((39.256,203.79), (45,205)),
    #Right
    ((119,205), (124.74,203.79)),
    ((124.74, 203.79), (129.52,200.52)),
    ((129.52,200.52), (132.79,195.74)),
    ((132.79,195.74), (134,190)),
    #Island Line
    ((74,90), (74,180))
]

customMarkings =[
    #Basket Lines
    #red
    ((0,60), (0,90), "red"),
    ((0,125), (0,155), "yellow"),
    ((0,190), (0,220), "blue")
    #yellow
    #blue
]
        
def worldToScreenCoords(x,y):
    screen_x = (x+28)*scale + margin #28 for the -28 coordinate cuz i'm too lazy to rewrite the coordinates
    screen_y = windowHeight - y*scale - margin
    
    return screen_x, screen_y
        
def renderMap():
    surface = pygame.Surface((windowWidth, windowHeight))
    surface.fill((255, 255, 255))
    
    #draw square to separate from the window handle
    pygame.draw.rect(surface, "black", (0,0, windowWidth, windowHeight), width=4) 
    
    for start, end in walls:
        startPos = worldToScreenCoords(*start)
        endPos = worldToScreenCoords(*end)
        pygame.draw.line(surface, "black", startPos, endPos, width=3)
    for start, end in lines:
        startPos = worldToScreenCoords(*start)
        endPos = worldToScreenCoords(*end)
        pygame.draw.line(surface, "black", startPos, endPos, width=3)
    for start, end, colour in customMarkings:
        startPos = worldToScreenCoords(*start)
        endPos = worldToScreenCoords(*end)
        pygame.draw.line(surface, colour, startPos, endPos, width=3)

    return surface

def init():
    pygame.init()
    print("Rendering window at " + str(windowWidth) + "x" + str(windowHeight))
    screen = pygame.display.set_mode((windowWidth, windowHeight))
    return screen

def renderBall(surface, ball):
    x = ball.transform.x
    y = ball.transform.y
    diameter = ball.diameter
    colour = ball.colour
    pygame.draw.circle(surface, colour, x, y, diameter/2, width=2)
    
def renderRobot(surface, robot):
    x = robot.transform.x
    y = robot.transform.y
    
    

def renderer(screen):
    if screen is None:
        print("YOU FORGOT TO INITIALISE")
        return None
    
    map_surface = renderMap()
    
    screen.fill((255, 255, 255))
    screen.blit(map_surface, (0, 0))
    
    pygame.display.flip()

