#!/usr/bin/env python
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

# Time-stamp: <2021-02-10 02:41:27>

# Standard libraries
import sys
import logging as log
import time
import pprint
import math
import csv

# External libraries
import yaml
import networkx as nx
from apscheduler.schedulers.blocking import BlockingScheduler
import pygame

# Name generator START
import sys
import argparse
import os
import random

from collections import defaultdict

HOME_FOLDER = os.path.dirname(os.path.abspath(__file__))
NAME_DATA_FOLDER = "namedata"
# Name generator END


# Pygame test
# Constants
NUM_STARS = 400
SCREEN_SIZE = [3360, 2100]
#SCREEN_SIZE = [800, 600]
WHITE = 255, 255, 255
BLACK = 20, 20, 40
LIGHTGRAY = 180, 180, 180
DARKGRAY = 120, 120, 120
LEFT = 0
RIGHT = 1
############



class MarkovChainNamer():
    def __init__(self):
        self.chains = defaultdict(list)
        self.splat = defaultdict(str)
        self.source = defaultdict(list)

    def next(self, listname, current):
        #print("next:",listname, current)
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
        #print ("load_chains:", listname, name)
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
        #print("load_wordlist:", listname, filepath)
        names = [line.strip() for line in open(filepath, 'rt').readlines()]
        for name in names:
            if name.startswith('#'):
                continue
            # Keep everything as unicode internally
            #name = name.decode('utf-8')
            self.load_chains(listname, name)
            self.load_chains("", name)

    def load_wordlist(self, listname):
        #print("load_wordlist:", listname)
        if listname == "":
            self.load_all_name_data()
        else:
            path = os.path.join(HOME_FOLDER, NAME_DATA_FOLDER, listname+".txt")
            if os.path.exists(path):
                self.load_wordlist_file(listname, path)
            else:
                print("Error: name data file '%s' not found." % (path))
                sys.exit(-1)

    def load_all_name_data(self):
        # print("load_all_name_data")
        for fn in os.listdir(os.path.join(HOME_FOLDER, NAME_DATA_FOLDER)):
            if fn.endswith(".txt"):
                listname, ext = os.path.splitext(fn)
                path = os.path.join(HOME_FOLDER, NAME_DATA_FOLDER, listname+".txt")
                self.load_wordlist_file(listname, path)

    def _gen_name(self, listname, min_lenght, max_lenght):
        #print ("_gen_name:",setname, options)
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
        #print("gen_name:", listname, min_lenght, max_lenght)
        acceptable = False
        while not acceptable:
            name = self._gen_name(listname, min_lenght, max_lenght)

            # Name should not exsist in word list
            if name not in self.source[listname]:
                acceptable = True
        return name





class SpaceMap:
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
            data = yaml.dump(self.map, file)

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
        if not id in self.objects:
            log.debug("ID:%s Name:%s Type:%s x_uu:%s y_uu:%s x_gu:%s y_gu:%s x_su:%s y_su:%s" %
                      (id, name, type, x_uu, y_uu, x_gu, y_gu, x_su, y_su))
            self.objects.append(id)
            od = self.map[id] = {}
            od['name'] = name
            od['type'] = type
            ol = od['location'] = {}
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
            return(self.map[id]['location'])
        else:
            log.error("Object not found (%s)" % (id))


class SpaceMapGenerator():

    markov = MarkovChainNamer()

    # Size of the space
    SPACE_X_MAX = 5 * 10**17
    SPACE_Y_MAX = 5 * 10**17
    STAR_MINIMUM_DISTANCE = 4.7302642 * 10**13




    # Initialize systems and and center system
    systems = {}
    systems['Suomi'] = {'location' : [0,0]}

    # Store maximum and minimum coordinates
    system_x_min = 0
    system_x_max  = 0
    system_y_min = 0
    system_y_max  = 0


    def __init__(self):
        log.debug("__init__")

    def generateStars(self):

        name = "Suomi"

        sc1r = 10
        sc2r = 10

        log.info ("Generating %s star names" % (sc1r*sc2r))

        for sc1 in range(sc1r):

            log.info("Generated %s of %s star names" %  (sc1*sc2r, sc1r*sc2r))

            for sc2 in range(sc2r):

                starcount = sc1*sc2r+sc1

                while name in self.systems:
                    name = self.markov.gen_name("finnish", 4, 13)

                distance_ok = False

                while not distance_ok:
                    x = random.randrange(-self.SPACE_X_MAX,self.SPACE_X_MAX)
                    y = random.randrange(-self.SPACE_Y_MAX,self.SPACE_Y_MAX)

                    distance_ok = True
                    for s in self.systems:
                        sc = self.systems[s]['location']
                        sx = sc[0]
                        sy = sc[1]
                        if math.sqrt((x-sx)**2 + (y-sy)**2) < self.STAR_MINIMUM_DISTANCE:

                            distance_ok = False
                            break

                self.systems[name] = {'location' : [x, y]}

                if x > self.system_x_max:
                    self.system_x_max = x
                elif x < self.system_x_min:
                    self.system_x_min = x

                if y > self.system_y_max:
                    self.system_y_max = y
                elif y < self.system_y_min:
                    self.system_y_min = y

        log.debug("System x_max:%s x_min:%s y_max %s y_min:%s" % (self.system_x_max,self.system_x_min,self.system_y_max,self.system_y_min))

    def scaleCoordinates(self,source,target_min,target_max):
        log.debug("source: %s, target_min: %s target: max: %s" % (source,target_min,target_max))
        s=source[0]
        smin=-10
        smax=10
        tmin=0
        tmax=100
        log.debug("s:%s smin:%s smax:%s tmin:%s tmax:%s" % (s,smin,smax,tmin,tmax))

        t = ((tmax - tmin)*(s - smin))/( smax - smin)+tmin

        print("t:",t)



