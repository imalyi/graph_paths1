from database import MongoDatabase
from data import ResidentialBuilding, PointOfInterest
import logging

MAX_DISTANCE = 1_000


class Result:
    def __init__(self, origin: ResidentialBuilding, destination: PointOfInterest, distance: float):
        self.destination = destination
        self.origin = origin
        self.distance = distance

    def __str__(self):
        return f"{str(self.origin)} - {str(self.destination)})"

    def is_distance_acceptable(self):
        if self.distance <= MAX_DISTANCE:
            return True
        return False


class Results:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.results = {}
        self.db = MongoDatabase()

    def add(self, result: Result) -> None:
        if not result.is_distance_acceptable():
            return
        self.results.setdefault(result.origin, {})
        self.results[result.origin].setdefault(str(result.destination.amenity), set()).add((result.destination, result.distance,))

    def _prepare_to_saving(self):
        prepared_data = []
        for origin, pois in self.results.items():
            data_row = origin.to_dict()
            data_row['points_of_interest'] = {}
            for poi_type, poi_data in pois.items():
                if data_row['points_of_interest'].get(poi_type) is None:
                    data_row['points_of_interest'][poi_type] = []
                for poi, distance in poi_data:
                    poi_with_dist = poi.to_dict()
                    poi_with_dist['distance'] = distance
                    data_row['points_of_interest'][poi_type].append(poi_with_dist)
            prepared_data.append(data_row)
        return prepared_data

    def save_to_db(self):
        prepared_data = self._prepare_to_saving()
        self.logger.info(f"Start saving {len(self.results)} addresses")
        self.db.insert_many(prepared_data)
        self.logger.info(f"Done saving {len(self.results)} addresses")
        self.results.clear()
