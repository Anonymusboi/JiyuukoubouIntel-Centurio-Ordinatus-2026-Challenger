import pygame
from mapping import Ball, Robot
import time
import datetime

arenaWidth = 180 + 28 #28 for the baskets
arenaHeight = 180 + 50 #50 for the robot start position

#Scale arena window (based on x value) proportional to arena,
margin = 50
arenaWindowHeight = 600
scale = (arenaWindowHeight - margin*2)/arenaHeight
arenaWindowWidth = int(scale*arenaWidth + margin*2 + 1)
#Values related to the left side bar.
sideBarWidthL = 420
#Values related to the right side bar
sideBarWidthR = 420
#Values related to the top bar
topBarHeight = 110
#values related to the bottom bar
bottomBarHeight = 200

windowHeight = topBarHeight + bottomBarHeight + arenaWindowHeight
windowWidth = sideBarWidthL + sideBarWidthR + arenaWindowWidth

screen = None
font = None

#Stuff for the info bars
startTime = datetime.datetime.now()
with open(r"assets\templates\TopBar.txt", "r", encoding="utf-8") as template:
    topBarTemplate = template.readlines()
clock = pygame.time.Clock()

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
    screen_y = arenaWindowHeight - y*scale - margin
    
    return screen_x, screen_y
        
def renderMap():
    frameColour = (0, 255, 255)
    arenaBGColour = "white"
    arenaOutlineColour = "black"
    
    surface = pygame.Surface((arenaWindowWidth, arenaWindowHeight))
    surface.fill(arenaBGColour)

    pygame.draw.rect(surface, frameColour, (0, 0, arenaWindowWidth, arenaWindowHeight), width=4) #add a black border to seprate from window
    
    for start, end in walls:
        startPos = worldToScreenCoords(*start)
        endPos = worldToScreenCoords(*end)
        pygame.draw.line(surface, arenaOutlineColour, startPos, endPos, width=3)
    for start, end in lines:
        startPos = worldToScreenCoords(*start)
        endPos = worldToScreenCoords(*end)
        pygame.draw.line(surface, arenaOutlineColour, startPos, endPos, width=3)
    for start, end, colour in customMarkings:
        startPos = worldToScreenCoords(*start)
        endPos = worldToScreenCoords(*end)
        pygame.draw.line(surface, colour, startPos, endPos, width=3)


    return surface

def renderBalls(surface, balls : list[Ball]):
    if balls is None:
        return surface
    for ball in balls:
        x,y = worldToScreenCoords(ball.transform.worldx, ball.transform.worldy)
        r = ball.diameter/10
        colour = ball.colour
        center = pygame.math.Vector2(x,y)
        pygame.draw.circle(surface, colour, center, r, width=1)
    return surface

def renderTargetBalls(surface, ball : Ball):
    if ball is None:
        return surface
    x,y = worldToScreenCoords(ball.transform.worldx, ball.transform.worldy)
    r = ball.diameter/10
    colour = ball.colour
    center = pygame.math.Vector2(x,y)
    margin = 3
    rectLeft = int(x - r - margin)
    rectTop = int(y - r - margin)
    rectSize = int(2 * r + 2*margin)
    rectPoints = (rectLeft, rectTop, rectSize, rectSize)
    pygame.draw.circle(surface, colour, center, r, width=1)
    pygame.draw.rect(surface, "green", rectPoints, width=2) 
    return surface

def renderRobot(surface, robot : Robot):
    for start, end in robot.transform.worldBoxCoords:
        startPos = worldToScreenCoords(*start)
        endPos = worldToScreenCoords(*end)
        pygame.draw.line(surface, "black", startPos, endPos, width=2)
    return surface

def renderTopBar(font):
    #Surface initialisation
    surface = pygame.Surface((windowWidth, topBarHeight))
    surface.fill("black")
    
    #Variables to display
    currentTime = datetime.datetime.now().strftime('%H:%M:%S')
    fps = f"{clock.get_fps():.0f}"
    packets = 20
    statusCam = "●"
    statusSer = "●"
    statusTrack = "●"
    statusMap = "●"
    warnings = 0
    uptime = datetime.datetime.now() - startTime

    total_ms = int(uptime.total_seconds() * 1000)

    minutes = total_ms // 60000
    seconds = (total_ms % 60000) // 1000
    milli = (total_ms % 1000) // 10

    uptime_str = f"{minutes:02}:{seconds:02}:{milli:02}"
    
    lineHeight = font.get_linesize()
    
    #LINE 1, THE TOP BORDER
    text = font.render(topBarTemplate[0].rstrip("\r\n"), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (windowWidth//2,10)
    surface.blit(text, textRect)
    
    #LINE 2, THE TITLE AND TIME
    formatted = topBarTemplate[1].rstrip("\r\n").format(currentTime=currentTime)
    text = font.render(formatted, True, "white", None)
    textRect = text.get_rect()
    textRect.center = (windowWidth//2,10 + lineHeight)
    surface.blit(text, textRect)
    
    #LINE 3, DIAGNOSTIC DATA
    formatted = topBarTemplate[2].rstrip("\r\n").format(fps=fps, packet=packets, camera=statusCam, serial=statusSer, tracking=statusTrack, mapping=statusMap, uptime=uptime_str, warnings=warnings)
    text = font.render(formatted, True, "white", None)
    textRect = text.get_rect()
    textRect.center = (windowWidth//2,10 + 2*lineHeight)
    surface.blit(text, textRect)
    
    #LINE 4, THE BOTTOM BORDER
    text = font.render(topBarTemplate[3].rstrip("\r\n"), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (windowWidth//2,10 + 3*lineHeight)
    surface.blit(text, textRect)
    
    return surface

def init():
    pygame.init()
    font = pygame.font.Font(r"assets\fonts\FiraCode-Light.ttf", 22)
    print("Rendering window at " + str(windowWidth) + "x" + str(windowHeight))
    screen = pygame.display.set_mode((windowWidth, windowHeight))
    return screen, font

def render(screen, font, balls : list[Ball], targetBall : Ball, robot : Robot):
    if screen is None:
        print("YOU FORGOT TO INITIALISE")
        return None
    
    map_surface = renderMap()
    object_surface = pygame.Surface((windowWidth, windowHeight), pygame.SRCALPHA)
    object_surface = renderBalls(object_surface, balls)
    object_surface = renderTargetBalls(object_surface, targetBall)
    object_surface = renderRobot(object_surface, robot)
    topBarSurface = renderTopBar(font)
    map_surface.blit(object_surface, (0,0))
    
    screen.fill((10, 23, 12))
    screen.blit(map_surface, (sideBarWidthL, topBarHeight)) #Map Layer
    screen.blit(topBarSurface, (0,0)) #Top bar layer
    pygame.display.flip()

def debug():
    screen, font = init()

    running = True
    
    robot = Robot((134, 65), 5, 5, 0)
    ball = [Ball(66, "red")]
    big = Ball(66, "red")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        render(screen, font, None, None, robot)
        clock.tick()
        
debug()
        