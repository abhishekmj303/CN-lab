import pygame
import json
import os

class GameState(object):
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)

    def __init__(self, H=0, W=0,
                 FourPlayers=False, 
                 p1x=0, p1y=0, 
                 p2x=0, p2y=0, 
                 p3x=0, p3y=0, 
                 p4x=0, p4y=0, 
                 ball_thrower=0,
                 p1score=0,p2score=0,p3score=0,p4score=0,
                 dmH=0,dmW=0,
                 paddle_width_v=0,paddle_height_v=0,
                 paddle_height_h=0,paddle_width_h=0,
                 bx=0,by=0,bw=0,
                 velocity_raito=0,
                 bxv=0,byv=0,
                 *args, **kwargs):
        self.H = H
        self.W = W
        self.FourPlayers = FourPlayers
        self.p1x = p1x
        self.p1y = p1y
        self.p2x = p2x
        self.p2y = p2y
        self.p3x = p3x
        self.p3y = p3y
        self.p4x = p4x
        self.p4y = p4y
        self.ball_thrower=ball_thrower
        self.p1score=p1score
        self.p2score=p2score
        self.p3score=p3score
        self.p4score=p4score
        self.dmH=dmH
        self.dmW=dmW
        self.paddle_width_v=paddle_width_v
        self.paddle_width_h=paddle_width_h
        self.paddle_height_v=paddle_height_v
        self.paddle_height_h=paddle_height_h
        self.bx=bx
        self.by=by
        self.bw=bw
        self.velocity_raito=velocity_raito
        self.bxv=bxv
        self.byv=byv

    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return cls(**json_dict)

gs = GameState()

### Colors
WHITE = (205, 214, 244)
RED = (243, 139, 168)
GREEN = (166, 227, 161)
BLUE = (137, 180, 250)
YELLOW = (249, 226, 175)
BLACK = (17, 17, 27)

#Colors of players
py1_Color = RED
py2_Color = GREEN
py3_Color = BLUE
py4_Color = YELLOW

### Constants
gs.W = 600 # Width of the game table
gs.H = gs.W # Height of the game table Game should be a square always to be fair for 4 player game
screen = pygame.display.set_mode((gs.W, gs.H)) # Screen

gs.FourPlayers = False ## 2 Players or 4 Players mode

### PY GAME FONT
pygame.font.init()
font = pygame.font.SysFont('JetBrainsMono Nerd Font', 20)

### Variables
wt = 10 #thread update wait time 

#Player Coordinates
gs.p1x = gs.W/30
gs.p1y = gs.H/2 - ((gs.W/60)**2)/2

gs.p2x = gs.W-(gs.W/30)
gs.p2y = gs.H/2 - ((gs.W/60)**2)/2

if gs.FourPlayers:
    gs.p3x = gs.W/2 - ((gs.H/60)**2)/2
    gs.p3y = gs.H/30

    gs.p4x = gs.W/2 - ((gs.H/60)**2)/2
    gs.p4y = gs.H-(gs.H/30)

gs.ball_thrower = 0 #No player is ball thrower in the first run, to get score the corresponding player should throw the ball, it is a little bit different in my game original one because of 4 play rules.

#Player Scores
gs.p1score = 0
gs.p2score = 0

if gs.FourPlayers:
    gs.p3score = 0
    gs.p4score = 0 

# W-S Key Params
w_p = False
s_p = False
wsr = False
# Up-Down Key Params
up_p = False
down_p = False
udr = False

if gs.FourPlayers:
    # A-D Key Params
    a_p = False
    d_p = False
    adr = False
    # Left-Right Key Params
    left_p = False
    right_p = False
    lrr = False

##Screen Margins for Paddles
gs.dmH = gs.H/40
gs.dmW = gs.W/40

#Vertical Players Paddle Size (Players which stands right and left)
gs.paddle_width_v = gs.W/60
gs.paddle_height_v = gs.paddle_width_v**2

#Horizontal Players Paddle Size (Players which stands up and down)
gs.paddle_height_h = gs.H/60
gs.paddle_width_h = gs.paddle_height_h**2

## Ball Geometry
gs.bx = gs.W/2 #Ball X Position
gs.by = gs.H/2 #Ball Y Position
gs.bw = gs.W/65 #Ball diameter

## Ball Velocity 
gs.velocity_raito = 240 #Initial velocity ratio (bigger makes the game slower, smaller makes the game faster)
gs.bxv = -gs.H/gs.velocity_raito # Ball X Velocity
gs.byv = 0 #Ball Y Velocity

### Functions
def drawpaddle(screen, x, y, w, h, color=WHITE):
    pygame.draw.rect(screen, color, (x, y, w, h))

def drawball(screen, x, y, bw):
    pygame.draw.circle(screen, WHITE, (int(x), int(y)), int(bw))


