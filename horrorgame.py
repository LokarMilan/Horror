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

# ---------------- DEATH SCREEN ----------------
death_alpha = 0
death_bg = None
exit_button_rect = pygame.Rect(0, 0, 0, 0)

# ---------------- MENU ----------------
menu_alpha = 0
menu_tick = 0
menu_button_rects = []
menu_music_started = False

# ---------------- MULTIPLAYER SCREEN ----------------
mp_alpha = 0
mp_tick = 0
mp_back_rect = pygame.Rect(0, 0, 0, 0)

WIDTH, HEIGHT = 720,480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(True)
pygame.event.set_grab(False)

# ---------------- MAP ----------------
world_map = np.array([
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
])

# ---------------- PLAYER ----------------
player_x, player_y = 6, 16.5
player_angle = math.radians(250)

enemy_x, enemy_y = 3, 15
enemy1_x, enemy1_y = 9, 15
enemy2_x, enemy2_y = 3, 12
enemy3_x, enemy3_y = 9, 12
enemy4_x, enemy4_y = 3, 8
enemy5_x, enemy5_y = 9, 8
finalenemy_x, finalenemy_y = 6, 3


menu_music = pygame.mixer.Sound("./sound/menu.ogg") 

# doors dict: key = (x, y), value = float 0.0 (closed) to 1.0 (open)
doors = {}
# door states: "closed", "opening", "open", "closing"
door_states = {}
DOOR_SPEED = 0.03  # how fast the door opens/closes per frame

enemy_hp = 100
enemy_alive = True
enemy1_hp = 200
enemy1_alive = True
enemy2_hp = 300
enemy2_alive = True
enemy3_hp = 400
enemy3_alive = True
enemy4_hp = 500
enemy4_alive = True
enemy5_hp = 600
enemy5_alive = True
finalenemy_hp = 1000
finalenemy_alive = True
shoot_flash = 0
shot = False
gun_state = "idle"
gun_timer = 0
gun_shake_x = 0
gun_shake_y = 0
player_hp=250
player_max_hp = 250
display_hp = 1000

# ---------------- TEXTURE ----------------
wall_texture = pygame.image.load("./img/bwall.png").convert()
tex_width, tex_height = wall_texture.get_size()
enemy_img = pygame.image.load("./img/enemy_idle.png").convert_alpha()
enemy1_img = pygame.image.load("./img/demon_idle.png").convert_alpha()
enemy2_img = pygame.image.load("./img/wizard idle.png").convert_alpha()
enemy3_img = pygame.image.load("./img/hell_idle.png").convert_alpha()
enemy4_img = pygame.image.load("./img/SentryCrab.png").convert_alpha()
enemy5_img = pygame.image.load("./img/hellish.png").convert_alpha()
finalenemy_img = pygame.image.load("./img/boss.png").convert_alpha()
door_texture = pygame.image.load("./img/wood_door_01.png").convert()
gun_idle_img = pygame.image.load("./img/gun.png").convert_alpha()
gun_shoot_img = pygame.image.load("./img/shoot.png").convert_alpha()
locked_texture = pygame.image.load("./img/locked_door.png").convert_alpha()
current_gun = gun_idle_img
wall_w, wall_h = wall_texture.get_size()
door_w, door_h = door_texture.get_size()
current_enemy = enemy_img
current_enemy1 = enemy1_img
current_enemy2 = enemy2_img
current_enemy3 = enemy3_img
current_enemy4 = enemy4_img
current_enemy5 = enemy5_img
current_finalenemy = finalenemy_img
enemy_shoot_img = pygame.image.load("./img/enemy_attack.png").convert_alpha()
enemy1_shoot_img = pygame.image.load("./img/demon_shoot.png").convert_alpha()
enemy2_shoot_img = pygame.image.load("./img/wizard attack.png").convert_alpha()
enemy3_shoot_img = pygame.image.load("./img/hell_attack.png").convert_alpha()
enemy4_shoot_img = pygame.image.load("./img/SentryCrab.png").convert_alpha()
enemy5_shoot_img = pygame.image.load("./img/hellish_attack.png").convert_alpha()
finalenemy_shoot_img = pygame.image.load("./img/Boss_attack.png").convert_alpha()

# ---------------- SETTINGS ----------------
FOV = math.pi / 3
move_speed = 0.05

# ---------------- FLASHLIGHT ----------------
FLASHLIGHT_LENGTH = 429
FLASHLIGHT_FOV = math.pi / 0.5
FLASHLIGHT_DARKNESS = 255

def draw_flashlight():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    cx, cy = WIDTH // 2, HEIGHT // 2
    max_radius = FLASHLIGHT_LENGTH

    step = 4  # kisebb = szebb, de lassabb

    for r in range(max_radius, 0, -step):
        t = r / max_radius

        # itt állítod a sötétedést
        base = int(255 * (t ** 1.7))
        boost = int(70 * (1 - t) ** 4)

        alpha = min(255, base + boost) # középen világos, szélen sötét

        pygame.draw.circle(
            overlay,
            (0, 0, 0, alpha),
            (cx, cy),
            r
        )

    screen.blit(overlay, (0, 0))
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
textures = {
    1: wall_texture,
    2: door_texture,
    3: locked_texture,
}


locked_walls = {
    "enemy":       (4, 15),   # bal alsó
    "enemy1":      (7, 15),   # jobb alsó
    "enemy2":      (4, 11),   # bal közép
    "enemy3":      (7, 11),   # jobb közép
    "enemy4":      (4,  7),   # bal felső
    "enemy5":      (7,  7),   # jobb felső
    "final_left":  (5,  5),   # boss ajtó bal
    "final_right": (6,  5),   # boss ajtó jobb
}


