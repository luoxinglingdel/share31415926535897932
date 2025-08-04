import pygame
import random
import time
import sys
from pygame.locals import *
pygame.init()
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('贪吃蛇游戏1.0')
BRIGHT_GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
font = pygame.font.SysFont('SimHei', 36)
small_font = pygame.font.SysFont('SimHei', 24)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
snake_direction = RIGHT
snake_color_gradient = [BRIGHT_GREEN]  
obstacles = []
for i in range(GRID_WIDTH):
    obstacles.append((i, 0))
    obstacles.append((i, GRID_HEIGHT - 1))
for i in range(1, GRID_HEIGHT - 1):
    obstacles.append((0, i))
    obstacles.append((GRID_WIDTH - 1, i))
cross_center_x, cross_center_y = GRID_WIDTH // 2, GRID_HEIGHT // 2
cross_size = 3
for i in range(cross_center_x - cross_size, cross_center_x + cross_size + 1):
    if 0 < i < GRID_WIDTH - 1:
        obstacles.append((i, cross_center_y))
for i in range(cross_center_y - cross_size, cross_center_y + cross_size + 1):
    if 0 < i < GRID_HEIGHT - 1:
        obstacles.append((cross_center_x, i))
corner_size = 2
corners = [
    (corner_size, corner_size),
    (GRID_WIDTH - corner_size - 1, corner_size),
    (corner_size, GRID_HEIGHT - corner_size - 1),
    (GRID_WIDTH - corner_size - 1, GRID_HEIGHT - corner_size - 1)
]
for corner in corners:
    for i in range(corner_size):
        obstacles.append((corner[0] + i, corner[1]))
        obstacles.append((corner[0], corner[1] + i))
        obstacles.append((corner[0] + i, corner[1] + corner_size))
        obstacles.append((corner[0] + corner_size, corner[1] + i))
def generate_food():
    while True:
        food = (random.randint(1, GRID_WIDTH - 2), random.randint(1, GRID_HEIGHT - 2))
        if food not in snake and food not in obstacles:
            return food

