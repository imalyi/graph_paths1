
class PathCalculator:
    def __init__(self, graph):
        self.results = Results()
        self.pairs = Pairs(self.amenities_list, self.buildings_list)
        self.graph = graph

    def calc_paths(self):
        i = 1
        for origins, destinations in self.pairs.pairs:
            logging.info(f"Start calculating shortest paths for {i}/{self.pairs.chunk_amounts}. Pairs count {len(origins)}")
            dists = self.graph.shortest_path_lengths(origins, destinations)
            logging.info(f"Done calculating shortest paths for {i}/{self.pairs.chunk_amounts}. Calculated {len(dists)} paths for {len(list(set(origins.copy())))} points")
            for orig, dest, dist in zip(origins, destinations, dists):
                self.results.add(orig.copy(), dest.copy(), dist)
            self.results.save_to_db()
            i += 1