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
light_palette = ((30, 30, 255), (50, 255, 50), (255, 30, 30),
                 (255, 255, 30))  # светло-синий, светло-зеленый, светло-красный, светло-желтый

white, gray, black = (255, 255, 255), (185, 185, 185), (0, 0, 0)
border_color, background_color, text_color, title_color, info_color = white, black, white, color_palette[3], \
color_palette[0]

figure_width, figure_height = 5, 5
empty_space = 'o'

# Определение фигур
shapes = {
    'S': [['ooooo', 'ooooo', 'ooxxo', 'oxxoo', 'ooooo'],
          ['ooooo', 'ooxoo', 'ooxxo', 'oooxo', 'ooooo']],
    'Z': [['ooooo', 'ooooo', 'oxxoo', 'ooxxo', 'ooooo'],
          ['ooooo', 'ooxoo', 'oxxoo', 'oxooo', 'ooooo']],
    'J': [['ooooo', 'oxooo', 'oxxxo', 'ooooo', 'ooooo'],
          ['ooooo', 'ooxxo', 'ooxoo', 'ooxoo', 'ooooo'],
          ['ooooo', 'ooooo', 'oxxxo', 'oooxo', 'ooooo'],
          ['ooooo', 'ooxoo', 'ooxoo', 'oxxoo', 'ooooo']],
    'L': [['ooooo', 'oooxo', 'oxxxo', 'ooooo', 'ooooo'],
          ['ooooo', 'ooxoo', 'ooxoo', 'ooxxo', 'ooooo'],
          ['ooooo', 'ooooo', 'oxxxo', 'oxooo', 'ooooo'],
          ['ooooo', 'oxxoo', 'ooxoo', 'ooxoo', 'ooooo']],
    'I': [['ooxoo', 'ooxoo', 'ooxoo', 'ooxoo', 'ooooo'],
          ['ooooo', 'ooooo', 'xxxxo', 'ooooo', 'ooooo']],
    'O': [['ooooo', 'ooooo', 'oxxoo', 'oxxoo', 'ooooo']],
    'T': [['ooooo', 'ooxoo', 'oxxxo', 'ooooo', 'ooooo'],
          ['ooooo', 'ooxoo', 'ooxxo', 'ooxoo', 'ooooo'],
          ['ooooo', 'ooooo', 'oxxxo', 'ooxoo', 'ooooo'],
          ['ooooo', 'ooxoo', 'oxxoo', 'ooxoo', 'ooooo']]
}


def displayPauseScreen():
    pause_surface = pg.Surface((600, 500), pg.SRCALPHA)
    pause_surface.fill((0, 0, 255, 127))
    screen.blit(pause_surface, (0, 0))


def render3DText(text, font, color, x, y):
    shadow_color = (50, 50, 50)  # Цвет для тени
    text_surface, text_rect = createTextObject(text, font, shadow_color)
    text_rect.topleft = (x + 2, y + 2)
    screen.blit(text_surface, text_rect)
    text_surface, text_rect = createTextObject(text, font, color)
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)


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
        playTetris()
        displayPauseScreen()
        showInitialText('Игра закончена')


def showGameRules():
    screen.fill(background_color)
    render3DText('Правила игры:', large_font, title_color, 150, 30)
    rules = [
        "1. Используйте стрелки для управления фигурой.",
        "2. Нажмите 'Вверх' для поворота фигуры.",
        "3. Нажмите 'Пробел' для паузы.",
        "4. Нажмите 'Enter' для мгновенного падения фигуры.",
        "5. Цель игры - заполнить ряды, чтобы они исчезли."
    ]
    for i, line in enumerate(rules):
        render3DText(line, small_font, text_color, 100, 100 + i * 30)

    render3DText('Нажмите любую клавишу для возвращения в меню', small_font, text_color, 100, 300)

    while checkForKeyPress() is None:
        pg.display.update()
        clock.tick()


