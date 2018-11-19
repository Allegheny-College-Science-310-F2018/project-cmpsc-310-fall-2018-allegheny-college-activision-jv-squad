import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random

# TODO: In order to get the AI to go to the ball, we will need to take the two
# locations and make some linear linear equation for it using the line formula.
# Then, we use the slope of this line in order to get some rise over run
# fraction. We the use this to develop a sequence of inputs to be passed through
# the movement function so that the AI moves to the ball.

def setup():
    pygame.init()
    pygame.font.init()
    myfont = pygame.font.SysFont('Georgia', 18, bold=True)
    screen = pygame.display.set_mode((700, 400))
    space = pymunk.Space()
    space.gravity = (0.0, 0.0)
    space.damping = .97
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    clock = pygame.time.Clock()
    return screen, space, draw_options, clock, myfont

def createBorder(space):
    static_body = space.static_body
    static_lines = list()
    static_lines.append(pymunk.Segment(static_body, (25.0, 25.0), (675.0, 25.0), 2.0))
    static_lines.append(pymunk.Segment(static_body, (25.0, 25.0), (25.0, 133.0), 2.0))
    static_lines.append(pymunk.Segment(static_body, (25.0, 266.0), (25.0, 375.0), 2.0))
    static_lines.append(pymunk.Segment(static_body, (25.0, 375.0), (675.0, 375.0), 2.0))
    static_lines.append(pymunk.Segment(static_body, (675.0, 25.0), (675.0, 133.0), 2.0))
    static_lines.append(pymunk.Segment(static_body, (675.0, 266.0), (675.0, 375.0), 2.0))
    for line in static_lines:
        line.elasticity = .95
        line.friction = .1
        line.color = pygame.color.THECOLORS["white"]
    return static_lines

def goalCheck(ball):
    if ball.position.x < 25.0:
        return "team1"
    if ball.position.x > 675.0:
        return "team2"
    return None


def draw_lines(screen):
    pygame.draw.line(screen, (255, 255, 255), (25, 120), (125, 120))
    pygame.draw.line(screen, (255, 255, 255), (25, 279), (125, 279))
    pygame.draw.line(screen, (255, 255, 255), (125, 120), (125, 279))
    pygame.draw.line(screen, (255, 255, 255), (675, 120), (575, 120))
    pygame.draw.line(screen, (255, 255, 255), (675, 279), (575, 279))
    pygame.draw.line(screen, (255, 255, 255), (575, 120), (575, 279))
    pygame.draw.line(screen, (255, 255, 255), (350, 25), (350, 375))
    pygame.draw.line(screen, (158, 158, 158), (25, 133), (25, 266))
    pygame.draw.line(screen, (158, 158, 158), (675, 133), (675, 266))

def createBall(space, friction, mass, radius, x, y, color):
    inertia = pymunk.moment_for_circle(mass, 0, radius, (0,0))
    body = pymunk.Body(mass, inertia)
    body.position = x, y
    shape = pymunk.Circle(body, radius, (0,0))
    shape.collision_type = 3
    shape.elasticity = .9
    shape.friction = friction
    shape.color = pygame.color.THECOLORS[color]
    space.add(body, shape)
    return body

def get_distance(obj1, obj2):
    x1 = obj1.position.x
    y1 = obj1.position.y
    x2 = obj2.position.x
    y2 = obj2.position.y
    distance = (x2 - x1)**2 + (y2 - y1)**2
    distance = math.sqrt(distance)
    return distance

def make_impulse(player, ball, magnitude):
    if (get_distance(player, ball) < (list(player.shapes)[0].radius + list(ball.shapes)[0].radius)):
        impulse = Vec2d(-1*(player.position.x-ball.position.x)*(magnitude), -1*(player.position.y-ball.position.y)*(magnitude))
        ball.apply_impulse_at_world_point((impulse), (player.position))

