from pyrosm import OSM, get_data
from database import MongoDatabase
from osm_residential_building import  *
from  osm_points_of_interest import *
from pairs import Pairs
from logging_config import configure_logging
from pandana_graph import PandanaGraph
from id_to_data import IDToData
from shortest_path_calculator import PathCalculator

configure_logging()
osm = OSM(get_data('Gliwice'))
b = OSMResidentialBuildings(osm)
pois = OSMPointsOfInterest(osm)
p = Pairs(pois, b)
pd = PandanaGraph(osm)
pthc = PathCalculator(pd, p)
pthc.calc_paths()
