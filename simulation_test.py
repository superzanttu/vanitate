#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Maps test for Vanitate
#
# Copyright (C) 2021 Kai Käpölä
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Time-stamp: <2021-02-13 10:00:29>

# Start logging before other libraries
from collections import defaultdict
import random
import os
# import argparse
import numpy
import pygame
# from apscheduler.schedulers.blocking import BlockingScheduler
import networkx as nx
import yaml
# import csv
import math
# import pprint
# import time
import sys

# Logging
import logging


class ListHandler(logging.Handler):  # Inherit from logging.Handler
    def __init__(self, log_list):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Our custom argument
        self.log_list = log_list

    def emit(self, record):
        # record.message is the log message
        self.log_list.append(record.msg)


logging.basicConfig(format='%(asctime)s|%(levelname)s|%(filename)s|%(funcName)s|%(lineno)d|%(message)s',
                    filename='./log/main.log', level=logging.DEBUG)

hud_console_log = []
hud_console = ListHandler(hud_console_log)
hud_console.setLevel(logging.INFO)

hud_formatter = logging.Formatter('%(asctime)s|%(message)s')
hud_console.setFormatter(hud_formatter)

logging.getLogger('').addHandler(hud_console)

log = logging.getLogger()


HOME_FOLDER = os.path.dirname(os.path.abspath(__file__))
NAME_DATA_FOLDER = "namedata"

# Pygame
# Constants
SCREEN_SIZE_X = 3360
SCREEN_SIZE_Y = 2100
# SCREEN_SIZE_X = 2880
# SCREEN_SIZE_Y = 1800
SCREEN_SIZE = [SCREEN_SIZE_X, SCREEN_SIZE_Y]
WHITE = 255, 255, 255
BLACK = 0, 0, 0
LIGHTGRAY = 180, 180, 180
DARKGRAY = 120, 120, 120
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
YELLOW = 255, 255, 0
CYAN = 0, 255, 255
MAGENTA = 255, 0, 255
LEFT = 0
RIGHT = 1
MOUSE_LEFT_BUTTON = 1
MOUSE_MIDDLE_BUTTON = 2
MOUSE_RIGHT_BUTTON = 3


class MarkovChainNamer():
    def __init__(self):
        self.chains = defaultdict(list)
        self.splat = defaultdict(str)
        self.source = defaultdict(list)

    def next(self, listname, current):
        if not current:
            return "^"

        while True:
            if current:
                if (listname, current) in self.chains:
                    return random.choice(self.chains[(listname, current)])
                current = current[1:]
            else:
                return random.choice(self.splat[listname])

    def load_chains(self, listname, name):
        if not name:
            return
        self.source[listname].append(name)
        name = "^" + name + "|"
        self.splat[listname] = self.splat[listname] + name
        # initials[listname] = initials[listname] + name[0]
        for count in range(2, 4):
            for i in range(len(name)):
                seq = name[i:i+count]
                if len(seq) > 1:
                    prefix = seq[:-1]
                    self.chains[(listname, prefix)].append(seq[-1])

    def load_wordlist_file(self, listname, filepath):
        names = [line.strip() for line in open(filepath, 'rt').readlines()]
        for name in names:
            if name.startswith('#'):
                continue
            # Keep everything as unicode internally
            # name = name.decode('utf-8')
            self.load_chains(listname, name)
            self.load_chains("", name)

    def load_wordlist(self, listname):
        if listname == "":
            self.load_all_name_data()
        else:
            path = os.path.join(HOME_FOLDER, NAME_DATA_FOLDER, listname+".txt")
            if os.path.exists(path):
                self.load_wordlist_file(listname, path)
            else:
                log.error("Error: name data file '%s' not found." % (path))
                sys.exit(-1)

    def load_all_name_data(self):
        for fn in os.listdir(os.path.join(HOME_FOLDER, NAME_DATA_FOLDER)):
            if fn.endswith(".txt"):
                listname, ext = os.path.splitext(fn)
                path = os.path.join(HOME_FOLDER, NAME_DATA_FOLDER, listname+".txt")
                self.load_wordlist_file(listname, path)

    def _gen_name(self, listname, min_lenght, max_lenght):
        ok = False

        if listname not in self.splat:
            self.load_wordlist(listname)

        while not ok:
            name = "^"

            while len(name) < max_lenght:
                next = self.next(listname, name)
                if next != "|":
                    name += next
                else:
                    if len(name) > min_lenght:
                        ok = True
                    break

        return name.replace("^", "")

    def gen_name(self, listname, min_lenght, max_lenght):
        acceptable = False
        while not acceptable:
            name = self._gen_name(listname, min_lenght, max_lenght)

            # Name should not exsist in word list
            if name not in self.source[listname]:
                acceptable = True
        return name


