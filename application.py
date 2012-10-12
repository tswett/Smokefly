# Copyright 2012 by Tanner Swett.
#
# This file is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division

import math
import random
import sys

import pygame

BLACK = 0, 0, 0
WHITE = 255, 255, 255

ASPHALT_COLOR = 128, 128, 128
PLAYER_COLOR = 255, 255, 0

VIEW_SIZE = VIEW_WIDTH, VIEW_HEIGHT = 640, 640
TILE_SIZE = TILE_WIDTH, TILE_HEIGHT = 32, 32

FRAMERATE = 50

ASPHALT_FREQUENCY = 0.05

class Menu:
    def __init__(self):
        self.screen = None
        self.items = None
        self.bg_color = BLACK
        self.fg_color = WHITE
        self.font_name = 'courier new'
        self.x_margin = 20
        self.y_margin = 20
        self.y_spacing = 20
        self.arrow_x = -10
        self.arrow_y = 0
        self.arrow_height = 10

    def display(self):
        self.screen.fill(self.bg_color)

        print 'Loading fonts...'
        menu_font = pygame.font.SysFont(self.font_name, 14)
        print 'Done loading fonts'

        for item_num, item in enumerate(self.items):
            text = menu_font.render(item[0], True, self.fg_color, self.bg_color)
            location = (self.x_margin, self.y_margin + item_num * self.y_spacing)
            self.screen.blit(text, location)

        menu_pos = 0

        def arrow(item_num):
            arrow_1 = (self.x_margin + self.arrow_x,
                       self.y_margin + self.arrow_y + item_num*self.y_spacing)

            arrow_2 = (self.x_margin + self.arrow_x + self.arrow_height // 2,
                       self.y_margin + self.arrow_y + self.arrow_height // 2 + item_num*self.y_spacing)

            arrow_3 = (self.x_margin + self.arrow_x,
                       self.y_margin + self.arrow_y + self.arrow_height + item_num*self.y_spacing)

            return [arrow_1, arrow_2, arrow_3]

        while True:
            # Erase all arrows that should be invisible
            for item_num in range(len(self.items)):
                if item_num != menu_pos:
                    pygame.draw.polygon(self.screen, self.bg_color, arrow(item_num))

            pygame.draw.polygon(self.screen, self.fg_color, arrow(menu_pos))
            pygame.display.update()

            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    menu_pos = (menu_pos + 1) % len(self.items)
                elif event.key == pygame.K_UP:
                    menu_pos = (menu_pos - 1) % len(self.items)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    return self.items[menu_pos][1]

            # TODO: Make this while loop less horrible.

class Application:
    # My instances represent instances of the application itself.

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Smokefly')
        self.screen = pygame.display.set_mode(VIEW_SIZE)

        self.main_menu()

    def main_menu(self):
        init_menu = Menu()
        init_menu.screen = self.screen
        init_menu.items = [('New Game', 'new_game'), ('Quit', 'quit')]

        cont_menu = Menu()
        cont_menu.screen = self.screen
        cont_menu.items = [('New Game', 'new_game'), ('Continue', 'continue'), ('Quit', 'quit')]

        option = init_menu.display()

        while True:
            print 'Menu option chosen:', option

            if option == 'new_game':
                self.session = Session()
                self.session.play(self.screen)
            elif option == 'continue':
                self.session.play(self.screen)
            elif option == 'quit':
                return

            option = cont_menu.display()

class Ambiance:
    # My instances contain the data associated with a particular landscape cell.
    # TODO: use a deterministic PRNG and store the seed instead of its output

    def __init__(self):
        self.lushness = random.random()
        self.asphalt = random.random() < ASPHALT_FREQUENCY
        self.paved = False

class Landscape:
    # My instances are landscapes or "maps" within a Smokefly universe.

    def __init__(self):
        self.ambiance = {}

    def get_ambiance(self, spot):
        if spot in self.ambiance:
            return self.ambiance[spot]
        elif (type(spot) != tuple or len(spot) != 2):
            raise KeyError
        else:
            ambiance = self.ambiance[spot] = Ambiance()
            return ambiance

    def get_lushness(self, spot):
        return self.get_ambiance(spot).lushness

    def get_has_asphalt(self, spot):
        return self.get_ambiance(spot).asphalt

    def set_has_asphalt(self, spot, val):
        self.get_ambiance(spot).asphalt = val

    def get_is_paved(self, spot):
        return self.get_ambiance(spot).paved

    def set_is_paved(self, spot, val):
        self.get_ambiance(spot).paved = val

    def try_take_asphalt(self, spot):
        took_asphalt = self.get_has_asphalt(spot)
        self.set_has_asphalt(spot, False)
        return took_asphalt

class Session:
    # My instances are instances of the game itself.  Conceptually, a "saved
    # game" consists of one Session.

    def __init__(self):
        self.scape = Landscape()
        self.port = Viewport(self.scape, TILE_WIDTH, TILE_HEIGHT, VIEW_WIDTH, VIEW_HEIGHT)

        # player_x and player_y are measured in tiles.
        self.player_x, self.player_y = 0, 0
        self.asphalt = 0

        self.frame_number = 0

    def tick(self, force_draw = False):
        # Returns True if the user has pressed escape.

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
                # TODO: this doesn't belong here

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            return True

        old_x, old_y = self.get_player()
        old_tile = int(math.floor(old_x)), int(math.floor(old_y))

        move_x, move_y = 0, 0

        if self.scape.get_is_paved(old_tile):
            speed = 1/4
        else:
            speed = 1/16

        if keys[pygame.K_RIGHT]:
            move_x = move_x + speed
        if keys[pygame.K_LEFT]:
            move_x = move_x - speed
        if keys[pygame.K_UP]:
            move_y = move_y - speed
        if keys[pygame.K_DOWN]:
            move_y = move_y + speed

        new_x, new_y = self.move_player_by(move_x, move_y)
        new_tile = int(math.floor(new_x)), int(math.floor(new_y))

        got_asphalt = self.scape.try_take_asphalt(new_tile)
        if got_asphalt:
            self.asphalt += 1
            print 'Got asphalt; now have', self.asphalt

        if keys[pygame.K_SPACE] and self.asphalt > 0 and not self.scape.get_is_paved(new_tile):
            self.asphalt -= 1
            self.scape.set_is_paved(new_tile, True)
            print 'Used asphalt; now have', self.asphalt

        return False

        # In fact, this class really shouldn't handle key presses at all.

    def move_player_by(self, dx, dy):
        self.player_x += dx
        self.player_y += dy
        return self.player_x, self.player_y

    def get_player(self):
        return self.player_x, self.player_y

    def play(self, screen):
        port = Viewport(self.scape, TILE_WIDTH, TILE_HEIGHT, VIEW_WIDTH, VIEW_HEIGHT)

        clock = pygame.time.Clock()

        while True:
            self.frame_number += 1

            port.center_on(self.player_x, self.player_y)
            port.draw_on(screen)
            if self.tick(): # if the user has pressed escape:
                return

            clock.tick(FRAMERATE)
            if self.frame_number % FRAMERATE == 0: # in other words, once per (nominal) second
                print 'FPS:', clock.get_fps()

class Viewport:
    # My instances represent rectangular regions within Landscapes.

    def __init__(self, landscape, tile_width, tile_height, width, height):
        self.scape = landscape
        self.tile_width, self.tile_height = tile_width, tile_height
        self.width, self.height = width, height
        self.x, self.y = 0, 0
            # x and y are the center of the viewport (measured in pixels)

    def get_pos(self):
        return self.x, self.y

    def set_pos(self, x, y):
        self.x, self.y = int(x), int(y)

    def move_by(self, move_x, move_y):
        x, y = self.get_pos()
        self.set_pos(x + move_x, y + move_y)

    def center_on(self, px_x, px_y):
        self.set_pos(px_x * TILE_WIDTH, px_y * TILE_HEIGHT)

    def visible_landscape_squares(self):
        # Return a list of all landscape squares visible in the viewport.  A
        # landscape tile with integer coordinate x is considered to cover the
        # real coordinates [x, x+1).

        # Convert our dimensions from pixels to landscape coordinates
        coord_width, coord_height = self.width / self.tile_width, self.height / self.tile_height
        coord_x, coord_y = self.x / self.tile_width, self.y / self.tile_height

        # Find the landscape tiles that our bounding box falls on
        coord_left = int(math.floor(coord_x - coord_width / 2))
        coord_right = int(math.floor(coord_x + coord_width / 2))
        coord_top = int(math.floor(coord_y - coord_height / 2))
        coord_bottom = int(math.floor(coord_y + coord_height / 2))

        # Return all the tiles from coord_left to coord_right inclusive
        return [(x,y) for x in range(coord_left, coord_right+1) for y in range(coord_top, coord_bottom+1)]

    def draw_on(self, screen):
        tiles = self.visible_landscape_squares()

        center = center_x, center_y = self.width // 2, self.height // 2

        for tile in tiles:
            x, y = tile

            tile_left = self.tile_width * x - self.x + center_x
            tile_top = self.tile_height * y - self.y + center_y

            if self.scape.get_is_paved(tile):
                tile_color = ASPHALT_COLOR
            else:
                tile_color = (0, 255*self.scape.get_lushness(tile), 0)

            tile_dims = (tile_left, tile_top, self.tile_width, self.tile_height)

            pygame.draw.rect(screen, tile_color, tile_dims)

            if self.scape.get_has_asphalt((x, y)):
                tile_center = (self.tile_width * x - self.x + (self.tile_width // 2) + center_x,
                               self.tile_height * y - self.y + (self.tile_height // 2) + center_y)

                pygame.draw.circle(screen, BLACK, tile_center, self.tile_width // 5 + 1, 0)
                pygame.draw.circle(screen, ASPHALT_COLOR, tile_center, self.tile_width // 5, 0)

        pygame.draw.circle(screen, BLACK, center, self.tile_width // 3 + 1, 0)
        pygame.draw.circle(screen, PLAYER_COLOR, center, self.tile_width // 3, 0)

        pygame.display.update()
            # It really seems like pygame.display ought to be connected to the screen somehow.

#   def get_scape(self):
#       return self.scape
