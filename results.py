from databas import MongoDatabase
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
        self.results.setdefault(result.origin, {'points_of_interest': {}})
        self.results[result.origin]['points_of_interest'].setdefault(str(result.destination.amenity), set()).add(result.destination)

    def save_to_db(self):
        self.logger.info(f"Start saving {len(self.results)} addresses")
        self.db.insert_many(self.results)
        self.logger.info(f"Done saving {len(self.results)} addresses")
        self.results.clear()