def playTetris():
    game_cup = createEmptyCup()
    last_move_down_time = time.time()
    last_side_move_time = time.time()
    last_fall_time = time.time()
    moving_down = False
    moving_left = False
    moving_right = False
    score = 0
    level, fall_speed = calculateSpeed(score)
    current_figure = generateNewFigure()
    next_figure = generateNewFigure()

    while True:
        if current_figure is None:
            current_figure = next_figure
            next_figure = generateNewFigure()
            last_fall_time = time.time()

            if not isPositionValid(game_cup, current_figure):
                return  # Игра закончена
        handleQuit()
        for event in pg.event.get():
            if event.type == KEYUP:
                if event.key == K_SPACE:
                    displayPauseScreen()
                    showInitialText('Пауза')
                    last_fall_time = time.time()
                    last_move_down_time = time.time()
                    last_side_move_time = time.time()
                elif event.key == K_LEFT:
                    moving_left = False
                elif event.key == K_RIGHT:
                    moving_right = False
                elif event.key == K_DOWN:
                    moving_down = False
                elif event.key == K_r:  # открыть правила
                    showGameRules()

            elif event.type == KEYDOWN:
                if event.key == K_LEFT and isPositionValid(game_cup, current_figure, adjX=-1):
                    current_figure['x'] -= 1
                    moving_left = True
                    moving_right = False
                    last_side_move_time = time.time()

                elif event.key == K_RIGHT and isPositionValid(game_cup, current_figure, adjX=1):
                    current_figure['x'] += 1
                    moving_right = True
                    moving_left = False
                    last_side_move_time = time.time()

                elif event.key == K_UP:
                    current_figure['rotation'] = (current_figure['rotation'] + 1) % len(shapes[current_figure['shape']])
                    if not isPositionValid(game_cup, current_figure):
                        current_figure['rotation'] = (current_figure['rotation'] - 1) % len(
                            shapes[current_figure['shape']])

                elif event.key == K_DOWN:
                    moving_down = True
                    if isPositionValid(game_cup, current_figure, adjY=1):
                        current_figure['y'] += 1
                    last_move_down_time = time.time()

                elif event.key == K_RETURN:
                    moving_down = False
                    moving_left = False
                    moving_right = False
                    for i in range(1, cup_height):
                        if not isPositionValid(game_cup, current_figure, adjY=i):
                            break
                    current_figure['y'] += i - 1

        # Управление падением фигуры при удержании клавиш
        if (moving_left or moving_right) and time.time() - last_side_move_time > side_move_freq:
            if moving_left and isPositionValid(game_cup, current_figure, adjX=-1):
                current_figure['x'] -= 1
            elif moving_right and isPositionValid(game_cup, current_figure, adjX=1):
                current_figure['x'] += 1
            last_side_move_time = time.time()

        if moving_down and time.time() - last_move_down_time > downward_move_freq and isPositionValid(game_cup,
                                                                                                      current_figure,
                                                                                                      adjY=1):
            current_figure['y'] += 1
            last_move_down_time = time.time()

        if time.time() - last_fall_time > fall_speed:
            if not isPositionValid(game_cup, current_figure, adjY=1):
                addFigureToCup(game_cup, current_figure)
                score += clearFullLines(game_cup)
                level, fall_speed = calculateSpeed(score)
                current_figure = None
            else:
                current_figure['y'] += 1
                last_fall_time = time.time()

        # Отрисовка окна игры со всеми надписями
        screen.fill(background_color)
        renderTitle()
        drawCup(game_cup)
        renderInfo(score, level)
        renderNextFigure(next_figure)
        if current_figure is not None:
            renderFigure(current_figure)
        pg.display.update()
        clock.tick(frames_per_second)


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


def showInitialText(text):
    title_surface, title_rect = createTextObject(text, large_font, title_color)
    title_rect.center = (int(screen_width / 2) - 3, int(screen_height / 2) - 3)
    screen.blit(title_surface, title_rect)

    press_key_surface, press_key_rect = createTextObject('Нажмите любую клавишу для продолжения', small_font,
                                                         title_color)
    press_key_rect.center = (int(screen_width / 2), int(screen_height / 2) + 100)
    screen.blit(press_key_surface, press_key_rect)

    while checkForKeyPress() is None:
        pg.display.update()
        clock.tick()


def handleQuit():
    for event in pg.event.get(QUIT):
        terminateGame()
    for event in pg.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminateGame()
        pg.event.post(event)


def calculateSpeed(points):
    level = int(points / 10) + 1
    fall_speed = 0.27 - (level * 0.02)
    return level, fall_speed


def generateNewFigure():
    shape = random.choice(list(shapes.keys()))
    new_figure = {'shape': shape,
                  'rotation': random.randint(0, len(shapes[shape]) - 1),
                  'x': int(cup_width / 2) - int(figure_width / 2),
                  'y': -2,
                  'color': random.randint(0, len(color_palette) - 1)}
    return new_figure


def addFigureToCup(cup, fig):
    for x in range(figure_width):
        for y in range(figure_height):
            if shapes[fig['shape']][fig['rotation']][y][x] != empty_space:
                cup[x + fig['x']][y + fig['y']] = fig['color']


def createEmptyCup():
    cup = []
    for i in range(cup_width):
        cup.append([empty_space] * cup_height)
    return cup


def isInCup(x, y):
    return x >= 0 and x < cup_width and y < cup_height


def isPositionValid(cup, fig, adjX=0, adjY=0):
    for x in range(figure_width):
        for y in range(figure_height):
            above_cup = y + fig['y'] + adjY < 0
            if above_cup or shapes[fig['shape']][fig['rotation']][y][x] == empty_space:
                continue
            if not isInCup(x + fig['x'] + adjX, y + fig['y'] + adjY):
                return False
            if cup[x + fig['x'] + adjX][y + fig['y'] + adjY] != empty_space:
                return False
    return True


