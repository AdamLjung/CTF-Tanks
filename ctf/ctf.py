""" Main file for the game.
"""
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import time

# ----- Initialisation ----- #

# -- Initialise the display
pygame.init()
pygame.display.set_mode()

# -- Initialise the clock
clock = pygame.time.Clock()

# -- Initialise the physics engine
space = pymunk.Space()
space.gravity = (0.0, 0.0)
space.damping = 0.1  # Adds friction to the ground for all objects

# -- Import from the ctf framework
# The framework needs to be imported after initialisation of pygame
import ai
import images
import gameobjects
import maps

# -- Constants
FRAMERATE = 50

# -- Variables
#   Define the current level

#   List of all game objects

game_objects_list = []
tanks_list = []
ai_list = []
screenHeight = 600
screenWidth = 600
# set screen to size of current level
headScreen = pygame.display.set_mode((screenWidth, screenHeight))
# generate background
background = pygame.Surface(headScreen.get_size())
startScreen = pygame.image.load("images/backgroundgrass.png")
mapScreen = pygame.image.load("images/backgroundgrass1.png")
bigTextFont = pygame.font.SysFont("Dhurjati", 50)
medTextFont = pygame.font.SysFont("Dhurjati", 40)
headlinePos = (145, 55)
headLineMapPos = (65, 30)
medTextPos = (160, 280)

pygame.display.update()


def generate_startPic_map(map, size):
    # height width
    map_surface = pygame.Surface(size)
    for y in range(0, map.width):
        for x in range(0, map.height):
            # 1 rockbox 2 woodbox, 3 metalbox
            if (map.boxes[x][y] == 0):

                map_surface.blit(images.grass, (x * images.TILE_SIZE, y * images.TILE_SIZE))
            elif (map.boxes[x][y] == 1):

                map_surface.blit(images.rockbox, (x * images.TILE_SIZE, y * images.TILE_SIZE))
            elif (map.boxes[x][y] == 2):

                map_surface.blit(images.woodbox, (x * images.TILE_SIZE, y * images.TILE_SIZE))
            elif (map.boxes[x][y] == 3):

                map_surface.blit(images.metalbox, (x * images.TILE_SIZE, y * images.TILE_SIZE))
    map_surface = pygame.transform.rotate(map_surface, 90)
    return map_surface


# start the screen

startTheScreen = True
map1 = generate_startPic_map(maps.map0, (360, 360))
map2 = generate_startPic_map(maps.map1, (400, 600))
map3 = generate_startPic_map(maps.map2, (200, 400))

while startTheScreen:
    headScreen.blit(startScreen, (0, 0))

    headLine = bigTextFont.render("Capture the flag", False, (255, 255, 255))
    pressBt = medTextFont.render("Press Enter to play", False, (255, 255, 255))

    headScreen.blit(headLine, headlinePos)
    headScreen.blit(pressBt, medTextPos)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == K_RETURN:

            startTheScreen = False
            chooseMap = True
        if event.type == pygame.QUIT:

            pygame.quit()

while chooseMap:
    headScreen.blit(mapScreen, (0, 0))
    headLineMap = bigTextFont.render("Choose a map key (1-3)", False, (255, 255, 255))
    one = bigTextFont.render("1.", False, (0, 255, 255))
    two = bigTextFont.render("2.", False, (0, 255, 255))
    three = bigTextFont.render("3.", False, (0, 255, 255))

    map1 = pygame.transform.scale(map1, (180, 180))
    map2 = pygame.transform.scale(map2, (300, 220))
    map3 = pygame.transform.scale(map3, (395, 200))

    headScreen.blit(headLineMap, headLineMapPos)
    headScreen.blit(one, (50, 100))
    headScreen.blit(map1, (50, 140))
    headScreen.blit(two, (300, 100))
    headScreen.blit(map2, (280, 140))
    headScreen.blit(three, (50, 350))
    headScreen.blit(map3, (50, 400))

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == K_1:

            FogOfWarPage = True
            chooseMap = False
            current_map = maps.map0
        elif event.type == pygame.KEYDOWN and event.key == K_2:

            FogOfWarPage = True
            chooseMap = False
            current_map = maps.map1
        elif event.type == pygame.KEYDOWN and event.key == K_3:

            FogOfWarPage = True
            chooseMap = False
            current_map = maps.map2
        elif event.type == pygame.QUIT:

            pygame.quit()
    pygame.display.update()

while FogOfWarPage:
    headScreen.blit(mapScreen, (0, 0))

    headLineMap = medTextFont.render("Do you want to play fog of war? (Y/N)", False, (255, 255, 255))
    FogPicture = pygame.image.load("images/fogofwar.png")
    FogPicture = pygame.transform.scale(FogPicture, (250, 250))

    headScreen.blit(headLineMap, headLineMapPos)
    headScreen.blit(FogPicture, (180, 140))

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == K_y:

            PlayFogOfWar = True
            FogOfWarPage = False
        elif event.type == pygame.KEYDOWN and event.key == K_n:

            PlayFogOfWar = False
            FogOfWarPage = False
        elif event.type == pygame.QUIT:

            pygame.quit()

    pygame.display.update()


def generate_boundries():
   
    static_body = space.static_body
    static_line = [pymunk.Segment(static_body, (0.0, 0.0), (0.0, current_map.height), 0.0)
    ,pymunk.Segment(static_body, (0.0, current_map.height), (current_map.width, current_map.height), 0.0)
    ,pymunk.Segment(static_body, (current_map.width, current_map.height), (current_map.width, 0.0), 0.0)
    , pymunk.Segment(static_body, (current_map.width, 0.0), (0.0, 0.0), 0.0)
    ]
    space.add(*static_line)

