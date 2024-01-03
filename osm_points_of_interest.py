import logging
from data import Address, Location, Amenity, Tags, BuildingName, PointOfInterest


class OSMPointsOfInterest:
    def __init__(self, osm):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.osm = osm
        self._data = self.get_pois()
        self.poi_iterator = iter(self._data)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.poi_iterator)
        except StopIteration:
            self.poi_iterator = iter(self._data)
            raise StopIteration

    def get_pois(self):
        custom_filter = {'amenity': True}
        pois = self.osm.get_pois()
        pois_list = []
        for index, building in pois.iterrows():
            address = Address(building.get('addr:street', None), building.get('addr:housenumber', None),
                              building.get('addr:city', None))
            location = Location(building.geometry.centroid.x, building.geometry.centroid.y)
            amenity = Amenity(building.get('amenity'))
            if amenity.is_allowed:
                tags = Tags(building.get('tags', "{}") or "{}")
                name = BuildingName(building.get('name'))
                pois_list.append(PointOfInterest(amenity, address, location, name, tags))
        self.logger.info(f"Collected {len(pois_list)} POIs")
        return pois_list

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        return self._data[index]