def uploc(): 
    ''' 
    Updates Player Locations
    ''' 
    global gs

    if w_p:
        if gs.p1y-gs.dmH < 0:
            gs.py1 = 0
        else:
            gs.p1y -= gs.dmH
    elif s_p:
        if gs.p1y+gs.dmH+gs.paddle_height_v > gs.H:
            gs.p1y = gs.H-gs.paddle_height_v
        else:
            gs.p1y += gs.dmH

    if up_p:
        if gs.p2y-gs.dmH < 0:
            gs.p2y = 0
        else:
            gs.p2y -= gs.dmH
    elif down_p:
        if gs.p2y+gs.dmH+gs.paddle_height_v > gs.H:
            gs.p2y = gs.H-gs.paddle_height_v
        else:
            gs.p2y += gs.dmH

    if gs.FourPlayers:
        if a_p:
            if gs.p3x-gs.dmW<0:
                gs.p3x = 0
            else:
                gs.p3x -=gs.dmW
        elif d_p:
            if gs.p3x+gs.dmW+gs.paddle_width_h>gs.W:
                gs.p3x = gs.W-gs.paddle_width_h
            else:
                gs.p3x += gs.dmW

        if left_p:
            if gs.p4x-gs.dmW<0:
                gs.p4x = 0
            else:
                gs.p4x -=gs.dmW
        elif right_p:
            if gs.p4x+gs.dmW+gs.paddle_width_h>gs.W:
                gs.p4x = gs.W-gs.paddle_width_h
            else:
                gs.p4x += gs.dmW


def upscr():
    '''
    Updates Score
    '''
    global gs
    if gs.ball_thrower == 1:
        gs.p1score += 1
    elif gs.ball_thrower == 2:
        gs.p2score += 1
    elif gs.FourPlayers:
        if gs.ball_thrower == 3:
            gs.p3score += 1
        elif gs.ball_thrower == 4:
            gs.p4score += 1

    gs.ball_thrower = 0 #Set Ball thrower 0 to be fair, when the corresponding player throws then begin to score it.
 

def upblnv():
    ''' 
    Updates Ball
    ''' 
    # global gs.ball_thrower

    # global gs.bx
    # global gs.bxv
    # global gs.by
    # global gs.byv

    # if gs.FourPlayers:
    #     global gs.p4score
    #     global gs.p3score

    # global gs.p2score
    # global gs.p1score
    
    global gs

    '''
    Updates score according to the last ball thrower
    '''
    
    if (gs.bx+gs.bxv < gs.p1x+gs.paddle_width_v) and ((gs.p1y < gs.by+gs.byv+gs.bw) and (gs.by+gs.byv-gs.bw < gs.p1y+gs.paddle_height_v)):
        gs.bxv = -gs.bxv
        gs.byv = ((gs.p1y+(gs.p1y+gs.paddle_height_v))/2)-gs.by
        gs.byv = -gs.byv/((5*gs.bw)/7)
        gs.ball_thrower = 1
    elif gs.bx+gs.bxv < 0:
        upscr()
        gs.bx = gs.W/2
        gs.bxv = gs.H/gs.velocity_raito
        gs.by = gs.H/2
        gs.byv = 0

    if (gs.bx+gs.bxv > gs.p2x) and ((gs.p2y < gs.by+gs.byv+gs.bw) and (gs.by+gs.byv-gs.bw < gs.p2y+gs.paddle_height_v)):
        gs.bxv = -gs.bxv
        gs.byv = ((gs.p2y+(gs.p2y+gs.paddle_height_v))/2)-gs.by
        gs.byv = -gs.byv/((5*gs.bw)/7)
        gs.ball_thrower = 2
    elif gs.bx+gs.bxv > gs.W:
        upscr()
        gs.bx = gs.W/2
        gs.bxv = -gs.H/gs.velocity_raito
        gs.by = gs.H/2
        gs.byv = 0

    
    if gs.FourPlayers:##4 Player Mode        
        if (gs.by+gs.byv < gs.p3y+gs.paddle_height_h) and ((gs.p3x < gs.bx+gs.bxv+gs.bw) and (gs.bx+gs.bxv-gs.bw < gs.p3x+gs.paddle_width_h)):
            gs.byv = -gs.byv
            gs.bxv = ((gs.p3x+(gs.p3x+gs.paddle_width_h))/2)-gs.bx
            gs.bxv = -gs.bxv/((5*gs.bw)/7)
            gs.ball_thrower = 3
        elif gs.by+gs.byv < 0:
            upscr()
            gs.by = gs.H/2
            gs.byv = gs.W/gs.velocity_raito
            gs.bx = gs.W/2
            gs.bxv = 0

        if (gs.by+gs.byv > gs.p4y) and ((gs.p4x < gs.bx+gs.bxv+gs.bw) and (gs.bx+gs.bxv-gs.bw < gs.p4x+gs.paddle_width_h)):
            gs.byv = -gs.byv
            gs.bxv = ((gs.p4x+(gs.p4x+gs.paddle_width_h))/2)-gs.bx
            gs.bxv = -gs.bxv/((5*gs.bw)/7)
            gs.ball_thrower = 4
        elif gs.by+gs.byv > gs.H:
            upscr()
            gs.by = gs.H/2
            gs.byv = -gs.W/gs.velocity_raito
            gs.bx = gs.W/2
            gs.bxv = 0
    else:##2 Player Mode    
        if gs.by+gs.byv > gs.H or gs.by+gs.byv < 0:
            gs.byv = -gs.byv
        
    gs.bx += gs.bxv
    gs.by += gs.byv

