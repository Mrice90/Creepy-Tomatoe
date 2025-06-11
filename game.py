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
    pygame.mixer.set_num_channels(32)
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
        # Custom sound effects are now included with the project so we no longer
        # generate placeholder sounds. Any required files should be placed under
        # ``assets/sounds`` beforehand.
        pass


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
        scaled = pygame.transform.scale(
            frame,
            (
                int(self.frame_width * ZOMBIE_SCALE),
                int(self.frame_height * ZOMBIE_SCALE),
            ),
        )
        return scaled

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
    sound_dir = os.path.join(ASSET_DIR, "sounds")

    def find_sound_files(prefix):
        paths = []
        for root, _, files in os.walk(sound_dir):
            for name in sorted(files):
                low = name.lower()
                if low.startswith(prefix) and low.split(".")[-1] in ("wav", "ogg", "mp3"):
                    paths.append(os.path.join(root, name))
        return paths

    def load_sound_variations(prefix):
        variations = []
        for path in find_sound_files(prefix):
            if prefix.startswith("hit") and path.lower().endswith(".mp3"):
                continue
            try:
                variations.append(pygame.mixer.Sound(path))
            except pygame.error:
                pass
        return variations

    # Load only single coin and swish sounds to avoid randomization issues
    coin_sound = None
    coin_path = os.path.join(sound_dir, "coin_sounds", "coin1.wav")
    if os.path.exists(coin_path):
        try:
            coin_sound = pygame.mixer.Sound(coin_path)
        except pygame.error:
            pass

    swish_sound = None
    swish_path = os.path.join(sound_dir, "swishes", "swishes", "swish-1.wav")
    if os.path.exists(swish_path):
        try:
            swish_sound = pygame.mixer.Sound(swish_path)
        except pygame.error:
            pass

    hit_sound_path = os.path.join(sound_dir, "5Hit_Sounds", "mp3", "hit3.mp3")
    if os.path.exists(hit_sound_path):
        try:
            hit_sound = pygame.mixer.Sound(hit_sound_path)
        except pygame.error:
            hit_sound = None
    else:
        hit_sound = None

    track_files = [
        ("8-bit Battler", "8 Bit Battler.wav"),
        ("Komiku", "Komiku - It's time for adventure vol 2 - 03 Battle Theme.mp3"),
        ("New Battle", "New Battle.wav"),
    ]
    bg_tracks = []
    bg_track_names = []
    for name, fname in track_files:
        path = os.path.join(sound_dir, fname)
        if os.path.exists(path):
            bg_tracks.append(path)
            bg_track_names.append(name)

    current_track_index = 0
    if "Komiku" in bg_track_names:
        current_track_index = bg_track_names.index("Komiku")
    if bg_tracks:
        try:
            pygame.mixer.music.load(bg_tracks[current_track_index])
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass
else:
    coin_sound = None
    swish_sound = None
    hit_sound = None
    bg_tracks = []
    bg_track_names = []
    current_track_index = 0

# ---------------------------------------------------------------------------
# Volume configuration helpers
# ---------------------------------------------------------------------------
master_volume = 100
sfx_volume = 100
music_volume = 100

def apply_volume():
    """Apply current volume settings to all loaded sounds."""
    global master_volume, sfx_volume, music_volume
    total_sfx = (master_volume / 100) * (sfx_volume / 100)
    total_music = (master_volume / 100) * (music_volume / 100)
    if pygame.mixer.get_init():
        if coin_sound:
            coin_sound.set_volume(total_sfx)
        if swish_sound:
            swish_sound.set_volume(total_sfx)
        if hit_sound:
            hit_sound.set_volume(total_sfx)
        pygame.mixer.music.set_volume(total_music)

apply_volume()

def start_music():
    """Ensure background music is playing using the selected track."""
    if pygame.mixer.get_init() and bg_tracks:
        path = bg_tracks[current_track_index]
        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass

