import json
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
EXCLUDED_AMENITIES = ['unknown', 'parking', 'waste_basket', 'bicycle_parking', 'fuel', 'toilets', 'bench']


class Location:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}; {self.y})"

    def __repr__(self):
        return f"({self.x}; {self.y})"

    def to_dict(self):
        return [self.x, self.y]


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


class BuildingName:
    def __init__(self, name: str) -> None:
        if name is None:
            name = 'unknown'
        self.name = name.strip()

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class ResidentialBuilding:
    def __init__(self, address: Address, location: Location):
        self.address = address
        self.location = location
        self.id_ = None
        self.data_source = 'https://www.openstreetmap.org'

    def to_dict(self):
        return {
            'address': self.address.to_dict(),
            'location': self.location.to_dict(),
            'source': self.data_source
        }

    def __str__(self):
        return f"{self.address}"


class Amenity:
    def __init__(self, name: str) -> None:
        if name is None:
            name = 'unknown'
        self.name = name.lower()

    @property
    def is_allowed(self):
        if self.name in EXCLUDED_AMENITIES:
            return False
        return True

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Tags:
    def __init__(self, tags: str) -> None:
        try:
            self.tags = json.loads(tags)
        except Exception:
            logging.warning(f"Error convert {tags} to dict", exc_info=True)
            self.tags = {}

    def to_dict(self):
        return self.tags

    def __str__(self):
        return json.dumps(self.tags)

    def __repr__(self):
        return json.dumps(self.tags)


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

    def __str__(self):
        return f"{self.name}-{self.address}-{self.tags}"


