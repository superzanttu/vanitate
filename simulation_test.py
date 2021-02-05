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

# Time-stamp: <2021-02-05 14:16:55>

# Standard libraries
import sys
import logging as log
import time

# External libraries
import yaml
import networkx as nx
from apscheduler.schedulers.blocking import BlockingScheduler


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
            sc = self.ship_data[id]['location'] = {}
            sc['x_uu'] = 0
            sc['y_uu'] = 0
            sc['x_gu'] = 0
            sc['y_gu'] = 0
            sc['x_su'] = 0
            sc['y_su'] = 0

            sc = self.ship_data[id]['target'] = {}
            sc['x_uu'] = 0
            sc['y_uu'] = 0
            sc['x_gu'] = 0
            sc['y_gu'] = 0
            sc['x_su'] = 0
            sc['y_su'] = 0

            ss= self.ship_data[id]['speed'] = {}
            ss['x_ms'] = 0
            ss['y_ms'] = 0
            sa = self.ship_data[id]['acceleration'] = {}
            sa['x_ms2'] = 0
            sa['y_ms2'] = 0

        else:
            log.error("Can't add ship with existing name (%s)" % id)

    def set_location(self, id,coordinates):

        if id in self.ships:
            log.debug("%s %s" % (id,coordinates))
            sc = self.ship_data[id]['location']
            sc['x_uu'] = coordinates['x_uu']
            sc['y_uu'] = coordinates['y_uu']
            sc['x_gu'] = coordinates['x_gu']
            sc['y_gu'] = coordinates['y_gu']
            sc['x_su'] = coordinates['x_su']
            sc['y_su'] = coordinates['y_su']
        else:
            log.error("Can't find ship %s" % id)


    def set_target(self, id,coordinates):
        if id in self.ships:
            log.debug("%s %s" % (id,coordinates))
            sc = self.ship_data[id]['target']
            sc['x_uu'] = coordinates['x_uu']
            sc['y_uu'] = coordinates['y_uu']
            sc['x_gu'] = coordinates['x_gu']
            sc['y_gu'] = coordinates['y_gu']
            sc['x_su'] = coordinates['x_su']
            sc['y_su'] = coordinates['y_su']
            self.set_heading_to(id,coordinates)
        else:
            log.error("Can't find ship %s" % id)

    def set_heading_to(self,id, coordinates):
        log.debug("%s" % coordinates)
        raise Exception('FIXME')


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


def main():

    log.basicConfig(format='%(asctime)s|%(levelname)s|%(filename)s|%(funcName)s|%(lineno)d|%(message)s',filename='./log/main.log', level=log.DEBUG)

    log.info("===========================================")
    log.info("START")

    map = SpaceMap()

    map.read_space_map()
    map.write_space_map()
    # map.write_networkx_map()
    # map.read_networkx_map()
    # print(map)

    ships = Ship()
    ships.map = map
    ships.add("Ship 1")
    ships.add("Ship 2")
    ships.add("Ship 3")
    ships.add("Ship 4")
    ships.delete("Ship 4")

    #scheduler = BlockingScheduler()
    #scheduler.add_job(simulate, 'interval', seconds=10, id='worker')
    # scheduler.start()

    c = map.get_coordinates('black-planet-5-3')
    ships.set_location("Ship 1",c)

    c = map.get_coordinates('black-planet-5-1')
    ships.set_target("Ship 1",c)

    #c = map.get_coordinates('black-planet-5-3')

    log.info("DONE")


def simulate():
    pass


if __name__ == "__main__":
    main()