def drawscore(screen, font, H, FourPlayers, gs):
    screen.blit(font.render("Score", False, WHITE), (30,30))
    
    screen.blit(font.render(f"{gs.p1score}",False,py1_Color),(H/5,30))
    screen.blit(font.render(f"{gs.p2score}",False,py2_Color),(2*H/5,30))
    
    if FourPlayers:
        screen.blit(font.render(f"{gs.p3score}",False,py3_Color),(3*H/5,30))
        screen.blit(font.render(f"{gs.p4score}",False,py4_Color),(4*H/5,30))


def game_loop():
    global w_p, s_p, wsr, up_p, down_p, udr, a_p, d_p, adr, left_p, right_p, lrr
    global gs

    playerCount = 2
    if gs.FourPlayers:
        playerCount = 4   
    pygame.display.set_caption(f'Pong for {playerCount} Players')

    screen.fill(BLACK)
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_w:
                    w_p = True
                    if s_p == True:
                        s_p = False
                        wsr = True
                if event.key == pygame.K_s:
                    s_p = True
                    if w_p == True:
                        w_p = False
                        wsr = True
                if event.key == pygame.K_UP:
                    up_p = True
                    if down_p == True:
                        down_p = False
                        udr = True
                if event.key == pygame.K_DOWN:
                    down_p = True
                    if up_p == True:
                        up_p = False
                        udr = True

                if gs.FourPlayers:
                    if event.key == pygame.K_a:
                        a_p = True
                        if d_p == True:
                            a_p = False
                            adr = True
                    if event.key == pygame.K_d:
                        d_p = True
                        if a_p == True:
                            d_p = False
                            adr = True
                    if event.key == pygame.K_LEFT:
                        left_p = True
                        if right_p == True:
                            left_p = False
                            lrr = True
                    if event.key == pygame.K_RIGHT:
                        right_p = True
                        if left_p == True:
                            right_p = False
                            lrr = True

                # uploc()
                # upblnv()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    w_p = False
                    if wsr == True:
                        s_p = True
                        wsr = False
                if event.key == pygame.K_s:
                    s_p = False
                    if wsr == True:
                        w_p = True
                        wsr = False
                if event.key == pygame.K_UP:
                    up_p = False
                    if udr == True:
                        down_p = True
                        udr = False
                if event.key == pygame.K_DOWN:
                    down_p = False
                    if udr == True:
                        up_p = True
                        udr = False

                if gs.FourPlayers:
                    if event.key == pygame.K_a:
                        a_p = False
                        if adr == True:
                            d_p = True
                            adr = False
                    if event.key == pygame.K_d:
                        d_p = False
                        if adr == True:
                            a_p = True
                            adr = False
                    if event.key == pygame.K_LEFT:
                        left_p = False
                        if lrr == True:
                            right_p = True
                            lrr = False
                    if event.key == pygame.K_RIGHT:
                        right_p = False
                        if lrr == True:
                            left_p = True
                            lrr = False


        screen.fill(BLACK)
        uploc()
        upblnv()
        drawscore(screen, font, gs.H, gs.FourPlayers, gs)
        drawball(screen, gs.bx, gs.by, gs.bw)

        drawpaddle(screen, gs.p1x, gs.p1y, gs.paddle_width_v, gs.paddle_height_v, py1_Color) 
        drawpaddle(screen, gs.p2x, gs.p2y, gs.paddle_width_v, gs.paddle_height_v, py2_Color)

        if gs.FourPlayers:
            drawpaddle(screen, gs.p3x, gs.p3y, gs.paddle_width_h, gs.paddle_height_h, py3_Color)
            drawpaddle(screen, gs.p4x, gs.p4y, gs.paddle_width_h, gs.paddle_height_h, py4_Color)

        pygame.display.flip()
        pygame.time.wait(wt)
        # print("gameloop p1score: ", gs.p1score)
    
    os._exit(0)


### Initialize
if __name__ == "__main__":
    game_loop()