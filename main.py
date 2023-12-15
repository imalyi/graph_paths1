from pyrosm import OSM, get_data
import json
import logging
from databas import MongoDatabase

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

EXCLUDED_AMENITIES = [None, 'parking', 'waste_basket', 'bicycle_parking', 'fuel', 'toilets', 'bench']
WINDOW = 11000
MAX_DISTANCE = 3_000


class IDToData:
    def __init__(self):
        self.data = {}

    def add(self, id_, data):
        self.data[id_] = data

    def get(self, id_):
        try:
            return self.data[id_]
        except KeyError:
            logging.warning(f"Cant find id {id_}", exc_info=True)


class Address:
    def __init__(self, street, housenumber, city):
        self.street = street
        self.housenumber = housenumber
        self.city = city

    @property
    def full(self) -> str:
        return f"{self.street} {self.housenumber}, {self.city}"

    @property
    def is_valid(self) -> bool:
        if self.street is not None and self.housenumber is not None and self.city is not None:
            return True
        return False

    def __str__(self):
        return self.full

    def __repr__(self):
        return self.full

    def to_dict(self) -> dict:
        return {
            'city': self.city,
            'housenumber': self.housenumber,
            'street': self.street,
            'full': self.full
        }


class Location:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}; {self.y})"

    def __repr__(self):
        return f"({self.x}; {self.y})"


class ResidentialBuilding:
    def __init__(self, address, location):
        self.address = address
        self.location = location
        self.id_ = None
        self.data_source = 'https://www.openstreetmap.org'

    def set_id(self, id_: int):
        self.id_ = id_

    def to_dict(self):
        return {
            'address': self.address.to_dict(),
            'location': self.location,
            'source': self.data_source
        }

    def __str__(self):
        return f"{self.address}"


class PointOfInterest:
    def __init__(self, amenity:str, address, location:Location, name:str, tags: str):
        self.address = address
        self.location = location
        self.tags = json.loads(tags)
        self.amenity = amenity
        self.name = name
        self.id_ = None
        self.distance = -1

        self.data_source = 'https://www.openstreetmap.org'

    def to_dict(self):
        data = {
                'name': self.name,
                'tags': self.tags,
                'location': self.location,
                'distance': self.distance,
                'amenity': self.amenity,
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
        self.amenities_list = list(set(amenities))
        self.residential_houses_list = residential_houses

    @property
    def pairs_amount(self) -> int:
        return len(self.amenities_list) * len(self.residential_houses_list)

    @property
    def chunk_amounts(self) -> int:
        return int(len(self.residential_houses_list) / WINDOW)

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
            if i == WINDOW:
                logging.info(f"Pairs generated: {i * len(self.amenities_list)}")
                yield origins, destinations
                i = 0
                origins.clear()
                destinations.clear()


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
            origin_obj = self.data_to_id.get(origin_id)
            destination_obj = self.data_to_id.get(destination_id)
            destination_obj.distance = distance

            if self.results.get(origin_obj.address.full, None) is None:
                self.results[origin_obj.address.full] = origin_obj.to_dict()
                self.results[origin_obj.address.full]['points_of_interest'] = {}

            if self.results[origin_obj.address.full]['points_of_interest'].get(destination_obj.amenity) is None:
                self.results[origin_obj.address.full]['points_of_interest'][destination_obj.amenity] = []
            self.results[origin_obj.address.full]['points_of_interest'][destination_obj.amenity].append(destination_obj.to_dict())
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
        self.set_ids()
        self.pairs = Pairs(self.amenities_list, self.buildings_list)

    def get_buildings(self):
        logging.info("Start loading buildings info..")
        buildings = self.osm.get_buildings()
        address_location = {}
        for index, building in buildings.iterrows():
            address = Address(building.get('addr:street', None), building.get('addr:housenumber', None), building.get('addr:city', None))
            location = [building.geometry.centroid.x, building.geometry.centroid.y]
            if building.get('amenity') not in EXCLUDED_AMENITIES:
                poi = PointOfInterest(building.get('amenity'), address, location, building.get('name'), building.get('tags', "{}") or "{}")
                self.amenities_list.append(poi)
            elif address.is_valid:
                if address_location.get(address.full, None) is None:
                    self.buildings_list.append(ResidentialBuilding(address, location))
                    address_location[address.full] = location
        logging.info(f"Unique address {len(self.buildings_list)}, amenity {len(self.amenities_list)}")
        logging.info("Building info loading done")

    def set_ids(self):
        logging.info("Start building id adding")
        x = []
        y = []
        data = self.buildings_list + self.amenities_list
        for row in data:
            x.append(row.location[0])
            y.append(row.location[1])
        ids = self.graph.get_node_ids(x, y).values
        i = 0
        for id_ in ids:
            data[i].set_id(id_)
            self.id_to_data.add(id_=id_, data=data[i])
            i += 1
        logging.info("Done building id adding")

    def calc_paths(self):
        i = 1
        for origins, destinations in self.pairs.pairs:
            logging.info(f"Start calculating shortest paths for {i}/{self.pairs.chunk_amounts}. Pairs count {len(origins)}")
            dists = self.graph.shortest_path_lengths(origins, destinations)
            logging.info(f"Done calculating shortest paths for {i}/{self.pairs.chunk_amounts}. Calculated {len(dists)} paths")
            for orig, dest, dist in zip(origins, destinations, dists):
                self.results.add(orig.copy(), dest.copy(), dist)
            self.results.save_to_db()
            i += 1


db = MongoDatabase()
db.bulk_delete_points_of_interest()
b = Buildings()
b.calc_paths()