def isLineCompleted(cup, y):
    for x in range(cup_width):
        if cup[x][y] == empty_space:
            return False
    return True


def clearFullLines(cup):
    removed_lines = 0
    y = cup_height - 1
    while y >= 0:
        if isLineCompleted(cup, y):
            for push_down_y in range(y, 0, -1):
                for x in range(cup_width):
                    cup[x][push_down_y] = cup[x][push_down_y - 1]
            for x in range(cup_width):
                cup[x][0] = empty_space
            removed_lines += 1
        else:
            y -= 1
    return removed_lines


def convertBlockCoords(block_x, block_y):
    return (side_offset + (block_x * block_size)), (top_offset + (block_y * block_size))


def drawBlockOnScreen(block_x, block_y, color, pixel_x=None, pixel_y=None):
    if color == empty_space:
        return
    if pixel_x is None and pixel_y is None:
        pixel_x, pixel_y = convertBlockCoords(block_x, block_y)
    pg.draw.rect(screen, color_palette[color], (pixel_x + 1, pixel_y + 1, block_size - 1, block_size - 1), 0, 3)
    pg.draw.rect(screen, light_palette[color], (pixel_x + 1, pixel_y + 1, block_size - 4, block_size - 4), 0, 3)
    pg.draw.circle(screen, color_palette[color], (pixel_x + block_size / 2, pixel_y + block_size / 2), 5)


def drawCup(cup):
    pg.draw.rect(screen, border_color,
                 (side_offset - 4, top_offset - 4, (cup_width * block_size) + 8, (cup_height * block_size) + 8), 5)
    pg.draw.rect(screen, background_color, (side_offset, top_offset, block_size * cup_width, block_size * cup_height))
    for x in range(cup_width):
        for y in range(cup_height):
            drawBlockOnScreen(x, y, cup[x][y])


def renderTitle():
    render3DText('Block Breakers', large_font, title_color, screen_width - 425, 30)


def renderInfo(points, level):
    points_surface = small_font.render(f'Баллы: {points}', True, text_color)
    points_rect = points_surface.get_rect()
    points_rect.topleft = (screen_width - 550, 180)
    screen.blit(points_surface, points_rect)

    level_surface = small_font.render(f'Уровень: {level}', True, text_color)
    level_rect = level_surface.get_rect()
    level_rect.topleft = (screen_width - 550, 250)
    screen.blit(level_surface, level_rect)

    pause_surface = small_font.render('Пауза: пробел', True, info_color)
    pause_rect = pause_surface.get_rect()
    pause_rect.topleft = (screen_width - 550, 420)
    screen.blit(pause_surface, pause_rect)

    exit_surface = small_font.render('Выход: Esc', True, info_color)
    exit_rect = exit_surface.get_rect()
    exit_rect.topleft = (screen_width - 550, 450)
    screen.blit(exit_surface, exit_rect)


def renderFigure(fig, pixel_x=None, pixel_y=None):
    figure_to_draw = shapes[fig['shape']][fig['rotation']]
    if pixel_x is None and pixel_y is None:
        pixel_x, pixel_y = convertBlockCoords(fig['x'], fig['y'])

    for x in range(figure_width):
        for y in range(figure_height):
            if figure_to_draw[y][x] != empty_space:
                pg.draw.rect(screen, color_palette[fig['color']],
                             (pixel_x + (x * block_size), pixel_y + (y * block_size), block_size, block_size))


def renderNextFigure(fig):
    next_surface = small_font.render('Следующая:', True, text_color)
    next_rect = next_surface.get_rect()
    next_rect.topleft = (screen_width - 150, 180)
    screen.blit(next_surface, next_rect)
    renderFigure(fig, pixel_x=screen_width - 150, pixel_y=230)


def drawBackground():
    for x in range(0, screen_width, block_size):
        for y in range(0, screen_height, block_size):
            color = random.choice(color_palette)
            pg.draw.rect(screen, color, (x, y, block_size, block_size))


def showInitialText(text):
    screen.fill(background_color)
    drawBackground()

    text_background = pg.Surface((400, 100))
    text_background.set_alpha(150)
    text_background.fill((0, 0, 0))
    screen.blit(text_background, (int(screen_width / 2) - 200, int(screen_height / 2) - 50))

    title_surface, title_rect = createTextObject(text, large_font, title_color)
    title_rect.center = (int(screen_width / 2), int(screen_height / 2) - 30)
    screen.blit(title_surface, title_rect)

    press_key_surface, press_key_rect = createTextObject('Нажмите любую клавишу для продолжения', small_font,
                                                         text_color)
    press_key_rect.center = (int(screen_width / 2), int(screen_height / 2) + 50)
    screen.blit(press_key_surface, press_key_rect)

    while checkForKeyPress() is None:
        pg.display.update()
        clock.tick()


if __name__ == '__main__':
    main()
