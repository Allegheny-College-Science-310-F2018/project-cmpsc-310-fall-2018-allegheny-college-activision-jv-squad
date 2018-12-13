import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random
import time
from fractions import Fraction
from random import randint

START_TIME = time.time()
STATE_CHANGES = []

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
    return body, shape

def path_find(ai_player, ai_goal_location_x, ai_goal_location_y, speeds, acceleration, top_speed, offense=True):
    keys_to_press = list()

    ai_current_path_y = ai_goal_location_y - ai_player.position.y # Up / Down

    if offense and ai_current_path_y > 80:
        ai_current_path_y = ai_current_path_y + 7.5
    elif offense and ai_current_path_y < -80:
        ai_current_path_y = ai_current_path_y - 7.5

    total = 0
    current_speed = max(abs(speeds[0]),abs(speeds[1]))
    iterations = 0.

    while total < abs(ai_current_path_y):
        iterations = iterations + 1
        total = total + current_speed
        if current_speed < top_speed:
            current_speed = current_speed + acceleration

    # Accounting for deceleration
    if (abs(ai_current_path_y) < 60):
        iterations = iterations * .7
    else:
        iterations = iterations * .675

    for i in range(0, int(iterations)):
        keys = [0 for i in range(0,323)]
        if ai_current_path_y >= 0:
            keys[K_UP] = 1
        else:
            keys[K_DOWN] = 1
        keys_to_press.append(tuple(keys))

    ai_current_path_x = ai_goal_location_x - ai_player.position.x # Left / Right

    for i in range(0, abs(int(ai_current_path_x/3))):
        keys = [0 for i in range(0,323)]
        if ai_current_path_x >= 0:
            keys[K_RIGHT] = 1
        else:
            keys[K_LEFT] = 1
        keys_to_press.append(tuple(keys))

    return keys_to_press

def play_defense(ball):
    x = 655
    y = ball.position.y
    if y > 266:
        y = 266
    elif y < 133:
        y = 133
    return x, y

def switch_state(defense, hit_ball, ball, ai_player, player):
    global STATE_CHANGES
    global START_TIME
    if defense and (hit_ball or (ai_player.position.x > 650 and get_distance(ball, player) - get_distance(ball, ai_player) >= 100)):
        print(get_distance(ball, player))
        print(get_distance(ball, ai_player))
        print(get_distance(ball, player) - get_distance(ball, ai_player) >= 100)
        print("Switching to offense!")
        STATE_CHANGES.append(time.time()-START_TIME)
        return False, True
    elif not defense:
        if ball.position.x - 25 >= ai_player.position.x:
            print("Switching to defense!")
            STATE_CHANGES.append(time.time()-START_TIME)
            return True, True
    return defense, False


def shoot(player, ball, keys_to_press, defending):
    if player.position.x <= ball.position.x or get_distance(player, ball) > (list(player.shapes)[0].radius + list(ball.shapes)[0].radius) + 1:
        return keys_to_press, False
    to_press = list()
    print("SHOOTING")
    if defending:
        if abs(player.position.y - ball.position.y) <= 5:
            # Left
            keys = [0 for i in range(0,323)]
            keys[K_LEFT] = 1
            for i in range(0, 13):
                to_press.append(tuple(keys))
            return to_press, True
        elif player.position.y > ball.position.y:
            # Left down
            keys = [0 for i in range(0,323)]
            keys[K_LEFT] = 1
            keys[K_DOWN] = 1
            for i in range(0, 13):
                to_press.append(tuple(keys))
            return to_press, True
        else:
            # Left up
            keys = [0 for i in range(0,323)]
            keys[K_LEFT] = 1
            keys[K_UP] = 1
            for i in range(0, 13):
                to_press.append(tuple(keys))
            return to_press, True
    else:
        if 180 <= ball.position.y <= 220:
            # Left
            keys = [0 for i in range(0,323)]
            keys[K_LEFT] = 1
            for i in range(0, 13):
                to_press.append(tuple(keys))
            return to_press, True
        elif ball.position.y > 220:
            # Left down
            keys = [0 for i in range(0,323)]
            keys[K_LEFT] = 1
            keys[K_DOWN] = 1
            for i in range(0, 13):
                to_press.append(tuple(keys))
            return to_press, True
        else:
            # Left up
            keys = [0 for i in range(0,323)]
            keys[K_LEFT] = 1
            keys[K_UP] = 1
            for i in range(0, 13):
                to_press.append(tuple(keys))
            return to_press, True

