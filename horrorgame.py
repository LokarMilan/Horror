import pygame
import numpy as np
import math
import random

pygame.init()
pygame.font.init()
font = pygame.font.SysFont("arial", 50)

game_state = "menu"
menu_options = ["singleplayer", "multiplayer", "exit"]
selected = 0

WIDTH, HEIGHT = 720,480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# ---------------- MAP ----------------
world_map = np.array([
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
])

# ---------------- PLAYER ----------------
player_x, player_y = 6, 16.5
player_angle = 250

enemy_x, enemy_y = 3, 15

# doors dict: key = (x, y), value = float 0.0 (closed) to 1.0 (open)
doors = {}
# door states: "closed", "opening", "open", "closing"
door_states = {}
DOOR_SPEED = 0.03  # how fast the door opens/closes per frame

enemy_hp = 100
enemy_alive = True
shoot_flash = 0
shot = False
gun_state = "idle"
gun_timer = 0
gun_shake_x = 0
gun_shake_y = 0

# ---------------- TEXTURE ----------------
wall_texture = pygame.image.load("./img/wall.png").convert()
tex_width, tex_height = wall_texture.get_size()
enemy_img = pygame.image.load("./img/ghost.png").convert_alpha()
door_texture = pygame.image.load("./img/door.png").convert()
gun_idle_img = pygame.image.load("./img/gun.png").convert_alpha()
gun_shoot_img = pygame.image.load("./img/shoot.png").convert_alpha()
current_gun = gun_idle_img
wall_w, wall_h = wall_texture.get_size()
door_w, door_h = door_texture.get_size()

# ---------------- SETTINGS ----------------
FOV = math.pi / 3
move_speed = 0.05

# ---------------- COLLISION ----------------
PLAYER_RADIUS = 0.2


def is_walkable(x, y):
    tile = world_map[int(y)][int(x)]

    if tile == 0:
        return True

    if tile == 2:
        # door is walkable if open_amt >= 0.8 (mostly open)
        return doors.get((int(x), int(y)), 0) >= 0.8

    return False


def can_move(x, y):
    return (
        is_walkable(x, y) and
        is_walkable(x + PLAYER_RADIUS, y) and
        is_walkable(x - PLAYER_RADIUS, y) and
        is_walkable(x, y + PLAYER_RADIUS) and
        is_walkable(x, y - PLAYER_RADIUS)
    )


# ---------------- DOOR UPDATE ----------------
def update_doors():
    for key in list(door_states.keys()):
        state = door_states[key]
        current = doors.get(key, 0.0)

        if state == "opening":
            current += DOOR_SPEED
            if current >= 1.0:
                current = 1.0
                door_states[key] = "open"
            doors[key] = current

        elif state == "closing":
            current -= DOOR_SPEED
            if current <= 0.0:
                current = 0.0
                door_states[key] = "closed"
            doors[key] = current


