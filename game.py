import pygame
import random
import sys
import os
import math
import wave
import struct

# Initialize pygame
pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    print("Warning: audio disabled")

WIDTH, HEIGHT = 800, 600
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ninja vs Zombies")


def ensure_directories():
    os.makedirs(os.path.join(ASSET_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(ASSET_DIR, "sounds"), exist_ok=True)


def generate_image(path, draw_func):
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    draw_func(surface)
    pygame.image.save(surface, path)


def generate_sound(path, frequency, duration):
    sample_rate = 44100
    amplitude = 32767
    frames = []
    for i in range(int(duration * sample_rate)):
        value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
        frames.append(struct.pack("<h", value))
    with wave.open(path, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"".join(frames))


def ensure_assets():
    ensure_directories()
    images = os.path.join(ASSET_DIR, "images")
    sounds = os.path.join(ASSET_DIR, "sounds")

    ninja_path = os.path.join(images, "ninja.png")
    if not os.path.exists(ninja_path):
        def draw_ninja(s):
            s.fill((0, 0, 0))
            pygame.draw.rect(s, (255, 255, 255), (6, 10, 20, 6))
        generate_image(ninja_path, draw_ninja)

    oni_path = os.path.join(images, "oni.png")
    if not os.path.exists(oni_path):
        generate_image(oni_path, lambda s: s.fill((200, 0, 0)))

    coin_path = os.path.join(images, "coin.png")
    if not os.path.exists(coin_path):
        def draw_coin(s):
            pygame.draw.circle(s, (255, 215, 0), (16, 16), 12)
        generate_image(coin_path, draw_coin)

    kunai_path = os.path.join(images, "kunai.png")
    if not os.path.exists(kunai_path):
        def draw_kunai(s):
            pygame.draw.polygon(s, (192, 192, 192), [(16, 0), (28, 20), (16, 31), (4, 20)])
        generate_image(kunai_path, draw_kunai)

    if pygame.mixer.get_init():
        coin_sound_path = os.path.join(sounds, "coin.wav")
        if not os.path.exists(coin_sound_path):
            generate_sound(coin_sound_path, 880, 0.1)
        throw_sound_path = os.path.join(sounds, "throw.wav")
        if not os.path.exists(throw_sound_path):
            generate_sound(throw_sound_path, 660, 0.1)
        hit_sound_path = os.path.join(sounds, "hit.wav")
        if not os.path.exists(hit_sound_path):
            generate_sound(hit_sound_path, 220, 0.1)
        bg_sound_path = os.path.join(sounds, "background.wav")
        if not os.path.exists(bg_sound_path):
            generate_sound(bg_sound_path, 110, 1.0)


class Zombie(pygame.sprite.Sprite):
    """Animated zombie enemy using 3x4 sprite sheets."""

    def __init__(self, spritesheet_path):
        super().__init__()
        self.sprite_sheet = pygame.image.load(spritesheet_path).convert_alpha()
        # Determine frame dimensions from the sheet itself (3 columns x 4 rows)
        sheet_w, sheet_h = self.sprite_sheet.get_size()
        self.frames_per_direction = 3
        self.frame_width = sheet_w // self.frames_per_direction
        self.frame_height = sheet_h // 4
        # Sprite sheet rows are ordered: down, right, up, left
        self.directions = {
            "down": 0,
            "right": 1,
            "up": 2,
            "left": 3,
        }

        self.direction = "down"
        self.current_frame = 0
        self.animation_timer = 0
        # Slightly slower animation for smoother movement
        self.animation_speed = 0.2  # seconds per frame

        self.image = self.get_frame()
        self.rect = self.image.get_rect()

    def get_frame(self):
        row = self.directions[self.direction]
        col = self.current_frame % self.frames_per_direction
        x = col * self.frame_width
        y = row * self.frame_height
        frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame.blit(
            self.sprite_sheet,
            (0, 0),
            pygame.Rect(x, y, self.frame_width, self.frame_height),
        )
        return frame

    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % self.frames_per_direction
            self.image = self.get_frame()

    def set_direction(self, new_direction):
        if new_direction in self.directions and new_direction != self.direction:
            self.direction = new_direction
            self.current_frame = 0
            self.image = self.get_frame()


ensure_assets()

# Load images
# Load Block Ninja sprites
player_idle_img = pygame.image.load(
    os.path.join(ASSET_DIR, "Block Ninja", "idle.PNG")
)
player_walk_imgs = [
    pygame.image.load(os.path.join(ASSET_DIR, "Block Ninja", "walk a.PNG")),
    pygame.image.load(os.path.join(ASSET_DIR, "Block Ninja", "walk b.PNG")),
    pygame.image.load(os.path.join(ASSET_DIR, "Block Ninja", "walk c.PNG")),
    pygame.image.load(os.path.join(ASSET_DIR, "Block Ninja", "walk d.PNG")),
]
# Zombie sprite sheets (3 columns x 4 rows)
zombie_sheet_paths = [
    os.path.join(ASSET_DIR, "Zombies", "Zombies", f"{i}ZombieSpriteSheet.png")
    for i in range(1, 7)
]

# Coin rotation sprite sheet (6 frames horizontally)
coin_sheet = pygame.image.load(os.path.join(ASSET_DIR, "coin_rot_anim.png")).convert_alpha()
coin_frame_size = coin_sheet.get_height()
coin_frames = []
for i in range(coin_sheet.get_width() // coin_frame_size):
    frame = pygame.Surface((coin_frame_size, coin_frame_size), pygame.SRCALPHA)
    frame.blit(
        coin_sheet,
        (0, 0),
        pygame.Rect(i * coin_frame_size, 0, coin_frame_size, coin_frame_size),
    )
    coin_frames.append(frame)
shuriken_img = pygame.image.load(
    os.path.join(ASSET_DIR, "Block Ninja", "shuriken.PNG")
)

# Load sounds
if pygame.mixer.get_init():
    coin_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "sounds", "coin.wav"))
    throw_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "sounds", "throw.wav"))
    hit_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "sounds", "hit.wav"))
    pygame.mixer.music.load(os.path.join(ASSET_DIR, "sounds", "background.wav"))
    pygame.mixer.music.play(-1)