def get_distance(obj1, obj2):
    x1 = obj1.position.x
    y1 = obj1.position.y
    x2 = obj2.position.x
    y2 = obj2.position.y
    distance = (x2 - x1)**2 + (y2 - y1)**2
    distance = math.sqrt(distance)
    return distance

def make_impulse(player, ball, magnitude, speeds):
    magnitude1 = magnitude + (max(speeds)/ (len(speeds)*2))
    if (get_distance(player, ball) < (list(player.shapes)[0].radius + list(ball.shapes)[0].radius)):
        impulse = Vec2d(-1*(player.position.x-ball.position.x)*(magnitude1), -1*(player.position.y-ball.position.y)*(magnitude1))
        ball.apply_impulse_at_world_point((impulse), (player.position))
        return True

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

def print_direction(keys):
    dir = ""
    if keys[K_UP]:
        dir = dir + "UP "
    if keys[K_DOWN]:
        dir = dir + "DOWN "
    if keys[K_LEFT]:
        dir = dir + "LEFT "
    if keys[K_RIGHT]:
        dir = dir + "RIGHT "
    print(dir)

def reset_ball(ball, ball_shape, space):
    if ball.position.y < 25:
        space.remove(ball, ball_shape)
        ball, ball_shape = createBall(space, .1, 3, 10, ball.position.x, 30, "white")
    elif ball.position.y > 375:
        space.remove(ball, ball_shape)
        ball, ball_shape = createBall(space, .1, 3, 10, ball.position.x, 370, "white")
    if ball.position.x < 25 and (ball.position.y < 130 or ball.position.y > 270):
        space.remove(ball, ball_shape)
        ball, ball_shape = createBall(space, .1, 3, 10, 30, ball.position.y, "white")
    elif ball.position.x > 675 and (ball.position.y < 130 or ball.position.y > 270):
        space.remove(ball, ball_shape)
        ball, ball_shape = createBall(space, .1, 3, 10, 670, ball.position.y, "white")
    return ball, ball_shape

def game_over(screen, space, draw_options, ball, ball_shape, player, player_shape, ai_player, ai_player_shape, team):
    myfont = pygame.font.SysFont('Georgia', 30, bold=True)
    textsurface = myfont.render(str(team)+' Wins! ', False, (255, 255, 255))
    screen.fill(pygame.Color(21, 155, 50, 1))
    screen.blit(textsurface,(253,100))
    draw_lines(screen)
    space.remove(ball, ball_shape)
    space.remove(player, player_shape)
    space.remove(ai_player, ai_player_shape)
    space.debug_draw(draw_options)
    pygame.display.flip()
    time.sleep(5)

