from ursina import *
import random
import math

app = Ursina()

window.title = "FS-Like VS Code Edition"
window.borderless = False

# =========================
# WORLD
# =========================
Sky()

ground = Entity(
    model='plane',
    scale=100,
    texture='grass',
    texture_scale=(40,40),
    collider='box'
)

# =========================
# GAME STATE
# =========================
money = 200
weather = "sun"
time_counter = 0

inventory = {
    "seeds": 5
}

# =========================
# WEATHER
# =========================
def update_weather():
    global weather, time_counter
    time_counter += time.dt

    if time_counter > 20:
        time_counter = 0
        weather = random.choice(["sun","rain","dry"])

# =========================
# FIELD SYSTEM
# =========================
TILE = 2
SIZE = 10

class FieldTile(Entity):
    def __init__(self, pos):
        super().__init__(
            model='cube',
            position=pos,
            scale=(TILE,0.2,TILE),
            collider='box'
        )

        self.state = 0  # 0 grass, 1 plowed, 2 planted, 3 grown
        self.grow = 0
        self.grow_max = random.randint(6,12)

        self.set_visual()

    def set_visual(self):
        if self.state == 0:
            self.color = color.green
        elif self.state == 1:
            self.color = color.rgb(120,70,30)
        elif self.state == 2:
            self.color = color.rgb(60,180,60)
        elif self.state == 3:
            self.color = color.yellow

    def update_growth(self):
        if self.state == 2:
            speed = 1

            if weather == "rain":
                speed = 1.5
            elif weather == "dry":
                speed = 0.7

            self.grow += time.dt * speed

            if self.grow > self.grow_max:
                self.state = 3
                self.set_visual()

# generate field
fields = []

for x in range(SIZE):
    for z in range(SIZE):
        fields.append(FieldTile((x*TILE,0,z*TILE)))

# =========================
# TRACTOR
# =========================
tractor = Entity(
    model='cube',
    color=color.red,
    scale=(1,1,2),
    position=(5,1,5)
)

velocity = Vec3(0,0,0)
acceleration = 12
friction = 4
max_speed = 8

# =========================
# CAMERA (FIXED 3RD PERSON)
# =========================
cam_yaw = 0
cam_pitch = 20
cam_distance = 12
cam_height = 5

def update_camera():
    global cam_yaw, cam_pitch

    if held_keys['right mouse']:
        cam_yaw += mouse.velocity[0] * 60
        cam_pitch -= mouse.velocity[1] * 60
        cam_pitch = clamp(cam_pitch, 5, 70)

    offset = Vec3(
        math.sin(math.radians(cam_yaw)) * cam_distance,
        cam_height + math.sin(math.radians(cam_pitch)) * 4,
        math.cos(math.radians(cam_yaw)) * cam_distance
    )

    camera.position = tractor.position + offset
    camera.look_at(tractor.position)

# =========================
# SHOP
# =========================
shop = Entity(
    model='cube',
    color=color.azure,
    scale=3,
    position=(15,1,15),
    collider='box'
)

shop_open = False

# =========================
# UI
# =========================
hud = Text("", position=(-0.85,0.45), scale=1.5)

shop_ui = Entity(enabled=False)
shop_bg = Entity(parent=shop_ui, model='quad', color=color.rgba(0,0,0,180), scale=(0.6,0.4))
shop_text = Text(parent=shop_ui, text="", origin=(0,0), scale=2)

# =========================
# HELPERS
# =========================
def near_shop():
    return distance(tractor.position, shop.position) < 4

def get_tile():
    closest = None
    best = 999

    for t in fields:
        d = distance(tractor.position, t.position)
        if d < best:
            best = d
            closest = t

    return closest

# =========================
# TRACTOR PHYSICS
# =========================
def update_tractor():
    global velocity

    move = Vec3(
        held_keys['d'] - held_keys['a'],
        0,
        held_keys['w'] - held_keys['s']
    )

    if move.length() > 0:
        velocity += move.normalized() * acceleration * time.dt

    traction = 1
    if weather == "rain":
        traction = 0.55
    elif weather == "dry":
        traction = 0.85

    velocity *= (1 - friction * time.dt / traction)

    if velocity.length() > max_speed:
        velocity = velocity.normalized() * max_speed

    tractor.position += velocity * time.dt * 2

    if velocity.length() > 0.1:
        tractor.look_at(tractor.position + velocity)

# =========================
# FARM ACTIONS
# =========================
def farm(tile):
    global money

    if not tile:
        return

    if held_keys['e'] and tile.state == 0:
        tile.state = 1
        tile.set_visual()

    if held_keys['r'] and tile.state == 1 and inventory["seeds"] > 0:
        tile.state = 2
        tile.grow = 0
        tile.set_visual()
        inventory["seeds"] -= 1

    if held_keys['f'] and tile.state == 3:
        tile.state = 0
        tile.set_visual()
        money += random.randint(20,60)

# =========================
# SHOP SYSTEM
# =========================
def shop_system():
    global shop_open

    if near_shop() and held_keys['b']:
        shop_open = True
        shop_ui.enabled = True

    if shop_open:
        shop_text.text = "SHOP\n\n1 - Seeds (50$)\nESC - Close"

        if held_keys['1'] and money >= 50:
            money -= 50
            inventory["seeds"] += 10

        if held_keys['escape']:
            shop_open = False
            shop_ui.enabled = False

# =========================
# MAIN LOOP
# =========================
def update():
    global money

    update_weather()
    update_tractor()

    for t in fields:
        t.update_growth()

    tile = get_tile()
    farm(tile)

    shop_system()
    update_camera()

    hud.text = f"""
Money: {money}
Weather: {weather}
Seeds: {inventory['seeds']}
Speed: {round(velocity.length(),2)}

Controls:
WASD move | RMB camera | E plow | R seed | F harvest | B shop
"""

app.run()