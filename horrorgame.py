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
    [1,0,0,0,2,0,0,2,0,0,0,1],
    [1,0,0,0,1,0,0,1,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1],
])

# ---------------- PLAYER ----------------
player_x, player_y = 6, 16.5
player_angle = 250


enemy_x, enemy_y = 3, 15


doors = {}

enemy_hp = 100
enemy_alive = True
shoot_flash = 0
shot = False
gun_state = "idle"
gun_timer = 0
# ---------------- TEXTURE ----------------
wall_texture = pygame.image.load("./img/wall.png").convert()
tex_width, tex_height = wall_texture.get_size()
enemy_img = pygame.image.load("./img/ghost.png").convert_alpha()
door_texture = pygame.image.load("./img/door.png").convert()
gun_idle_img = pygame.image.load("./img/gun.png").convert_alpha()
gun_shoot_img = pygame.image.load("./img/shoot.png").convert_alpha()
current_gun = gun_idle_img
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

            tile = world_map[map_y][map_x]

            if tile == 1:
                hit = True

            elif tile == 2:
                if doors.get((map_x, map_y), 0) == 0:
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

        if tile == 2:
            texture = door_texture
        else:
            texture = wall_texture

        tex_column = texture.subsurface((tex_x, 0, 1, tex_height))
        tex_column = pygame.transform.scale(tex_column, (1, wall_height))

        screen.blit(
            tex_column,
            (ray, HEIGHT//2 - wall_height//2)
        )
        z_buffer[ray] = dist

def draw_enemy():
    if not enemy_alive:
        return
    dx = enemy_x - player_x
    dy = enemy_y - player_y

    dist = math.sqrt(dx*dx + dy*dy)

    angle = math.atan2(dy, dx) - player_angle

    # normalize angle
    angle = (angle + math.pi) % (2 * math.pi) - math.pi

    # FOV check
    if abs(angle) > math.pi / 4:
        return

    # screen pozíció
    screen_x = int((angle / (math.pi / 4)) * (WIDTH / 2) + WIDTH / 2)

    if screen_x < 0 or screen_x >= WIDTH:
        return

    if dist > z_buffer[screen_x]:
        return

    # méret
    size = int(min(800 / (dist + 0.1), HEIGHT))

    sprite = pygame.transform.scale(enemy_img, (size, size))

    screen.blit(
        sprite,
        (screen_x - size // 2, HEIGHT // 2 - size // 2)
    )


def shoot():
    global enemy_hp,enemy_alive,shoot_flash,gun_state,gun_timer
    shoot_flash = 5
    gun_state = "shoot"
    gun_timer = 5
    if not enemy_alive:
        return
    dx = enemy_x - player_x
    dy = enemy_y - player_y

    dist = math.sqrt(dx*dx + dy*dy)

    angle_to_enemy = math.atan2(dy,dx)
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
        print("HIT!",enemy_hp)

        if enemy_hp <= 0:
            enemy_alive = False
            print("ENEMY DEAD")

def melee_attack():
    global enemy_hp,enemy_alive

    if not enemy_alive:
        return
    dx = enemy_x - player_x
    dy = enemy_y - player_y

    dist = math.sqrt(dx*dx + dy*dy)

    if dist < 1.5:
        enemy_hp-=50
        print("MELEE HIT",enemy_hp)
        
        if enemy_hp <=0:
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
        if event.type ==pygame.MOUSEBUTTONDOWN:
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

                        if key not in doors:
                            doors[key] = 1
                        else:
                            doors[key] = 1 - doors[key]

    # ---------------- LOGIKA ----------------
    if game_state == "menu":

        if selected < 0:
            selected = len(menu_options) - 1

        if selected >= len(menu_options):
            selected = 0
    # ---------------- GAME ----------------
    if game_state == "game":
        if gun_timer > 0:
            gun_timer -= 1
        else:
            gun_state = "idle"

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
        pygame.draw.line(screen, (255,255,255), (WIDTH//2 - 10, HEIGHT//2), (WIDTH//2 + 10, HEIGHT//2), 2)
        pygame.draw.line(screen, (255,255,255), (WIDTH//2, HEIGHT//2 - 10), (WIDTH//2, HEIGHT//2 + 10), 2)
        

        gun_x = WIDTH - 2*(current_gun.get_width()//2)
        gun_y = HEIGHT - current_gun.get_height()

        if gun_state == "shoot":
            current_gun = gun_shoot_img
        else:
            current_gun = gun_idle_img
        screen.blit(current_gun, (gun_x,gun_y))


        if shoot_flash > 0:
            pygame.draw.circle(screen,(255,255,255),(WIDTH//2,HEIGHT//2),8)
            shoot_flash -=1

    pygame.display.flip()

pygame.quit()