# -- Resize the screen to the size of the current level
screen = pygame.display.set_mode(current_map.rect().size)

# <INSERT GENERATE BACKGROUND>
background = pygame.Surface(screen.get_size())


def generate_background():
    for x in range(0, current_map.width):
        for y in range(0, current_map.height):

            background.blit(images.grass, (x * images.TILE_SIZE, y * images.TILE_SIZE))
    return


# <INSERT CREATE BOXES>
def create_boxes():
    for x in range(0, current_map.width):
        for y in range(0, current_map.height):

            box_type = current_map.boxAt(x, y)

            if (box_type != 0):
                box = gameobjects.get_box_with_type(x, y, box_type, space)
                game_objects_list.append(box)


# <INSERT CREATE TANKS>
def create_tanks():

    for i in range(0, len(current_map.start_positions)):

        pos = current_map.start_positions[i]
        tank = gameobjects.Tank(pos[0], pos[1], pos[2], images.tanks[i], space, i, FRAMERATE)
        tanks_list.append(tank)

        if i != 0:
            tank_ai = ai.Ai(tanks_list[i], game_objects_list, tanks_list, space, current_map)
            ai_list.append(tank_ai)

        base = gameobjects.GameVisibleObject(pos[0], pos[1], images.bases[i])
        game_objects_list.append(base)


# <INSERT CREATE FLAG>
def create_flag():
    flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
    game_objects_list.append(flag)
    return flag


def collision_bullet_tank(arb, space, data):
    bullet = arb.shapes[0].parent
    tank = arb.shapes[1].parent
    if tank.id != bullet.id:

        game_objects_list.remove(bullet)
        space.remove(bullet.shape, bullet.body)
        if tank.hp <= 1:

            tank.flag = None
            flag.is_on_tank = False
            i = tank.id
            pos = current_map.start_positions[i]
            tank.body.position = (pos[0], pos[1])
            tank.body.angle = pos[2]
            tank.hp = 3
        elif tank.hp > 1:

            tank.hp -= 1
    return False


def collision_bullet_box(arb, space, data):
    bullet = arb.shapes[0].parent
    box = arb.shapes[1].parent

    if bullet in game_objects_list:

        game_objects_list.remove(bullet)
        space.remove(bullet.shape, bullet.body)
        if box.destructable and box in game_objects_list:

            if box.hp <= 1:

                game_objects_list.remove(box)
                space.remove(box.shape, box.body)
            elif box.hp > 1:

                box.hp -= 1

    return False


def run_handeler():

    handler = space.add_collision_handler(1, 2)
    handler.pre_solve = collision_bullet_tank
    handler_box = space.add_collision_handler(1, 3)
    handler_box.pre_solve = collision_bullet_box
    handler_box = space.add_collision_handler(1, 4)
    handler_box.pre_solve = collision_bullet_box


def fog_of_war():

    if PlayFogOfWar:
        fog_of_war = pygame.Surface(screen.get_size())
        fog_of_war.fill((0, 0, 0))
        pygame.draw.circle(fog_of_war, (60, 60, 60), (tanks_list[0].body.position[0] * images.TILE_SIZE, tanks_list[0].body.position[1] * images.TILE_SIZE), 100)
        fog_of_war.set_colorkey((60, 60, 60))
        screen.blit(fog_of_war, (0, 0))


# ----- Main Loop -----#
def main_loop():

    # -- Control whether the game run
    running = True
    skip_update = 0
    while running:
        # -- Handle the events
        for event in pygame.event.get():
            # Check if we receive a QUIT event (for instance, if the user press the
            # close button of the wiendow) or if the user press the escape key.
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):

                running = False
            elif event.type == KEYDOWN and event.key == K_UP:

                tanks_list[0].accelerate()
            elif event.type == KEYDOWN and event.key == K_DOWN:

                tanks_list[0].decelerate()
            elif event.type == KEYDOWN and event.key == K_LEFT:

                tanks_list[0].turn_left()
            elif event.type == KEYDOWN and event.key == K_RIGHT:

                tanks_list[0].turn_right()
            elif (event.type == KEYUP and event.key == K_UP) or (event.type == KEYUP and event.key == K_DOWN):

                tanks_list[0].stop_moving()
            elif (event.type == KEYUP and event.key == K_LEFT) or (event.type == KEYUP and event.key == K_RIGHT):

                tanks_list[0].stop_turning()
            elif (event.type == KEYDOWN and event.key == K_SPACE):

                if tanks_list[0].cd < 1:

                    game_objects_list.append(tanks_list[0].shoot(space))

        # -- Update physics
        if skip_update == 0:
            # Loop over all the game objects and update their speed in function of their
            # acceleration.
            for tank in tanks_list:
                tank.try_grab_flag(flag)
                tank.update()
                tank.post_update()
                if tank.has_won():
                    running = False

            for obj in game_objects_list:
                obj.update()

            skip_update = 2
        else:
            skip_update -= 1

        #   Check collisions and update the objects position
        space.step(1 / FRAMERATE)

        # -- Update Display

        # <INSERT DISPLAY BACKGROUND>
        screen.blit(background, (0, 0))

        # <INSERT DISPLAY OBJECTS>
        #   Update object that depends on an other object position (for instance a flag)
        for obj in game_objects_list:
            obj.update_screen(screen)
        # Redisplay the entire screen (see double buffer technique)

        # flag.update_screen(screen)
        for tank in tanks_list:

            tank.update_screen(screen)
        for ai in ai_list:

            ai.decide()
        fog_of_war()

        pygame.display.flip()

        #   Control the game framerate
        clock.tick(FRAMERATE)


generate_boundries()
generate_background()
create_boxes()
create_tanks()
flag = create_flag()
run_handeler()
main_loop()
