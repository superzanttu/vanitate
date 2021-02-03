#!/usr/bin/env python

import yaml
import networkx as nx

class SpaceMap:
  """Space map"""

  def __init__(self):
      self.planet_types = []
      self.map = nx.Graph()

  def read_space_map(self):
    with open("./resources/map.yaml", 'r') as stream:
      try:
        yaml_data = yaml.load(stream)
      except yaml.YAMLError as exc:
          print(exc)

      #print ("\nSOLAR SYSTEMS:",yaml_data['solar systems'])
      #print ("\nSOLAR SYSTEM RED:",yaml_data['solar systems']['red'])

      for ss in yaml_data['solar systems'].keys():
        print ("\nSOLAR SYSTEM ID:",ss)
        print ("ALL DATA:",yaml_data['solar systems'][ss])
        ss_id = ss
        ss_name = yaml_data['solar systems'][ss]['name']
        ss_neighbors = yaml_data['solar systems'][ss]['neighbors']
        self.add_solar_system(ss_id,ss_name,ss_neighbors)

      print ("MAP INFO:",nx.info(self.map))
      print ("MAP NODES:",self.map.nodes())
      print ("MAP EDGES:",self.map.edges())

      print ("ISOLATED NODES:",list(nx.isolates(self.map)))

  def add_solar_system(self,id,name,neighbors):
    print ("/nADD_SOLAR_SYSTEM:",id,name,neighbors)
    self.map.add_node(id,name=name)
    print(neighbors,len(list(neighbors)))
    if neighbors != [None] :
      for n in neighbors:
        self.map.add_edge(id,n)


  def write_networkx_map(self):
    pass

  def read_networkx_map(self):
    pass


def main():
  map = SpaceMap()
  map.read_space_map()



if __name__ == "__main__":
    main()
