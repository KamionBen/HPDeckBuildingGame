import pygame
import pygame.image

pygame.init()
#RESOLUTION = 1920, 1080
RESOLUTION = 1280, 720
VERSION = '0.1'

if pygame.display.get_desktop_sizes()[0][0] < 1920:
    RESOLUTION = 1280, 720



FPS = 30
SCREEN = pygame.display.set_mode(RESOLUTION)
""" IMAGES """
MAIN_BACKGROUND = pygame.image.load("images/poudlardexpress/poudlardexpress_00000.png").convert()

""" FONTS """
FONT = {x: pygame.font.Font(None, x) for x in range(12, 120)}
AQUIFER = {x: pygame.font.Font('fonts/Aquifer.ttf', x) for x in range(12, 120)}
ENCHANTED = {x: pygame.font.Font('fonts/Enchanted Land.otf', x) for x in range(12, 120)}


YELLOW = 201, 200, 77
RED = 146, 40, 47
BLUE = 64, 105, 158
