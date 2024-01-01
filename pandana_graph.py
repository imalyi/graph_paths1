import logging


class PandanaGraph:
    def __init__(self, osm):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.osm = osm

    def shortest_path_lengths(self, origins, destinations):
        pass

    def get_node_ids(self, origins, destinations):
        pass


    def set_building_ids(self):
        logging.info("Start buildings id adding")
        x = []
        y = []
        data = self.buildings_list
        for row in data:
            x.append(row.location.x)
            y.append(row.location.y)
        ids = self.graph.get_node_ids(x, y).values
        i = 0
        for id_ in ids:
            data[i].set_id(id_)
            self.building_id_to_data.add(id_=id_, data=data[i])
            i += 1
        logging.info(f"Done buildings id adding")