food = generate_food()
is_special_food = random.random() < 0.25  
food_timer = time.time()
score = 0
game_over = False
game_start_time = time.time()
invincible_timer = game_start_time  
food_visible = True  
blink_timer = time.time()  
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if game_over and event.key == K_r:
                snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
                snake_direction = RIGHT
                snake_color_gradient = [BRIGHT_GREEN]  # 重置颜色梯度
                food = generate_food()
                is_special_food = random.random() < 0.25
                score = 0
                game_over = False
                game_start_time = time.time()
                invincible_timer = game_start_time
            elif not game_over:
                if event.key == K_UP and snake_direction != DOWN:
                    snake_direction = UP
                elif event.key == K_DOWN and snake_direction != UP:
                    snake_direction = DOWN
                elif event.key == K_LEFT and snake_direction != RIGHT:
                    snake_direction = LEFT
                elif event.key == K_RIGHT and snake_direction != LEFT:
                    snake_direction = RIGHT

    if not game_over:
        new_head = (snake[0][0] + snake_direction[0], snake[0][1] + snake_direction[1])
        if (time.time() - invincible_timer >= 5):
            if (new_head in obstacles or
                new_head[0] <= 0 or new_head[0] >= GRID_WIDTH - 1 or
                new_head[1] <= 0 or new_head[1] >= GRID_HEIGHT - 1):
                game_over = True
            if (time.time() - invincible_timer < 5 and new_head in snake):
                pass
            elif new_head in snake:
                game_over = True
        snake.insert(0, new_head)
        if new_head == food:
            if is_special_food:
                score += 20
                for _ in range(2):
                    snake_color_gradient.append(DARK_GREEN)
            else:
                score += 10
                snake_color_gradient.append(DARK_GREEN)
            food = generate_food()
            is_special_food = random.random() < 0.25
            food_timer = time.time()
        else:
            snake.pop()
            if snake_color_gradient:  
                snake_color_gradient.pop()
    screen.fill(BLACK)
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, DARK_GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, DARK_GRAY, (0, y), (WIDTH, y))
    for obs in obstacles:
        pygame.draw.rect(screen, GRAY, (obs[0] * CELL_SIZE, obs[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for i, (x, y) in enumerate(snake):
        if not snake_color_gradient:
            snake_color_gradient = [BRIGHT_GREEN]
        snake_color = snake_color_gradient[i % len(snake_color_gradient)]
        pygame.draw.rect(screen, snake_color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        if i == 0:
            eye_size = CELL_SIZE // 5
            eye_offset_x = CELL_SIZE // 4
            eye_offset_y = CELL_SIZE // 4
            if snake_direction == UP:
                left_eye = (x * CELL_SIZE + eye_offset_x, y * CELL_SIZE + eye_offset_y)
                right_eye = (x * CELL_SIZE + CELL_SIZE - eye_offset_x - eye_size, y * CELL_SIZE + eye_offset_y)
            elif snake_direction == DOWN:
                left_eye = (x * CELL_SIZE + eye_offset_x, y * CELL_SIZE + CELL_SIZE - eye_offset_y - eye_size)
                right_eye = (x * CELL_SIZE + CELL_SIZE - eye_offset_x - eye_size, y * CELL_SIZE + CELL_SIZE - eye_offset_y - eye_size)
            elif snake_direction == LEFT:
                left_eye = (x * CELL_SIZE + eye_offset_y, y * CELL_SIZE + eye_offset_x)
                right_eye = (x * CELL_SIZE + eye_offset_y, y * CELL_SIZE + CELL_SIZE - eye_offset_x - eye_size)
            else:  # RIGHT
                left_eye = (x * CELL_SIZE + CELL_SIZE - eye_offset_y - eye_size, y * CELL_SIZE + eye_offset_x)
                right_eye = (x * CELL_SIZE + CELL_SIZE - eye_offset_y - eye_size, y * CELL_SIZE + CELL_SIZE - eye_offset_x - eye_size)

            pygame.draw.rect(screen, BLACK, (left_eye[0], left_eye[1], eye_size, eye_size))
            pygame.draw.rect(screen, BLACK, (right_eye[0], right_eye[1], eye_size, eye_size))
    food_x, food_y = food
    food_rect = (food_x * CELL_SIZE, food_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    if is_special_food:
        if time.time() - blink_timer > 0.3:
            blink_timer = time.time()
            food_visible = not food_visible if 'food_visible' in locals() else True
        if food_visible:
            pygame.draw.circle(screen, GOLD, (food_x * CELL_SIZE + CELL_SIZE // 2, food_y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)
            for i in range(5):
                angle = i * 2 * 3.14159 / 5
                x = food_x * CELL_SIZE + CELL_SIZE // 2 + int(CELL_SIZE * 0.3 * (0.5 + 0.5 * i) * (1.5 * (i % 2)) * (i % 3) * (i % 4) * (i % 5)) * i * i * i
                y = food_y * CELL_SIZE + CELL_SIZE // 2 + int(CELL_SIZE * 0.3 * (0.5 + 0.5 * i) * i * i * i)
                pygame.draw.circle(screen, WHITE, (x, y), 2)
    else:
        pygame.draw.circle(screen, RED, (food_x * CELL_SIZE + CELL_SIZE // 2, food_y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)
    if is_special_food and time.time() - food_timer > 5:  
        food = generate_food()
        is_special_food = False
        food_visible = True  # 重置可见性
    score_text = font.render(f'分数: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))
    if time.time() - invincible_timer < 5:
        invincible_text = small_font.render('无敌时间: 前5秒可以穿墙', True, WHITE)
        screen.blit(invincible_text, (10, 50))
    if game_over:
        game_over_text = font.render('游戏结束！', True, WHITE)
        restart_text = small_font.render('按R键重新开始', True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))

    pygame.display.update()
    clock.tick(10)  