else:
    coin_sound = throw_sound = hit_sound = None

WIDTH, HEIGHT = 800, 600
# Use a dark green background instead of an image
BACKGROUND_COLOR = (0, 100, 0)

player_radius = player_idle_img.get_width() // 2
player_speed = 5

projectile_radius = shuriken_img.get_width() // 2
projectile_speed = 10

# Determine enemy sprite size from a sample zombie sheet
sample_sheet = pygame.image.load(zombie_sheet_paths[0])
enemy_frame_w = sample_sheet.get_width() // 3
enemy_frame_h = sample_sheet.get_height() // 4
enemy_size = max(enemy_frame_w, enemy_frame_h)
enemy_speed = 3
coin_size = coin_frame_size
coin_speed = 4

# new color for ammo pickup/projectile ui
AMMO_COLOR = (255, 255, 255)
player_idle_img = player_idle_img.convert_alpha()
player_walk_imgs = [img.convert_alpha() for img in player_walk_imgs]
shuriken_img = shuriken_img.convert_alpha()
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def check_collision(px, py, ex, ey, size, radius):
    circle_rect = pygame.Rect(px - radius, py - radius,
                              radius * 2, radius * 2)
    square_rect = pygame.Rect(ex, ey, size, size)
    return circle_rect.colliderect(square_rect)


def spawn_enemy():
    """Spawn an enemy from a random edge moving inwards."""
    direction = random.choice(["down", "up", "left", "right"])
    if direction == "down":
        x = random.randint(0, WIDTH - enemy_size)
        y = -enemy_size
        dx, dy = 0, enemy_speed
    elif direction == "up":
        x = random.randint(0, WIDTH - enemy_size)
        y = HEIGHT
        dx, dy = 0, -enemy_speed
    elif direction == "left":
        x = WIDTH
        y = random.randint(0, HEIGHT - enemy_size)
        dx, dy = -enemy_speed, 0
    else:  # right
        x = -enemy_size
        y = random.randint(0, HEIGHT - enemy_size)
        dx, dy = enemy_speed, 0
    return x, y, dx, dy, direction


