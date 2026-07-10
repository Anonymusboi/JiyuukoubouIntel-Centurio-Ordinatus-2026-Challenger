import math
import pygame
import numpy as np

#30 pixel margin
arenaWidth = 180 + 30 
arenaHeight = 180 + 50 + 30

windowWidth = 900
windowHeight = 600


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
    ((88,90), (60,90))
]

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
        
        
def worldToScreenCoords(x, y, bounds):
    min_x, min_y, max_x, max_y = bounds
    world_width = max(1, max_x - min_x)
    world_height = max(1, max_y - min_y)
    margin = 20

    scale_x = (windowWidth - margin * 2) / world_width
    scale_y = (windowHeight - margin * 2) / world_height
    scale = min(scale_x, scale_y)
    


    screen_x = int((x - min_x) * scale + margin)
    screen_y = int(windowHeight - margin - (y - min_y) * scale)
    return screen_x, screen_y

def renderMap():
    surface = pygame.Surface((windowWidth, windowHeight))
    surface.fill((255, 255, 255))

    pygame.draw.rect(surface, "black", (0, 0, windowWidth, windowHeight), width=4)

    bounds = [0, 0, arenaWidth, arenaHeight]
    for start, end in walls:
        startPoint = worldToScreenCoords(*start, bounds)
        endPoint = worldToScreenCoords(*end, bounds)
        pygame.draw.line(surface, "black", startPoint, endPoint, width=3)

    return surface

pygame.init()
screen = pygame.display.set_mode((windowWidth, windowHeight))
map_surface = renderMap()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    screen.blit(map_surface, (0, 0))
    pygame.display.flip()

pygame.quit()
