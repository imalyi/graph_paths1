from pairs import Pairs
from results import Results, Result
from pairs import Pairs
import logging
from id_to_data import IDToData


class PathCalculator:
    def __init__(self, graph, pairs: Pairs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.graph = graph
        self.pairs = pairs
        self.results = Results()

    def calc_paths(self):
        i = 1
        for origins, destinations in self.pairs:
            logging.info(
                f"Start calculating shortest paths for {i}/{self.pairs.chunk_amounts}. Pairs count {len(origins)}")
            dists = self.graph.calculate_shortest_path(origins, destinations)
            logging.info(
                f"Done calculating shortest paths for {i}/{self.pairs.chunk_amounts}. Calculated {len(dists)} paths for {len(list(set(origins.copy())))} points")
            for orig, dest, dist in zip(origins, destinations, dists):
                result = Result(orig, dest, dist)
                self.results.add(result)
            i += 1
            self.results.save_to_db()