def move_player(player, speeds, keys, top_speed, acceleration):
    if (keys[K_UP]):
        if (speeds[0] > top_speed):
            speeds[0] = top_speed
        else:
            speeds[0] = speeds[0] + acceleration
        player.position += Vec2d(0,1) * speeds[0]
    else:
        if (speeds[0] <= 0):
            speeds[0] = 0
        else:
            speeds[0] = speeds[0] - acceleration
        player.position += Vec2d(0,1) * speeds[0]
    if (keys[K_DOWN]):
        if (speeds[1] > top_speed):
            speeds[1] = top_speed
        else:
            speeds[1] = speeds[1] + acceleration
        player.position += Vec2d(0,-1) * speeds[1]
    else:
        if (speeds[1] <= 0):
            speeds[1] = 0
        else:
            speeds[1] = speeds[1] - acceleration
        player.position += Vec2d(0,-1) * speeds[1]
    if (keys[K_LEFT]):
        if (speeds[2] > top_speed):
            speeds[2] = top_speed
        else:
            speeds[2] = speeds[2] + acceleration
        player.position += Vec2d(-1,0) * speeds[2]
    else:
        if (speeds[2] <= 0):
            speeds[2] = 0
        else:
            speeds[2] = speeds[2] - acceleration
        player.position += Vec2d(-1,0) * speeds[2]
    if (keys[K_RIGHT]):
        if (speeds[3] > top_speed):
            speeds[3] = top_speed
        else:
            speeds[3] = speeds[3] + acceleration
        player.position += Vec2d(1,0) * speeds[3]
    else:
        if (speeds[3] <= 0):
            speeds[3] = 0
        else:
            speeds[3] = speeds[3] - acceleration
        player.position += Vec2d(1,0) * speeds[3]
    return speeds

def run():
    screen, space, draw_options, clock, myfont = setup()
    space.add(createBorder(space))
    running = True
    ball = createBall(space, .1, 3, 10, 350, 200, "white")
    player = createBall(space, 1.0, 1000000, 13, 100, 200, "dodgerblue4")

    team1Score = 0
    team2Score = 0

    speeds = [0,0,0,0]
    acceleration = .1
    top_speed = 3.0

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == KEYDOWN and event.key == K_p:
                pygame.image.save(screen, "bouncing_balls.png")

        goalChecker = goalCheck(ball)
        if (goalChecker == "team1"):
            team1Score = team1Score + 1
            space.remove(ball, player)
            ball = createBall(space, .1, 3, 10, 350, 200, "white")
            player = createBall(space, 1.0, 1000000, 13, 100, 200, "dodgerblue4")
        elif (goalChecker == "team2"):
            team2Score = team2Score + 1
            space.remove(ball, player)
            ball = createBall(space, .1, 3, 10, 350, 200, "white")
            player = createBall(space, 1.0, 1000000, 13, 100, 200, "dodgerblue4")

        if (team1Score >= 3 and team1Score - team2Score > 1):
            textsurface = myfont.render('Team 1 Wins! ', False, (255, 255, 255))
            screen.blit(textsurface,(275,100))
            time.sleep(5)
            break
        if(team2Score >= 3 and team2Score - team1Score > 1):
            textsurface = myfont.render('Team 2 Wins! ', False, (255, 255, 255))
            screen.blit(textsurface,(275,100))
            time.sleep(5)
            break

        keys = pygame.key.get_pressed()

        speeds = move_player(player, speeds, keys, top_speed, acceleration)

        make_impulse(player, ball, (1/5))

        screen.fill(pygame.Color(21, 155, 50, 1))
        draw_lines(screen)
        space.debug_draw(draw_options)
        # Code that is commented will display text for the score
        #textsurface = myfont.render('Team 1 score %s' % (team1Score), False, (255, 255, 255))
        textsurface = myfont.render('Team 1: %s | Team 2: %s' % (str(team1Score), str(team2Score)), False, (255, 255, 255))
        screen.blit(textsurface,(275,0))
        dt = 1.0/60.0
        for x in range(10):
            space.step(dt)
        pygame.display.flip()
        clock.tick(50)
        pygame.display.set_caption("fps: " + str(clock.get_fps()))

def main():
    run()

if __name__ == '__main__':
    main()
