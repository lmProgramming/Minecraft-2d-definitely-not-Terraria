import pygame as pg
import os

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 30)

pg.init()


def gameLoop():
    global position_bias

    # initializing
    width = 1800
    height = 1000
    pg.display.set_caption("Platform Space Simulator")
    clock = pg.time.Clock()
    display = pg.display.set_mode((width, height))
    done = False
    font = pg.font.SysFont('None', 32)
    width_of_map = 8000

    debug = True

    # background
    background = pg.image.load("background.png").convert_alpha()
    death_screen = pg.image.load("death_screen.png").convert_alpha()

    # blocks
    dirt_block = pg.image.load("dirt_block.png").convert_alpha()
    grass_block = pg.image.load("grass_block.png").convert_alpha()
    wood_block = pg.image.load("wood_block.png").convert_alpha()
    stone_block = pg.image.load("stone_block.png").convert_alpha()
    cobblestone_block = pg.image.load("cobblestone_block.png").convert_alpha()
    glass_block = pg.image.load("glass_block.png").convert_alpha()
    log_block = pg.image.load("log_block.png").convert_alpha()

    # decorations
    shadow_cave = pg.image.load("shadow_cave.png").convert_alpha()
    stone_wall = pg.image.load('stone_wall.png').convert_alpha()
    vine = pg.image.load("vine.png").convert_alpha()

    # weapon sprites
    weapon_sprite = pg.image.load("weapon.png").convert_alpha()
    bullet_sprite = pg.image.load("bullet.png").convert_alpha()

    # player sprite
    l1 = pg.image.load("l1.png").convert_alpha()
    r1 = pg.transform.flip(l1, True, False)

    # enemy sprite
    enemy_l1 = pg.image.load("enemy.png").convert_alpha()
    enemy_r1 = pg.transform.flip(enemy_l1, True, False)

    # some colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # ui and other
    transparent_mask = pg.image.load("transparent_mask.png").convert_alpha()
    heart = pg.image.load("heart.png").convert_alpha()
    dead_heart = pg.image.load("dead_heart.png").convert_alpha()
    inventory_slots = pg.image.load("inventory_slots.png").convert_alpha()
    slot_focus = pg.image.load("slot_focus.png").convert_alpha()

    # classes
    class Character(object):
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.sprite = r1
            self.width, self.height = self.sprite.get_rect().size
            self.velx = 0
            self.vely = 0
            self.jumped = False
            self.try_to_jump = False
            self.on_platform = False
            self.weapon_sprite = None
            self.wait_for_weapon = 0
            self.mask = pg.mask.from_surface(self.sprite)
            self.alive = True
            self.inventory = [['Block', 64, dirt_block],
                              ['Block', 64, wood_block],
                              ['Block', 64, cobblestone_block],
                              ['Block', 64, glass_block],
                              ['Block', 64, log_block]]
            self.currently_held_num = 0
            self.currently_held = self.inventory[self.currently_held_num]
            self.health = 10

        def controls(self):
            self.on_platform = False

            if keys[pg.K_LEFT] and not keys[pg.K_RIGHT]:
                if self.velx > 0:
                    self.velx -= 4 + abs(self.velx) ** 0.8
                else:
                    self.velx -= 4 - abs(self.velx) ** 0.8
                self.sprite = l1

            if keys[pg.K_RIGHT] and not keys[pg.K_LEFT]:
                if self.velx < 0:
                    self.velx += 4 + abs(self.velx) ** 0.8
                else:
                    self.velx += 4 - self.velx ** 0.8

                self.sprite = r1

            if not keys[pg.K_LEFT] and not keys[pg.K_RIGHT] and not self.jumped:
                self.velx *= 0.9
                if 1 > self.velx > -1:
                    self.velx = 0

            if keys[pg.K_UP] and not self.jumped:
                self.try_to_jump = True

            if keys[pg.K_SPACE] and not self.wait_for_weapon and self.weapon_sprite:
                if self.sprite == l1:
                    bullets.append(Bullet(self.x - 36, self.y + 46, -1))
                if self.sprite == r1:
                    bullets.append(Bullet(self.x + 105, self.y + 46, 1))
                self.wait_for_weapon = 10

            if self.wait_for_weapon > 0:
                self.wait_for_weapon -= 1

        def choose_slot(self):
            if keys[pg.K_1]:
                self.currently_held_num = 0
            if keys[pg.K_2]:
                self.currently_held_num = 1
            if keys[pg.K_3]:
                self.currently_held_num = 2
            if keys[pg.K_4]:
                self.currently_held_num = 3
            if keys[pg.K_5]:
                self.currently_held_num = 4
            if keys[pg.K_6]:
                self.currently_held_num = 5
            if keys[pg.K_7]:
                self.currently_held_num = 6
            if keys[pg.K_8]:
                self.currently_held_num = 7
            if keys[pg.K_9]:
                self.currently_held_num = 8
            if mouse_pressed[0] and mouse_y in range(880, 929):
                slot_counter = 0
                for i in range(734, 1180, 50):
                    if mouse_x in range(i, i + 50):
                        self.currently_held_num = slot_counter
                        print(self.currently_held_num)
                        break
                    slot_counter += 1
            try:
                self.currently_held = self.inventory[self.currently_held_num]
            except IndexError:
                self.currently_held = ['Nothing', 0, None]

        def move_screen(self):
            global position_bias
            if self.x > width // 2 and not (self.x > width_of_map - 600):
                position_bias -= int(self.velx)
            if position_bias > 0:
                position_bias = 0
            if self.y > height or self.x > width_of_map - 600:
                self.alive = False

        def place_a_ghost_block(self):
            if self.currently_held[0] == 'Block' and self.currently_held[1] > 0:
                display.blit(transparent_mask, (mouse_x - (mouse_x - position_bias) % 40, mouse_y - mouse_y % 40))

        def place_a_block(self):
            if mouse_pressed[2] and self.currently_held[0] == 'Block' and self.currently_held[1] > 0 and \
                    ((mouse_x - self.x - position_bias) ** 2 + (mouse_y - self.y) ** 2) ** 0.5 < 200:
                for platform in platforms:
                    if mouse_x - position_bias - (mouse_x - position_bias) % 40 in range(platform.x, platform.x +
                        platform.width) and mouse_y - mouse_y % 40 in range(platform.y, platform.y + platform.height):
                        return 0
                platforms.append(Platform(mouse_x - position_bias, mouse_y, 40, 40, self.currently_held[2]))
                self.currently_held[1] -= 1

        def grab_grabbables(self):
            for grabbable in grabbables:
                offset = int(grabbable.x - self.x), int(grabbable.y - self.y)
                if self.mask.overlap(grabbable.mask, offset) and not grabbable.grabbed:
                    grabbable.grabbed = True
                    self.weapon_sprite = grabbable.type

        def collide_with_enemies(self):
            for enemy in enemies:
                offset = int(enemy.x - self.x), int(enemy.y - self.y)
                if enemy.mask.overlap(self.mask, offset) and enemy.alive:
                    self.alive = False

        def collide_with_platforms(self):
            for platform in platforms:
                if (int(self.x) + self.width == platform.x or int(self.x) == platform.x + platform.width) and (self.y <
                        platform.y < int(self.y + self.height) or platform.y < int(self.y) < platform.y +
                        platform.height):
                    print('LOL')
                    self.velx = 0
                    if self.x < platform.x:
                        self.x -= 1
                    else:
                        self.x += 1

                if self.x + self.width > platform.x and self.x < platform.x + platform.width and int(self.y) == \
                        platform.y + platform.height:
                    self.vely *= -0.5
                    self.y += 1

                if platform.x - self.width < self.x < platform.x + platform.width and self.y <= platform.y \
                        <= self.y + self.height:
                    self.on_platform = True
                    self.jumped = False
                    self.vely = 0
                    self.y = platform.y - self.height
                    if self.try_to_jump and not self.jumped:
                        self.vely -= 15
                        self.y -= 1
                        self.jumped = True
                        self.try_to_jump = False

        def move(self):
            if abs(self.velx) > abs(self.vely):
                higher_num = self.velx
                try:
                    lower_num = self.vely / abs(self.velx) + 0.01
                except ZeroDivisionError:
                    lower_num = 0
            else:
                higher_num = self.vely
                try:
                    lower_num = self.velx / abs(self.vely) + 0.01
                except ZeroDivisionError:
                    lower_num = 0

            if self.velx == higher_num:
                for i in range(abs(int(higher_num))):
                    if self.velx > 0:
                        self.x += 1
                    else:
                        self.x -= 1
                    self.y += lower_num
                    self.collide_with_platforms()
            else:
                for i in range(abs(int(higher_num))):
                    if self.vely > 0:
                        self.y += 1
                    else:
                        self.y -= 1
                    self.x += lower_num
                    self.collide_with_platforms()

            self.collide_with_platforms()

            if not self.on_platform:
                self.vely += 0.5

        def draw(self):
            display.blit(self.sprite, (self.x + position_bias, self.y))
            if self.sprite == l1 and self.weapon_sprite:
                display.blit(pg.transform.flip(weapon_sprite, True, False), (self.x - 36 + position_bias, self.y + 40))
            elif self.weapon_sprite:
                display.blit(self.weapon_sprite, (self.x + position_bias, self.y + 40))

    class Enemy(object):
        def __init__(self, x, y, start_x, end_x):
            self.x = x
            self.y = y
            self.start_x = start_x
            self.end_x = end_x
            self.sprite = enemy_r1
            self.width, self.height = self.sprite.get_rect().size
            self.velx = 0
            self.vely = 0
            self.on_platform = False
            self.direction = 1
            self.mask = pg.mask.from_surface(self.sprite)
            self.alive = True

        def collide_with_platforms(self):
            for platform in platforms:
                if (int(self.x) + self.width == platform.x or int(self.x) == platform.x + platform.width) and \
                        (self.y <= platform.y <= self.y + self.height or platform.y <= self.y <= platform.y +
                         platform.height):
                    self.velx = 0
                    if self.x < platform.x:
                        self.x -= 1
                    else:
                        self.x += 1

                if self.x + self.width > platform.x and self.x < platform.x + platform.width and int(self.y) == \
                        platform.y + platform.height:
                    self.vely *= -0.5
                    self.y += 1

                elif self.x + self.width > platform.x and self.x < platform.x + platform.width and self.y <= platform.y \
                        <= self.y + self.height:
                    self.vely = 0
                    self.y = platform.y - self.height

        def collide_with_weapons(self):
            i = 0
            for bullet in bullets:
                offset = int(self.x - bullet.x), int(self.y - bullet.y)
                if bullet.mask.overlap(self.mask, offset):
                    self.alive = False
                    bullets.pop(i)
                i += 1

        def move(self):
            if self.x + self.width > self.end_x or self.direction == -1:
                if self.velx > 0:
                    self.velx -= 2 + abs(self.velx) ** 0.8
                else:
                    self.velx -= 2 - abs(self.velx) ** 0.8
                self.sprite = enemy_l1
                self.direction = -1

            if self.x < self.start_x or self.direction == 1:
                if self.velx < 0:
                    self.velx += 2 + abs(self.velx) ** 0.8
                else:
                    self.velx += 2 - self.velx ** 0.8
                self.direction = 1
                self.sprite = enemy_r1

            if abs(self.velx) > abs(self.vely):
                higher_num = self.velx
                try:
                    lower_num = self.vely / abs(self.velx)
                except ZeroDivisionError:
                    lower_num = 0
            else:
                higher_num = self.vely
                try:
                    lower_num = self.velx / abs(self.vely)
                except ZeroDivisionError:
                    lower_num = 0

            if self.velx == higher_num:
                for i in range(abs(int(higher_num))):
                    if self.velx > 0:
                        self.x += 1
                    else:
                        self.x -= 1
                    self.y += lower_num
                    self.collide_with_platforms()
            else:
                for i in range(abs(int(higher_num))):
                    if self.vely > 0:
                        self.y += 1
                    else:
                        self.y -= 1
                    self.x += lower_num
                    self.collide_with_platforms()

            self.collide_with_platforms()

            if not self.on_platform:
                self.vely += 0.5

        def draw(self):
            display.blit(self.sprite, (self.x + position_bias, self.y))

    player = Character(220, 404)

    position_bias = -(player.x - 220)

    enemies = []

    class Platform(object):
        def __init__(self, x, y, width, height, texture=dirt_block, collisions=True):
            self.x = x - x % 40
            self.y = y - y % 40
            self.width = width
            self.height = height
            self.color = WHITE
            self.texture = texture
            self.collistions = collisions
            if self.texture:
                self.blocks_x = 0
                self.blocks_y = 0
                for i in range(0, self.width, 40):
                    self.blocks_x += 1
                for i in range(0, self.height, 40):
                    self.blocks_y += 1

        def draw(self):
            if self.texture:
                for y in range(self.blocks_y):
                    for x in range(self.blocks_x):
                        if self.texture == grass_block and y > 0:
                            if x in range(int(player.x - width + position_bias), int(player.x + width + position_bias)):
                                display.blit(dirt_block, (self.x + x * 40 + position_bias, self.y + y * 40))
                        else:
                            if x in range(int(player.x - width + position_bias), int(player.x + width + position_bias)):
                                display.blit(self.texture, (self.x + x * 40 + position_bias, self.y + y * 40))

    class Bullet(object):
        def __init__(self, x, y, direction):
            self.x = x
            self.y = y
            self.vely = 0
            if direction == 1:
                self.sprite = bullet_sprite
                self.velx = 10
            else:
                self.sprite = pg.transform.flip(bullet_sprite, True, False)
                self.velx = -10
            self.width, self.height = bullet_sprite.get_rect().size
            self.mask = pg.mask.from_surface(self.sprite)

        def move(self):
            self.x += self.velx
            self.y += self.vely

        def draw(self):
            if self.x in range(player.x - width, player.x + width):
                display.blit(self.sprite, (self.x + position_bias, self.y))

    class Grabbable(object):
        def __init__(self, x, y, type):
            self.x = x
            self.y = y
            self.type = type
            self.y_bias = 1
            self.bias_direction = 1
            self.grabbed = False
            self.mask = pg.mask.from_surface(self.type)

        def change_bias(self):
            if self.bias_direction == 1:
                self.y_bias += 0.4
                if self.y_bias > 20:
                    self.bias_direction *= -1
            else:
                self.y_bias -= 0.4
                if self.y_bias < 2:
                    self.bias_direction *= -1

        def draw(self):
            if self.x in range(player.x - width, player.x + width):
                display.blit(self.type, (self.x + position_bias, self.y + self.y_bias))

    bullets = []

    platforms = [Platform(0, 0, 1, height, False),
                 Platform(0, 720, 7000, 400, grass_block),
                 Platform(7998, 0, 2, height, False),

                 # cave
                 Platform(6960, 480, 1540, 40, stone_block),
                 Platform(7000, 440, 1460, 40, stone_block),
                 Platform(7080, 360, 1380, 80, stone_block),
                 Platform(7120, 320, 80, 40, stone_block),
                 Platform(7240, 280, 1300, 80, stone_block),
                 Platform(7320, 0, 1200, 280, stone_block),
                 Platform(7000, 720, 1500, 400)]

    decorations = [[shadow_cave, 7000, 520, True],
                   [stone_wall, 7000, 520, False],
                   [vine, 7320, 0, True],
                   [vine, 7320, 40, True],
                   [vine, 7320, 80, True],
                   [vine, 7320, 120, True],
                   [vine, 7320, 160, True],
                   [vine, 7320, 200, True],
                   [vine, 7320, 240, True]]

    grabbables = []

    def ui():
        display.blit(font.render(str(int(clock.get_fps())), True, pg.Color('white')), (20, 20))

        manage_health()

        display.blit(inventory_slots, (729, 880))

        manage_ui_inventory()

    def manage_health():
        this_x = 1135
        for i in range(10):
            if player.health > i:
                display.blit(heart, (this_x, 800))
            else:
                display.blit(dead_heart, (this_x, 800))
            this_x -= 45

    def manage_ui_inventory():
        t = 0
        for i in player.inventory:
            display.blit(i[2], (734 + t * 50, 885))
            display.blit(font.render(str(i[1]), True, pg.Color('white')), (750 + t * 50, 908))
            t += 1
        display.blit(slot_focus, (729 + player.currently_held_num * 50, 880))

    def death_scene():
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()

            keys = pg.key.get_pressed()
            mouse_pressed = pg.mouse.get_pressed()
            x, y = pg.mouse.get_pos()

            if keys[pg.K_ESCAPE]:
                exit()

            if keys[pg.K_r]:
                restart()

            redrawGameWindow()

    def restart():
        gameLoop()
        exit()

    def redrawGameWindow():
        display.blit(background, (0, 0))

        for decor in decorations:
            if not decor[3]:
                display.blit(decor[0], (decor[1] + position_bias, decor[2]))

        if player.alive:
            player.draw()

        for enemy in enemies:
            if enemy.alive:
                enemy.draw()

        for bullet in bullets:
            bullet.draw()

        for grabbable in grabbables:
            if not grabbable.grabbed:
                grabbable.draw()

        for platform in platforms:
            platform.draw()

        for decor in decorations:
            if decor[3]:
                display.blit(decor[0], (decor[1] + position_bias, decor[2]))

        player.place_a_ghost_block()

        ui()

        if not player.alive:
            display.blit(death_screen, (0, 0))

        pg.display.update()

    fps = 0

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
                exit()
            if event.type == pg.MOUSEBUTTONUP:
                if player.alive:
                    player.place_a_block()

        keys = pg.key.get_pressed()
        mouse_pressed = pg.mouse.get_pressed()
        mouse_x, mouse_y = pg.mouse.get_pos()

        if keys[pg.K_f] and debug:
            fp = 1000
            print('START')
            for platform in platforms:
                print('Platform(', platform.x, ',', platform.y, ',', platform.width, ',', platform.height, '),')
            print('END')
        else:
            fp = 60

        if keys[pg.K_ESCAPE]:
            done = True

        if keys[pg.K_r]:
            restart()

        if player.alive:
            player.controls()
            player.move()
            player.move_screen()
            player.collide_with_enemies()
            player.grab_grabbables()
            player.choose_slot()
        else:
            death_scene()

        for enemy in enemies:
            if enemy.alive:
                enemy.move()
                enemy.collide_with_weapons()

        for grabbable in grabbables:
            if not grabbable.grabbed:
                grabbable.change_bias()

        for bullet in bullets:
            bullet.move()

        redrawGameWindow()

        clock.tick(fp)
        fps += 1


gameLoop()
