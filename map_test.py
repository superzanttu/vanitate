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

# Standard libraries
import importlib.util
import sys
import sys
import logging as log

# External libraries
import yaml
import networkx as nx


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

    def delete(self, name):
        if name in self.ships:
            self.ships.remove(name)
            log.debug("Ship %s deleted" % name)
        else:
            log.error("Ship no found %s" % name)

    def add(self, name):
        if not name in self.ships:
            log.debug("Ship %s added" % name)
            self.ships.append(name)

            self.ship_data[name] = {}
            self.ship_data[name]['location'] = None
            self.ship_data[name]['route'] = ()
            self.ship_data[name]['speed'] = 0
        else:
            log.error("Can't add ship with existing name (%s)" % name)

    def set_location(self, name):
        if name in self.ships:
            pass


class SpaceMap:
    """Space map functions"""

    def __init__(self):
        self.planet_types = []
        self.map = nx.Graph()
        self.solar_systems = []

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

    def read_space_map(self):
        log.debug("Reading space map")
        with open("./resources/map.yaml", 'r') as stream:
            try:
                yaml_data = yaml.load(stream, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)

        for ss in yaml_data['solar systems'].keys():
            ss_id = ss
            ss_name = yaml_data['solar systems'][ss]['name']
            ss_neighbors = yaml_data['solar systems'][ss]['neighbors']
            self.add_solar_system(ss_id, ss_name, ss_neighbors)

    def add_solar_system(self, id, name, neighbors):
        if not id in self.solar_systems:
            log.debug("%s %s %s" % (id, name, neighbors))
            self.map.add_node(id, name=name)
            self.solar_systems.append(id)
            if neighbors != [None]:
                for n in neighbors:
                    self.map.add_edge(id, n)
        else:
            log.error("Can't add solar system with existing name %s %s %s" %
                      (id, name, neighbors))


def main():

    log.basicConfig(format='%(asctime)s %(levelname)s %(filename)s %(funcName)s %(lineno)d %(message)s',
                    filename='./log/main.log', level=log.DEBUG)

    log.info("===========================================")
    log.info("START")

    map = SpaceMap()

    map.add_solar_system("test", "Jee", "")
    map.read_space_map()
    # map.write_networkx_map()
    # map.read_networkx_map()
    # print(map)

    ships = Ship()
    ships.map = map
    ships.add("Mega1")
    ships.add("Mega2")
    ships.add("Mega3")
    ships.add("Mega4")
    ships.delete("Mega4")

    # print(ships)

    log.info("DONE")


if __name__ == "__main__":
    main()
