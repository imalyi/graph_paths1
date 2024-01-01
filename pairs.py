import logging
from config import WINDOW


class Pairs:
    def __init__(self, pois, residential_houses):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pois = pois
        self.residential_houses_list = residential_houses
        self.pairs_iterator = iter(self.get_pairs())

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.pairs_iterator)

    @property
    def pairs_amount(self) -> int:
        return len(self.pois) * len(self.residential_houses_list)

    @property
    def chunk_amounts(self) -> int:
        return round(len(self.residential_houses_list) / WINDOW)

    def get_pairs(self):
        origins = []
        destinations = []
        i = 0
        for address in self.residential_houses_list:
            i += 1
            for amenity in self.pois:
                origins.append(address)
                destinations.append(amenity)
            if i >= WINDOW:
                self.logger.info(f"For {i} addresses and {len(self.pois)} amenities generated {len(destinations)} pairs")
                yield origins, destinations
                i = 0
                origins.clear()
                destinations.clear()
        self.logger.info(f"For {len(self.residential_houses_list) - self.chunk_amounts * WINDOW} addresses {len(destinations)} pairs generated")
        yield origins, destinations
