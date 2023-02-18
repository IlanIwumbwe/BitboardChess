"""
contains all settings, not being used yet, to be continued

"""


import pygame

WIDTH = 650
HEIGHT = 650

BOARD_DIMENSION = 8

SQUARE_SIZE = 70
IMAGE_SIZE = 70

BOARD_WIDTH = SQUARE_SIZE*BOARD_DIMENSION
BOARD_HEIGHT = SQUARE_SIZE*BOARD_DIMENSION

TOP_X = (WIDTH-BOARD_WIDTH)//2
TOP_Y = (HEIGHT-BOARD_HEIGHT)//2

odd_squares_colour = (255,51,51) # odd squares colour
text_colour = (0,0,22) # rendering text
even_squares_colour = (255, 255, 153)#(170, 70, 70) # # even squares colour
bg_colour = (255, 255, 153) # (150, 100, 100)  # background colour
dp_initial_square_colour = (255, 128, 0) # initial drag piece square
possible_esq_colour = (87, 200, 77) # possible squares
possible_osq_colour = (171, 224, 152) # possible squares

f = 'freesansbold.ttf'

SPRITES = {'K_w':pygame.image.load('./pieces/K_w.png'),
           'B_w':pygame.image.load('./pieces/B_w.png'),
           'N_w':pygame.image.load('./pieces/N_w.png'),
           'R_w':pygame.image.load('./pieces/R_w.png'),
           'Q_w':pygame.image.load('./pieces/Q_w.png'),
           'P_w':pygame.image.load('./pieces/P_w.png'),
           'K_b':pygame.image.load('./pieces/K_b.png'),
           'B_b':pygame.image.load('./pieces/B_b.png'),
           'N_b':pygame.image.load('./pieces/N_b.png'),
           'R_b':pygame.image.load('./pieces/R_b.png'),
           'Q_b':pygame.image.load('./pieces/Q_b.png'),
           'P_b':pygame.image.load('./pieces/P_b.png')
           }