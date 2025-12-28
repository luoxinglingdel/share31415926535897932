import pygame
import sys
import random
import math

pygame.init()
pygame.mixer.init()
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 700
FPS = 60
DIFFICULTY_INCREASE_RATE = 0.02
MAX_DIFFICULTY = 3.0
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
explosions = []
bullet_trails = []
def create_sound(frequency, volume, duration, type='square'):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = pygame.sndarray.create(n_samples, pygame.mixer.get_init()[0])
    if type == 'square':
        period = sample_rate // frequency
        for i in range(n_samples):
            buf[i] = int(32767 * volume * (-1 if i % period < period // 2 else 1))
    elif type == 'sine':
        for i in range(n_samples):
            buf[i] = int(32767 * volume * math.sin(2 * math.pi * frequency * i / sample_rate))
    elif type == 'explosion':
        for i in range(n_samples):
            amp = volume * (1 - i / n_samples) * 32767
            buf[i] = int(random.uniform(-amp, amp))
    return pygame.sndarray.make_sound(buf)
try:
    shoot_sound = create_sound(1000, 0.2, 0.1, 'square')
    explosion_sound = create_sound(200, 0.3, 0.3, 'explosion')
    hit_sound = create_sound(500, 0.2, 0.2, 'square')
    powerup_sound = create_sound(1500, 0.2, 0.3, 'sine')
except Exception as e:
    print(f"无法创建音效: {e}")
    shoot_sound = pygame.mixer.Sound(b'')
    explosion_sound = pygame.mixer.Sound(b'')
    hit_sound = pygame.mixer.Sound(b'')
    powerup_sound = pygame.mixer.Sound(b'')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("飞机大战 - FishC Demo")
clock = pygame.time.Clock()
pygame.font.init()
try:
    font = pygame.font.SysFont(["SimHei", "Microsoft YaHei", "WenQuanYi Micro Hei"], 36)
    small_font = pygame.font.SysFont(["SimHei", "Microsoft YaHei", "WenQuanYi Micro Hei"], 24)
except:
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
class GameState:
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
class GameObject:
    def __init__(self, x, y, width, height, speed=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.rect = pygame.Rect(x, y, width, height)
        self.is_visible = True
    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y
    def draw(self, screen):
        if self.is_visible:
            pygame.draw.rect(screen, WHITE, self.rect)
    def is_off_screen(self):
        return (self.x < -self.width or self.x > SCREEN_WIDTH or
                self.y < -self.height or self.y > SCREEN_HEIGHT)
    def check_collision(self, other):
        if not self.is_visible or not other.is_visible:
            return False
        if (self.x > other.x + other.width or
                self.x + self.width < other.x or
                self.y > other.y + other.height or
                self.y + self.height < other.y):
            return False
        return self.rect.colliderect(other.rect)
    def create_explosion(self):
        global explosions
        particle_count = min(20, max(5, int((self.width + self.height) / 10)))
        size_range = (1, 5) if (self.width < 50 and self.height < 50) else (2, 8)
        color_range = (200, 255) if isinstance(self, Player) else (150, 220)
        for _ in range(particle_count):
            x = self.x + random.uniform(0, self.width)
            y = self.y + random.uniform(0, self.height)
            explosions.append(ExplosionParticle(x, y, size_range, color_range))
        try:
            explosion_sound.play()
        except:
            pass
class ExplosionParticle(GameObject):
    def __init__(self, x, y, size_range=(2, 4), color_range=(200, 255)):
        size = random.randint(*size_range)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = random.randint(15, 30)
        r = random.randint(*color_range)
        g = random.randint(100, min(r, 255))
        b = 0
        self.color = (r, g, b)
        super().__init__(x, y, size, size)
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.vx *= 0.95
        self.vy *= 0.95
        if self.lifetime < 15:
            self.color = (max(0, self.color[0] - 10), max(0, self.color[1] - 15), 0)
        super().update()
    def draw(self, screen):
        pygame.draw.circle(screen, self.color,
                           (int(self.x + self.width // 2),
                            int(self.y + self.height // 2)),
                           max(1, self.width // 2))
    def is_alive(self):
        return self.lifetime > 0
class BulletTrail(GameObject):
    def __init__(self, x, y, angle):
        size = random.randint(1, 3)
        speed = random.uniform(4, 7)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = random.randint(5, 10)
        self.color = (255, 255, random.randint(100, 255))  # 蓝白色系
        super().__init__(x, y, size, size)
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        super().update()
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
    def is_alive(self):
        return self.lifetime > 0
class Bullet(GameObject):
    def __init__(self, x, y, speed=-10, color=YELLOW):
        width = 4
        height = 15
        super().__init__(x, y, width, height, speed)
        self.color = color
        self.create_trail()
    def update(self):
        self.y += self.speed
        if random.random() < 0.3:
            self.create_trail()
        super().update()
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        glow_rect = pygame.Rect(self.x - 2, self.y - 2, self.width + 4, self.height + 4)
        temp_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(temp_surf, (255, 255, 0, 50), temp_surf.get_rect())
        screen.blit(temp_surf, (glow_rect.x, glow_rect.y))
    def check_collision(self, other):
        return self.rect.colliderect(other)
    def create_trail(self):
        global bullet_trails
        trail_x = self.x + self.width // 2
        trail_y = self.y + self.height
        bullet_trails.append(BulletTrail(trail_x, trail_y, math.pi))
class Enemy(GameObject):
    def __init__(self, x, y, width, height, speed, health=1, score_value=100):
        super().__init__(x, y, width, height, speed)
        self.health = health
        self.max_health = health
        self.score_value = score_value
        self.hit = False
        self.hit_time = 0
        self.animation_frame = 0
    def update(self):
        self.y += self.speed
        if self.hit:
            self.hit_time -= 1
            if self.hit_time <= 0:
                self.hit = False
        self.animation_frame = (self.animation_frame + 0.1) % 10
        super().update()
    def take_damage(self):
        self.health -= 1
        self.hit = True
        self.hit_time = 5
        if self.health <= 0:
            self.create_explosion()
        return self.health <= 0
    def check_collision(self, other):
        return self.rect.colliderect(other.rect)
class SmallEnemy(Enemy):
    def __init__(self, difficulty=1.0):
        width = 30
        height = 30
        x = random.randint(0, SCREEN_WIDTH - width)
        y = -height
        base_speed = random.uniform(2, 4)
        speed = base_speed * difficulty
        super().__init__(x, y, width, height, speed, health=1, score_value=100)
    def draw(self, screen):
        color = RED if self.hit else WHITE
        points = [
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + self.height // 2),
            (self.x + self.width // 2, self.y + self.height),
            (self.x, self.y + self.height // 2)
        ]
        pygame.draw.polygon(screen, color, points)
        frame = int(self.animation_frame)
        if frame % 3 == 0:
            pygame.draw.circle(screen, RED,
                               (int(self.x + self.width // 2),
                                int(self.y + self.height // 2)), 3)
        if self.speed > 3:
            for i in range(1, 4):
                alpha = 100 - i * 30
                trail_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.polygon(trail_surf, (color[0], color[1], color[2], alpha), points)
                screen.blit(trail_surf, (self.x, self.y + self.speed * i))
class LargeEnemy(Enemy):
    def __init__(self, difficulty=1.0):
        width = 80
        height = 100
        x = random.randint(0, SCREEN_WIDTH - width)
        y = -height
        base_speed = random.uniform(1, 2)
        speed = base_speed * difficulty
        health = max(1, int(5 * min(difficulty, 2.0)))
        super().__init__(x, y, width, height, speed, health=health, score_value=500)
    def draw(self, screen):
        color = RED if self.hit else WHITE
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, color, (self.x - 20, self.y + self.height // 3, 20, 40))
        pygame.draw.rect(screen, color, (self.x + self.width, self.y + self.height // 3, 20, 40))
        pygame.draw.rect(screen, GRAY,
                         (self.x + 20, self.y + self.height - 20, 10, 20))
        pygame.draw.rect(screen, GRAY,
                         (self.x + self.width - 30, self.y + self.height - 20, 10, 20))
        if int(self.animation_frame) % 3 == 0:
            pygame.draw.circle(screen, RED,
                               (int(self.x + 10), int(self.y + 10)), 5)
            pygame.draw.circle(screen, RED,
                               (int(self.x + self.width - 10), int(self.y + 10)), 5)
        health_ratio = self.health / self.max_health
        health_color = GREEN if health_ratio > 0.5 else YELLOW if health_ratio > 0.2 else RED
        pygame.draw.rect(screen, WHITE,
                         (self.x - 1, self.y - 11, self.width + 2, 7))
        pygame.draw.rect(screen, health_color,
                         (self.x, self.y - 10, self.width * health_ratio, 5))
class Player(GameObject):
    def __init__(self):
        width = 60
        height = 80
        x = SCREEN_WIDTH // 2 - width // 2
        y = SCREEN_HEIGHT - height - 20
        speed = 5
        super().__init__(x, y, width, height, speed)
        self.lives = 3
        self.invincible = False
        self.invincible_time = 0
        self.shoot_cooldown = 0
    def update(self):
        if self.invincible:
            self.invincible_time -= 1
            if self.invincible_time <= 0:
                self.invincible = False
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
        super().update()
    def shoot(self):
        if self.shoot_cooldown == 0:
            bullet_x = self.x + self.width // 2 - 2
            bullet_y = self.y
            bullet = Bullet(bullet_x, bullet_y)
            self.shoot_cooldown = 15
            try:
                shoot_sound.play()
            except:
                pass
            return bullet
        return None
    def draw(self, screen):
        if not self.invincible or pygame.time.get_ticks() % 100 < 50:
            main_color = BLUE if self.invincible else WHITE
            points = [
                (self.x + self.width // 2, self.y),
                (self.x, self.y + self.height),
                (self.x + self.width, self.y + self.height)
            ]
            pygame.draw.polygon(screen, main_color, points)
            pygame.draw.rect(screen, main_color, (self.x - 10, self.y + self.height // 2, 10, 20))
            pygame.draw.rect(screen, main_color, (self.x + self.width, self.y + self.height // 2, 10, 20))
            pygame.draw.rect(screen, main_color, (self.x + self.width // 2 - 5, self.y + self.height - 10, 10, 20))
            pygame.draw.circle(screen, YELLOW,
                               (int(self.x + self.width // 2),
                                int(self.y + self.height // 3)), 5)
            if random.random() < 0.7:
                for i in range(2):
                    offset = (-15, 15)[i]
                    flame_height = random.randint(8, 15)
                    flame_width = random.randint(3, 6)
                    flame_x = self.x + self.width // 2 - flame_width // 2 + offset
                    flame_y = self.y + self.height
                    for j in range(flame_height):
                        intensity = 1.0 - j / flame_height
                        flame_color = (
                            255,
                            int(165 * intensity),
                            0
                        )
                        pygame.draw.rect(screen, flame_color,
                                         (flame_x, flame_y + j, flame_width, 1))
    def take_damage(self):
        if not self.invincible:
            try:
                hit_sound.play()
            except:
                pass
            self.create_explosion()

            self.lives -= 1
            self.invincible = True
            self.invincible_time = 120
            return True
        return False
    def die(self):
        self.create_explosion()
        self.is_visible = False
    def reset(self):
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.invincible = True
        self.invincible_time = 120
        self.is_visible = True
class Star(GameObject):
    def __init__(self):
        size = random.randint(1, 3)
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        brightness = random.randint(100, 255)
        self.color = (brightness, brightness, brightness)
        speed = random.uniform(0.5, 2.0)
        super().__init__(x, y, size, size, speed)
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = -self.height
            self.x = random.randint(0, SCREEN_WIDTH)
        super().update()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

def game_loop():
    game_state = GameState.MENU
    score = 0
    player = Player()
    bullets = []
    enemies = []
    stars = []
    for _ in range(100):
        stars.append(Star())
    enemy_spawn_timer = 0
    game_time = 0
    difficulty = 1.0
    base_small_spawn_rate = 60
    base_large_spawn_rate = 300
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_state == GameState.MENU and event.key == pygame.K_SPACE:
                    game_state = GameState.PLAYING
                    player.reset()
                    bullets.clear()
                    enemies.clear()
                    explosions.clear()
                    bullet_trails.clear()
                    enemy_spawn_timer = 0
                elif game_state == GameState.PLAYING:
                    if event.key == pygame.K_p:
                        game_state = GameState.PAUSED
                    elif event.key == pygame.K_ESCAPE:
                        game_state = GameState.MENU
                elif game_state == GameState.PAUSED:
                    if event.key == pygame.K_p:
                        game_state = GameState.PLAYING
                    elif event.key == pygame.K_r:
                        game_state = GameState.PLAYING
                        score = 0
                        player.lives = 3
                        player.reset()
                        bullets.clear()
                        enemies.clear()
                        explosions.clear()
                        bullet_trails.clear()
                        enemy_spawn_timer = 0
                    elif event.key == pygame.K_ESCAPE:
                        game_state = GameState.MENU
                elif game_state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        game_state = GameState.PLAYING
                        score = 0
                        player.lives = 3
                        player.reset()
                        bullets.clear()
                        enemies.clear()
                        explosions.clear()
                        bullet_trails.clear()
                        enemy_spawn_timer = 0
                    elif event.key == pygame.K_ESCAPE:
                        game_state = GameState.MENU
                if game_state == GameState.PLAYING and event.key == pygame.K_SPACE:
                    bullet = player.shoot()
                    if bullet:
                        bullets.append(bullet)
        if game_state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                bullet = player.shoot()
                if bullet:
                    bullets.append(bullet)
        screen.fill(BLACK)
        if game_state == GameState.MENU:
            # 更新和绘制星星背景
            for star in stars:
                star.update()
                star.draw(screen)
            draw_menu()
        elif game_state == GameState.PLAYING:
            game_time += 1
            if game_time % 100 == 0:
                difficulty = min(MAX_DIFFICULTY, difficulty + DIFFICULTY_INCREASE_RATE)
            small_enemy_spawn_rate = max(20, int(base_small_spawn_rate / difficulty))
            large_enemy_spawn_rate = max(100, int(base_large_spawn_rate / difficulty))
            for star in stars:
                star.update()
                star.draw(screen)
            player.update()
            player.draw(screen)
            for bullet in bullets[:]:
                bullet.update()
                bullet.draw(screen)
                if bullet.is_off_screen():
                    bullets.remove(bullet)
            enemy_spawn_timer += 1
            if enemy_spawn_timer % small_enemy_spawn_rate == 0:
                enemies.append(SmallEnemy(difficulty))
            if enemy_spawn_timer % large_enemy_spawn_rate == 0:
                enemies.append(LargeEnemy(difficulty))
            for enemy in enemies[:]:
                enemy.update()
                enemy.draw(screen)
                if enemy.is_off_screen():
                    enemies.remove(enemy)
                if player.check_collision(enemy):
                    player.die()
                    enemies.remove(enemy)
                    game_state = GameState.GAME_OVER
            bullets_to_remove = []
            enemies_to_remove = []
            for i, bullet in enumerate(bullets):
                for j, enemy in enumerate(enemies):
                    if bullet.check_collision(enemy):
                        bullets_to_remove.append(i)
                        if enemy.take_damage():
                            enemies_to_remove.append(j)
                            score += enemy.score_value
                        break
            for i in sorted(bullets_to_remove, reverse=True):
                del bullets[i]
            for j in sorted(enemies_to_remove, reverse=True):
                del enemies[j]
            for explosion in explosions[:]:
                explosion.update()
                explosion.draw(screen)
                if not explosion.is_alive():
                    explosions.remove(explosion)
            for trail in bullet_trails[:]:
                trail.update()
                trail.draw(screen)
                if not trail.is_alive():
                    bullet_trails.remove(trail)
            draw_lives(player.lives)
            draw_score(score)
            if player.lives <= 0:
                game_state = GameState.GAME_OVER
        elif game_state == GameState.PAUSED:
            for star in stars:
                star.draw(screen)
            player.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            for explosion in explosions:
                explosion.draw(screen)
            for trail in bullet_trails:
                trail.draw(screen)
            draw_lives(player.lives)
            draw_score(score)
            draw_pause()
        elif game_state == GameState.GAME_OVER:
            for star in stars:
                star.update()
                star.draw(screen)
            for explosion in explosions:
                explosion.draw(screen)
            for trail in bullet_trails:
                trail.draw(screen)
            draw_game_over(score)
        pygame.display.flip()
        clock.tick(FPS)
def draw_lives(lives):
    lives_text = small_font.render(f"生命: {lives}", True, WHITE)
    screen.blit(lives_text, (10, 10))
def draw_score(score):
    score_text = small_font.render(f"得分: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))
def draw_menu():
    menu_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    menu_bg.fill((0, 0, 0, 128))
    screen.blit(menu_bg, (0, 0))
    title_text = font.render("飞机大战", True, WHITE)
    title_shadow = font.render("飞机大战", True, (100, 100, 100))
    screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 2, 200 + 2))
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 200))
    start_text = small_font.render("按空格键开始游戏", True, WHITE)
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 300))
    controls_text1 = small_font.render("使用方向键移动", True, WHITE)
    controls_text2 = small_font.render("按空格键射击", True, WHITE)
    controls_text3 = small_font.render("按P键暂停游戏", True, WHITE)
    screen.blit(controls_text1, (SCREEN_WIDTH // 2 - controls_text1.get_width() // 2, 350))
    screen.blit(controls_text2, (SCREEN_WIDTH // 2 - controls_text2.get_width() // 2, 380))
    screen.blit(controls_text3, (SCREEN_WIDTH // 2 - controls_text3.get_width() // 2, 410))
def draw_pause():
    pause_bg = pygame.Surface((SCREEN_WIDTH * 0.8, SCREEN_HEIGHT * 0.4), pygame.SRCALPHA)
    pause_bg.fill((0, 0, 0, 180))  # 半透明黑色
    bg_x = SCREEN_WIDTH // 2 - pause_bg.get_width() // 2
    bg_y = SCREEN_HEIGHT // 2 - pause_bg.get_height() // 2
    screen.blit(pause_bg, (bg_x, bg_y))
    pause_text = font.render("游戏暂停", True, WHITE)
    resume_text = small_font.render("按P键继续游戏", True, WHITE)
    restart_text = small_font.render("按R键重新开始", True, WHITE)
    menu_text = small_font.render("按ESC返回主菜单", True, WHITE)
    screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, bg_y + 30))
    screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, bg_y + 80))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, bg_y + 110))
    screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, bg_y + 140))
def draw_game_over(score):
    over_bg = pygame.Surface((SCREEN_WIDTH * 0.8, SCREEN_HEIGHT * 0.5), pygame.SRCALPHA)
    over_bg.fill((0, 0, 0, 180))  # 半透明黑色
    bg_x = SCREEN_WIDTH // 2 - over_bg.get_width() // 2
    bg_y = SCREEN_HEIGHT // 2 - over_bg.get_height() // 2
    screen.blit(over_bg, (bg_x, bg_y))
    over_text = font.render("游戏结束", True, RED)
    score_text = small_font.render(f"你的得分: {score}", True, WHITE)
    restart_text = small_font.render("按R键重新开始", True, WHITE)
    menu_text = small_font.render("按ESC返回主菜单", True, WHITE)
    screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, bg_y + 30))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, bg_y + 80))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, bg_y + 130))
    screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, bg_y + 160))
if __name__ == "__main__":
    game_loop()