def run():
    screen, space, draw_options, clock, myfont = setup()
    border = createBorder(space)
    space.add(border)

    running = True

    ball, ball_shape = createBall(space, .1, 3, 10, 350, 200, "white")
    player, player_shape = createBall(space, 1.0, 1000000, 13, 100, 200, "dodgerblue4")
    ai_player, ai_player_shape = createBall(space, 1.0, 1000000, 13, 600, 200, "red3")

    ai_keys_to_press = []
    ai_goal_location_x = 0
    ai_goal_location_y = 0

    team1Score = 0
    team2Score = 0

    speeds = [0,0,0,0]
    speeds_ai = [0,0,0,0]
    acceleration = .1
    top_speed = 3.0

    hit_ball = False
    defense = False
    just_switched = False

    if randint(0, 1) == 0:
        defense = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == KEYDOWN and event.key == K_p:
                pygame.image.save(screen, "game_screenshot.png")

        # Physics Problems
        ball, ball_shape = reset_ball(ball, ball_shape, space)

        # Check for score
        goalChecker = goalCheck(ball)
        if (goalChecker == "team1"):
            team1Score = team1Score + 1
            space.remove(ball, ball_shape)
            space.remove(player, player_shape)
            space.remove(ai_player, ai_player_shape)
            pygame.display.update()
            speeds = [0,0,0,0]
            speeds_ai = [0,0,0,0]
            ai_keys_to_press = []
            ai_goal_location_x = 0
            ai_goal_location_y = 0
            ball, ball_shape = createBall(space, .1, 3, 10, 350, 200, "white")
            player, player_shape = createBall(space, 1.0, 1000000, 13, 100, 200, "dodgerblue4")
            ai_player, ai_player_shape = createBall(space, 1.0, 1000000, 13, 600, 200, "red3")
            defense = False
            if randint(0, 1) == 0:
                defense = True
        elif (goalChecker == "team2"):
            team2Score = team2Score + 1
            space.remove(ball, ball_shape)
            space.remove(player, player_shape)
            space.remove(ai_player, ai_player_shape)
            pygame.display.update()
            speeds = [0,0,0,0]
            speeds_ai = [0,0,0,0]
            ai_keys_to_press = []
            ai_goal_location_x = 0
            ai_goal_location_y = 0
            ball, ball_shape = createBall(space, .1, 3, 10, 350, 200, "white")
            player, player_shape = createBall(space, 1.0, 1000000, 13, 100, 200, "dodgerblue4")
            ai_player, ai_player_shape = createBall(space, 1.0, 1000000, 13, 600, 200, "red3")
            defense = False
            if randint(0, 1) == 0:
                defense = True

        # Game over
        if (team1Score >= 3 and team1Score - team2Score > 1):
            game_over(screen, space, draw_options, ball, ball_shape, player, player_shape, ai_player, ai_player_shape, "Team 1")
            break
        if(team2Score >= 3 and team2Score - team1Score > 1):
            game_over(screen, space, draw_options, ball, ball_shape, player, player_shape, ai_player, ai_player_shape, "Team 2")
            break

        # AI Stuff
        if (defense):
            if (just_switched):
                ai_goal_location_x, ai_goal_location_y = play_defense(ball)
                ai_keys_to_press = path_find(ai_player, ai_goal_location_x, ai_goal_location_y, speeds_ai, acceleration, top_speed)
                just_switched = False
            elif (ai_player.position.x >= 650 and abs(ai_goal_location_y - ball.position.y) >= 50 or len(ai_keys_to_press) == 0):
                ai_goal_location_x, ai_goal_location_y = play_defense(ball)
                ai_keys_to_press = path_find(ai_player, ai_goal_location_x, ai_goal_location_y, speeds_ai, acceleration, top_speed)
        else:
            if ((abs(ai_goal_location_y - ball.position.y) >= 30 or abs(ai_goal_location_x - ball.position.x) >= 100 or len(ai_keys_to_press) == 0) and (ai_goal_location_x is None or ai_goal_location_x != ball.position.x or ai_goal_location_y is None or ai_goal_location_y != ball.position.y)):
                ai_goal_location_x = ball.position.x
                ai_goal_location_y =  ball.position.y
                ai_keys_to_press = path_find(ai_player, ai_goal_location_x, ai_goal_location_y, speeds_ai, acceleration, top_speed)

        ai_keys_to_press, hit_ball = shoot(ai_player, ball, ai_keys_to_press, defense)

        if (len(ai_keys_to_press) > 0):
            speeds_ai = move_player(ai_player, speeds_ai, ai_keys_to_press[0], top_speed, acceleration)
            del ai_keys_to_press[0]
        else:
            speeds_ai = move_player(ai_player, speeds_ai, tuple([0 for i in range(0,323)]), top_speed, acceleration)
        make_impulse(ai_player, ball, (1/5), speeds_ai)
        defense, just_switched = switch_state(defense, hit_ball, ball, ai_player, player)
        hit_ball = False

        if just_switched and len(ai_keys_to_press) == 0:
            just_switched = False

        # User stuff
        keys = pygame.key.get_pressed()
        speeds = move_player(player, speeds, keys, top_speed, acceleration)
        make_impulse(player, ball, (1/5), speeds)

        # Update Visualize
        screen.fill(pygame.Color(21, 155, 50, 1))
        draw_lines(screen)
        space.debug_draw(draw_options)
        textsurface = myfont.render('Team 1: %s      |      Team 2: %s' % (str(team1Score), str(team2Score)), False, (255, 255, 255))
        screen.blit(textsurface,(241,0))

        # Update physics
        dt = 1.0/60.0
        for x in range(10):
            space.step(dt)

        # Misc
        pygame.display.flip()
        clock.tick(50)
        pygame.display.set_caption("fps: " + str(clock.get_fps()))

def main():
    run()

if __name__ == '__main__':
    main()
    print("\n\n\n")
    i = 0
    for change in STATE_CHANGES:
        print(str(change)+","+str(i))
        i = i + 1
