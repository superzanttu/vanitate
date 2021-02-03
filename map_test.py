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
    ships = []
    ship_data = {}

    def __init__(self):
        pass

    def add(self, name):
        if not name in self.ships:
            self.ships.append(name)
            print("Ship", name, "added")

            self.ship_data['location']=None
            self.ship_data['route']=()
            self.ship_data['speed']=0

        else:
            print("EXIT: Duplicate ship name", name)
            sys.exit

    def __str__(self):
        text = "SHIP INFO\n\tTotal ships: %s\n\tShips:" % (len(self.ships))
        for s in self.ships:
            text += "\n\t\t%s" % (s)
        return(text)

    def delete(self, name):
        if not name in self.ships:
            self.ships.remove(name)
            print("Ship", name, "deleted")

    def set_location(self, name):
        if name in slelf.ships:
            pass

class SpaceMap:
    """Space map functions"""

    def __init__(self):
        self.planet_types = []
        self.map = nx.Graph()

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
        self.map.add_node(id, name=name)

        if neighbors != [None]:
            for n in neighbors:
                self.map.add_edge(id, n)

    def write_networkx_map(self):
        print("WRITING NX MAP")
        nx.write_yaml(self.map, "./resources/nx_map.yaml")

    def read_networkx_map(self):
        print("READING NX MAP")
        self.map = nx.read_yaml("./resources/nx_map.yaml")


def main():

    log.basicConfig(format='%(asctime)s:FILE %(filename)s:FUNCTION %(funcName)s:ROW %(lineno)d:%(levelname)s:%(message)s', filename='./log/main.log', level=log.DEBUG)

    log.debug("START")

    map = SpaceMap()

    map.add_solar_system("test","Jee","")
    map.read_space_map()
    #map.write_networkx_map()
    #map.read_networkx_map()
    print(map)

    ships = Ship()
    ships.add("Mega1")
    ships.add("Mega2")
    ships.add("Mega3")

    print(ships)

    log.debug("DONE")


if __name__ == "__main__":
    main()
