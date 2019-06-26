import pygame as pg
import os
import random

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
    all_blocks = [dirt_block,
                  grass_block,
                  wood_block,
                  stone_block,
                  cobblestone_block,
                  glass_block,
                  log_block]

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

    # cracks
    cracks = [pg.image.load("crack_1.png").convert_alpha(),
              pg.image.load("crack_2.png").convert_alpha(),
              pg.image.load("crack_3.png").convert_alpha(),
              pg.image.load("crack_4.png").convert_alpha(),
              pg.image.load("crack_5.png").convert_alpha(),
              pg.image.load("crack_6.png").convert_alpha(),
              pg.image.load("crack_7.png").convert_alpha(),
              pg.image.load("crack_8.png").convert_alpha(),
              pg.image.load("crack_9.png").convert_alpha(),
              pg.image.load("crack_10.png").convert_alpha()]

    # ui and other
    transparent_mask = pg.image.load("transparent_mask.png").convert_alpha()
    heart = pg.image.load("heart.png").convert_alpha()
    dead_heart = pg.image.load("dead_heart.png").convert_alpha()
    inventory_slots = pg.image.load("inventory_slots.png").convert_alpha()
    slot_focus = pg.image.load("slot_focus.png").convert_alpha()

    # sounds
    walking_sound = ['grass1.ogg', 'grass2.ogg', 'grass3.ogg', 'grass4.ogg', 'grass5.ogg', 'grass6.ogg']
    placing_sound = pg.mixer.Sound('placing_sound.ogg')

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
            self.currently_breaked_block = None

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

            if self.wait_for_weapon > 0:
                self.wait_for_weapon -= 1

            if mouse_pressed[0] and self.currently_held[0] == 'Weapon':
                self.attack()

        def choose_slot(self):
            if keys[pg.K_1]:
                self.currently_held_num = 0
            elif keys[pg.K_2]:
                self.currently_held_num = 1
            elif keys[pg.K_3]:
                self.currently_held_num = 2
            elif keys[pg.K_4]:
                self.currently_held_num = 3
            elif keys[pg.K_5]:
                self.currently_held_num = 4
            elif keys[pg.K_6]:
                self.currently_held_num = 5
            elif keys[pg.K_7]:
                self.currently_held_num = 6
            elif keys[pg.K_8]:
                self.currently_held_num = 7
            elif keys[pg.K_9]:
                self.currently_held_num = 8
            if mouse_pressed[0] and mouse_y in range(880, 929):
                slot_counter = 0
                for i in range(734, 1180, 50):
                    if mouse_x in range(i, i + 50):
                        self.currently_held_num = slot_counter
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
            if self.y > height or self.x > width_of_map - 600 and not debug:
                self.alive = False

        def place_a_ghost_block(self):
            if self.currently_held[0] == 'Block' and self.currently_held[1] > 0:
                display.blit(transparent_mask, (mouse_x - (mouse_x - position_bias) % 40, mouse_y - mouse_y % 40))

        def break_a_block(self):
            if mouse_pressed[0]:
                for platform in platforms:
                    if mouse_x - position_bias - (mouse_x - position_bias) % 40 in range(platform.x, platform.x +
                            platform.width) and mouse_y - mouse_y % 40 in range(platform.y, platform.y +
                            platform.height) and platform.diggable:
                        if ((mouse_x - self.x - position_bias) ** 2 + (mouse_y - self.y) ** 2) < 40000:
                            platform.break_level -= 1
                            self.currently_breaked_block = platform
                            if platform.break_level == 0:
                                grabbables.append(Grabbable(platform.x, platform.y, platform.texture))
                                platforms.remove(platform)
                        else:
                            platform.break_level = platform.hardness * 50
                    else:
                        platform.break_level = platform.hardness * 50

        def place_a_block(self):
            if mouse_pressed[2] and self.currently_held[0] == 'Block' and self.currently_held[1] > 0 and \
                    ((mouse_x - self.x - position_bias) ** 2 + (mouse_y - self.y) ** 2) < 40000:
                for platform in platforms:
                    if mouse_x - position_bias - (mouse_x - position_bias) % 40 in range(platform.x, platform.x +
                        platform.width) and mouse_y - mouse_y % 40 in range(platform.y, platform.y + platform.height):
                        return 0
                platforms.append(Platform(mouse_x - position_bias, mouse_y, self.currently_held[2]))
                offset = int(platforms[-1].x - self.x), int(platforms[-1].y - self.y)
                if self.mask.overlap(pg.mask.from_surface(platforms[-1].texture), offset):
                    platforms.pop(-1)
                else:
                    self.currently_held[1] -= 1
                    placing_sound.play(0)

        def grab_grabbables(self):
            for grabbable in grabbables:
                offset = int(grabbable.x - self.x), int(grabbable.y - self.y)
                if self.mask.overlap(grabbable.mask, offset):
                    grabbable.effect()
                    grabbables.remove(grabbable)

        def attack(self):
            print('Hello zombie!')

        def collide_with_enemies(self):
            for enemy in enemies:
                offset = int(enemy.x - self.x), int(enemy.y - self.y)
                if enemy.mask.overlap(self.mask, offset) and enemy.alive and not debug:
                    self.alive = False

        def collide_with_platforms(self):
            for platform in platforms:
                if platform.x - 41 < self.x < platform.x + 81 and platform.y - 81 < self.y < platform.y + 121:
                    if (int(self.x) + self.width == platform.x or int(self.x) == platform.x + platform.width) and (self.y <
                            platform.y < int(self.y + self.height) or platform.y < int(self.y) < platform.y +
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

        def play_sounds(self):
            if (self.velx or self.vely) and self.on_platform:
                pg.mixer.music.load(walking_sound[random.randrange(len(walking_sound))])
                pg.mixer.music.play()

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

    player = Character(7220, 404)

    position_bias = -(player.x - 220) + 1000

    enemies = []

    class Platform(object):
        def __init__(self, x, y, texture=dirt_block, diggable=True):
            self.x = x - x % 40
            self.y = y - y % 40
            self.width = 40
            self.height = 40
            self.texture = texture
            self.diggable = diggable
            self.hardness = 1
            self.break_level = self.hardness * 50

        def draw(self):
            if self.texture:
                display.blit(self.texture, (self.x + position_bias, self.y))

    class Grabbable(object):
        def __init__(self, x, y, type):
            self.x = x
            self.y = y
            self.real_y = y
            self.type = type
            self.y_bias = 1
            self.bias_direction = 1
            self.mask = pg.mask.from_surface(self.type)
            if self.type in all_blocks:
                if self.type == grass_block:
                    self.type = dirt_block
                elif self.type == stone_block:
                    self.type = cobblestone_block
                self.width = 20
                self.height = 20
            else:
                self.width, self.height = self.type.get_rect().size

        def change_bias(self):
            if self.bias_direction == 1:
                self.y_bias += 0.3
                if self.y_bias > 20:
                    self.bias_direction *= -1
            else:
                self.y_bias -= 0.3
                if self.y_bias < 2:
                    self.bias_direction *= -1

        def effect(self):
            if self.type in all_blocks:
                for thing in player.inventory:
                    if self.type == thing[2]:
                        thing[1] += 1
                        return 0
                player.inventory.append(['Block', 1, self.type])

        def move(self):
            self.real_y += 1
            for platform in platforms:
                if self.real_y + self.height + 19 == platform.y and self.x in \
                        range(platform.x, platform.x + platform.width):
                    self.real_y -= 1
                    break
            self.y = self.real_y

        def draw(self):
            if self.x in range(int(player.x) - width, int(player.x) + width):
                if self.type in all_blocks:
                    display.blit(pg.transform.scale(self.type, (20, 20)),
                                 (self.x + position_bias + 10, self.y + self.y_bias))

    bullets = []

    platforms = []

    for x in range(0, 7000, 40):
        platforms.append(Platform(x, 720, grass_block))

    for x in range(0, 7000, 40):
        platforms.append(Platform(x, 760))

    for x in range(0, 8000, 40):
        for y in range(800, 961, 40):
            platforms.append(Platform(x, y, stone_block))

    for x in range(7000, 8000, 40):
        for y in range(440, 481, 40):
            platforms.append(Platform(x, y, stone_block, False))

    for x in range(7000, 8000, 40):
        for y in range(440, 481, 40):
            platforms.append(Platform(x, y, stone_block, False))

    for x in range(7080, 8000, 40):
        for y in range(360, 401, 40):
            platforms.append(Platform(x, y, stone_block, False))

    for x in range(7240, 8000, 40):
        for y in range(280, 321, 40):
            platforms.append(Platform(x, y, stone_block, False))

    for x in range(7320, 8000, 40):
        for y in range(0, 241, 40):
            platforms.append(Platform(x, y, stone_block, False))

    for x in range(7000, 8000, 40):
        for y in range(720, 761, 40):
            platforms.append(Platform(x, y))

    for y in range(0, 1000):
        platforms.append(Platform(-40, y, False))
        platforms.append(Platform(8000, y, False))

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

        place_cracks()

    def manage_health():
        this_x = 1135
        for i in range(10):
            if player.health > i:
                display.blit(heart, (this_x, 800))
            else:
                display.blit(dead_heart, (this_x, 800))
            this_x -= 45

    def place_cracks():
        for platform in platforms:
            if platform == player.currently_breaked_block:
                loop_number = 0
                for i in range(0, platform.hardness * 180, platform.hardness * 50 // 10):
                    if platform.break_level in range(i, i + platform.hardness * 50 // 10):
                        display.blit(cracks[9 - loop_number], (platform.x + position_bias, platform.y))
                        break
                    loop_number += 1

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

        if player.alive and player.health > 0:
            player.currently_breaked_block = None
            player.controls()
            player.move()
            player.move_screen()
            player.collide_with_enemies()
            player.grab_grabbables()
            player.choose_slot()
            player.break_a_block()
            player.play_sounds()
        else:
            death_scene()

        for enemy in enemies:
            if enemy.alive:
                enemy.move()
                enemy.collide_with_weapons()

        for grabbable in grabbables:
            grabbable.change_bias()
            grabbable.move()

        for bullet in bullets:
            bullet.move()

        redrawGameWindow()

        clock.tick(fp)
        fps += 1


gameLoop()
