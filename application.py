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
import yaml

BLACK = 0, 0, 0
WHITE = 255, 255, 255

ASPHALT_COLOR = 128, 128, 128
PLAYER_COLOR = 255, 255, 0

ASPHALT_RADIUS = 6
PLAYER_RADIUS = 10

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 960, 640
VIEW_SIZE = VIEW_WIDTH, VIEW_HEIGHT = 640, 640
TILE_SIZE = TILE_WIDTH, TILE_HEIGHT = 32, 32

FRAMERATE = 50

ASPHALT_FREQUENCY = 0.05

class DisplayList:
    def __init__(self):
        self.surface = None
        self.items = None
        self.bg_color = BLACK
        self.fg_color = WHITE
        self.font_name = 'courier new'
        self.x_margin = 20
        self.y_margin = 20
        self.y_spacing = 20

        print 'Loading fonts...'
        self.font = pygame.font.SysFont(self.font_name, 14)
        print 'Done loading fonts'

    def draw(self):
        # Draw yourself on the surface, possibly for the first time.

        self.surface.fill(self.bg_color)

        for item_num, item in enumerate(self.items):
            text = self.font.render(item[0], True, self.fg_color, self.bg_color)
            location = (self.x_margin, self.y_margin + item_num * self.y_spacing)
            self.surface.blit(text, location)

        self.redraw()

    def redraw(self):
        # Draw yourself on the surface, assuming that you have already been drawn there.

        pass

