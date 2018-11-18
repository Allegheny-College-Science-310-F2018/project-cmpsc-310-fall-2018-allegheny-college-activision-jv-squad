import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random

def setup():
    pygame.init()
    screen = pygame.display.set_mode((700, 400))
    space = pymunk.Space()
    space.gravity = (0.0, 0.0)
    space.damping = .98
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    clock = pygame.time.Clock()
    return screen, space, draw_options, clock

def createBorder(space):
    static_body = space.static_body
    static_lines = list()
    static_lines.append(pymunk.Segment(static_body, (25.0, 25.0), (675.0, 25.0), 0.0))
    static_lines.append(pymunk.Segment(static_body, (25.0, 25.0), (25.0, 375.0), 0.0))
    static_lines.append(pymunk.Segment(static_body, (25.0, 375.0), (675.0, 375.0), 0.0))
    static_lines.append(pymunk.Segment(static_body, (675.0, 25.0), (675.0, 375.0), 0.0))
    for line in static_lines:
        line.elasticity = .95
        line.friction = .1
        line.color = pygame.color.THECOLORS["white"]
    return static_lines

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

def run():
    screen, space, draw_options, clock = setup()
    space.add(createBorder(space))
    running = True
    ball = createBall(space, .1, 3, 10, 450, 200, "white")
    player = createBall(space, 1.0, 1000000, 13, 300, 200, "blue")

    speed = 0
    last_keys = list()

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == KEYDOWN and event.key == K_p:
                pygame.image.save(screen, "bouncing_balls.png")

        keys = pygame.key.get_pressed()

        if (keys[K_UP] or keys[K_DOWN] or keys[K_LEFT] or keys[K_RIGHT]):
            if (speed > 3.0):
                speed = 3.0
            else:
                speed = speed + .05
            last_keys.clear()
        if (not keys[K_UP] and not keys[K_DOWN] and not keys[K_LEFT] and not keys[K_RIGHT]):
            if (speed <= 0):
                speed = 0
            else:
                speed = speed - .05
                if ("UP" in last_keys):
                    player.position += Vec2d(0,1) * speed
                if ("DOWN" in last_keys):
                    player.position += Vec2d(0,-1) * speed
                if ("LEFT" in last_keys):
                    player.position += Vec2d(-1,0) * speed
                if ("RIGHT" in last_keys):
                    player.position += Vec2d(1,0) * speed
        if (keys[K_UP]):
            player.position += Vec2d(0,1) * speed
            last_keys.append("UP")
        if (keys[K_DOWN]):
            player.position += Vec2d(0,-1) * speed
            last_keys.append("DOWN")
        if (keys[K_LEFT]):
            player.position += Vec2d(-1,0) * speed
            last_keys.append("LEFT")
        if (keys[K_RIGHT]):
            player.position += Vec2d(1,0) * speed
            last_keys.append("RIGHT")
        if (keys[K_SPACE]):
            make_impulse(player, ball, (1/2))

        make_impulse(player, ball, (1/20))

        screen.fill(THECOLORS["green"])
        space.debug_draw(draw_options)
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
