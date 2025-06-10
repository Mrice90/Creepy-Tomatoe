import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()

WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 0)
PLAYER_COLOR = (0, 0, 255)
ENEMY_COLOR = (255, 0, 0)
COIN_COLOR = (255, 255, 0)

player_radius = 20
player_speed = 5

enemy_size = 40
enemy_speed = 3
coin_size = 20
coin_speed = 4

SCORES_FILE = "scores.txt"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circle vs Square")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def check_collision(px, py, ex, ey, size):
    circle_rect = pygame.Rect(px - player_radius, py - player_radius,
                              player_radius * 2, player_radius * 2)
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
    return x, y, dx, dy


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


def load_scores():
    """Return a list of saved scores sorted descending."""
    if not os.path.exists(SCORES_FILE):
        return []
    with open(SCORES_FILE, "r") as f:
        scores = [int(line.strip()) for line in f if line.strip().isdigit()]
    return sorted(scores, reverse=True)


def save_score(score):
    """Save score to file and return updated top scores list."""
    scores = load_scores()
    scores.append(score)
    scores = sorted(scores, reverse=True)[:5]
    with open(SCORES_FILE, "w") as f:
        for s in scores:
            f.write(f"{s}\n")
    return scores


def run_game():
    player_x = WIDTH // 2
    player_y = HEIGHT // 2

    enemy_x, enemy_y, enemy_dx, enemy_dy = spawn_enemy()

    coin_x, coin_y, coin_dx, coin_dy = spawn_coin()

    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
        if keys[pygame.K_UP]:
            player_y -= player_speed
        if keys[pygame.K_DOWN]:
            player_y += player_speed

        player_x = max(player_radius, min(WIDTH - player_radius, player_x))
        player_y = max(player_radius, min(HEIGHT - player_radius, player_y))

        enemy_x += enemy_dx
        enemy_y += enemy_dy
        if (
            enemy_x < -enemy_size
            or enemy_x > WIDTH
            or enemy_y < -enemy_size
            or enemy_y > HEIGHT
        ):
            enemy_x, enemy_y, enemy_dx, enemy_dy = spawn_enemy()

        coin_x += coin_dx
        coin_y += coin_dy
        if (
            coin_x < -coin_size
            or coin_x > WIDTH
            or coin_y < -coin_size
            or coin_y > HEIGHT
        ):
            coin_x, coin_y, coin_dx, coin_dy = spawn_coin()

        if check_collision(player_x, player_y, enemy_x, enemy_y, enemy_size):
            running = False

        if check_collision(player_x, player_y, coin_x, coin_y, coin_size):
            score += 1
            coin_x, coin_y, coin_dx, coin_dy = spawn_coin()

        screen.fill(BACKGROUND_COLOR)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        pygame.draw.circle(screen, PLAYER_COLOR, (player_x, player_y), player_radius)
        pygame.draw.rect(screen, ENEMY_COLOR, (enemy_x, enemy_y, enemy_size, enemy_size))
        pygame.draw.rect(screen, COIN_COLOR, (coin_x, coin_y, coin_size, coin_size))

        pygame.display.flip()
        clock.tick(60)

    return score


def game_over_screen(score):
    over_font = pygame.font.SysFont(None, 48)
    info_font = pygame.font.SysFont(None, 36)

    top_scores = save_score(score)

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
        leaderboard_y = HEIGHT * 2 // 3
        for idx, s in enumerate(top_scores, start=1):
            entry = info_font.render(f"{idx}. {s}", True, (255, 255, 255))
            screen.blit(entry, entry.get_rect(center=(WIDTH // 2, leaderboard_y)))
            leaderboard_y += 30

        screen.blit(prompt_text, prompt_text.get_rect(center=(WIDTH // 2, HEIGHT - 40)))

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
