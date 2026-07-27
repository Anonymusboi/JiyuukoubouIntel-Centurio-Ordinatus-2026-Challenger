import pygame
from mapping import Ball, Robot
import datetime
import random

class TopBarInfo():
    def __init__(self, packets=0, camera_status="҉", serial_status="҉", tracking_status="҉", mapping_status="҉", warnings=0):
        
        self.packets = packets
        self.warnings = warnings
        
        #STATUSES
        # † means FUNCTIONAL. 
        # ? means WARNING. 
        # ! means ERROR. 
        # × means FATAL ERROR or CANNOT CONTACT
        # ҉ means UNINITIALISED
        self.camera_status = camera_status
        self.serial_status = serial_status
        self.tracking_status = tracking_status
        self.mapping_status = mapping_status
    
    def updateInfo(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
class RobotInfoBar():
    def __init__(self, state="INIT", x=0, y=0, heading=0, linearVel=0, angularVel=0):
        self.state = state
        self.x = x
        self.y = y
        self.heading = heading
        self.linearVel = linearVel
        self.angularVel = angularVel
        
    def updateInfo(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            
        
arenaWidth = 180 + 28 #28 for the baskets
arenaHeight = 180 + 50 #50 for the robot start position

#Scale arena window (based on x value) proportional to arena,
margin = 50
arenaWindowHeight = 660
scale = (arenaWindowHeight - margin*2)/arenaHeight
arenaWindowWidth = int(scale*arenaWidth + margin*2 + 1)
#Values related to the left side bar.
sideBarWidthL = 431
sideBarHeightL = 660
#Values related to the right side bar
sideBarWidthR = 430
sideBarHeightR = 660
robotInfoData = RobotInfoBar()
#Values related to the top bar
topBarData = TopBarInfo()
topBarHeight = 110
#values related to the bottom bar
bottomBarHeight = 200

windowHeight = topBarHeight + bottomBarHeight + arenaWindowHeight 
windowWidth = sideBarWidthL + sideBarWidthR + arenaWindowWidth

screen = None
font = None

#Stuff for the info bars
#top bar info template
startTime = datetime.datetime.now()
with open(r"assets\templates\TopBar.txt", "r", encoding="utf-8") as template:
    topBarTemplate = template.readlines()
clock = pygame.time.Clock()
#right side bar info template
with open(r"assets\templates\sideBarR.txt", "r", encoding="utf-8") as template:
    sideBarRTemplate = template.readlines()
#left side bar info template
with open(r"assets\templates\sideBarL.txt", "r", encoding="utf-8") as template:
    sideBarLTemplate = template.readlines()
flavourtext = random.randrange(1,6)
path = r"assets\templates\Funny flavour text\\" + str(flavourtext) + ".txt"
with open(path, "r", encoding="utf-8") as template:
    prayer = template.readlines()
    
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
    
    packets = topBarData.packets
    statusCam = topBarData.camera_status
    statusSer = topBarData.serial_status
    statusTrack = topBarData.tracking_status
    statusMap = topBarData.mapping_status
    warnings = topBarData.warnings
    uptime = datetime.datetime.now() - startTime

    total_ms = int(uptime.total_seconds() * 1000)

    minutes = total_ms // 60000
    seconds = (total_ms % 60000) // 1000
    milli = (total_ms % 1000) // 10

    uptime_str = f"{minutes:02}:{seconds:02}:{milli:02}"
    
    lineHeight = font.get_linesize()
    AlignmentMargin = 5 #offset to align it with the side bars
    #LINE 1, THE TOP BORDER
    text = font.render(topBarTemplate[0].rstrip("\r\n"), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (windowWidth//2 + AlignmentMargin, 10)
    surface.blit(text, textRect)
    
    #LINE 2, THE TITLE AND TIME
    formatted = topBarTemplate[1].rstrip("\r\n").format(currentTime=currentTime)
    text = font.render(formatted, True, "white", None)
    textRect = text.get_rect()
    textRect.center = (windowWidth//2 + AlignmentMargin, 10 + lineHeight)
    surface.blit(text, textRect)
    
    #LINE 3, DIAGNOSTIC DATA
    formatted = topBarTemplate[2].rstrip("\r\n").format(fps=fps, packet=packets, camera=statusCam, serial=statusSer, tracking=statusTrack, mapping=statusMap, uptime=uptime_str, warnings=warnings)
    text = font.render(formatted, True, "white", None)
    textRect = text.get_rect()
    textRect.center = (windowWidth//2 + AlignmentMargin, 10 + 2*lineHeight)
    surface.blit(text, textRect)
    
    #LINE 4, THE BOTTOM BORDER
    text = font.render(topBarTemplate[3].rstrip("\r\n"), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (windowWidth//2 + AlignmentMargin, 10 + 3*lineHeight)
    surface.blit(text, textRect)
    
    return surface

def renderSideBarR(font):
    surface = pygame.Surface((sideBarWidthR, sideBarHeightR))
    surface.fill("black")
    
    #Variables to put in
    state = robotInfoData.state
    x = robotInfoData.x
    y = robotInfoData.y
    heading = robotInfoData.heading
    linearVel = robotInfoData.linearVel
    angularVel = robotInfoData.angularVel
    
    lineHeight = font.get_linesize()
    #LINE 1, STATE TRACKING
    #The states are: SEARCHING (finding balls), HUNTING (approaching singular ball),
    #HARVESTING(Collecting the ball),, FIRING (shooting the ball)
    formatted = sideBarRTemplate[0].rstrip("\r\n").format(state=state)
    text = font.render(formatted, True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15)
    surface.blit(text, textRect)
    
    #LINE 2, COORDINATE SYSTEM
    formatted = sideBarRTemplate[1].rstrip("\r\n").format(x=f"{x:.0f}", y=f"{y:.0f}")
    text = font.render(formatted, True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + lineHeight)
    surface.blit(text, textRect)
    
    #LINE 3, BORDER
    text = font.render(sideBarRTemplate[2].rstrip("\r\n"), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + 2*lineHeight)
    surface.blit(text, textRect)
    
    #LINE 4, ROBOT HEADING    
    formatted = sideBarRTemplate[3].rstrip("\r\n").format(heading=f"{heading:+.1f}")
    text = font.render(formatted, True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + 3*lineHeight)
    surface.blit(text, textRect)
    
    #COMPASS IMAGE
    for i in range(4,11):
        text = font.render(sideBarRTemplate[i].rstrip("\r\n"), True, "white", None)
        textRect = text.get_rect()
        textRect.center = (sideBarWidthL//2 + 5, 15 + i*lineHeight)
        surface.blit(text, textRect)
        
    #LINE 12, LINEAR VEL  
    formatted = sideBarRTemplate[11].rstrip("\r\n").format(linearVel=f"{linearVel:+.2f}")
    text = font.render(formatted, True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + 11*lineHeight)
    surface.blit(text, textRect)
    
    #LINE 13, ANGULAR VEL  
    formatted = sideBarRTemplate[12].rstrip("\r\n").format(angularVel=f"{angularVel:+.2f}")
    text = font.render(formatted, True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + 12*lineHeight)
    surface.blit(text, textRect)
        
    #LINE 14, BORDER
    text = font.render(sideBarRTemplate[13].rstrip("\r\n"), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + 13*lineHeight)
    surface.blit(text, textRect)

    #MOTOR INFO
    LTargetRPM = 0.23
    RTargetRPM = 0.23
    LActualRPM = 0.21
    RActualRPM = 0.21
    LErrorRPM = LTargetRPM - LActualRPM
    RErrorRPM = RTargetRPM - RActualRPM
    motorMode = "FWRD" #the 4 moves modes are FWRD, BACK, RGHT, LEFT
    packetDelay = 23
    
    #LINE 15, LEFT RIGHT indicator
    text = font.render(sideBarRTemplate[14].rstrip("\r\n"), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + 14*lineHeight)
    surface.blit(text, textRect)
    
    #LINE 16, TARGET RPM values
    text = font.render(sideBarRTemplate[15].rstrip("\r\n").format(LTargetRPM=f"{LTargetRPM:+.2f}", RTargetRPM=f"{RTargetRPM:+.2f}"), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + 15*lineHeight)
    surface.blit(text, textRect)

    #LINE 17, ACTUAL RPM values
    text = font.render(sideBarRTemplate[16].rstrip("\r\n").format(LActualRPM=f"{LActualRPM:+.2f}", RActualRPM=f"{RActualRPM:+.2f}"), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + 16*lineHeight)
    surface.blit(text, textRect)
    
    #LINE 18, ERROR RPM values
    text = font.render(sideBarRTemplate[17].rstrip("\r\n").format(LErrorRPM=f"{LErrorRPM:+.2f}", RErrorRPM=f"{RErrorRPM:+.2f}"), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + 17*lineHeight)
    surface.blit(text, textRect)
    
    #LINE 19, BLANK SPACE
    text = font.render(sideBarRTemplate[18].rstrip("\r\n"), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + 18*lineHeight)
    surface.blit(text, textRect)
    
    #LINE 20, MOVE MODE indicator
    text = font.render(sideBarRTemplate[19].rstrip("\r\n").format(motorMode=motorMode), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + 19*lineHeight)
    surface.blit(text, textRect)
    
    #LINE 21, PACKET DELAY value
    text = font.render(sideBarRTemplate[20].rstrip("\r\n").format(packetDelay=f"{packetDelay:.0f}"), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + 20*lineHeight)
    surface.blit(text, textRect)
    
    #LINE 22, BORDER
    text = font.render(sideBarRTemplate[21].rstrip("\r\n"), True, "white", None)
    textRect = text.get_rect()
    textRect.center = (sideBarWidthL//2 + 5, 15 + 21*lineHeight)
    surface.blit(text, textRect)
    
    return surface


def renderSideBarL(font):
    surface = pygame.Surface((sideBarWidthL, sideBarHeightL))
    surface.fill("black")
    
    lineHeight = font.get_linesize()
    for i in range(0, 22):
        text = font.render(sideBarLTemplate[i].rstrip("\r\n"), True, "white", None)
        textRect = text.get_rect()
        textRect.center = (sideBarWidthL//2 + 5, 15 + i*lineHeight)
        surface.blit(text, textRect)

    
    prayerSurfaceHeight = lineHeight*7
    prayerSurfaceWidth = 22*32
    prayerSurface = pygame.Surface((prayerSurfaceWidth, prayerSurfaceHeight), pygame.SRCALPHA)
    prayerFont = pygame.font.Font(r"assets\fonts\RobotoMono-ExtraLight.ttf", 14)
    prayerLineHeight = prayerFont.get_linesize()
    for i in range(0, len(prayer) - 2):
        text = prayerFont.render(prayer[i].rstrip("\r\n"), True, "white", None)
        textRect = text.get_rect()
        textRect.center = (sideBarWidthL//2 + 5, 15 + i*prayerLineHeight)
        prayerSurface.blit(text, textRect)
    
    surface.blit(prayerSurface, (0, lineHeight*14))
    return surface
    
    
def init():
    #topBarData.updateInfo(packets=20, camera_status="?", serial_status="†", tracking_status="†", mapping_status="!", warnings=0)
    #robotInfoData.updateInfo(state="HARVESTING", x=23, y=240, heading=113.2, linearVel=0.43, angularVel=2.12)
    pygame.init()
    font = pygame.font.Font(r"assets\fonts\RobotoMono-ExtraLight.ttf", 22)
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
    sideBarRSurface = renderSideBarR(font)
    sideBarLSurface = renderSideBarL(font)
    map_surface.blit(object_surface, (0,0))
    
    screen.fill((10, 23, 12))
    screen.blit(map_surface, (sideBarWidthL, topBarHeight)) #Map Layer
    screen.blit(topBarSurface, (0,0)) #Top bar layer
    screen.blit(sideBarRSurface, (windowWidth - sideBarWidthR, topBarHeight))
    screen.blit(sideBarLSurface, (0, topBarHeight))
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
        