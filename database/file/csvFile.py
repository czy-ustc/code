import csv

from ..utils.log import logger
from .file import file


class csvFile(file):
    _type = "csv"

    def __init__(self, name=None):
        super().__init__(name)

    def write(self, data):
        with open(self._name, "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            try:
                writer.writerows(data)
            except Exception as e:
                logger.warning(e)
                return False
        return True

    def add(self, data):
        with open(self._name, "a", encoding="utf-8") as f:
            writer = csv.writer(f)
            try:
                writer.writerows(data)
            except Exception as e:
                logger.warning(e)
                return False
        return True

    def read(self):
        with open(self._name, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            return [row for row in reader]

    def delete(self):
        super().delete()

    def __call__(self, name=None):
        return csvFile(name)
