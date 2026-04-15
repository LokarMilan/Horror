import pygame
import numpy as np
import math

pygame.init()

WIDTH, HEIGHT = 720, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# ---------------- MAP ----------------
world_map = np.array([
    [1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,0,1],
    [1,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,0,1],
    [1,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1],
])

# ---------------- PLAYER ----------------
player_x, player_y = 3.5, 3.5
player_angle = 0

# ---------------- ENEMY ----------------
enemy_x, enemy_y = 5.5, 5.5

# ---------------- TEXTURE ----------------
wall_texture = pygame.image.load("wall.png").convert()
tex_width, tex_height = wall_texture.get_size()

# ---------------- SETTINGS ----------------
FOV = math.pi / 3
move_speed = 0.05

# ---------------- COLLISION ----------------
def can_move(x, y):
    return world_map[int(y)][int(x)] == 0

# ---------------- RAYCAST ----------------
def cast_rays():
    for ray in range(WIDTH):
        camera_x = 2 * ray / WIDTH - 1

        ray_dir_x = math.cos(player_angle) + camera_x * math.cos(player_angle + math.pi/2)
        ray_dir_y = math.sin(player_angle) + camera_x * math.sin(player_angle + math.pi/2)

        map_x = int(player_x)
        map_y = int(player_y)

        delta_dist_x = abs(1 / (ray_dir_x + 1e-6))
        delta_dist_y = abs(1 / (ray_dir_y + 1e-6))

        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (player_x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - player_x) * delta_dist_x

        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (player_y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - player_y) * delta_dist_y

        hit = False
        side = 0

        while not hit:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            if world_map[map_y][map_x] == 1:
                hit = True
                
        if side == 0:
            dist = (map_x - player_x + (1 - step_x) / 2) / (ray_dir_x + 1e-6)
        else:
            dist = (map_y - player_y + (1 - step_y) / 2) / (ray_dir_y + 1e-6)

        dist = max(dist, 0.0001)

        if side == 0:
            wall_x = player_y + dist * ray_dir_y
        else:
            wall_x = player_x + dist * ray_dir_x

        wall_x -= math.floor(wall_x)

        tex_x = int(wall_x * tex_width)
        tex_x = max(0, min(tex_width - 1, tex_x))

        wall_height = int(HEIGHT / (dist + 0.0001))

        tex_column = wall_texture.subsurface((tex_x, 0, 1, tex_height))
        tex_column = pygame.transform.scale(tex_column, (1, wall_height))

        screen.blit(
            tex_column,
            (ray, HEIGHT//2 - wall_height//2)
        )
        
# ---------------- GAME LOOP ----------------
running = True

while running:
    clock.tick(60)
    screen.fill((0, 0, 0))

        # ég
    screen.fill((70, 120, 200))

    # padló
    pygame.draw.rect(screen, (50, 50, 50), (0, HEIGHT//2, WIDTH, HEIGHT//2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_x, mouse_y = pygame.mouse.get_pos()
    center_x = WIDTH // 2

    dx = mouse_x - center_x

    player_angle += dx * 0.0005

    pygame.mouse.set_pos((center_x, HEIGHT // 2))

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        nx = player_x + move_speed * math.cos(player_angle)
        ny = player_y + move_speed * math.sin(player_angle)
        if not can_move(nx, player_y) or not can_move(player_x, ny):
            pygame.quit()
            exit()

        player_x = nx
        player_y = ny

    if keys[pygame.K_s]:
        nx = player_x - move_speed * math.cos(player_angle)
        ny = player_y - move_speed * math.sin(player_angle)
        if not can_move(nx, player_y) or not can_move(player_x, ny):
            pygame.quit()
            exit()

        player_x = nx
        player_y = ny

    if keys[pygame.K_d]:
        nx = player_x - move_speed * math.sin(player_angle)
        ny = player_y + move_speed * math.cos(player_angle)
        if can_move(nx, player_y): player_x = nx
        if can_move(player_x, ny): player_y = ny

    if keys[pygame.K_a]:
        nx = player_x + move_speed * math.sin(player_angle)
        ny = player_y - move_speed * math.cos(player_angle)
        if can_move(nx, player_y): player_x = nx
        if can_move(player_x, ny): player_y = ny

    # -------- RENDER --------
    cast_rays()

    pygame.display.flip()

pygame.quit()