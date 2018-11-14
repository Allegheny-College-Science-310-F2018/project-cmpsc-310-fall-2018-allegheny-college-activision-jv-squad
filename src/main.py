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
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    clock = pygame.time.Clock()
    return screen, space, draw_options, clock

def createBorder(space):
    static_body = space.static_body
    static_lines = list()
    static_lines.append(pymunk.Segment(static_body, (25.0, 25.0), (675.0, 25.0), 0.0))
    static_lines.append(pymunk.Segment(static_body, (25.0, 25.0), (25.0, 475.0), 0.0))
    static_lines.append(pymunk.Segment(static_body, (25.0, 475.0), (675.0, 475.0), 0.0))
    static_lines.append(pymunk.Segment(static_body, (675.0, 25.0), (675.0, 475.0), 0.0))
    for line in static_lines:
        line.elasticity = .95
        line.friction = .1
    return static_lines

def createBall(space, friction, mass, radius, x, y):
    inertia = pymunk.moment_for_circle(mass, 0, radius, (0,0))
    body = pymunk.Body(mass, inertia)
    body.position = x, y
    shape = pymunk.Circle(body, radius, (0,0))
    shape.collision_type = 3
    shape.elasticity = 1.0
    shape.friction = friction
    body.velocity = 10
    space.add(body, shape)
    return body

def run():
    screen, space, draw_options, clock = setup()
    space.add(createBorder(space))
    running = True
    ball = createBall(space, .1, 3, 15, 450, 200)
    player = createBall(space, .9, 10, 20, 300, 200)

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == KEYDOWN and event.key == K_p:
                pygame.image.save(screen, "bouncing_balls.png")

        keys = pygame.key.get_pressed()
        speed = 2.5
        if (keys[K_UP]):
            player.position += Vec2d(0,1) * speed
        if (keys[K_DOWN]):
            player.position += Vec2d(0,-1) * speed
        if (keys[K_LEFT]):
            player.position += Vec2d(-1,0) * speed
        if (keys[K_RIGHT]):
            player.position += Vec2d(1,0) * speed

        screen.fill(THECOLORS["white"])
        space.debug_draw(draw_options)
        dt = 1.0/60.0
        for x in range(1):
            space.step(dt)
        pygame.display.flip()
        clock.tick(50)
        pygame.display.set_caption("fps: " + str(clock.get_fps()))

def main():
    setup()
    run()

if __name__ == '__main__':
    main()
