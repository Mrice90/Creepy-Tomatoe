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

enemy_size = 40
enemy_speed = 3
coin_size = 20
coin_speed = 4

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circle vs Square")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def check_collision(px, py, ex, ey, size):
    circle_rect = pygame.Rect(px - player_radius, py - player_radius,
                              player_radius * 2, player_radius * 2)
    square_rect = pygame.Rect(ex, ey, size, size)
    return circle_rect.colliderect(square_rect)


def run_game():
    player_x = WIDTH // 2
    player_y = HEIGHT - player_radius - 10

    enemy_x = random.randint(0, WIDTH - enemy_size)
    enemy_y = 0

    coin_x = -coin_size
    coin_y = random.randint(0, HEIGHT - coin_size)

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

        enemy_y += enemy_speed
        if enemy_y > HEIGHT:
            enemy_x = random.randint(0, WIDTH - enemy_size)
            enemy_y = 0

        coin_x += coin_speed
        if coin_x > WIDTH:
            coin_x = -coin_size
            coin_y = random.randint(0, HEIGHT - coin_size)

        if check_collision(player_x, player_y, enemy_x, enemy_y, enemy_size):
            running = False

        if check_collision(player_x, player_y, coin_x, coin_y, coin_size):
            score += 1
            coin_x = -coin_size
            coin_y = random.randint(0, HEIGHT - coin_size)

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
