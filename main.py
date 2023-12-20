from pyrosm import OSM, get_data
from databas import MongoDatabase
from data import *
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

WINDOW = 3000
MAX_DISTANCE = 3_000
EXCLUDED_AMENITIES = ['unknown', 'parking', 'waste_basket', 'bicycle_parking', 'fuel', 'toilets', 'bench']


class IDToData:
    def __init__(self):
        self.data = {}

    def add(self, id_, data):
        if self.data.get(id_) is None:
            self.data[id_] = [data]
            return
        else:
            logging.warning(f"Graph id {id_} already exists in dict with data {data}")
            self.data[id_].append(data)

    def get(self, id_):
        try:
            return self.data[id_]
        except KeyError:
            logging.warning(f"Cant find id {id_}", exc_info=True)


class PointOfInterest:
    def __init__(self, amenity: Amenity, address, location: Location, name: BuildingName, tags: Tags):
        self.address = address
        self.location = location
        self.tags = tags
        self.amenity = amenity
        self.name = name
        self.id_ = None
        self.distance = -1
        self.data_source = 'https://www.openstreetmap.org'

    def to_dict(self):
        data = {
                'name': str(self.name),
                'tags': self.tags.to_dict(),
                'location': self.location.to_dict(),
                'distance': self.distance,
                'amenity': str(self.amenity),
                'source': self.data_source,
        }
        if self.address.is_valid:
            data['address'] = self.address.to_dict()
        return data

    def set_id(self, id_: int):
        self.id_ = id_

    def __str__(self):
        return f"{self.name}-{self.address}-{self.tags}"


class Pairs:
    def __init__(self, amenities, residential_houses):
        self.amenities_list = amenities
        self.residential_houses_list = residential_houses

    @property
    def pairs_amount(self) -> int:
        return len(self.amenities_list) * len(self.residential_houses_list)

    @property
    def chunk_amounts(self) -> int:
        return round(len(self.residential_houses_list) / WINDOW)

    @property
    def pairs(self):
        logging.info("Generating pairs...")
        origins = []
        destinations = []
        i = 0

        for address in self.residential_houses_list:
            i += 1
            for amenity in self.amenities_list:
                origins.append(address.id_)
                destinations.append(amenity.id_)
            if i >= WINDOW:
                logging.info(f"For {i} addresses and {len(self.amenities_list)} amenities generated {len(destinations)} pairs")
                yield origins, destinations
                i = 0
                origins.clear()
                destinations.clear()
        logging.info(f"For {len(self.residential_houses_list) - self.chunk_amounts * WINDOW} addresses {len(destinations)} pairs generated")
        yield origins, destinations


class Result:
    def __init__(self, destination, distance):
        self.destination = destination
        self.distance = distance

    def __str__(self):
        return self.destination.name


class Results:
    def __init__(self, data_to_id):
        self.results = {}
        self.data_to_id = data_to_id
        self.db = MongoDatabase()

    def add(self, origin_id, destination_id, distance) -> bool:
        if distance < MAX_DISTANCE:
            origin_objs = self.data_to_id.get(origin_id)
            destination_objs = self.data_to_id.get(destination_id)
            for origin_obj in origin_objs:
                for destination_obj in destination_objs:
                    destination_obj.distance = distance
                    if self.results.get(origin_obj.address.full) is None:
                        self.results[origin_obj.address.full] = origin_obj.to_dict()
                        self.results[origin_obj.address.full]['points_of_interest'] = {}

                    if not isinstance(destination_obj, PointOfInterest):
                        continue

                    if self.results[origin_obj.address.full]['points_of_interest'].get(destination_obj.amenity) is None:
                        self.results[origin_obj.address.full]['points_of_interest'][str(destination_obj.amenity)] = []
                    self.results[origin_obj.address.full]['points_of_interest'][str(destination_obj.amenity)].append(destination_obj.to_dict())
            return True
        return False

    def save_to_db(self):
        logging.info(f"Start saving {len(self.results)} addresses")
        self.db.insert_many(self.results)
        logging.info(f"Done saving {len(self.results)} addresses")
        self.results.clear()


class Buildings:
    def __init__(self):
        self.osm = OSM(get_data('gdansk'))
        nodes, edges = self.osm.get_network(nodes=True, network_type='walking')
        self.graph = self.osm.to_graph(nodes, edges, graph_type="pandana", pandana_weights=["length"])

        self.buildings_list = []
        self.amenities_list = []
        self.id_to_data = IDToData()
        self.results = Results(self.id_to_data)
        self.get_buildings()
        self.get_pois()
        self.set_ids()
        self.pairs = Pairs(self.amenities_list, self.buildings_list)

    def get_pois(self):
        custom_filter = {'amenity': True}
        pois = self.osm.get_pois(custom_filter=custom_filter)
        for index, building in pois.iterrows():
            address = Address(building.get('addr:street', None), building.get('addr:housenumber', None),
                              building.get('addr:city', None))
            location = Location(building.geometry.centroid.x, building.geometry.centroid.y)
            amenity = Amenity(building.get('amenity'))
            if str(amenity) not in EXCLUDED_AMENITIES:
                tags = Tags(building.get('tags', "{}") or "{}")
                name = BuildingName(building.get('name'))
                poi = PointOfInterest(amenity, address, location, name, tags)
                self.amenities_list.append(poi)
        logging.info(f"Collected {len(self.amenities_list)} POIs")

    def get_buildings(self):
        logging.info("Start loading buildings info..")
        buildings = self.osm.get_buildings()
        address_location = {}
        for index, building in buildings.iterrows():
            address = Address(building.get('addr:street', None), building.get('addr:housenumber', None), building.get('addr:city', None))
            location = Location(building.geometry.centroid.x, building.geometry.centroid.y)
            if address.is_valid:
                if address_location.get(address.full, None) is None:
                    self.buildings_list.append(ResidentialBuilding(address, location))
                    address_location[address.full] = location
        logging.info(f"Unique address {len(self.buildings_list)}, amenity {len(self.amenities_list)}")
        logging.info("Building info loading done")

    def set_ids(self):
        logging.info("Start buildings id adding")
        x = []
        y = []
        data = self.buildings_list + self.amenities_list
        for row in data:
            x.append(row.location.x)
            y.append(row.location.y)
        ids = self.graph.get_node_ids(x, y).values
        i = 0
        for id_ in ids:
            data[i].set_id(id_)
            self.id_to_data.add(id_=id_, data=data[i])
            i += 1
        logging.info(f"Done buildings id adding.")

    def calc_paths(self):
        i = 1
        for origins, destinations in self.pairs.pairs:
            logging.info(f"Start calculating shortest paths for {i}/{self.pairs.chunk_amounts}. Pairs count {len(origins)}")
            dists = self.graph.shortest_path_lengths(origins.copy(), destinations.copy())
            logging.info(f"Done calculating shortest paths for {i}/{self.pairs.chunk_amounts}. Calculated {len(dists)} paths for {len(list(set(origins.copy())))} points")
            for orig, dest, dist in zip(origins, destinations, dists):
                self.results.add(orig.copy(), dest.copy(), dist)
            self.results.save_to_db()
            i += 1


db = MongoDatabase()
db.bulk_delete_points_of_interest()
b = Buildings()
b.calc_paths()
