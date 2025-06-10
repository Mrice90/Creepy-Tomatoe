import pygame
import random
import sys

# Initialize pygame
pygame.init()

WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 0)
PLAYER_COLOR = (0, 0, 255)
ENEMY_COLOR = (255, 0, 0)
COIN_COLOR = (255, 255, 0)

player_radius = 20
player_speed = 5

projectile_radius = 5
projectile_speed = 10

enemy_size = 40
enemy_speed = 3
coin_size = 20
coin_speed = 4

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circle vs Square")
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


def run_game():
    player_x = WIDTH // 2
    player_y = HEIGHT // 2

    enemy_x, enemy_y, enemy_dx, enemy_dy = spawn_enemy()

    coin_x, coin_y, coin_dx, coin_dy = spawn_coin()

    projectiles = []

    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    projectiles.append([player_x, player_y, -projectile_speed, 0])
                elif event.key == pygame.K_RIGHT:
                    projectiles.append([player_x, player_y, projectile_speed, 0])
                elif event.key == pygame.K_UP:
                    projectiles.append([player_x, player_y, 0, -projectile_speed])
                elif event.key == pygame.K_DOWN:
                    projectiles.append([player_x, player_y, 0, projectile_speed])

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_d]:
            player_x += player_speed
        if keys[pygame.K_w]:
            player_y -= player_speed
        if keys[pygame.K_s]:
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

        # Update projectiles
        for p in projectiles[:]:
            p[0] += p[2]
            p[1] += p[3]
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
                enemy_x, enemy_y, enemy_dx, enemy_dy = spawn_enemy()
                projectiles.remove(p)
                continue
            if check_collision(p[0], p[1], coin_x, coin_y, coin_size, projectile_radius):
                score += 1
                coin_x, coin_y, coin_dx, coin_dy = spawn_coin()
                projectiles.remove(p)

        if check_collision(player_x, player_y, enemy_x, enemy_y, enemy_size, player_radius):
            running = False

        if check_collision(player_x, player_y, coin_x, coin_y, coin_size, player_radius):
            score += 1
            coin_x, coin_y, coin_dx, coin_dy = spawn_coin()

        screen.fill(BACKGROUND_COLOR)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        pygame.draw.circle(screen, PLAYER_COLOR, (player_x, player_y), player_radius)
        pygame.draw.rect(screen, ENEMY_COLOR, (enemy_x, enemy_y, enemy_size, enemy_size))
        pygame.draw.rect(screen, COIN_COLOR, (coin_x, coin_y, coin_size, coin_size))
        for p in projectiles:
            pygame.draw.circle(screen, (255, 255, 255), (int(p[0]), int(p[1])), projectile_radius)

        pygame.display.flip()
        clock.tick(60)

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
