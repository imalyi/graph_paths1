from databas import MongoDatabase

MAX_DISTANCE = 1_000


class Result:
    def __init__(self, origin_id: int, destination_id: int, distance: float):
        self.destination = destination_id
        self.origin = origin_id
        self.distance = distance

    def __str__(self):
        return self.destination

    def is_distance_acceptable(self):
        if self.distance <= MAX_DISTANCE:
            return True
        return False


class Results:
    def __init__(self, poi_ids_to_data, building_id_to_data):
        self.results = {}
        self.poi_ids_to_data = poi_ids_to_data
        self.building_id_to_data = building_id_to_data

        self.db = MongoDatabase()

    def add(self, origin, destination, distance) -> bool:
        origin_objs = self.building_id_to_data.get(origin_id)
        destination_objs = self.poi_ids_to_data.get(destination_id)
        for origin_obj in origin_objs:
            for destination_obj in destination_objs:
                destination_obj.distance = distance
                if self.results.get(origin_obj.address.full) is None:
                    self.results[origin_obj.address.full] = origin_obj.to_dict()
                    self.results[origin_obj.address.full]['points_of_interest'] = {}

                if self.results[origin_obj.address.full]['points_of_interest'].get(str(destination_obj.amenity)) is None:
                    self.results[origin_obj.address.full]['points_of_interest'][str(destination_obj.amenity)] = []
                self.results[origin_obj.address.full]['points_of_interest'][str(destination_obj.amenity)].append(destination_obj.to_dict())

    def save_to_db(self):
        logging.info(f"Start saving {len(self.results)} addresses")
        self.db.insert_many(self.results)
        logging.info(f"Done saving {len(self.results)} addresses")
        self.results.clear()
