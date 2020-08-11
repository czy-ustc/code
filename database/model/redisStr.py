from redis import StrictRedis

from .model import Pair


class redisStr(Pair):
    _type = "redisStr"

    def __init__(self, db, name, **kwargs):
        super().__init__(db, name, **kwargs)
        host = self._objectInfo["host"]
        port = self._objectInfo["port"]
        password = self._objectInfo["password"]
        db = self._objectInfo["info"][0]
        self.encode_db = StrictRedis(host=host,
                                     port=port,
                                     password=password,
                                     db=db)

    def __len__(self):
        return self._db.strlen(self._name)

    def __str__(self):
        baseStr = super().__str__()
        length = self.__len__()
        _ty = self._db.object("encoding", self._name)
        if length <= 100:
            baseStr += "\nvalue:{} (length:{} type:{})".format(
                self._db.get(self._name), length, _ty)
        else:
            baseStr += "\nvalue:{}......{} (length:{} type:{})".format(
                self.encode_db.getrange(self._name, 0, 24),
                self.encode_db.substr(self._name, length - 25), length, _ty)
        return baseStr

    def get(self):
        return self._db.get(self._name)

    def set(self, value):
        self._db.set(self._name, value)

    def clear(self):
        self._db.delete(self._name)

    @property
    def str(self):
        return self._db.get(self._name)

    @property
    def bytes(self):
        return self.encode_db.get(self._name)

    @property
    def int(self):
        return int(self._db.get(self._name))

    @property
    def float(self):
        return float(self._db.get(self._name))
