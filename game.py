import pygame
import random
import sys

# Initialize pygame
pygame.init()

WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 0)
PLAYER_COLOR = (0, 0, 255)
ENEMY_COLOR = (255, 0, 0)

player_radius = 20
player_speed = 5

enemy_size = 40
enemy_speed = 3

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circle vs Square")
clock = pygame.time.Clock()

player_x = WIDTH // 2
player_y = HEIGHT - player_radius - 10

enemy_x = random.randint(0, WIDTH - enemy_size)
enemy_y = 0

def check_collision(px, py, ex, ey):
    circle_rect = pygame.Rect(px - player_radius, py - player_radius,
                              player_radius * 2, player_radius * 2)
    square_rect = pygame.Rect(ex, ey, enemy_size, enemy_size)
    return circle_rect.colliderect(square_rect)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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

    if check_collision(player_x, player_y, enemy_x, enemy_y):
        print("Game Over!")
        running = False

    screen.fill(BACKGROUND_COLOR)
    pygame.draw.circle(screen, PLAYER_COLOR, (player_x, player_y), player_radius)
    pygame.draw.rect(screen, ENEMY_COLOR, (enemy_x, enemy_y, enemy_size, enemy_size))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
