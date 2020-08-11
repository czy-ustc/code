import datetime
import os


class file(object):
    _type = "file"

    def __init__(self, name=None):
        self._name = name or datetime.datetime.now().strftime(
            '%y-%m-%d %H-%M-%S')
        self._name += ".{}".format(self._type)

    def write(self, data):
        with open(self._name, "w", encoding="utf-8") as f:
            f.write(data)

    def add(self, data):
        with open(self._name, "a", encoding="utf-8") as f:
            f.write(data)

    def read(self):
        with open(self._name, "r", encoding="utf-8") as f:
            return f.read()

    def delete(self):
        if not os.path.exists(self._name):
            return False
        os.remove(self._name)
        return True

    def __call__(self, name=None):
        return file(name)
