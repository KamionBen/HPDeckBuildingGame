import pygame as pg
import pygame.image

pg.init()
RESOLUTION = 1920, 1080
FPS = 30
SCREEN = pg.display.set_mode(RESOLUTION)
FONT = {x: pg.font.Font(None, x) for x in range(2, 120, 2)}
AQUIFER = {x: pg.font.Font('fonts/Aquifer.ttf', x) for x in range(2, 120, 2)}
ENCHANTED = {x: pg.font.Font('fonts/Enchanted Land.otf', x) for x in range(2, 120, 2)}
VERSION = '0.1'

YELLOW = 201, 200, 77
RED = 146, 40, 47
BLUE = 64, 105, 158
