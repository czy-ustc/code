import json

from ..utils.log import logger
from .file import file


class jsonFile(file):
    _type = "json"

    def __init__(self, name=None):
        super().__init__(name)

    def write(self, data):
        with open(self._name, "w", encoding="utf-8") as f:
            try:
                json.dump(data, f)
            except Exception as e:
                logger.warning(e)
                return False
        return True

    def add(self, data):
        with open(self._name, "a", encoding="utf-8") as f:
            try:
                json.dump(data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                logger.warning(e)
                return False
        return True

    def read(self):
        with open(self._name, "r", encoding="utf-8") as f:
            try:
                result = json.load(f)
            except Exception as e:
                logger.warning(e)
                return False
        return result

    def delete(self):
        super().delete()

    def __call__(self, name=None):
        return jsonFile(name)
