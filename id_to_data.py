from logging_config import configure_logging
import logging

configure_logging()


class IDToData:
    def __init__(self, graph):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.graph = graph

    def generate_nodes_ids(self, source):
        logging.info("Start generating nodes ids")
        x = []
        y = []
        for row in source:
            x.append(row.location.x)
            y.append(row.location.y)
        ids = self.graph.get_node_ids(x, y)
        return ids