def spawn_coin():
    """Spawn a coin from a random edge moving across the screen."""
    direction = random.choice(["down", "up", "left", "right"])
    if direction == "down":
        x = random.randint(0, WIDTH - coin_size)
        y = -coin_size
        dx, dy = 0, coin_speed
    elif direction == "up":
        x = random.randint(0, WIDTH - coin_size)
        y = HEIGHT
        dx, dy = 0, -coin_speed
    elif direction == "left":
        x = WIDTH
        y = random.randint(0, HEIGHT - coin_size)
        dx, dy = -coin_speed, 0
    else:  # right
        x = -coin_size
        y = random.randint(0, HEIGHT - coin_size)
        dx, dy = coin_speed, 0
    return x, y, dx, dy


def spawn_ammo():
    """Spawn a stationary ammo pickup inside the screen."""
    x = random.randint(projectile_radius, WIDTH - projectile_radius)
    y = random.randint(projectile_radius, HEIGHT - projectile_radius)
    return x, y


def run_game():
    player_x = WIDTH // 2
    player_y = HEIGHT // 2

    player_anim_index = 0
    player_anim_timer = 0
    current_img = player_idle_img

    enemy_x, enemy_y, enemy_dx, enemy_dy, enemy_dir = spawn_enemy()
    enemy = Zombie(random.choice(zombie_sheet_paths))
    enemy.set_direction(enemy_dir)
    enemy.rect.topleft = (enemy_x, enemy_y)
    enemy_spawn_count = 1

    coin_x, coin_y, coin_dx, coin_dy = spawn_coin()
    coin_anim_index = 0
    coin_anim_timer = 0

    ammo_x, ammo_y = None, None

    projectiles = []

    score = 0
    ammo = 5

    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and ammo > 0:
                    projectiles.append([player_x, player_y, -projectile_speed, 0, 0])
                    ammo -= 1
                    if throw_sound:
                        throw_sound.play()
                elif event.key == pygame.K_RIGHT and ammo > 0:
                    projectiles.append([player_x, player_y, projectile_speed, 0, 0])
                    ammo -= 1
                    if throw_sound:
                        throw_sound.play()
                elif event.key == pygame.K_UP and ammo > 0:
                    projectiles.append([player_x, player_y, 0, -projectile_speed, 0])
                    ammo -= 1
                    if throw_sound:
                        throw_sound.play()
                elif event.key == pygame.K_DOWN and ammo > 0:
                    projectiles.append([player_x, player_y, 0, projectile_speed, 0])
                    ammo -= 1
                    if throw_sound:
                        throw_sound.play()

        keys = pygame.key.get_pressed()
        moving = False
        if keys[pygame.K_a]:
            player_x -= player_speed
            moving = True
        if keys[pygame.K_d]:
            player_x += player_speed
            moving = True
        if keys[pygame.K_w]:
            player_y -= player_speed
            moving = True
        if keys[pygame.K_s]:
            player_y += player_speed
            moving = True

        if moving:
            player_anim_timer += 1
            if player_anim_timer >= 10:
                player_anim_timer = 0
                player_anim_index = (player_anim_index + 1) % len(player_walk_imgs)
            current_img = player_walk_imgs[player_anim_index]
        else:
            player_anim_timer = 0
            current_img = player_idle_img

        player_x = max(player_radius, min(WIDTH - player_radius, player_x))
        player_y = max(player_radius, min(HEIGHT - player_radius, player_y))

        enemy.update(dt)

        enemy_x += enemy_dx
        enemy_y += enemy_dy
        enemy.rect.topleft = (enemy_x, enemy_y)
        if (
            enemy_x < -enemy_size
            or enemy_x > WIDTH
            or enemy_y < -enemy_size
            or enemy_y > HEIGHT
        ):
            enemy_x, enemy_y, enemy_dx, enemy_dy, enemy_dir = spawn_enemy()
            enemy = Zombie(random.choice(zombie_sheet_paths))
            enemy.set_direction(enemy_dir)
            enemy.rect.topleft = (enemy_x, enemy_y)
            enemy_spawn_count += 1
            if enemy_spawn_count % 4 == 0 and ammo_x is None:
                ammo_x, ammo_y = spawn_ammo()

        coin_x += coin_dx
        coin_y += coin_dy
        coin_anim_timer += dt
        if coin_anim_timer >= 0.1:
            coin_anim_timer = 0
            if coin_dx > 0 or coin_dy < 0:
                coin_anim_index = (coin_anim_index + 1) % len(coin_frames)
            else:
                coin_anim_index = (coin_anim_index - 1) % len(coin_frames)
        if (
            coin_x < -coin_size
            or coin_x > WIDTH
            or coin_y < -coin_size
            or coin_y > HEIGHT
        ):
            coin_x, coin_y, coin_dx, coin_dy = spawn_coin()
            coin_anim_index = 0
            coin_anim_timer = 0

        # Update projectiles
        for p in projectiles[:]:
            p[0] += p[2]
            p[1] += p[3]
            p[4] = (p[4] + 15) % 360
            if (
                p[0] < -projectile_radius
                or p[0] > WIDTH + projectile_radius
                or p[1] < -projectile_radius
                or p[1] > HEIGHT + projectile_radius
            ):
                projectiles.remove(p)
                continue
            if check_collision(p[0], p[1], enemy_x, enemy_y, enemy_size, projectile_radius):
                score += 1
                if hit_sound:
                    hit_sound.play()
                enemy_x, enemy_y, enemy_dx, enemy_dy, enemy_dir = spawn_enemy()
                enemy = Zombie(random.choice(zombie_sheet_paths))
                enemy.set_direction(enemy_dir)
                enemy.rect.topleft = (enemy_x, enemy_y)
                enemy_spawn_count += 1
                if enemy_spawn_count % 4 == 0 and ammo_x is None:
                    ammo_x, ammo_y = spawn_ammo()
                projectiles.remove(p)
                continue
            if check_collision(p[0], p[1], coin_x, coin_y, coin_size, projectile_radius):
                score += 1
                if coin_sound:
                    coin_sound.play()
                coin_x, coin_y, coin_dx, coin_dy = spawn_coin()
                coin_anim_index = 0
                coin_anim_timer = 0
                projectiles.remove(p)

        if check_collision(player_x, player_y, enemy_x, enemy_y, enemy_size, player_radius):
            running = False

        if check_collision(player_x, player_y, coin_x, coin_y, coin_size, player_radius):
            score += 1
            if coin_sound:
                coin_sound.play()
            coin_x, coin_y, coin_dx, coin_dy = spawn_coin()
            coin_anim_index = 0
            coin_anim_timer = 0

        if ammo_x is not None and check_collision(
            player_x, player_y,
            ammo_x - projectile_radius, ammo_y - projectile_radius,
            projectile_radius * 2, player_radius
        ):
            ammo += 1
            ammo_x, ammo_y = None, None

        screen.fill(BACKGROUND_COLOR)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        # ammo indicator
        screen.blit(shuriken_img, shuriken_img.get_rect(center=(10, 50)))
        ammo_text = font.render(str(ammo), True, (255, 255, 255))
        screen.blit(ammo_text, (25, 40))

        screen.blit(current_img, current_img.get_rect(center=(player_x, player_y)))
        screen.blit(enemy.image, enemy.rect)
        screen.blit(coin_frames[coin_anim_index], (coin_x, coin_y))
        if ammo_x is not None:
            screen.blit(shuriken_img, shuriken_img.get_rect(center=(ammo_x, ammo_y)))
        for p in projectiles:
            rotated = pygame.transform.rotate(shuriken_img, p[4])
            rect = rotated.get_rect(center=(int(p[0]), int(p[1])))
            screen.blit(rotated, rect)

        pygame.display.flip()

    return score


def game_over_screen(score):
    over_font = pygame.font.SysFont(None, 48)
    info_font = pygame.font.SysFont(None, 36)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    return False

        screen.fill(BACKGROUND_COLOR)
        over_text = over_font.render("Game Over!", True, (255, 255, 255))
        score_text = info_font.render(f"Score: {score}", True, (255, 255, 255))
        prompt_text = info_font.render("Press R to Play Again or Q to Quit", True, (255, 255, 255))

        screen.blit(over_text, over_text.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
        screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        screen.blit(prompt_text, prompt_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3)))

        pygame.display.flip()
        clock.tick(60)


def main():
    while True:
        score = run_game()
        if not game_over_screen(score):
            break

    pygame.quit()


if __name__ == "__main__":
    main()
