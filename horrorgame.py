import pygame
import numpy as np
import math

pygame.init()
pygame.font.init()
font =pygame.font.SysFont("arial",50)

game_state = "menu"
menu_options = ["singleplayer","multiplayer","exit"]
selected=0


WIDTH, HEIGHT = 720,480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# ---------------- MAP ----------------
world_map = np.array([
    [1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,0,0,1,1,1,1,1],
    [1,0,0,0,1,0,0,1,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,1,0,0,1,0,0,0,1],
    [1,1,1,1,1,0,0,1,1,1,1,1],
    [1,0,0,0,1,0,0,1,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,1,0,0,1,0,0,0,1],
    [1,1,1,1,1,0,0,1,1,1,1,1],
    [1,0,0,0,1,0,0,1,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,1,0,0,1,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1],
])

# ---------------- PLAYER ----------------
player_x, player_y = 6, 16.5
player_angle = 250


enemy_x, enemy_y = 3, 15

# ---------------- TEXTURE ----------------
wall_texture = pygame.image.load("wall.png").convert()
tex_width, tex_height = wall_texture.get_size()
enemy_img = pygame.image.load("ghost.png").convert_alpha()

# ---------------- SETTINGS ----------------
FOV = math.pi / 3
move_speed = 0.05

# ---------------- COLLISION ----------------
PLAYER_RADIUS = 0.2
def can_move(x, y):
    return (
        world_map[int(y)][int(x)] == 0 and
        world_map[int(y + PLAYER_RADIUS)][int(x)] == 0 and
        world_map[int(y - PLAYER_RADIUS)][int(x)] == 0 and
        world_map[int(y)][int(x + PLAYER_RADIUS)] == 0 and
        world_map[int(y)][int(x - PLAYER_RADIUS)] == 0
    )

# ---------------- RAYCAST ----------------
def cast_rays():
    global z_buffer
    z_buffer =[float("inf")] * WIDTH
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

        dist = max(dist, 0.01)

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
        z_buffer[ray] = dist

def draw_enemy():
    dx = enemy_x - player_x
    dy = enemy_y - player_y

    dist = math.sqrt(dx*dx + dy*dy)

    angle = math.atan2(dy, dx) - player_angle

    # normalize angle
    angle = (angle + math.pi) % (2 * math.pi) - math.pi

    # ha nincs a látómezőben
    if abs(angle) > math.pi / 4:
        return

    # screen pozíció (stabilabb)
    screen_x = (angle / (math.pi / 4)) * (WIDTH / 2) + WIDTH / 2

    size = min(800 / (dist + 0.1), HEIGHT)

        # sprite méret
    size = int(size)

    # kép méretezés
    sprite = pygame.transform.scale(enemy_img, (size, size))

    # kirajzolás
    screen.blit(
        sprite,
        (int(screen_x - size/2), int(HEIGHT/2 - size/2))
    )
# ---------------- GAME LOOP ----------------
running = True

while running:
    clock.tick(60)

    # ---------------- EVENT ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "menu":

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    selected -= 1

                if event.key == pygame.K_DOWN:
                    selected += 1

                if event.key == pygame.K_RETURN:

                    if selected == 0:
                        game_state = "game"

                    elif selected == 1:
                        game_state = "multiplayer"

                    elif selected == 2:
                        running = False
        elif game_state == "game":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"

    # ---------------- LOGIKA ----------------
    if game_state == "menu":

        if selected < 0:
            selected = len(menu_options) - 1

        if selected >= len(menu_options):
            selected = 0

    # ---------------- GAME ----------------
    if game_state == "game":

        mouse_x, _ = pygame.mouse.get_pos()
        center_x = WIDTH // 2

        dx = mouse_x - center_x
        player_angle += dx * 0.002

        pygame.mouse.set_pos((center_x, HEIGHT // 2))

        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            nx = player_x + move_speed * math.cos(player_angle)
            ny = player_y + move_speed * math.sin(player_angle)
            if can_move(nx, player_y): player_x = nx
            if can_move(player_x, ny): player_y = ny

        if keys[pygame.K_s]:
            nx = player_x - move_speed * math.cos(player_angle)
            ny = player_y - move_speed * math.sin(player_angle)
            if can_move(nx, player_y): player_x = nx
            if can_move(player_x, ny): player_y = ny

        if keys[pygame.K_a]:
            nx = player_x + move_speed * math.sin(player_angle)
            ny = player_y - move_speed * math.cos(player_angle)
            if can_move(nx, player_y): player_x = nx
            if can_move(player_x, ny): player_y = ny

        if keys[pygame.K_d]:
            nx = player_x - move_speed * math.sin(player_angle)
            ny = player_y + move_speed * math.cos(player_angle)
            if can_move(nx, player_y): player_x = nx
            if can_move(player_x, ny): player_y = ny

    # ---------------- RENDER ----------------
    screen.fill((0, 0, 0))

    if game_state == "menu":

        for i, option in enumerate(menu_options):

            color = (255, 255, 255)
            if i == selected:
                color = (255, 255, 0)

            text = font.render(option, True, color)
            screen.blit(text, (WIDTH//2 - 100, HEIGHT//2 + i * 40))

    elif game_state == "game":

        screen.fill((70, 120, 200))
        pygame.draw.rect(screen, (50, 50, 50), (0, HEIGHT//2, WIDTH, HEIGHT//2))
        cast_rays()
        draw_enemy()

    pygame.display.flip()

pygame.quit()