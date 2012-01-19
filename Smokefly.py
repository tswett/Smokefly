#!/usr/bin/env python

# Copyright © 2011-2012 by Tanner Swett.  All rights reserved.
# This file may be redistributed and used according to the BSD 2-clause license,
# as it appears in the file COPYING.

from __future__ import division

import math
import random
import sys

import pygame

BLACK = 0, 0, 0
VIEW_SIZE = VIEW_WIDTH, VIEW_HEIGHT = 640, 480
TILE_SIZE = TILE_WIDTH, TILE_HEIGHT = 32, 32

class Landscape:
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
    def __init__(self):
        self.scape = Landscape()
        self.port = Viewport(TILE_WIDTH, TILE_HEIGHT, VIEW_WIDTH, VIEW_HEIGHT)

        pygame.init()
        self.screen = pygame.display.set_mode(VIEW_SIZE)
        self.event_loop(True)

        while 1:
            self.event_loop()

    def event_loop(self, force_draw = False):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

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

        if (move_x, move_y) != (0, 0) or force_draw:
            self.port.move(move_x, move_y)
            player_x, player_y = self.port.get_pos()
            tiles = self.port.visible_landscape_squares()

            for (x, y) in tiles:
                tile_left, tile_top = TILE_WIDTH * x - player_x + (VIEW_WIDTH // 2), TILE_HEIGHT * y - player_y + (VIEW_HEIGHT // 2)
                pygame.draw.rect(self.screen, (0, 255*self.scape.get_lushness((x, y)), 0), (tile_left, tile_top, TILE_WIDTH, TILE_HEIGHT))

            pygame.display.update()

        pygame.time.wait(50)

class Viewport:
    def __init__(self, tile_width, tile_height, width, height):
        self.tile_width, self.tile_height = tile_width, tile_height
        self.width, self.height = width, height
        self.x, self.y = 0, 0
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

Session()