# Helper functions to play randomized sounds without immediate repeats
def play_coin_sound():
    if coin_sound:
        coin_sound.play()

def play_swish_sound():
    if swish_sound:
        swish_sound.play()

WIDTH, HEIGHT = 800, 600
# Use a dark green background instead of an image
BACKGROUND_COLOR = (0, 100, 0)

player_radius = player_idle_img.get_width() // 2
player_speed = 5

projectile_radius = shuriken_img.get_width() // 2
projectile_speed = 10

# Scale factor for zombie size (increased for larger zombies)
ZOMBIE_SCALE = 2.0

# Determine enemy sprite size from a sample zombie sheet
sample_sheet = pygame.image.load(zombie_sheet_paths[0])
enemy_frame_w = sample_sheet.get_width() // 3
enemy_frame_h = sample_sheet.get_height() // 4
enemy_size = int(max(enemy_frame_w, enemy_frame_h) * ZOMBIE_SCALE)
# Slightly smaller hitbox than the sprite size
ZOMBIE_HITBOX_SCALE = 0.85
BASE_ENEMY_SPEED = 3
coin_size = coin_frame_size
# Coins move slower by default
BASE_COIN_SPEED = 2
BASE_AMMO_INTERVAL = 4
# Longer delay before coins respawn
BASE_COIN_DELAY = 1.5

# new color for ammo pickup/projectile ui
AMMO_COLOR = (255, 255, 255)
player_idle_img = player_idle_img.convert_alpha()
player_walk_imgs = [img.convert_alpha() for img in player_walk_imgs]
shuriken_img = shuriken_img.convert_alpha()
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Global game state
score = 0
lives = 3
next_life_score = 10
current_level = 1

def check_collision(px, py, ex, ey, size, radius, scale=1.0):
    """Collision between a circle and square with optional square scaling."""
    circle_rect = pygame.Rect(px - radius, py - radius, radius * 2, radius * 2)
    if scale != 1.0:
        adj = size * scale
        offset = (size - adj) / 2
        square_rect = pygame.Rect(ex + offset, ey + offset, adj, adj)
    else:
        square_rect = pygame.Rect(ex, ey, size, size)
    return circle_rect.colliderect(square_rect)


def spawn_enemy(speed):
    """Spawn an enemy from a random edge moving inwards."""
    direction = random.choice(["down", "up", "left", "right"])
    if direction == "down":
        x = random.randint(0, WIDTH - enemy_size)
        y = -enemy_size
        dx, dy = 0, speed
    elif direction == "up":
        x = random.randint(0, WIDTH - enemy_size)
        y = HEIGHT
        dx, dy = 0, -speed
    elif direction == "left":
        x = WIDTH
        y = random.randint(0, HEIGHT - enemy_size)
        dx, dy = -speed, 0
    else:  # right
        x = -enemy_size
        y = random.randint(0, HEIGHT - enemy_size)
        dx, dy = speed, 0
    return x, y, dx, dy, direction


def spawn_coin(speed):
    """Spawn a coin from a random edge moving across the screen."""
    direction = random.choice(["down", "up", "left", "right"])
    if direction == "down":
        x = random.randint(0, WIDTH - coin_size)
        y = -coin_size
        dx, dy = 0, speed
    elif direction == "up":
        x = random.randint(0, WIDTH - coin_size)
        y = HEIGHT
        dx, dy = 0, -speed
    elif direction == "left":
        x = WIDTH
        y = random.randint(0, HEIGHT - coin_size)
        dx, dy = -speed, 0
    else:  # right
        x = -coin_size
        y = random.randint(0, HEIGHT - coin_size)
        dx, dy = speed, 0
    return x, y, dx, dy


def spawn_ammo():
    """Spawn a stationary ammo pickup inside the screen."""
    x = random.randint(projectile_radius, WIDTH - projectile_radius)
    y = random.randint(projectile_radius, HEIGHT - projectile_radius)
    return x, y