class Ship:
    """Ship functions"""

    def __init__(self):
        self.ships = []
        self.ship_data = {}
        self.map = None

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
        if not id in self.ships:
            log.debug("Ship %s added" % id)
            self.ships.append(id)

            self.ship_data[id] = {}
            sl = self.ship_data[id]['location'] = {}
            #sl['x_uu'] = 0
            #sl['y_uu'] = 0
            #sl['x_gu'] = 0
            #sl['y_gu'] = 0
            sl['x_su'] = 0
            sl['y_su'] = 0

            st = self.ship_data[id]['target'] = {}
            #st['x_uu'] = 0
            #st['y_uu'] = 0
            #st['x_gu'] = 0
            #st['y_gu'] = 0
            st['x_su'] = 0
            st['y_su'] = 0

            ss = self.ship_data[id]['speed'] = {}
            ss['x_ms'] = 0
            ss['y_ms'] = 0
            sa = self.ship_data[id]['acceleration'] = {}
            sa['x_ms2'] = 0
            sa['y_ms2'] = 0

        else:
            log.error("Can't add ship with existing name (%s)" % id)

    def set_location(self, id, coordinates):

        if id in self.ships:
            log.debug("%s %s" % (id, coordinates))
            sc = self.ship_data[id]['location']
            #sc['x_uu'] = coordinates['x_uu']
            #sc['y_uu'] = coordinates['y_uu']
            #sc['x_gu'] = coordinates['x_gu']
            #sc['y_gu'] = coordinates['y_gu']
            sc['x_su'] = coordinates['x_su']
            sc['y_su'] = coordinates['y_su']
        else:
            log.error("Can't find ship %s" % id)

    def set_target(self, id, coordinates):
        if id in self.ships:
            log.debug("%s %s" % (id, coordinates))
            sc = self.ship_data[id]['target']
            #sc['x_uu'] = coordinates['x_uu']
            #sc['y_uu'] = coordinates['y_uu']
            #sc['x_gu'] = coordinates['x_gu']
            #sc['y_gu'] = coordinates['y_gu']
            sc['x_su'] = coordinates['x_su']
            sc['y_su'] = coordinates['y_su']
            self.set_heading_to(id, coordinates)
        else:
            log.error("Can't find ship %s" % id)

    def set_heading_to(self, id, coordinates):
        log.debug("%s" % coordinates)

        # Current location
        sl = self.ship_data[id]['location']
        # cx_uu=sl['x_uu']
        # cy_uu=sl['y_uu']
        # cx_gu=sl['x_gu']
        # cy_hu=sl['y_gu']
        cx_su = sl['x_su']
        cy_su = sl['y_su']

        # double angle = atan2(y2 - y1, x2 - x1) * 180 / PI;".
        FIXME


def draw_map(space):



    random.seed()

    # Initialize the pygame library.
    pygame.init()

    print(pygame.display.list_modes())
    screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)
    pygame.display.set_caption("Starfield")
    pygame.mouse.set_visible(0)

    # Set the background to black.
    screen.fill(BLACK)
    # Place ten white stars
    for key in space.systems:
        c1 = space.systems[key]['location']
        c2=space.scaleCoordinates(c1,[0,0],SCREEN_SIZE)
        screen.set_at(c2, WHITE)

    # Update the screen.
    pygame.display.update()

    # Main loop
    while 1:

        # Handle input events.
        event = pygame.event.poll()
        if (event.type == pygame.QUIT):
            break
        elif (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_ESCAPE):
                break







def main_map():
    space = SpaceMapGenerator()
    space.generateStars()

    print("Writing CVS file")
    with open('stars.csv', 'w') as f:
        for key in space.systems.keys():
            f.write("%s,%s\n" % (key, space.systems[key]))

def main_namegen():
    markov = MarkovChainNamer()

    for i in range(1):
        print(markov.gen_name("", 4, 13))
        print(markov.gen_name("finnish", 4, 13))

def main_ship():

    log.basicConfig(format='%(asctime)s|%(levelname)s|%(filename)s|%(funcName)s|%(lineno)d|%(message)s',
                    filename='./log/main.log', level=log.DEBUG)

    log.info("===========================================")
    log.info("START")


    space = SpaceMapGenerator()
    space.generateStars()

    ships = Ship()

    ships.add("Ship 1")

    space.scaleCoordinates([10,20],[0,0],SCREEN_SIZE)
    exit(1)


    #scheduler = BlockingScheduler()
    #scheduler.add_job(simulate, 'interval', seconds=10, id='worker')
    # scheduler.start()

    draw_map(space)

    log.info("DONE")






if __name__ == "__main__":
    #main_namegen()
    #main_map()
    main_ship()
