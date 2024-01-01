from pyrosm import OSM, get_data
from databas import MongoDatabase
from data import *
from osm_residential_building import  *
from  osm_points_of_interest import *
from pairs import Pairs

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# USE Visitor to export result
# возможность добавить другие аменити, дома из других источников к сушествующим
#шаблон строитель


osm = OSM(get_data('Gliwice'))
db = MongoDatabase()
#db.bulk_delete_points_of_interest()
b = OSMResidentialBuildings(osm)
c = OSMPointsOfInterest(osm)
p = Pairs(c, b)

for ori, dest in p:
    print(len(ori), len(dest))

#b.calc_paths()