# ---------------- RAYCAST ----------------
def cast_rays():
    global z_buffer
    z_buffer = [float("inf")] * WIDTH

    for ray in range(WIDTH):
        camera_x = 2 * ray / WIDTH - 1

        ray_dir_x = math.cos(player_angle) + camera_x * math.cos(player_angle + math.pi / 2)
        ray_dir_y = math.sin(player_angle) + camera_x * math.sin(player_angle + math.pi / 2)

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
        tile = 0
        door_hit = False
        door_open_amt = 0.0

        while not hit:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            tile = world_map[map_y][map_x]

            if tile == 1:
                hit = True

            elif tile == 2:
                open_amt = doors.get((map_x, map_y), 0)
                door_open_amt = open_amt

                # Door is rendered as sliding into the wall
                # Calculate where the ray hits within the cell
                if side == 0:
                    hit_dist = (map_x - player_x + (1 - step_x) / 2) / (ray_dir_x + 1e-6)
                else:
                    hit_dist = (map_y - player_y + (1 - step_y) / 2) / (ray_dir_y + 1e-6)

                if side == 0:
                    wall_x = player_y + hit_dist * ray_dir_y
                else:
                    wall_x = player_x + hit_dist * ray_dir_x

                wall_x -= math.floor(wall_x)

                # The door slides from 0 to open_amt
                # If wall_x < open_amt, the ray passes through (door slid away)
                # If wall_x >= open_amt, the ray hits the door
                if wall_x >= open_amt:
                    hit = True
                    door_hit = True
                # else: ray passes through the open part

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

        if tile == 2 and door_hit:
            texture = door_texture
            # Adjust texture coordinate for sliding door
            # The visible part of door is from open_amt to 1.0
            # Map wall_x from [open_amt, 1.0] to [0, 1.0] for texture
            if door_open_amt < 1.0:
                tex_coord = (wall_x - door_open_amt) / (1.0 - door_open_amt)
            else:
                tex_coord = wall_x
            tex_coord = max(0.0, min(1.0, tex_coord))
        else:
            texture = wall_texture
            tex_coord = wall_x

        tex_w = texture.get_width()
        tex_x = int(tex_coord * tex_w)
        tex_x = max(0, min(tex_w - 1, tex_x))

        wall_height = int(HEIGHT / (dist + 0.0001))

        tex_h = texture.get_height()

        tex_column = texture.subsurface((tex_x, 0, 1, tex_h))
        tex_column = pygame.transform.scale(tex_column, (1, wall_height))

        screen.blit(
            tex_column,
            (ray, HEIGHT // 2 - wall_height // 2)
        )
        z_buffer[ray] = dist


def draw_enemy():
    if not enemy_alive:
        return
    dx = enemy_x - player_x
    dy = enemy_y - player_y

    dist = math.sqrt(dx * dx + dy * dy)

    angle = math.atan2(dy, dx) - player_angle

    angle = (angle + math.pi) % (2 * math.pi) - math.pi

    if abs(angle) > math.pi / 4:
        return

    screen_x = int((angle / (math.pi / 4)) * (WIDTH / 2) + WIDTH / 2)

    if screen_x < 0 or screen_x >= WIDTH:
        return

    if dist > z_buffer[screen_x]:
        return

    size = int(min(800 / (dist + 0.1), HEIGHT))

    sprite = pygame.transform.scale(enemy_img, (size, size))

    screen.blit(
        sprite,
        (screen_x - size // 2, HEIGHT // 2 - size // 2)
    )


def shoot():
    global enemy_hp, enemy_alive, shoot_flash, gun_state, gun_timer, gun_shake_x, gun_shake_y
    shoot_flash = 5
    gun_state = "shoot"
    gun_timer = 5
    gun_shake_x = random.randint(-8, 8)
    gun_shake_y = random.randint(-10, 5)
    if not enemy_alive:
        return
    dx = enemy_x - player_x
    dy = enemy_y - player_y

    dist = math.sqrt(dx * dx + dy * dy)

    angle_to_enemy = math.atan2(dy, dx)
    angle_diff = angle_to_enemy - player_angle

    angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

    if abs(angle_diff) < 0.1:
        ray_x = player_x
        ray_y = player_y

        for i in range(int(dist * 10)):
            ray_x += math.cos(player_angle) * 0.1
            ray_y += math.sin(player_angle) * 0.1

            if world_map[int(ray_y)][int(ray_x)] == 1:
                return
        enemy_hp -= 25
        print("HIT!", enemy_hp)

        if enemy_hp <= 0:
            enemy_alive = False
            print("ENEMY DEAD")


def melee_attack():
    global enemy_hp, enemy_alive

    if not enemy_alive:
        return
    dx = enemy_x - player_x
    dy = enemy_y - player_y

    dist = math.sqrt(dx * dx + dy * dy)

    if dist < 1.5:
        enemy_hp -= 50
        print("MELEE HIT", enemy_hp)

        if enemy_hp <= 0:
            enemy_alive = False
            print("ENEMY DEAD")


# ---------------- GAME LOOP ----------------
running = True

while running:
    clock.tick(60)

    # ---------------- EVENT ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                shoot()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                melee_attack()

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

                if event.key == pygame.K_e:
                    front_x = int(player_x + math.cos(player_angle))
                    front_y = int(player_y + math.sin(player_angle))

                    if world_map[front_y][front_x] == 2:
                        key = (front_x, front_y)

                        # Initialize door if not yet tracked
                        if key not in doors:
                            doors[key] = 0.0
                            door_states[key] = "closed"

                        # Toggle door state
                        current_state = door_states.get(key, "closed")
                        if current_state in ("closed", "closing"):
                            door_states[key] = "opening"
                        elif current_state in ("open", "opening"):
                            door_states[key] = "closing"

    # ---------------- LOGIKA ----------------
    if game_state == "menu":

        if selected < 0:
            selected = len(menu_options) - 1

        if selected >= len(menu_options):
            selected = 0

    # ---------------- GAME ----------------
    if game_state == "game":
        # Update door animations
        update_doors()

        if gun_timer > 0:
            gun_timer -= 1
        else:
            gun_state = "idle"

        gun_shake_x *= 0.85
        gun_shake_y *= 0.85

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
            screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 + i * 40))

    elif game_state == "game":
        screen.fill((70, 120, 200))
        pygame.draw.rect(screen, (50, 50, 50), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
        cast_rays()
        draw_enemy()
        pygame.draw.line(screen, (255, 255, 255), (WIDTH // 2 - 10, HEIGHT // 2), (WIDTH // 2 + 10, HEIGHT // 2), 2)
        pygame.draw.line(screen, (255, 255, 255), (WIDTH // 2, HEIGHT // 2 - 10), (WIDTH // 2, HEIGHT // 2 + 10), 2)

        if gun_state == "shoot":
            current_gun = gun_shoot_img
        else:
            current_gun = gun_idle_img

        scale = WIDTH // 400
        gun_scaled = pygame.transform.scale(current_gun, (
        int(current_gun.get_width() * scale), int(current_gun.get_height() * scale)))

        gun_x = WIDTH - 2 * (gun_scaled.get_width() // 2) + gun_shake_x
        gun_y = HEIGHT - gun_scaled.get_height() + gun_shake_y

        screen.blit(gun_scaled, (gun_x, gun_y))

        if shoot_flash > 0:
            pygame.draw.circle(screen, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 8)
            shoot_flash -= 1

    pygame.display.flip()

pygame.quit()