class Menu(DisplayList):
    def __init__(self):
        DisplayList.__init__(self)

        self.arrow_x = -10
        self.arrow_y = 0
        self.arrow_height = 10

        self.menu_pos = 0

    def redraw(self):
        DisplayList.redraw(self)

        def arrow(item_num):
            arrow_1 = (self.x_margin + self.arrow_x,
                       self.y_margin + self.arrow_y + item_num*self.y_spacing)

            arrow_2 = (self.x_margin + self.arrow_x + self.arrow_height // 2,
                       self.y_margin + self.arrow_y + self.arrow_height // 2 + item_num*self.y_spacing)

            arrow_3 = (self.x_margin + self.arrow_x,
                       self.y_margin + self.arrow_y + self.arrow_height + item_num*self.y_spacing)

            return [arrow_1, arrow_2, arrow_3]

        # Erase all arrows that should be invisible
        for item_num in range(len(self.items)):
            if item_num != self.menu_pos:
                pygame.draw.polygon(self.surface, self.bg_color, arrow(item_num))

        pygame.draw.polygon(self.surface, self.fg_color, arrow(self.menu_pos))

    def display(self):
        self.draw()
        pygame.display.update()

        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.menu_pos = (self.menu_pos + 1) % len(self.items)
                elif event.key == pygame.K_UP:
                    self.menu_pos = (self.menu_pos - 1) % len(self.items)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    return self.items[self.menu_pos][1]

            self.redraw()
            pygame.display.update()

            # TODO: Make this while loop less horrible.

class Application:
    # My instances represent instances of the application itself.

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Smokefly')

        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.session = None

        self.main_menu()

    def main_menu(self):
        init_menu = Menu()
        init_menu.surface = self.screen
        init_menu.items = [('New Game', 'new_game'), ('Load Game', 'load_game'), ('Quit', 'quit')]

        cont_menu = Menu()
        cont_menu.surface = self.screen
        cont_menu.items = [('New Game', 'new_game'), ('Load Game', 'load_game'), ('Save Game', 'save_game'), ('Continue', 'continue'), ('Quit', 'quit')]

        while True:
            if self.session:
                option = cont_menu.display()
            else:
                option = init_menu.display()

            print 'Menu option chosen:', option

            if option == 'new_game':
                self.session = Session()
                self.session.play(self.screen)

            elif option == 'load_game':
                print 'Loading saved games from an untrusted source may damage your computer.'
                print 'Enter path:'
                path = raw_input()

                try:
                    loadee = yaml.load(file(path, 'r'))
                except:
                    print 'Load error'
                else:
                    if isinstance(loadee, Session):
                        print 'Load successful'
                        self.session = loadee
                        self.session.play(self.screen)
                    else:
                        print 'Document loaded is not a Session'

            elif option == 'save_game':
                print 'Enter path:'
                path = raw_input()

                try:
                    yaml.dump(self.session, file(path, 'w+'))
                except:
                    print 'Save error'
                else:
                    print 'Save successful'

            elif option == 'continue':
                self.session.play(self.screen)

            elif option == 'quit':
                return

class Ambiance(yaml.YAMLObject):
    # My instances contain the data associated with a particular landscape cell.
    # TODO: use a deterministic PRNG and store the seed instead of its output

    def __init__(self):
        self.lushness = random.random()
        self.asphalt = random.random() < ASPHALT_FREQUENCY
        self.paved = False

class Landscape(yaml.YAMLObject):
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

class Session(yaml.YAMLObject):
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

        if keys[pygame.K_q] and self.asphalt > 0 and not self.scape.get_is_paved(new_tile):
            self.asphalt -= 1
            self.scape.set_is_paved(new_tile, True)

        return False

        # In fact, this class really shouldn't handle key presses at all.

    def move_player_by(self, dx, dy):
        self.player_x += dx
        self.player_y += dy
        return self.player_x, self.player_y

    def get_player(self):
        return self.player_x, self.player_y

    def play(self, screen):
        viewarea = screen.subsurface((0, 0) + VIEW_SIZE)
        statusarea = screen.subsurface((VIEW_WIDTH, 0, SCREEN_WIDTH - VIEW_WIDTH, VIEW_HEIGHT))

        port = Viewport(self.scape, TILE_WIDTH, TILE_HEIGHT, VIEW_WIDTH, VIEW_HEIGHT)

        statuslist = DisplayList()
        statuslist.surface = statusarea
        statuslist.items = [('', None), ('', None)]

        clock = pygame.time.Clock()

        while True:
            self.frame_number += 1

            clock.tick(FRAMERATE)

            port.center_on(self.player_x, self.player_y)
            port.draw_on(viewarea)

            statuslist.items[0] = ('FPS: ' + str(int(math.floor(clock.get_fps()))), None)
            statuslist.items[1] = ('Asphalt: ' + str(self.asphalt), None)
            statuslist.draw()

            pygame.display.update()

            if self.tick(): # if the user has pressed escape:
                return

class Viewport(yaml.YAMLObject):
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

    def draw_on(self, surface):
        tiles = self.visible_landscape_squares()

        center = center_x, center_y = self.width // 2, self.height // 2

        for tile in tiles:
            x, y = tile

            tile_left = self.tile_width * x - self.x + center_x
            tile_top = self.tile_height * y - self.y + center_y

            if self.scape.get_is_paved(tile):
                tile_color = ASPHALT_COLOR
            else:
                lushness = self.scape.get_lushness(tile)
                tile_color = (64 - 64*lushness, 64 + 128*lushness, 32)

            tile_dims = (tile_left, tile_top, self.tile_width, self.tile_height)

            pygame.draw.rect(surface, tile_color, tile_dims)

            if self.scape.get_has_asphalt((x, y)):
                tile_center = (self.tile_width * x - self.x + (self.tile_width // 2) + center_x,
                               self.tile_height * y - self.y + (self.tile_height // 2) + center_y)

                pygame.draw.circle(surface, BLACK, tile_center, ASPHALT_RADIUS + 1, 0)
                pygame.draw.circle(surface, ASPHALT_COLOR, tile_center, ASPHALT_RADIUS, 0)

        pygame.draw.circle(surface, BLACK, center, PLAYER_RADIUS + 1, 0)
        pygame.draw.circle(surface, PLAYER_COLOR, center, PLAYER_RADIUS, 0)

#   def get_scape(self):
#       return self.scape
