from logging_config import configure_logging
import logging

configure_logging()


class IDToData:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.data = {}

    def add(self, id_, data):
        if self.data.get(id_) is None:
            self.data[id_] = [data]
            return
        else:
            self.logger.info(f"Graph node with ID:{id_} already exists in DB")
            self.data[id_].append(data)

    def get(self, id_):
        try:
            return self.data[id_]
        except KeyError:
            self.logger.error(f"Cant find id {id_}")
