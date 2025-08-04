import pygame
import random
import time
import sys

pygame.init()
pygame.key.stop_text_input()
BLOCK_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 40

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]]
]

SHAPE_COLORS = [
    (0, 255, 255),
    (255, 255, 0),
    (128, 0, 128),
    (0, 255, 0),
    (255, 0, 0),
    (0, 0, 255),
    (255, 165, 0)
]

WINDOW_WIDTH = GRID_WIDTH * BLOCK_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
INFO_WIDTH = 200
SCREEN_WIDTH = WINDOW_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = WINDOW_HEIGHT

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('俄罗斯方块')

font = pygame.font.SysFont('Arial', 24)
big_font = pygame.font.SysFont('Arial', 48)

grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
current_piece = None
next_piece = None
score = 0
last_fall_time = time.time()
fall_speed = 0.5
level = 1
game_over = False

def new_piece():
    shape = random.choice(SHAPES)
    color = SHAPE_COLORS[SHAPES.index(shape)]
    piece = {'shape': shape, 'color': color, 'x': GRID_WIDTH // 2 - len(shape[0]) // 2, 'y': 0, 'rotation': 0}
    return piece

def valid_space(piece, grid):
    shape = rotate_shape(piece['shape'], piece['rotation'])
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x] != 0:
                if (piece['y'] + y >= GRID_HEIGHT or piece['x'] + x < 0 or piece['x'] + x >= GRID_WIDTH or
                    (piece['y'] + y >= 0 and grid[piece['y'] + y][piece['x'] + x] != 0)):
                    return False
    return True

def rotate_shape(shape, rotation):
    rotated = []
    for _ in range(rotation % 4):
        shape = [list(row)[::-1] for row in zip(*shape)]
    return shape

def add_to_grid(piece, grid):
    shape = rotate_shape(piece['shape'], piece['rotation'])
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x] != 0:
                grid[piece['y'] + y][piece['x'] + x] = piece['color']

def clear_rows(grid):
    global score, level, fall_speed
    rows_cleared = 0
    for y in range(GRID_HEIGHT - 1, -1, -1):
        if 0 not in grid[y]:
            rows_cleared += 1
            for y2 in range(y, 0, -1):
                grid[y2] = grid[y2 - 1][:]
            grid[0] = [0 for _ in range(GRID_WIDTH)]
    if rows_cleared > 0:
        score += [0, 100, 300, 500, 800][rows_cleared]
        level = 1 + (score // 1000)
        fall_speed = max(0.05, 0.5 - (level - 1) * 0.05)
    return rows_cleared

def draw_block(x, y, color):
    pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    pygame.draw.rect(screen, GRAY, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)
    highlight = (255, 255, 255)
    shadow = (0, 0, 0)
    pygame.draw.line(screen, highlight, (x * BLOCK_SIZE, y * BLOCK_SIZE), ((x + 1) * BLOCK_SIZE - 1, y * BLOCK_SIZE))
    pygame.draw.line(screen, highlight, (x * BLOCK_SIZE, y * BLOCK_SIZE), (x * BLOCK_SIZE, (y + 1) * BLOCK_SIZE - 1))
    pygame.draw.line(screen, shadow, (x * BLOCK_SIZE + 1, (y + 1) * BLOCK_SIZE - 1), ((x + 1) * BLOCK_SIZE - 1, (y + 1) * BLOCK_SIZE - 1))
    pygame.draw.line(screen, shadow, ((x + 1) * BLOCK_SIZE - 1, y * BLOCK_SIZE + 1), ((x + 1) * BLOCK_SIZE - 1, (y + 1) * BLOCK_SIZE - 1))

def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            cell = grid[y][x]
            if cell != 0:
                draw_block(x, y, cell)

def draw_current_piece():
    if current_piece:
        shape = rotate_shape(current_piece['shape'], current_piece['rotation'])
        for y in range(len(shape)):
            for x in range(len(shape[y])):
                if shape[y][x] != 0:
                    draw_block(current_piece['x'] + x, current_piece['y'] + y, current_piece['color'])

def draw_next_piece():
    if next_piece:
        shape = next_piece['shape']
        x_offset = WINDOW_WIDTH + 30
        y_offset = 100
        text = font.render('下一个方块:', True, WHITE)
        screen.blit(text, (x_offset, 50))
        for y in range(len(shape)):
            for x in range(len(shape[y])):
                if shape[y][x] != 0:
                    draw_block(x_offset + x * BLOCK_SIZE, y_offset + y * BLOCK_SIZE, next_piece['color'])

def draw_score():
    score_text = font.render(f'分数: {score}', True, WHITE)
    level_text = font.render(f'等级: {level}', True, WHITE)
    time_text = font.render(f'时间: {int(time.time() - start_time)}秒', True, WHITE)
    screen.blit(score_text, (WINDOW_WIDTH + 30, 200))
    screen.blit(level_text, (WINDOW_WIDTH + 30, 240))
    screen.blit(time_text, (WINDOW_WIDTH + 30, 280))

def draw_game_over():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    game_over_text = big_font.render('游戏结束!', True, WHITE)
    score_text = font.render(f'最终分数: {score}', True, WHITE)
    restart_text = font.render('按R键重新开始', True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

def reset_game():
    global grid, current_piece, next_piece, score, last_fall_time, fall_speed, level, game_over, start_time
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    current_piece = new_piece()
    next_piece = new_piece()
    score = 0
    last_fall_time = time.time()
    fall_speed = 0.5
    level = 1
    game_over = False
    start_time = time.time()

def main():
    global current_piece, next_piece, grid, last_fall_time, game_over
    if current_piece is None:
        current_piece = new_piece()
        next_piece = new_piece()
    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill(BLACK)
        if not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        current_piece['x'] -= 1
                        if not valid_space(current_piece, grid):
                            current_piece['x'] += 1
                    elif event.key == pygame.K_d:
                        current_piece['x'] += 1
                        if not valid_space(current_piece, grid):
                            current_piece['x'] -= 1
                    elif event.key == pygame.K_w:
                        current_piece['rotation'] += 1
                        if not valid_space(current_piece, grid):
                            current_piece['rotation'] -= 1
                    elif event.key == pygame.K_s:
                        while valid_space(current_piece, grid):
                            current_piece['y'] += 1
                        current_piece['y'] -= 1
                        add_to_grid(current_piece, grid)
                        clear_rows(grid)
                        current_piece = next_piece
                        next_piece = new_piece()
                        if not valid_space(current_piece, grid):
                            game_over = True
                    elif event.key == pygame.K_r:
                        reset_game()
            current_time = time.time()
            if current_time - last_fall_time > fall_speed:
                last_fall_time = current_time
                current_piece['y'] += 1
                if not valid_space(current_piece, grid):
                    current_piece['y'] -= 1
                    add_to_grid(current_piece, grid)
                    clear_rows(grid)
                    current_piece = next_piece
                    next_piece = new_piece()
                    if not valid_space(current_piece, grid):
                        game_over = True
        draw_grid()
        draw_current_piece()
        draw_next_piece()
        draw_score()
        if game_over:
            draw_game_over()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    reset_game()
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    start_time = time.time()
    main()