def pause_menu():
    """Display a simple pause/options menu and adjust audio settings."""
    global master_volume, sfx_volume, music_volume, current_track_index
    selected = 0
    options = ["Master", "SFX", "Music"]
    values = [master_volume, sfx_volume, music_volume]
    track_len = 240
    label_offset = 100  # space between labels and sliders
    exit_rect = pygame.Rect(0, 0, 200, 50)
    exit_rect.center = (WIDTH // 2, HEIGHT // 2 + 220)
    dropdown_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 240, 300, 40)
    dropdown_open = False
    option_rects = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    master_volume, sfx_volume, music_volume = values
                    apply_volume()
                    return
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % 3
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 3
                if event.key == pygame.K_LEFT:
                    values[selected] = max(0, values[selected] - 5)
                    master_volume, sfx_volume, music_volume = values
                    apply_volume()
                if event.key == pygame.K_RIGHT:
                    values[selected] = min(100, values[selected] + 5)
                    master_volume, sfx_volume, music_volume = values
                    apply_volume()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                if dropdown_rect.collidepoint(event.pos):
                    dropdown_open = not dropdown_open
                elif dropdown_open:
                    for i, rect in enumerate(option_rects):
                        if rect.collidepoint(event.pos):
                            current_track_index = i
                            try:
                                pygame.mixer.music.load(bg_tracks[current_track_index])
                                pygame.mixer.music.play(-1)
                            except pygame.error:
                                pass
                            dropdown_open = False
                            break

        screen.fill(BACKGROUND_COLOR)
        title = font.render("Paused", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

        pygame.draw.rect(screen, (80, 80, 80), dropdown_rect)
        current_name = "No Tracks" if not bg_tracks else bg_track_names[current_track_index][:20]
        text_surf = font.render(current_name, True, (255, 255, 255))
        screen.blit(text_surf, text_surf.get_rect(center=dropdown_rect.center))
        option_rects = []
        if dropdown_open:
            for i, name in enumerate(bg_track_names):
                rect = pygame.Rect(dropdown_rect.x, dropdown_rect.bottom + i * 40, dropdown_rect.width, 40)
                pygame.draw.rect(screen, (60, 60, 60), rect)
                lbl = font.render(name[:20], True, (255, 255, 255))
                screen.blit(lbl, lbl.get_rect(center=rect.center))
                option_rects.append(rect)

        for i, (name, val) in enumerate(zip(options, values)):
            label = font.render(name, True, (255, 255, 255))
            y = HEIGHT // 2 - 80 + i * 80
            screen.blit(label, (WIDTH // 2 - track_len // 2 - label_offset, y - 15))
            track = pygame.Rect(WIDTH // 2 - track_len // 2, y, track_len, 8)
            pygame.draw.rect(screen, (80, 80, 80), track)
            handle_x = track.x + int((val / 100) * track.width)
            color = (200, 0, 0) if i == selected else (200, 200, 200)
            pygame.draw.circle(screen, color, (handle_x, track.centery), 10)

        prompt = font.render("Space to Resume", True, (255, 255, 255))
        screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT * 3 // 4)))

        pygame.draw.rect(screen, (150, 0, 0), exit_rect)
        exit_text = font.render("Exit Game", True, (255, 255, 255))
        screen.blit(exit_text, exit_text.get_rect(center=exit_rect.center))

        pygame.display.flip()
        clock.tick(60)


def run_level(level_num, enemy_speed, coin_speed, enemy_count, ammo_interval, coin_delay):
    global master_volume, sfx_volume, music_volume, score, lives, next_life_score
    if pygame.mixer.get_init() and not pygame.mixer.music.get_busy():
        start_music()

    # Display level number before starting
    screen.fill((0, 0, 0))
    level_text = font.render(f"Level {level_num}", True, (255, 255, 255))
    screen.blit(level_text, level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    pygame.display.flip()
    pygame.time.delay(1500)
    player_x = WIDTH // 2
    player_y = HEIGHT // 2

    player_anim_index = 0
    player_anim_timer = 0
    current_img = player_idle_img

    enemies = []
    for _ in range(enemy_count):
        ex, ey, edx, edy, edir = spawn_enemy(enemy_speed)
        eobj = Zombie(random.choice(zombie_sheet_paths))
        eobj.set_direction(edir)
        eobj.rect.topleft = (ex, ey)
        enemies.append([ex, ey, edx, edy, edir, eobj])
    enemy_spawn_count = enemy_count

    coin_x, coin_y, coin_dx, coin_dy = spawn_coin(coin_speed)
    coin_anim_index = 0
    coin_anim_timer = 0
    coin_active = True
    coin_respawn_timer = 0

    ammo_x, ammo_y = None, None

    projectiles = []
    ammo = 5

    elapsed = 0
    running = True
    while running:
        dt = clock.tick(60) / 1000
        elapsed += dt
        if elapsed >= 60:
            return "complete"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pause_menu()
                elif event.key == pygame.K_LEFT and ammo > 0:
                    projectiles.append([player_x, player_y, -projectile_speed, 0, 0])
                    ammo -= 1
                    play_swish_sound()
                elif event.key == pygame.K_RIGHT and ammo > 0:
                    projectiles.append([player_x, player_y, projectile_speed, 0, 0])
                    ammo -= 1
                    play_swish_sound()
                elif event.key == pygame.K_UP and ammo > 0:
                    projectiles.append([player_x, player_y, 0, -projectile_speed, 0])
                    ammo -= 1
                    play_swish_sound()
                elif event.key == pygame.K_DOWN and ammo > 0:
                    projectiles.append([player_x, player_y, 0, projectile_speed, 0])
                    ammo -= 1
                    play_swish_sound()

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

        # Update enemies
        for enemy in enemies:
            enemy[5].update(dt)
            enemy[0] += enemy[2]
            enemy[1] += enemy[3]
            enemy[5].rect.topleft = (enemy[0], enemy[1])
            if (
                enemy[0] < -enemy_size
                or enemy[0] > WIDTH
                or enemy[1] < -enemy_size
                or enemy[1] > HEIGHT
            ):
                enemy[0], enemy[1], enemy[2], enemy[3], enemy[4] = spawn_enemy(enemy_speed)
                enemy[5] = Zombie(random.choice(zombie_sheet_paths))
                enemy[5].set_direction(enemy[4])
                enemy[5].rect.topleft = (enemy[0], enemy[1])
                enemy_spawn_count += 1
                if enemy_spawn_count % ammo_interval == 0 and ammo_x is None:
                    ammo_x, ammo_y = spawn_ammo()

        if coin_active:
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
                coin_active = False
                coin_respawn_timer = coin_delay
        else:
            coin_respawn_timer -= dt
            if coin_respawn_timer <= 0:
                coin_x, coin_y, coin_dx, coin_dy = spawn_coin(coin_speed)
                coin_anim_index = 0
                coin_anim_timer = 0
                coin_active = True

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
            hit_any = False
            for enemy in enemies:
                if check_collision(
                    p[0],
                    p[1],
                    enemy[0],
                    enemy[1],
                    enemy_size,
                    projectile_radius,
                    ZOMBIE_HITBOX_SCALE,
                ):
                    score += 1
                    if hit_sound:
                        hit_sound.play()
                    enemy[0], enemy[1], enemy[2], enemy[3], enemy[4] = spawn_enemy(enemy_speed)
                    enemy[5] = Zombie(random.choice(zombie_sheet_paths))
                    enemy[5].set_direction(enemy[4])
                    enemy[5].rect.topleft = (enemy[0], enemy[1])
                    enemy_spawn_count += 1
                    if enemy_spawn_count % ammo_interval == 0 and ammo_x is None:
                        ammo_x, ammo_y = spawn_ammo()
                    hit_any = True
                    break
            if hit_any:
                projectiles.remove(p)
                continue
            if coin_active and check_collision(p[0], p[1], coin_x, coin_y, coin_size, projectile_radius):
                score += 5
                play_coin_sound()
                coin_active = False
                coin_respawn_timer = coin_delay
                projectiles.remove(p)

        for enemy in enemies:
            if check_collision(
                player_x,
                player_y,
                enemy[0],
                enemy[1],
                enemy_size,
                player_radius,
                ZOMBIE_HITBOX_SCALE,
            ):
                if hit_sound:
                    hit_sound.play()
                return "dead"

        if coin_active and check_collision(player_x, player_y, coin_x, coin_y, coin_size, player_radius):
            score += 1
            play_coin_sound()
            coin_active = False
            coin_respawn_timer = coin_delay

        if ammo_x is not None and check_collision(
            player_x, player_y,
            ammo_x - projectile_radius, ammo_y - projectile_radius,
            projectile_radius * 2, player_radius
        ):
            ammo += 1
            ammo_x, ammo_y = None, None

        while score >= next_life_score:
            lives += 1
            next_life_score += 10

        screen.fill(BACKGROUND_COLOR)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
        level_text = font.render(f"Lvl {level_num}", True, (255, 255, 255))
        ammo_text = font.render(f"Shuriken: {ammo}", True, (255, 255, 255))
        timer_text = font.render(f"{int(60 - elapsed)}", True, (255, 255, 255))

        # Score and level on the left
        screen.blit(score_text, (20, 10))
        screen.blit(level_text, (20, 40))

        # Lives and ammo on the right
        screen.blit(lives_text, (WIDTH - lives_text.get_width() - 20, 10))
        screen.blit(ammo_text, (WIDTH - ammo_text.get_width() - 20, 40))

        # Timer centered at the top
        timer_rect = timer_text.get_rect(center=(WIDTH // 2, 20))
        screen.blit(timer_text, timer_rect)

        screen.blit(current_img, current_img.get_rect(center=(player_x, player_y)))
        for enemy in enemies:
            screen.blit(enemy[5].image, enemy[5].rect)
        if coin_active:
            screen.blit(coin_frames[coin_anim_index], (coin_x, coin_y))
        if ammo_x is not None:
            screen.blit(shuriken_img, shuriken_img.get_rect(center=(ammo_x, ammo_y)))
        for p in projectiles:
            rotated = pygame.transform.rotate(shuriken_img, p[4])
            rect = rotated.get_rect(center=(int(p[0]), int(p[1])))
            screen.blit(rotated, rect)

        pygame.display.flip()

    return "dead"


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
    global score, lives, next_life_score, current_level
    enemy_speed = BASE_ENEMY_SPEED
    coin_speed = BASE_COIN_SPEED
    ammo_interval = BASE_AMMO_INTERVAL
    coin_delay = BASE_COIN_DELAY
    while True:
        enemy_count = 1 + (current_level - 1) // 2
        result = run_level(current_level, enemy_speed, coin_speed, enemy_count, ammo_interval, coin_delay)
        if result == "complete":
            current_level += 1
            enemy_speed *= 1.05
            coin_speed *= 1.05
            ammo_interval = max(1, ammo_interval * 0.95)
            coin_delay *= 1.1
            continue
        else:  # player died
            lives -= 1
            if lives > 0:
                continue
            if game_over_screen(score):
                score = 0
                lives = 3
                next_life_score = 10
                current_level = 1
                enemy_speed = BASE_ENEMY_SPEED
                coin_speed = BASE_COIN_SPEED
                ammo_interval = BASE_AMMO_INTERVAL
                coin_delay = BASE_COIN_DELAY
                continue
            else:
                break

    pygame.quit()


if __name__ == "__main__":
    main()