def check_locked_doors():
    global world_map

    def unlock(key):
        x, y = locked_walls[key] 
        if world_map[y][x] == 3:
            world_map[y][x] = 2
            print(f"Ajtó kinyílt: ({x},{y})")

    if not enemy_alive:        unlock("enemy1")
    if not enemy1_alive:       unlock("enemy2")
    if not enemy2_alive:       unlock("enemy3")
    if not enemy3_alive:       unlock("enemy4")
    if not enemy4_alive:       unlock("enemy5")
    if not enemy5_alive:       
        unlock("final_left")
        unlock("final_right")
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

            if tile in (1,3):
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
            texture = textures.get(tile,wall_texture)
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

    sprite = pygame.transform.scale(current_enemy, (size, size))

    screen.blit(
        sprite,
        (screen_x - size // 2, HEIGHT // 2 - size // 2)
    )
    draw_enemy_hp_bar(screen_x, size, enemy_hp, 100)

def shoot():
    global enemy_hp, enemy_alive, shoot_flash, gun_state, gun_timer, gun_shake_x, gun_shake_y,enemy1_alive,enemy1_hp,enemy2_alive,enemy2_hp,enemy3_alive,enemy3_hp,enemy4_alive,enemy4_hp,enemy5_hp, enemy5_alive, finalenemy_hp, finalenemy_alive
    shoot_flash = 5
    gun_state = "shoot"
    gun_timer = 5
    gun_shake_x = random.randint(-10, 10)
    gun_shake_y = random.randint(-15, 10)
    if enemy_alive:
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
    else:

        if enemy1_alive:
            dx = enemy1_x - player_x
            dy = enemy1_y - player_y

            dist = math.sqrt(dx * dx + dy * dy)

            angle_to_enemy1 = math.atan2(dy, dx)
            angle_diff = angle_to_enemy1 - player_angle

            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

            if abs(angle_diff) < 0.1:
                ray_x = player_x
                ray_y = player_y

                for i in range(int(dist * 10)):
                    ray_x += math.cos(player_angle) * 0.1
                    ray_y += math.sin(player_angle) * 0.1

                    if world_map[int(ray_y)][int(ray_x)] == 1:
                        return
                enemy1_hp -= 25
                print("HIT!", enemy1_hp)

            if enemy1_hp <= 0:
                enemy1_alive = False
                print("ENEMY DEAD")
    if enemy2_alive:
        dx = enemy2_x - player_x
        dy = enemy2_y - player_y

        dist = math.sqrt(dx * dx + dy * dy)

        angle_to_enemy2 = math.atan2(dy, dx)
        angle_diff = angle_to_enemy2 - player_angle

        angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

        if abs(angle_diff) < 0.1:
            ray_x = player_x
            ray_y = player_y

            for i in range(int(dist * 10)):
                ray_x += math.cos(player_angle) * 0.1
                ray_y += math.sin(player_angle) * 0.1

                if world_map[int(ray_y)][int(ray_x)] == 1:
                    return
            enemy2_hp -= 25
            print("HIT!", enemy2_hp)

            if enemy2_hp <= 0:
                enemy2_alive = False
                print("ENEMY DEAD")
    if enemy3_alive:
        dx = enemy3_x - player_x
        dy = enemy3_y - player_y

        dist = math.sqrt(dx * dx + dy * dy)

        angle_to_enemy3 = math.atan2(dy, dx)
        angle_diff = angle_to_enemy3 - player_angle

        angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

        if abs(angle_diff) < 0.1:
            ray_x = player_x
            ray_y = player_y

            for i in range(int(dist * 10)):
                ray_x += math.cos(player_angle) * 0.1
                ray_y += math.sin(player_angle) * 0.1

                if world_map[int(ray_y)][int(ray_x)] == 1:
                    return
            enemy3_hp -= 25
            print("HIT!", enemy3_hp)

            if enemy3_hp <= 0:
                enemy3_alive = False
                print("ENEMY DEAD")

    if enemy4_alive:
        dx = enemy4_x - player_x
        dy = enemy4_y - player_y

        dist = math.sqrt(dx * dx + dy * dy)

        angle_to_enemy4 = math.atan2(dy, dx)
        angle_diff = angle_to_enemy4 - player_angle

        angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

        if abs(angle_diff) < 0.1:
            ray_x = player_x
            ray_y = player_y

            for i in range(int(dist * 10)):
                ray_x += math.cos(player_angle) * 0.1
                ray_y += math.sin(player_angle) * 0.1

                if world_map[int(ray_y)][int(ray_x)] == 1:
                    return
            enemy4_hp -= 25
            print("HIT!", enemy4_hp)

            if enemy4_hp <= 0:
                enemy4_alive = False
                print("ENEMY DEAD")
    
    if enemy5_alive:
        dx = enemy5_x - player_x
        dy = enemy5_y - player_y

        dist = math.sqrt(dx * dx + dy * dy)

        angle_to_enemy5 = math.atan2(dy, dx)
        angle_diff = angle_to_enemy5 - player_angle

        angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

        if abs(angle_diff) < 0.1:
            ray_x = player_x
            ray_y = player_y

            for i in range(int(dist * 10)):
                ray_x += math.cos(player_angle) * 0.1
                ray_y += math.sin(player_angle) * 0.1

                if world_map[int(ray_y)][int(ray_x)] == 1:
                    return
            enemy5_hp -= 25
            print("HIT!", enemy5_hp)

            if enemy5_hp <= 0:
                enemy5_alive = False
                print("ENEMY DEAD")
    
    if finalenemy_alive:
        dx = finalenemy_x - player_x
        dy = finalenemy_y - player_y

        dist = math.sqrt(dx * dx + dy * dy)

        angle_to_finalenemy = math.atan2(dy, dx)
        angle_diff = angle_to_finalenemy - player_angle

        angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

        if abs(angle_diff) < 0.1:
            ray_x = player_x
            ray_y = player_y

            for i in range(int(dist * 10)):
                ray_x += math.cos(player_angle) * 0.1
                ray_y += math.sin(player_angle) * 0.1

                if world_map[int(ray_y)][int(ray_x)] == 1:
                    return
            finalenemy_hp -= 25
            print("HIT!", finalenemy_hp)

            if finalenemy_hp <= 0:
                finalenemy_alive = False
                print("ENEMY DEAD")


def melee_attack():
    global enemy_hp, enemy_alive,enemy1_hp,enemy1_alive,enemy2_alive,enemy2_hp,enemy3_alive,enemy3_hp,enemy4_alive,enemy4_hp,enemy5_hp, enemy5_alive, finalenemy_hp, finalenemy_alive
    shoot_flash = 5

    if enemy_alive:
        dx = enemy_x - player_x
        dy = enemy_y - player_y

        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 1.5:
            enemy_hp -= 50
            print("MELEE HIT", enemy_hp)

            if enemy_hp <= 0:
                enemy_alive = False
                print("ENEMY DEAD")

    if enemy1_alive:
        dx = enemy1_x - player_x
        dy = enemy1_y - player_y

        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 1.5:
            enemy1_hp -= 50
            print("MELEE HIT", enemy1_hp)

            if enemy1_hp <= 0:
                enemy1_alive = False
                print("ENEMY DEAD")

    if enemy2_alive:
        dx = enemy2_x - player_x
        dy = enemy2_y - player_y

        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 1.5:
            enemy2_hp -= 50
            print("MELEE HIT", enemy2_hp)

            if enemy2_hp <= 0:
                enemy2_alive = False
                print("ENEMY DEAD")
    if enemy3_alive:
        dx = enemy3_x - player_x
        dy = enemy3_y - player_y

        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 1.5:
            enemy3_hp -= 50
            print("MELEE HIT", enemy3_hp)

            if enemy3_hp <= 0:
                enemy3_alive = False
                print("ENEMY DEAD")
    
    if enemy4_alive:
        dx = enemy4_x - player_x
        dy = enemy4_y - player_y

        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 1.5:
            enemy4_hp -= 50
            print("MELEE HIT", enemy4_hp)

            if enemy4_hp <= 0:
                enemy4_alive = False
                print("ENEMY DEAD")
    
    if enemy5_alive:
        dx = enemy5_x - player_x
        dy = enemy5_y - player_y

        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 1.5:
            enemy5_hp -= 50
            print("MELEE HIT", enemy5_hp)

            if enemy5_hp <= 0:
                enemy5_alive = False
                print("ENEMY DEAD")
    
    if finalenemy_alive:
        dx = finalenemy_x - player_x
        dy = finalenemy_y - player_y

        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 1.5:
            finalenemy_hp -= 50
            print("MELEE HIT", finalenemy_hp)

            if finalenemy_hp <= 0:
                finalenemy_alive = False
                print("ENEMY DEAD")



def draw_enemy1():
    if not enemy1_alive:
        return
    dx = enemy1_x - player_x
    dy = enemy1_y - player_y

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

    sprite = pygame.transform.scale(current_enemy1, (size, size))

    screen.blit(
    sprite,
    (screen_x - size // 2, HEIGHT // 2 - size // 2)
)
    draw_enemy_hp_bar(screen_x, size, enemy1_hp, 200)
def draw_enemy2():
    if not enemy2_alive:
        return
    dx = enemy2_x - player_x
    dy = enemy2_y - player_y

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

    sprite = pygame.transform.scale(current_enemy2, (size, size))

    screen.blit(
        sprite,
        (screen_x - size // 2, HEIGHT // 2 - size // 2)
    )
    draw_enemy_hp_bar(screen_x, size, enemy2_hp, 300)

def draw_enemy3():
    if not enemy3_alive:
        return
    dx = enemy3_x - player_x
    dy = enemy3_y - player_y

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

    sprite = pygame.transform.scale(current_enemy3, (size, size))

    screen.blit(
        sprite,
        (screen_x - size // 2, HEIGHT // 2 - size // 2)
    )
    draw_enemy_hp_bar(screen_x, size, enemy3_hp, 400)
def draw_enemy4():
    if not enemy4_alive:
        return
    dx = enemy4_x - player_x
    dy = enemy4_y - player_y

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

    sprite = pygame.transform.scale(current_enemy4, (size, size))

    screen.blit(
        sprite,
        (screen_x - size // 2, HEIGHT // 2 - size // 2)
    )
    draw_enemy_hp_bar(screen_x, size, enemy4_hp, 500)
def draw_enemy5():
    if not enemy5_alive:
        return
    dx = enemy5_x - player_x
    dy = enemy5_y - player_y

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

    sprite = pygame.transform.scale(current_enemy5, (size, size))

    screen.blit(
        sprite,
        (screen_x - size // 2, HEIGHT // 2 - size // 2)
    )
    draw_enemy_hp_bar(screen_x, size, enemy5_hp, 600)
def draw_finalenemy():
    if not finalenemy_alive:
        return
    dx = finalenemy_x - player_x
    dy = finalenemy_y - player_y

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

    sprite = pygame.transform.scale(current_finalenemy, (size, size))

    screen.blit(
        sprite,
        (screen_x - size // 2, HEIGHT // 2 - size // 2)
    )
    draw_enemy_hp_bar(screen_x, size, finalenemy_hp, 1000)
def draw_hp_bar():
    bar_width = 300
    bar_height = 25

    x = WIDTH // 2 - bar_width // 2
    y = HEIGHT - 40

    # háttér
    pygame.draw.rect(screen, (40, 40, 40), (x, y, bar_width, bar_height))

    # hp arány FIX maximumhoz
    hp_ratio = player_hp / player_max_hp

    # ne mehessen 100% fölé
    hp_ratio = min(hp_ratio, 1)

    current_width = int(bar_width * hp_ratio)

    # szín
    if hp_ratio > 0.6:
        color = (0, 255, 0)
    elif hp_ratio > 0.3:
        color = (255, 165, 0)
    else:
        color = (255, 0, 0)

    # hp csík
    pygame.draw.rect(screen, color, (x, y, current_width, bar_height))

    # keret
    pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)

    # kisebb font a hp számhoz
    hp_font = pygame.font.SysFont("arial", 18, bold=True)

    hp_text = hp_font.render(f"{player_hp} HP", True, (255,255,255))

    text_rect = hp_text.get_rect(center=(x + bar_width // 2, y + bar_height // 2))

    screen.blit(hp_text, text_rect)

enemy_attack_cooldown = 0
enemy1_attack_cooldown = 0
enemy2_attack_cooldown = 0
enemy3_attack_cooldown = 0
enemy4_attack_cooldown = 0
enemy5_attack_cooldown = 0
finalenemy_attack_cooldown = 0
enemy_morehp = False
enemy1_morehp = False
enemy2_morehp = False
enemy3_morehp = False
enemy4_morehp = False
enemy5_morehp = False
enemy_state = "idle"
enemy1_state = "idle"
enemy2_state = "idle"
enemy3_state = "idle"
enemy4_state = "idle"
enemy5_state = "idle"
finalenemy_state= "idle"
enemy_shoot_timer = 10
enemy1_shoot_timer = 10
enemy2_shoot_timer = 10
enemy3_shoot_timer = 10
enemy4_shoot_timer = 10
enemy5_shoot_timer = 10
finalenemy_shoot_timer = 10


def draw_enemy_hp_bar(screen_x, size, hp, max_hp):
    bar_width = size
    bar_height = 8

    x = screen_x - bar_width // 2
    y = HEIGHT // 2 - size // 2 - 18

    # háttér
    pygame.draw.rect(screen, (60, 60, 60), (x, y, bar_width, bar_height))

    # hp arány
    hp_ratio = hp / max_hp
    hp_ratio = max(0, min(1, hp_ratio))

    current_width = int(bar_width * hp_ratio)

    # szín
    if hp_ratio > 0.6:
        color = (0, 255, 0)
    elif hp_ratio > 0.3:
        color = (255, 165, 0)
    else:
        color = (255, 0, 0)

    # hp
    pygame.draw.rect(screen, color, (x, y, current_width, bar_height))

    # keret
    pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 1)


def death():
    global game_state, death_bg, death_alpha
    if game_state == "dead":
        return
    game_state = "dead"
    death_alpha = 0
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    # Freeze frame + grayscale konverzió
    snapshot = pygame.Surface((WIDTH, HEIGHT))
    snapshot.blit(screen, (0, 0))
    try:
        px = pygame.surfarray.pixels3d(snapshot)
        gray = (px[:, :, 0] * 0.299 + px[:, :, 1] * 0.587 + px[:, :, 2] * 0.114).astype(np.uint8)
        px[:, :, 0] = gray
        px[:, :, 1] = gray
        px[:, :, 2] = gray
        del px
    except Exception:
        pass
    death_bg = snapshot


def draw_menu():
    global menu_alpha, menu_tick, selected, menu_button_rects

    menu_tick += 1

    # Fade in
    if menu_alpha < 255:
        menu_alpha = min(255, menu_alpha + 3)

    # Vörös sarok vignette
    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for cx, cy in [(0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT)]:
        for r in range(300, 0, -10):
            t = r / 300
            a = int(160 * (t ** 1.5))
            pygame.draw.circle(vignette, (55, 0, 0, a), (cx, cy), r)
    screen.blit(vignette, (0, 0))

    # Scanline effekt
    for y in range(0, HEIGHT, 4):
        scan = pygame.Surface((WIDTH, 2), pygame.SRCALPHA)
        scan.fill((0, 0, 0, 35))
        screen.blit(scan, (0, y))

    # Pulzáló cím
    title_pulse = int(math.sin(menu_tick * 0.05) * 3)
    try:
        title_font = pygame.font.SysFont("impact", 70)
    except Exception:
        title_font = pygame.font.SysFont("arial", 70, bold=True)

    ty = 45 + title_pulse
    # Árnyék
    t_shadow = title_font.render("HORROR DUNGEON", True, (12, 0, 0))
    t_shadow.set_alpha(menu_alpha)
    for ox, oy in [(-5, -5), (5, -5), (-5, 5), (5, 5)]:
        screen.blit(t_shadow, (WIDTH // 2 - t_shadow.get_width() // 2 + ox, ty + oy))
    # Fő cím
    t_main = title_font.render("HORROR DUNGEON", True, (205, 10, 10))
    t_main.set_alpha(menu_alpha)
    screen.blit(t_main, (WIDTH // 2 - t_main.get_width() // 2, ty))

    # Vízszintes elválasztó
    div_y = ty + t_main.get_height() + 8
    div = pygame.Surface((300, 2), pygame.SRCALPHA)
    div.fill((160, 20, 20, menu_alpha))
    screen.blit(div, (WIDTH // 2 - 150, div_y))

    # Gombok
    menu_button_rects.clear()
    mx, my = pygame.mouse.get_pos()
    labels = ["SINGLEPLAYER", "MULTIPLAYER", "EXIT"]
    btn_w, btn_h, gap = 280, 52, 16
    start_y = div_y + 18

    try:
        btn_font = pygame.font.SysFont("impact", 25)
    except Exception:
        btn_font = pygame.font.SysFont("arial", 22, bold=True)

    for i, label in enumerate(labels):
        btn_x = WIDTH // 2 - btn_w // 2
        btn_y = start_y + i * (btn_h + gap)
        rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        menu_button_rects.append(rect)

        hovering = rect.collidepoint(mx, my)
        active = (i == selected)

        # Gomb háttér
        btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        if active or hovering:
            btn_surf.fill((165, 15, 15, min(menu_alpha, 210)))
        else:
            btn_surf.fill((48, 5, 5, min(menu_alpha, 165)))
        screen.blit(btn_surf, (btn_x, btn_y))

        # Gomb keret
        brd_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        brd_col = (235, 55, 55, menu_alpha) if (active or hovering) else (110, 18, 18, menu_alpha)
        pygame.draw.rect(brd_surf, brd_col, (0, 0, btn_w, btn_h), 2)
        screen.blit(brd_surf, (btn_x, btn_y))

        # Bal oldali aktív jelző csík
        if active:
            bar = pygame.Surface((4, btn_h - 10), pygame.SRCALPHA)
            bar.fill((235, 55, 55, menu_alpha))
            screen.blit(bar, (btn_x + 6, btn_y + 5))

        # Felirat
        tcol = (255, 255, 255) if (active or hovering) else (195, 140, 140)
        btn_label = btn_font.render(label, True, tcol)
        btn_label.set_alpha(menu_alpha)
        screen.blit(btn_label, (btn_x + btn_w // 2 - btn_label.get_width() // 2,
                                 btn_y + btn_h // 2 - btn_label.get_height() // 2))

    # Lábléc tipp
    hint_font = pygame.font.SysFont("arial", 13)
    hint = hint_font.render("↑↓ or mouse to navigate   •   ENTER or click to select", True, (110, 55, 55))
    hint.set_alpha(min(menu_alpha, 150))
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 26))


def draw_death_screen():
    global death_alpha, exit_button_rect

    # Fagyasztott szürkeárnyalatos háttér
    if death_bg is not None:
        screen.blit(death_bg, (0, 0))

    # Alpha növelése
    if death_alpha < 220:
        death_alpha = min(death_alpha + 2, 220)

    # Sötét vörös overlay (vignette)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((70, 0, 0, min(int(death_alpha * 0.65), 145)))
    screen.blit(overlay, (0, 0))

    # Scanline effekt (GTA-szerű)
    if death_alpha > 40:
        scan_alpha = min(80, int(death_alpha * 0.36))
        for y in range(0, HEIGHT, 4):
            scan_line = pygame.Surface((WIDTH, 2), pygame.SRCALPHA)
            scan_line.fill((0, 0, 0, scan_alpha))
            screen.blit(scan_line, (0, y))

    # "YOU DIED" felirat
    if death_alpha >= 70:
        text_alpha = min(255, int((death_alpha - 70) * 5))
        try:
            death_font_big = pygame.font.SysFont("impact", 92)
        except Exception:
            death_font_big = pygame.font.SysFont("arial", 92, bold=True)

        # Árnyék (GTA-stílusú)
        shadow = death_font_big.render("YOU DIED", True, (15, 0, 0))
        shadow.set_alpha(text_alpha)
        for ox, oy in [(-5, -5), (5, -5), (-5, 5), (5, 5)]:
            screen.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + ox,
                                  HEIGHT // 2 - shadow.get_height() // 2 - 50 + oy))

        # Fő szöveg – mélyvörös
        main_text = death_font_big.render("YOU DIED", True, (210, 10, 10))
        main_text.set_alpha(text_alpha)
        screen.blit(main_text, (WIDTH // 2 - main_text.get_width() // 2,
                                 HEIGHT // 2 - main_text.get_height() // 2 - 50))

    # Alcím
    if death_alpha >= 120:
        sub_alpha = min(255, int((death_alpha - 120) * 5))
        sub_font = pygame.font.SysFont("arial", 18)
        sub_text = sub_font.render("you were consumed by the darkness", True, (170, 90, 90))
        sub_text.set_alpha(sub_alpha)
        screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2,
                                HEIGHT // 2 + 14))

    # EXIT gomb
    if death_alpha >= 155:
        btn_alpha = min(255, int((death_alpha - 155) * 8))

        btn_w, btn_h = 220, 52
        btn_x = WIDTH // 2 - btn_w // 2
        btn_y = HEIGHT // 2 + 55
        exit_button_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        mx, my = pygame.mouse.get_pos()
        hovering = exit_button_rect.collidepoint(mx, my)

        # Gomb háttér
        btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        fill_color = (185, 20, 20, btn_alpha) if hovering else (90, 8, 8, btn_alpha)
        btn_surf.fill(fill_color)
        screen.blit(btn_surf, (btn_x, btn_y))

        # Gomb keret
        brd_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        border_color = (240, 60, 60, btn_alpha) if hovering else (190, 35, 35, btn_alpha)
        pygame.draw.rect(brd_surf, border_color, (0, 0, btn_w, btn_h), 2)
        screen.blit(brd_surf, (btn_x, btn_y))

        # Gomb szöveg
        btn_font = pygame.font.SysFont("arial", 22, bold=True)
        btn_label = btn_font.render("EXIT GAME", True, (255, 255, 255))
        btn_label.set_alpha(btn_alpha)
        screen.blit(btn_label, (btn_x + btn_w // 2 - btn_label.get_width() // 2,
                                 btn_y + btn_h // 2 - btn_label.get_height() // 2))


def draw_multiplayer_screen():
    global mp_alpha, mp_tick, mp_back_rect

    mp_tick += 1

    # Fade in
    if mp_alpha < 255:
        mp_alpha = min(255, mp_alpha + 3)

    # Vörös sarok vignette (identical to menu)
    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for cx, cy in [(0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT)]:
        for r in range(300, 0, -10):
            t = r / 300
            a = int(160 * (t ** 1.5))
            pygame.draw.circle(vignette, (55, 0, 0, a), (cx, cy), r)
    screen.blit(vignette, (0, 0))

    # Scanline effekt
    for y in range(0, HEIGHT, 4):
        scan = pygame.Surface((WIDTH, 2), pygame.SRCALPHA)
        scan.fill((0, 0, 0, 35))
        screen.blit(scan, (0, y))

    # Halvány vörös grid háttér
    if mp_alpha >= 50:
        grid_alpha = min(40, int((mp_alpha - 50) * 0.5))
        grid_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for gx in range(0, WIDTH, 40):
            pygame.draw.line(grid_surf, (120, 10, 10, grid_alpha), (gx, 0), (gx, HEIGHT), 1)
        for gy in range(0, HEIGHT, 40):
            pygame.draw.line(grid_surf, (120, 10, 10, grid_alpha), (0, gy), (WIDTH, gy), 1)
        screen.blit(grid_surf, (0, 0))

    # Pulzáló "MULTIPLAYER" cím
    title_pulse = int(math.sin(mp_tick * 0.05) * 3)
    try:
        title_font = pygame.font.SysFont("impact", 70)
    except Exception:
        title_font = pygame.font.SysFont("arial", 70, bold=True)

    ty = 45 + title_pulse

    # Árnyék
    t_shadow = title_font.render("MULTIPLAYER", True, (12, 0, 0))
    t_shadow.set_alpha(mp_alpha)
    for ox, oy in [(-5, -5), (5, -5), (-5, 5), (5, 5)]:
        screen.blit(t_shadow, (WIDTH // 2 - t_shadow.get_width() // 2 + ox, ty + oy))
    # Fő cím
    t_main = title_font.render("MULTIPLAYER", True, (205, 10, 10))
    t_main.set_alpha(mp_alpha)
    screen.blit(t_main, (WIDTH // 2 - t_main.get_width() // 2, ty))

    # Vízszintes elválasztó
    div_y = ty + t_main.get_height() + 8
    div = pygame.Surface((300, 2), pygame.SRCALPHA)
    div.fill((160, 20, 20, mp_alpha))
    screen.blit(div, (WIDTH // 2 - 150, div_y))

    # "COMING SOON" – pulzáló vörös szöveg
    if mp_alpha >= 60:
        cs_alpha = min(255, int((mp_alpha - 60) * 3))
        try:
            cs_font = pygame.font.SysFont("impact", 44)
        except Exception:
            cs_font = pygame.font.SysFont("arial", 44, bold=True)
        pulse_r = int(185 + 20 * abs(math.sin(mp_tick * 0.04)))
        cs_text = cs_font.render("COMING SOON", True, (pulse_r, 8, 8))
        cs_text.set_alpha(cs_alpha)
        screen.blit(cs_text, (WIDTH // 2 - cs_text.get_width() // 2, div_y + 28))

    # Alcím
    if mp_alpha >= 100:
        sub_alpha = min(255, int((mp_alpha - 100) * 4))
        sub_font = pygame.font.SysFont("arial", 15)
        sub_text = sub_font.render("the darkness awaits... but not yet", True, (170, 90, 90))
        sub_text.set_alpha(sub_alpha)
        screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, div_y + 82))

    # BACK TO MENU gomb
    if mp_alpha >= 140:
        btn_alpha = min(255, int((mp_alpha - 140) * 5))
        btn_w, btn_h = 240, 52
        btn_x = WIDTH // 2 - btn_w // 2
        btn_y = HEIGHT // 2 + 80
        mp_back_rect.update(btn_x, btn_y, btn_w, btn_h)

        mx, my = pygame.mouse.get_pos()
        hovering = mp_back_rect.collidepoint(mx, my)

        try:
            btn_font = pygame.font.SysFont("impact", 25)
        except Exception:
            btn_font = pygame.font.SysFont("arial", 22, bold=True)

        # Gomb háttér
        btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        fill_color = (165, 15, 15, min(btn_alpha, 210)) if hovering else (48, 5, 5, min(btn_alpha, 165))
        btn_surf.fill(fill_color)
        screen.blit(btn_surf, (btn_x, btn_y))

        # Gomb keret
        brd_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        brd_col = (235, 55, 55, btn_alpha) if hovering else (110, 18, 18, btn_alpha)
        pygame.draw.rect(brd_surf, brd_col, (0, 0, btn_w, btn_h), 2)
        screen.blit(brd_surf, (btn_x, btn_y))

        # Bal oldali aktív jelző csík hover esetén
        if hovering:
            bar = pygame.Surface((4, btn_h - 10), pygame.SRCALPHA)
            bar.fill((235, 55, 55, btn_alpha))
            screen.blit(bar, (btn_x + 6, btn_y + 5))

        # Gomb felirat
        tcol = (255, 255, 255) if hovering else (195, 140, 140)
        btn_label = btn_font.render("BACK TO MENU", True, tcol)
        btn_label.set_alpha(btn_alpha)
        screen.blit(btn_label, (btn_x + btn_w // 2 - btn_label.get_width() // 2,
                                 btn_y + btn_h // 2 - btn_label.get_height() // 2))

    # Lábléc tipp
    hint_font = pygame.font.SysFont("arial", 13)
    hint = hint_font.render("ESC or click to return to menu", True, (110, 55, 55))
    hint.set_alpha(min(mp_alpha, 150))
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 26))


def enemy_attack():
    global enemy_attack_cooldown,player_hp,player_max_hp,enemy_morehp,enemy_state,enemy_shoot_timer
    attack_distance = 1.5  # támadás távolsága
    damage = 10  # sebzés értéke

    # Csak ha van ellenség élőben
    if enemy_alive:
        dx = enemy_x - player_x
        dy = enemy_y - player_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < attack_distance:
            
            if enemy_attack_cooldown == 0:
                enemy_state = "shoot"
                enemy_shoot_timer = 10
                print("Enemy támad!")
                loves = random.randint(0,1)
                if loves == 1:
                    player_hp -= damage
                    print(f"Player HP: {player_hp}")
                    if player_hp <= 0:
                        death()
                        print("Game Over!")
                    
                    print("Az enemy eltalált!")
                else:
                    print("Az enemy nem talált el!")
                enemy_attack_cooldown = 90
    if not enemy_alive:
        if not enemy_morehp:
            print("Max HP 300!")
            player_hp = 300
            enemy_morehp = True
            
    # Csökkentjük a cooldown-t
    if enemy_attack_cooldown > 0:
        enemy_attack_cooldown -= 1

def enemy1_attack():
    global enemy1_attack_cooldown,player_hp,player_max_hp,enemy1_morehp,enemy1_state,enemy1_shoot_timer
    attack_distance = 1.5  # támadás távolsága
    damage = 20  # sebzés értéke

    # Csak ha van ellenség élőben
    if enemy1_alive:
        dx = enemy1_x - player_x
        dy = enemy1_y - player_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < attack_distance:
            if enemy1_attack_cooldown == 0:
                enemy1_state = "shoot"
                enemy1_shoot_timer = 10
                print("Enemy támad!")
                loves = random.randint(0,1)
                if loves == 1:
                    player_hp -= damage
                    print(f"Player HP: {player_hp}")
                    if player_hp <= 0:
                        death()
                        print("Game Over!")
                    
                    print("Az enemy eltalált!")
                else:
                    print("Az enemy nem talált el!")
                enemy1_attack_cooldown = 30 
    if not enemy1_alive:
        if not enemy1_morehp:
            print("Max HP 300!")
            player_max_hp += 50
            player_hp += 50
            enemy1_morehp = True
    # Csökkentjük a cooldown-t
    if enemy1_attack_cooldown > 0:
        enemy1_attack_cooldown -= 1

def enemy2_attack():
    global enemy2_attack_cooldown,player_hp,enemy2_morehp,enemy2_state,enemy2_shoot_timer
    attack_distance = 1.5  # támadás távolsága
    damage = 30  # sebzés értéke

    # Csak ha van ellenség élőben
    if enemy2_alive:
        dx = enemy2_x - player_x
        dy = enemy2_y - player_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < attack_distance:
            if enemy2_attack_cooldown == 0:
                enemy2_state = "shoot"
                enemy2_shoot_timer = 10
                print("Enemy támad!")
                loves = random.randint(0,1)
                if loves == 1:
                    player_hp -= damage
                    print(f"Player HP: {player_hp}")
                    if player_hp <= 0:
                        death()
                        print("Game Over!")
                    print("Az enemy eltalált!")
                else:
                    print("Az enemy nem talált el!")
                enemy2_attack_cooldown = 30 
    if not enemy2_alive:
        if not enemy2_morehp:
            print("Max HP 300!")
            player_hp = 400
            enemy2_morehp = True
    # Csökkentjük a cooldown-t
    if enemy2_attack_cooldown > 0:
        enemy2_attack_cooldown -= 1

def enemy3_attack():
    global enemy3_attack_cooldown,player_hp,player_max_hp,enemy3_morehp,enemy3_state,enemy3_shoot_timer
    attack_distance = 1.5  # támadás távolsága
    damage = 40  # sebzés értéke

    # Csak ha van ellenség élőben
    if enemy3_alive:
        dx = enemy3_x - player_x
        dy = enemy3_y - player_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < attack_distance:
            if enemy3_attack_cooldown == 0:
                enemy3_state = "shoot"
                enemy3_shoot_timer = 10
                print("Enemy támad!")
                loves = random.randint(0,1)
                if loves == 1:
                    player_hp -= damage
                    print(f"Player HP: {player_hp}")
                    if player_hp <= 0:
                        death()
                        print("Game Over!")
                
                else:
                    print("Az enemy nem talált el!")
                enemy3_attack_cooldown = 30
    if not enemy3_alive:
        if not enemy3_morehp:
            print("Max HP 300!")
            player_hp = 450
            enemy3_morehp = True
    # Csökkentjük a cooldown-t
    if enemy3_attack_cooldown > 0:
        enemy3_attack_cooldown -= 1

def enemy4_attack():
    global enemy4_attack_cooldown,player_hp,player_max_hp,enemy4_morehp,enemy4_state,enemy4_shoot_timer
    attack_distance = 1.5  # támadás távolsága
    damage = 30  # sebzés értéke

    # Csak ha van ellenség élőben
    if enemy4_alive:
        dx = enemy4_x - player_x
        dy = enemy4_y - player_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < attack_distance:
            if enemy4_attack_cooldown == 0:
                enemy4_state = "shoot"
                enemy4_shoot_timer = 10
                print("Enemy támad!")
                loves = random.randint(0,1)
                if loves == 1:
                    player_hp -= damage
                    print(f"Player HP: {player_hp}")
                    if player_hp <= 0:
                        death()
                        print("Game Over!")
                    
                    print("Az enemy eltalált!")
                else:
                    print("Az enemy nem talált el!")
                enemy4_attack_cooldown = 20
    if not enemy4_alive:
        if not enemy4_morehp:
            print("Max HP 300!")
            player_hp = 500
            enemy4_morehp = True
    # Csökkentjük a cooldown-t
    if enemy4_attack_cooldown > 0:
        enemy4_attack_cooldown -= 1


def enemy5_attack():
    global enemy5_attack_cooldown,player_hp,player_max_hp,enemy5_morehp,enemy5_state,enemy5_shoot_timer
    attack_distance = 1.5  # támadás távolsága
    damage = 45  # sebzés értéke

    # Csak ha van ellenség élőben
    if enemy5_alive:
        dx = enemy5_x - player_x
        dy = enemy5_y - player_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < attack_distance:
            if enemy5_attack_cooldown == 0:
                enemy5_state = "shoot"
                enemy5_shoot_timer = 10
                print("Enemy támad!")
                loves = random.randint(0,1)
                if loves == 1:
                    player_hp -= damage
                    print(f"Player HP: {player_hp}")
                    if player_hp <= 0:
                        death()
                        print("Game Over!")
                    
                    print("Az enemy eltalált!")
                else:
                    print("Az enemy nem talált el!")
                enemy5_attack_cooldown = 30 
    if not enemy5_alive:
        if not enemy5_morehp:
            print("Max HP 300!")
            player_hp = 550
            enemy5_morehp = True
    # Csökkentjük a cooldown-t
    if enemy5_attack_cooldown > 0:
        enemy5_attack_cooldown -= 1

def finalenemy_attack():
    global finalenemy_attack_cooldown,player_max_hp,player_hp,finalenemy_state,finalenemy_shoot_timer
    attack_distance = 1.5  # támadás távolsága
    damage = 60  # sebzés értéke

    # Csak ha van ellenség élőben
    if finalenemy_alive:
        dx = finalenemy_x - player_x
        dy = finalenemy_y - player_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < attack_distance:
            if finalenemy_attack_cooldown == 0:
                finalenemy_state = "shoot"
                finalenemy_shoot_timer = 10
                print("Enemy támad!")
                loves = random.randint(0,1)
                if loves == 1:
                    player_hp -= damage
                    print(f"Player HP: {player_hp}")
                    if player_hp <= 0:
                        death()
                        print("Game Over!")
                    
                    print("Az enemy eltalált!")
                else:
                    print("Az enemy nem talált el!")
                finalenemy_attack_cooldown = 30 
    # Csökkentjük a cooldown-t
    if finalenemy_attack_cooldown > 0:
        finalenemy_attack_cooldown -= 1


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
                if game_state == "game":
                    shoot()
                elif game_state == "dead":
                    if exit_button_rect.collidepoint(event.pos):
                        running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                if game_state == "game":
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
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        menu_music.stop()
                        menu_music_started = False
                        menu_alpha = 0

                    elif selected == 1:
                        game_state = "multiplayer"
                        menu_music.stop()
                        menu_music_started = False
                        mp_alpha = 0
                        mp_tick = 0

                    elif selected == 2:
                        running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(menu_button_rects):
                    if rect.collidepoint(event.pos):
                        selected = i
                        if i == 0:
                            game_state = "game"
                            pygame.mouse.set_visible(False)
                            pygame.event.set_grab(True)
                            menu_music.stop()
                            menu_music_started = False
                            menu_alpha = 0
                        elif i == 1:
                            game_state = "multiplayer"
                            menu_music.stop()
                            menu_music_started = False
                            mp_alpha = 0
                            mp_tick = 0
                        elif i == 2:
                            running = False

            if event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(menu_button_rects):
                    if rect.collidepoint(event.pos):
                        selected = i

        elif game_state == "game":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                    menu_alpha = 0
                    menu_music_started = False

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
            enemy_attack()
            enemy1_attack()
            enemy2_attack()
            enemy3_attack()
            enemy4_attack()
            enemy5_attack()
            finalenemy_attack()

        elif game_state == "multiplayer":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                    menu_alpha = 0
                    menu_music_started = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if mp_back_rect.collidepoint(event.pos):
                    game_state = "menu"
                    menu_alpha = 0
                    menu_music_started = False

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
        if enemy_shoot_timer > 0:
            enemy_shoot_timer -= 1
        else:
            enemy_state = "idle"

    # ---------------- RENDER ----------------
    screen.fill((0, 0, 0))

    if game_state == "menu":
        if not menu_music_started:
            menu_music.play(-1)
            menu_music_started = True
        draw_menu()

    elif game_state == "game":
        menu_music.stop()
        screen.fill((70, 120, 200))
        pygame.draw.rect(screen, (50, 50, 50), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
        cast_rays()
        check_locked_doors()
        draw_enemy()
        draw_enemy1()
        draw_enemy2()
        draw_enemy3()
        draw_enemy4()
        draw_enemy5()
        draw_finalenemy()
        draw_flashlight()
        draw_hp_bar()
        pygame.draw.line(screen, (255, 255, 255), (WIDTH // 2 - 10, HEIGHT // 2), (WIDTH // 2 + 10, HEIGHT // 2), 2)
        pygame.draw.line(screen, (255, 255, 255), (WIDTH // 2, HEIGHT // 2 - 10), (WIDTH // 2, HEIGHT // 2 + 10), 2)

        if gun_state == "shoot":
            current_gun = gun_shoot_img
        else:
            current_gun = gun_idle_img
        if enemy_state == "shoot":
            current_enemy = enemy_shoot_img
        else:
            current_enemy = enemy_img
        if enemy1_state == "shoot":
            current_enemy1 = enemy1_shoot_img
        else:
            current_enemy1 = enemy1_img
        if enemy2_state == "shoot":
            current_enemy2 = enemy2_shoot_img
        else:
            current_enemy2 = enemy2_img
        if enemy3_state == "shoot":
            current_enemy3 = enemy3_shoot_img
        else:
            current_enemy3 = enemy3_img
        if enemy4_state == "shoot":
            current_enemy4 = enemy4_shoot_img
        else:
            current_enemy4 = enemy4_img
        if enemy5_state == "shoot":
            current_enemy5 = enemy5_shoot_img
        else:
            current_enemy5 = enemy5_img
        if finalenemy_state == "shoot":
            current_finalenemy = finalenemy_shoot_img
        else:
            current_finalenemy = finalenemy_img


        scale = WIDTH // 400
        gun_scaled = pygame.transform.scale(current_gun, (
        int(current_gun.get_width() * scale), int(current_gun.get_height() * scale)))

        gun_x = WIDTH - 2 * (gun_scaled.get_width() // 2) + gun_shake_x
        gun_y = HEIGHT - gun_scaled.get_height() + gun_shake_y

        screen.blit(gun_scaled, (gun_x, gun_y))

        if shoot_flash > 0:
            pygame.draw.circle(screen, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 8)
            shoot_flash -= 1
    if game_state == "multiplayer":
        draw_multiplayer_screen()

    elif game_state == "dead":
        draw_death_screen()

    pygame.display.flip()

pygame.quit()