from __future__ import division

import math
import random
import sys

import pygame

BLACK = 0, 0, 0
WHITE = 255, 255, 255

VIEW_SIZE = VIEW_WIDTH, VIEW_HEIGHT = 640, 480
TILE_SIZE = TILE_WIDTH, TILE_HEIGHT = 32, 32

def menu(screen, items, bg_color=BLACK, fg_color=WHITE, font_name='courier new', x_margin=20, y_margin=20, y_spacing=20, arrow_x=-10, arrow_y=0, arrow_height=10):
    screen.fill(bg_color)

    print 'Loading fonts...'
    menu_font = pygame.font.SysFont(font_name, 14)
    print 'Done loading fonts'

    for item_num, item in enumerate(items):
        screen.blit(menu_font.render(item[0], True, fg_color, bg_color), (x_margin, y_margin + item_num * y_spacing))

    menu_pos = 0

    def arrow(item_num):
        arrow_1 = (x_margin + arrow_x,                     y_margin + arrow_y +                     item_num*y_spacing)
        arrow_2 = (x_margin + arrow_x + arrow_height // 2, y_margin + arrow_y + arrow_height // 2 + item_num*y_spacing)
        arrow_3 = (x_margin + arrow_x,                     y_margin + arrow_y + arrow_height      + item_num*y_spacing)
        return [arrow_1, arrow_2, arrow_3]

    while True:
        for item_num in range(len(items)):
            if item_num != menu_pos:
                pygame.draw.polygon(screen, bg_color, arrow(item_num))

        pygame.draw.polygon(screen, fg_color, arrow(menu_pos))
        pygame.display.update()

        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                menu_pos = (menu_pos + 1) % len(items)
            elif event.key == pygame.K_UP:
                menu_pos = (menu_pos - 1) % len(items)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                items[menu_pos][1]()

        # TODO: Make this while loop less horrible.

class Application:
    # My instances represent instances of the application itself.

    def __init__(self):
        self.session = Session()

        pygame.init()
        pygame.display.set_caption('Smokefly')
        self.screen = pygame.display.set_mode(VIEW_SIZE)

        self.main_menu()

    def main_menu(self):
        menu(self.screen,
            [('Play', lambda: self.session.main_interface(self.screen)),
                ('Exit', sys.exit)])

class Landscape:
    # My instances are landscapes or "maps" within a Smokefly universe.
    # TODO: use a deterministic PRNG and store the seed instead of its output

    def __init__(self):
        self.lushness = {}

    def get_lushness(self, spot):
        if spot in self.lushness:
            return self.lushness[spot]
        elif (type(spot) != tuple or len(spot) != 2):
            raise KeyError
        else:
            self.lushness[spot] = random.random()
            return self.lushness[spot]

class Session:
    # My instances are instances of the game itself.  Conceptually, a "saved
    # game" consists of one Session.

    def __init__(self):
        self.scape = Landscape()
        self.port = Viewport(self.scape, TILE_WIDTH, TILE_HEIGHT, VIEW_WIDTH, VIEW_HEIGHT)

        self.player_x, self.player_y = 0, 0

    def tick(self, force_draw = False):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
                # TODO: this doesn't belong here

        keys = pygame.key.get_pressed()
        move_x, move_y = 0, 0

        if keys[pygame.K_RIGHT]:
            move_x = move_x + 5
        if keys[pygame.K_LEFT]:
            move_x = move_x - 5
        if keys[pygame.K_UP]:
            move_y = move_y - 5
        if keys[pygame.K_DOWN]:
            move_y = move_y + 5

        self.move_player(move_x, move_y)

        # In fact, this class really shouldn't handle key presses at all.

    def get_landscape(self):
        return self.scape

    def move_player(self, dx, dy):
        self.player_x += dx
        self.player_y += dy

    def get_player(self):
        return self.player_x, self.player_y

    def main_interface(self, screen):
        port = Viewport(self.scape, TILE_WIDTH, TILE_HEIGHT, VIEW_WIDTH, VIEW_HEIGHT)

        while 1:
            port.center_on(self.player_x, self.player_y)
            port.draw_on(screen)
            self.tick()
            pygame.time.wait(50)

class Viewport:
    # My instances represent rectangular regions within Landscapes.

    def __init__(self, landscape, tile_width, tile_height, width, height):
        self.scape = landscape
        self.tile_width, self.tile_height = tile_width, tile_height
        self.width, self.height = width, height
        self.x, self.y = 0, 0
            # x and y are the center of the viewport

    def get_pos(self):
        return self.x, self.y

    def set_pos(self, x, y):
        self.x, self.y = x, y

    def move(self, move_x, move_y):
        self.x, self.y = self.x + move_x, self.y + move_y

    def visible_landscape_squares(self):
        # Return a list of all landscape squares visible in the viewport.  A
        # landscape tile with integer coordinate x is considered to cover the
        # real coordinates [x, x+1).

        coord_width, coord_height = self.width / self.tile_width, self.height / self.tile_height
        coord_x, coord_y = self.x / self.tile_width, self.y / self.tile_height

        coord_left = int(math.floor(coord_x - coord_width / 2))
        coord_right = int(math.floor(coord_x + coord_width / 2))
        coord_top = int(math.floor(coord_y - coord_height / 2))
        coord_bottom = int(math.floor(coord_y + coord_height / 2))

        return [(x,y) for x in range(coord_left, coord_right+1) for y in range(coord_top, coord_bottom+1)]

    def draw_on(self, screen):
        tiles = self.visible_landscape_squares()

        for (x, y) in tiles:
            tile_left, tile_top = TILE_WIDTH * x - self.x + (VIEW_WIDTH // 2), TILE_HEIGHT * y - self.y + (VIEW_HEIGHT // 2)
            pygame.draw.rect(screen, (0, 255*self.scape.get_lushness((x, y)), 0), (tile_left, tile_top, TILE_WIDTH, TILE_HEIGHT))

        pygame.display.update()
            # It really seems like pygame.display ought to be connected to the screen somehow.

    def center_on(self, x, y):
        self.x, self.y = x, y

#   def get_scape(self):
#       return self.scape
