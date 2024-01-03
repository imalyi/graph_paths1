import logging
from id_to_data import IDToData


class Graph:
    def __init__(self, osm):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.osm = osm


class PandanaGraph:
    def __init__(self, osm):
        self.osm = osm
        nodes, edges = self.osm.get_network(nodes=True)
        self.graph = self.osm.to_graph(nodes, edges, graph_type="pandana")
        self.coords_to_ids = IDToData(self.graph)

    def __shortest_path_lengths(self, origins: list, destinations: list):
        return self.graph.shortest_path_lengths(origins, destinations)

    def get_node_ids(self, origins: list, destinations: list) -> list:
        return self.graph.get_node_ids(origins, destinations).values

    def calculate_shortest_path(self, origins, destinations):
        origins_ids = self.coords_to_ids.generate_nodes_ids(origins)
        destination_ids = self.coords_to_ids.generate_nodes_ids(destinations)
        dists = self.__shortest_path_lengths(origins_ids, destination_ids)
        return dists