import pygame as pg
import random
import time
import sys
import os
from pygame.locals import *

# Настройки
frames_per_second = 25
screen_width, screen_height = 600, 500
block_size, cup_height, cup_width = 20, 20, 10

side_move_freq, downward_move_freq = 0.15, 0.1  # передвижение в сторону и вниз

side_offset = int((screen_width - cup_width * block_size) / 2)
top_offset = screen_height - (cup_height * block_size) - 5

color_palette = ((0, 0, 225), (0, 225, 0), (225, 0, 0), (225, 225, 0))  # синий, зеленый, красный, желтый
light_palette = ((30, 30, 255), (50, 255, 50), (255, 30, 30), (255, 255, 30))  # светло-синий, светло-зеленый, светло-красный, светло-желтый

white, gray, black = (255, 255, 255), (185, 185, 185), (0, 0, 0)
border_color, background_color, text_color, title_color, info_color = white, black, white, color_palette[3], color_palette[0]

figure_width, figure_height = 5, 5
empty_space = 'o'

def main():
    global clock, screen, small_font, large_font
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode((screen_width, screen_height))
    small_font = pg.font.SysFont('arial', 20)
    large_font = pg.font.SysFont('verdana', 45)
    pg.display.set_caption('Block Breakers')
    showInitialText('Block Breakers')
    while True:
        showInitialText('Игра закончена')

def showInitialText(text):
    title_surface, title_rect = createTextObject(text, large_font, title_color)
    title_rect.center = (int(screen_width / 2) - 3, int(screen_height / 2) - 3)
    screen.blit(title_surface, title_rect)

    press_key_surface, press_key_rect = createTextObject('Нажмите любую клавишу для продолжения', small_font, title_color)
    press_key_rect.center = (int(screen_width / 2), int(screen_height / 2) + 100)
    screen.blit(press_key_surface, press_key_rect)

    while checkForKeyPress() is None:
        pg.display.update()
        clock.tick()


def createTextObject(text, font, color):
    surface = font.render(text, True, color)
    return surface, surface.get_rect()

def terminateGame():
    pg.quit()
    sys.exit()

def checkForKeyPress():
    handleQuit()

    for event in pg.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None

def handleQuit():
    for event in pg.event.get(QUIT):
        terminateGame()
    for event in pg.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminateGame()
        pg.event.post(event)



if __name__ == '__main__':
    main()