class SpaceMap_YAML:
    """Space map functions"""

    def __init__(self):
        self.map = {}
        self.planet_types = []
        self.map_nx = nx.Graph()
        self.objects = []

    def __str__(self):
        text = "MAP INFO\n"
        for n in nx.info(self.map).splitlines():
            text += "\t%s\n" % (n)

        text += "\tIsolated nodes: %s\n" % (len(list(nx.isolates(self.map))))

        text += "\tNodes:\n\t\t"
        for n in self.map.nodes():
            text += "%s " % (n)

        text += "\n\tEdges:\n\t\t"
        for n in self.map.edges():
            e = ",".join(n)
            text += "(%s) " % (e)

        if len(list(nx.isolates(self.map))) > 0:
            text += "\n\tIsolated nodes:\n\t\t"
            for n in list(nx.isolates(self.map)):
                text += "%s " % (n)

        return(text)

    def write_space_map(self):
        log.debug("Writing space map")
        with open('./resources/map_dump.yaml', 'w') as file:
            yaml.dump(self.map, file)

    def read_space_map(self):
        log.debug("Reading space map")
        with open("./resources/map.yaml", 'r') as stream:
            try:
                yaml_data = yaml.load(stream, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
                exit(1)

        for g in yaml_data['universum']['galaxies']:
            print(g)
            g_id = g['id']
            g_type = "galaxy"
            g_name = g['name']
            g_x_uu = g['x_uu']
            g_y_uu = g['y_uu']
            g_x_gu = 0
            g_y_gu = 0
            g_x_su = 0
            g_y_su = 0
            self.add_object(g_id, g_type, g_name, g_x_uu, g_y_uu,
                            g_x_gu, g_y_gu, g_x_su, g_y_su)  # Add galaxy
            for s in yaml_data['galaxy'][g_id]['systems']:
                print("  ", s)
                s_id = s['id']
                s_type = "System"
                s_name = s['name']
                s_x_uu = g['x_uu']
                s_y_uu = g['y_uu']
                s_x_gu = s['x_gu']
                s_y_gu = s['x_gu']
                s_x_su = 0
                s_y_su = 0
                self.add_object(s_id, s_type, s_name, s_x_uu, s_y_uu,
                                s_x_gu, s_y_gu, s_x_su, s_y_su)  # Add system

                r_id = yaml_data['system'][s_id]['star']
                r_type = "Star"
                r_name = yaml_data['star'][r_id]['name']
                r_x_uu = s_x_uu
                r_y_uu = s_x_uu
                r_x_gu = s_x_uu
                r_y_gu = s_x_uu
                r_x_su = 0
                r_y_su = 0
                self.add_object(r_id, r_type, r_name, r_x_uu, r_y_uu, r_x_gu,
                                r_y_gu, r_x_su, r_y_su)  # Add star of system

                for p in yaml_data['system'][s_id]['planets']:
                    print("    ", p)
                    p_id = p['id']
                    p_type = "Planet"
                    p_name = s['name']
                    p_x_uu = g['x_uu']
                    p_y_uu = g['y_uu']
                    p_x_gu = s['x_gu']
                    p_y_gu = s['x_gu']
                    p_x_su = p['x_su']
                    p_y_su = p['y_su']
                    self.add_object(p_id, p_type, p_name, p_x_uu, p_y_uu,
                                    p_x_gu, p_y_gu, p_x_su, p_y_su)  # Add planet

    def add_object(self, id, type, name, x_uu, y_uu, x_gu, y_gu, x_su, y_su):
        if id not in self.objects:
            log.debug("ID:%s Name:%s Type:%s x_uu:%s y_uu:%s x_gu:%s y_gu:%s x_su:%s y_su:%s" %
                      (id, name, type, x_uu, y_uu, x_gu, y_gu, x_su, y_su))
            self.objects.append(id)
            od = self.map[id] = {}
            od['name'] = name
            od['type'] = type
            ol = od['location_xy'] = {}
            ol['x_uu'] = x_uu
            ol['y_uu'] = y_uu
            ol['x_gu'] = x_gu
            ol['y_gu'] = y_gu
            ol['x_su'] = x_su
            ol['y_su'] = y_su
        else:
            log.error("Can't add object with existing name ID:%s Name:%s Type:%s" % (id, name, type))

    def get_coordinates(self, id):
        if id in self.objects:
            return(self.map[id]['location_xy'])
        else:
            log.error("Object not found (%s)" % (id))


class Ship:
    """Ship functions"""

    font = None
    screen = None
    space = None

    def __init__(self):
        log.debug("__init__")
        self.ships = []
        self.ship_data = {}

    def __str__(self):
        text = "SHIP INFO\n\tTotal ships: %s\n\tShips:" % (len(self.ships))
        for s in self.ships:
            text += "\n\t\t%s" % (s)
            for k in self.ship_data[s].keys():
                text += "\n\t\t\t%s: %s" % (k, self.ship_data[s][k])
        return(text)

    def delete(self, id):
        if id in self.ships:
            self.ships.remove(id)
            log.debug("Ship %s deleted" % id)
        else:
            log.error("Ship not found %s" % id)

    def add(self, id):
        if id not in self.ships:
            log.debug("Ship %s added" % id)
            self.ships.append(id)

            self.ship_data[id] = {}
            self.ship_data[id]['location_xy'] = [0, 0]

            self.ship_data[id]['angle'] = math.pi/6

            self.ship_data[id]['velosity_xy_ms'] = [0, 0]

            self.ship_data[id]['acceleration_ms2'] = [0]

            self.ship_data[id]['acceleration_xy_ms2'] = [0, 0]

        else:
            log.error("Can't add ship with existing name (%s)" % id)

    def set_location(self, id, coordinates):

        if id in self.ships:
            log.debug("%s %s" % (id, coordinates))
            self.ship_data[id]['location_xy'] = coordinates

        else:
            log.error("Can't find ship %s" % id)

    def set_acceleration(self, id, acceleration_ms2):
        log.debug("Set ship %s acceleration to %s m/sˆ" % (id, acceleration_ms2))
        ax = acceleration_ms2 * math.cos(self.ship_data[id]['angle'])
        ay = acceleration_ms2 * math.sin(self.ship_data[id]['angle'])
        self.ship_data[id]['acceleration_xy_ms2'] = [ax, ay]
        self.ship_data[id]['acceleration_ms2'] = acceleration_ms2

        self.draw_ship_data(id)

    def draw_ship_data(self, id):

        s = self.ship_data[id]
        t_id = "ID:%s   " % id
        t_location = "Location:%s   " % s['location_xy']
        t_angle = "Angle:%s   " % s['angle']
        t_velosity = "Velosity: %s m/sˆ2   " % s['velosity_xy_ms']
        t_acceleration = "Acceleration: %s m/s2   " % s['acceleration_ms2']
        t_acceleration_xy = "Acceleration XY: %s m/s2   " % s['acceleration_xy_ms2']

        text = (t_id, t_location, t_angle, t_velosity, t_acceleration, t_acceleration_xy)

        text_y = 0
        text_y_step = 32

        pygame.draw.rect(self.screen, (0, 200, 0), (0, 0, 1000, len(text)*text_y_step))

        for t in text:

            img = self.font.render(t, True, (0, 0, 255))
            self.screen.blit(img, (0, text_y))
            text_y += text_y_step

    def update(self, id):
        sd = self.ship_data[id]
        lo = sd['location_xy']
        ve = sd['velosity_xy_ms']
        ac = sd['acceleration_xy_ms2']

        ac_a = numpy.array(ac)
        lo_a = numpy.array(lo)
        ve_a = numpy.array(ve)

        ve = ve_a + ac_a
        self.ship_data[id]['velosity_xy_ms'] = ve

        lo = lo_a + ve
        self.ship_data[id]['location_xy'] = lo

        sc = self.space.scale_coordinates(
            lo, [SCREEN_SIZE[0]*0.02, SCREEN_SIZE[1]*0.02], [SCREEN_SIZE[0]*0.98, SCREEN_SIZE[1]*0.98])
        pygame.draw.circle(self.screen, (0, 0, 255), sc, 10, 0)


class SpaceMapGenerator():

    markov = MarkovChainNamer()

    # Size of the space
    SPACE_X_MAX = 5 * 10**17
    SPACE_Y_MAX = 5 * 10**17
    STAR_MINIMUM_DISTANCE = 4.7302642 * 10**13

    # Initialize systems and and center system
    systems = {}
    systems['Suomi'] = {}
    systems['Suomi']['location_xy'] = (0, 0)
    systems['Suomi']['planets'] = {}

    # Store maximum and minimum coordinates for space
    space_x_min = 0
    space_x_max = 0
    space_y_min = 0
    space_y_max = 0

    view_x_min = 0
    view_x_max = 0
    view_y_min = 0
    view_y_max = 0

    # space_view = ()

    # Pygame screen and font
    screen = None
    font_size_s = None
    font_size_m = None
    font_size_l = None

    def __init__(self):
        log.debug("__init__")
        log.debug("Initial systems: %s" % self.systems)

    def generate_stars(self):

        name = "Suomi"

        sc1r = 2
        sc2r = 10

        log.debug("Generating %s star names" % (sc1r*sc2r))

        for sc1 in range(sc1r):

            log.debug("Generated %s of %s star names" % (sc1*sc2r, sc1r*sc2r))

            for sc2 in range(sc2r):

                while name in self.systems:
                    name = self.markov.gen_name("finnish", 4, 13)

                distance_ok = False

                while not distance_ok:
                    x = random.randrange(-self.SPACE_X_MAX, self.SPACE_X_MAX)
                    y = random.randrange(-self.SPACE_Y_MAX, self.SPACE_Y_MAX)

                    distance_ok = True
                    # log.debug("Systems: %s" % self.systems)
                    for s in self.systems:
                        # log.debug("Checking distance to s: %s" % s)

                        sd = self.systems[s]
                        # log.debug("sd: %s" % sd)

                        sc = sd['location_xy']
                        # log.debug("sc: (%s,%s)" % sc)

                        sx = sc[0]
                        # log.debug("sx: %s" % sx)

                        sy = sc[1]
                        # log.debug("sy: %s" % sy)

                        if math.sqrt((x-sx)**2 + (y-sy)**2) < self.STAR_MINIMUM_DISTANCE:
                            distance_ok = False
                            break

                self.systems[name] = {}
                self.systems[name]['location_xy'] = (x, y)

                # log.debug("New system: %s %s" % (name, self.systems[name]))

                if x > self.space_x_max:
                    self.space_x_max = x
                    self.view_x_max = x
                elif x < self.space_x_min:
                    self.space_x_min = x
                    self.view_x_min = x

                if y > self.space_y_max:
                    self.space_y_max = y
                    self.view_y_max = y
                elif y < self.space_y_min:
                    self.space_y_min = y
                    self.view_y_min = y

                # self.space_view = (self.space_x_min, self.space_y_min, self.space_x_max, self.space_y_max)

                self.systems[name]['planets'] = {}

        log.debug("System x_max:%s x_min:%s y_max %s y_min:%s" %
                  (self.space_x_max, self.space_x_min, self.space_y_max, self.space_y_min))

    def scale_to_range(self, v, v_min, v_max, range_min, range_max):
        v_scaled = int(((range_max - range_min)*(v - v_min))/(v_max - v_min)+range_min)
        # log.debug("Scale %s <= %s <= %s --> %s <= %s <= %s" % (v_min, v, v_max, range_min, v_scaled, range_max))
        return(v_scaled)

    def space_coordinates_to_screen(self, source):
        # log.info("source: %s, target_min: %s target: max: %s" % (source, target_min, target_max))

        # t = ((tmax - tmin)*(s - smin))/( smax - smin)+tmin

        tx = self.scale_to_range(source[0], self.view_x_min, self.view_x_max,
                                 0, SCREEN_SIZE_X)
        ty = self.scale_to_range(source[1], self.view_y_min, self.view_y_max,
                                 0, SCREEN_SIZE_Y)
        # Scale x coordinate
        # tx = int(((target_max[0] - target_min[0])*(source[0] - self.space_x_min))/(self.space_x_max - self.space_x_min)+target_min[0])
        # ty = int(((target_max[1] - target_min[1])*(source[1] - self.space_y_min))/(self.space_y_max - self.space_y_min)+target_min[1])

        # log.debug("Scaled coordinates: %s, %s" % (tx, ty))
        return (tx, ty)

    def screen_coordinates_to_space_view(self, source):
        # log.info("source: %s, target_min: %s target: max: %s" % (source, target_min, target_max))

        # t = ((tmax - tmin)*(s - smin))/( smax - smin)+tmin

        tx = self.scale_to_range(source[0], 0, SCREEN_SIZE_X, self.view_x_min, self.view_x_max)
        ty = self.scale_to_range(source[1], 0, SCREEN_SIZE_Y, self.view_y_min, self.view_y_max)

        # Scale x coordinate
        # tx = int(((target_max[0] - target_min[0])*(source[0] - self.space_x_min))/(self.space_x_max - self.space_x_min)+target_min[0])
        # ty = int(((target_max[1] - target_min[1])*(source[1] - self.space_y_min))/(self.space_y_max - self.space_y_min)+target_min[1])

        # log.debug("Scaled coordinates: %s, %s" % (tx, ty))
        return (tx, ty)

    def is_visible_location(self, c):
        print(c, self.space_view)
        log.debug("Location: %s View: %s" % (c, self.space_view))
        return True

    def draw_stars(self):
        log.debug("Drawing stars and names")

        for key in self.systems:
            c1 = self.systems[key]['location_xy']

            if True:

                log.debug("Star location: (%s, %s)" % (c1[0], c1[1]))

                # Scale system coordinates to screeb coordinates
                c2 = self.space_coordinates_to_screen(c1)

                # Draw star
                log.debug("Draw star to: (%s, %s)" % (c1[0], c1[1]))
                pygame.draw.circle(self.screen, WHITE, c2, 5, 0)

                # Draw system name
                system_name = self.font_size_m.render(key, True, (255, 255, 255))
                self.screen.blit(system_name, [c2[0]+7, c2[1]-6])

                self.generate_planets(key)
                self.draw_planets(key)

        pygame.display.update()

    def draw_planets(self, system):
        # log.debug("Drawing planets and names for system %s" % system)
        # log.debug("Planets at %s: %s" % (system, self.systems[system]['planets']))

        for key in self.systems[system]['planets']:
            # log.debug("Key: %s" % key)
            # log.debug("Planet %s: %s" % (key, self.systems[system]['planets'][key]))

            angle = self.systems[system]['planets'][key]['angle']
            orbit = self.systems[system]['planets'][key]['orbit']

            # log.debug("Orbit: %s Angle: %s" % (orbit, angle))

            px = orbit * math.cos(angle)
            py = orbit * math.sin(angle)

            log.debug("Planet %s location: (%s, %s)" % (key, px, py))

            # Scale planet coordinates to screen coordinates
            sc = self.space_coordinates_to_screen((px, py))

            # log.debug("Scaled coordinates: (%s, %s)" % (sc[0], sc[1]))

            # Draw planet
            pygame.draw.circle(self.screen, RED, sc, 5, 0)

            # Draw planet name
            planet_name = self.font_size_m.render(key, True, RED)
            self.screen.blit(planet_name, [sc[0]+7, sc[1]-6])

        pygame.display.update()

    def generate_planets(self, system):
        log.debug("Generating planets for system %s" % system)

        planets = random.randrange(3, 12)

        orbit_min = 57950000 + random.randrange(-10000000, 10000000)
        ormit_max = 5913000000 + random.randrange(-10000000, 10000000)

        for p in range(1, planets+1):
            orbit = int((ormit_max-orbit_min)/planets*p + random.randrange(-10000000, 10000000))
            angle = random.uniform(0, math.pi*2)
            name = self.markov.gen_name("finnish", 4, 13)
            log.debug("New planet %s (%s/%s) orbiting at %s m angle %s" %
                      (name, p, planets, orbit, angle))
            self.systems[system]['planets'][name] = {'orbit': orbit, 'angle': angle}

    def draw_space_info(self, x, y):
        # log.debug("Draw space info to (%s,%s)" % (x, y))
        view_text = ("System x_max:%s x_min:%s y_max %s y_min:%s" % (self.space_x_max, self.space_x_min, self.space_y_max, self.space_y_min))
        # log.debug("View data: %s" % view_text)
        view_rect = self.font_size_l.render(view_text, True, YELLOW)
        self.screen.blit(view_rect, (x, y))

    def reset_view(self):
        log.info("Reset view to space minmax")
        self.view_x_max = self.space_x_max
        self.view_x_min = self.space_x_min
        self.view_y_max = self.space_y_max
        self.view_y_min = self.space_y_min
        self.screen.fill(BLACK)
        self.draw_stars()


class HudLog():

    font = None
    screen = None

    def __init__(self):
        self.log_visible = ["Row 1", "Row 2",
                            "Row 3", "Row 4", "Row 5", "Row 6", "Row 7"]

    def draw(self):
        x = 0
        empty_text = " " * 120
        black_rect = self.font.render(empty_text, True, BLACK)
        black_rect.fill(DARKGRAY)

        for r in range(0, len(self.log_visible)):

            text_rect = self.font.render(self.log_visible[r], True, WHITE)
            y = SCREEN_SIZE_Y - text_rect.get_height() * (len(self.log_visible) - r)
            self.screen.blit(black_rect, (x, y))
            self.screen.blit(text_rect, (x, y))
        self.screen

    def add(self, msg):
        self.log_visible.pop(0)
        self.log_visible.append(msg)


def main():

    for _ in range(1, 20):
        log.debug("")

    log.info("===========================================")
    log.info("START")

    random.seed()

    # Initialize the pygame library.
    pygame.init()
    # print (pygame.font.get_fonts())

    space = SpaceMapGenerator()
    space.generate_stars()
    # space.generate_planets("Suomi")

    ships = Ship()
    ships.space = space

    ships.add("Ship 1")

    log.debug("pygame dislay modes: %s", pygame.display.list_modes())
    log.debug("Initializing pygame fonts")

    pygame_font_size_16 = pygame.font.SysFont("menlo", 12)
    pygame_font_size_22 = pygame.font.SysFont("menlo", 16)
    pygame_font_size_32 = pygame.font.SysFont("menlo", 22)
    ships.font = pygame_font_size_22
    space.font_size_s = pygame_font_size_16
    space.font_size_m = pygame_font_size_22
    space.font_size_l = pygame_font_size_32

    screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)
    # (SCREEN_SIZE_X, SCREEN_SIZE_Y)=pygame.display.get_surface().get_size()
    # FIXME
    pygame.display.set_caption("Starfield")
    pygame.mouse.set_visible(True)

    ships.screen = screen
    space.screen = screen

    hudlog = HudLog()
    hudlog.font = pygame_font_size_32
    hudlog.screen = screen

    space.reset_view()

    log.info("Simulation runnning. Press ESC to stop.")

    # Main loop

    mouse_state = 0
    hudlog.draw()

    screen.fill(BLACK)
    space.draw_stars()

    log.info("Visible space: %s, %s %s, %s" %
             (space.space_x_min, space.space_y_min, space.space_x_max, space.space_y_max))

    while 1:

        space.draw_space_info(0, 0)

        # Draw hud logging
        if len(hud_console_log) > 0:
            hudlog.add(hud_console_log.pop(0))
            hudlog.draw()

        # for _ in range(10000):
        #    ships.update("Ship 1")

        # ships.draw_ship_data("Ship 1")

        # Handle input events.
        event = pygame.event.poll()
        # keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                break
            elif event.key == pygame.K_UP:
                ships.set_acceleration("Ship 1", 100)
            elif event.key == pygame.K_DOWN:
                ships.set_acceleration("Ship 1", 0)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == MOUSE_RIGHT_BUTTON:
            space.reset_view()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == MOUSE_LEFT_BUTTON:
            if mouse_state == 0:
                mouse_pos_1 = pygame.mouse.get_pos()
                screen.set_at(mouse_pos_1, YELLOW)
                mouse_state = 1
                log.info("Selection 1: %s %s" % mouse_pos_1)
            elif mouse_state == 2:
                mouse_pos_2 = pygame.mouse.get_pos()
                log.info("Selection 2: %s %s" % mouse_pos_2)
                screen.set_at(mouse_pos_2, YELLOW)
                mouse_state = 3

                r = pygame.Rect(
                    mouse_pos_1, (mouse_pos_2[0] - mouse_pos_1[0], mouse_pos_2[1] - mouse_pos_1[1]))

                log.info("Yellow %s" % r)

                sc1 = space.screen_coordinates_to_space_view(mouse_pos_1)
                sc2 = space.screen_coordinates_to_space_view(mouse_pos_2)

                # Select smallest x coordinate
                if sc1[0] < sc2[0]:
                    x_min = sc1[0]
                    x_max = sc2[0]
                else:
                    x_min = sc2[0]
                    x_max = sc1[0]

                # Select smallest y coordinate
                if sc1[1] < sc2[1]:
                    y_min = sc1[1]
                    y_max = sc2[1]
                else:
                    y_min = sc2[1]
                    y_max = sc1[1]

                log.info("Space range: %s, %s %s, %s" % (x_min, y_min, x_max, y_max))

                pygame.draw.rect(screen, YELLOW, r, 1)

                space.view_x_min = x_min
                space.view_y_min = y_min
                space.view_x_max = x_max
                space.view_y_max = y_max

                screen.fill(BLACK)
                space.draw_stars()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == MOUSE_LEFT_BUTTON:
            if mouse_state == 1:
                mouse_state = 2
            elif mouse_state == 3:
                mouse_state = 0

        # elif event.type ==  pygame.VIDEORESIZE:
            # SCREEN_SIZE = [event.w, event.h]

        # elif event.type == pygame.MOUSEBUTTONUP:
        #    if mouse_state == True:
        #        mouse_pos_2 = pygame.mouse.get_pos()
        #        #pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(mouse_pos_1[0], mouse_pos_1[1], mouse_pos_2[0], mouse_pos_2[1]))
        #        mouse_state = False

        # elif keys[pygame.K_UP]:
        #    ships.setAcceleration
        pygame.display.update()

    log.info("DONE")
    print(hud_console_log)


if __name__ == "__main__":
    main()


# scheduler = BlockingScheduler()
# scheduler.add_job(simulate, 'interval', seconds=10, id='worker')
# scheduler.start()
