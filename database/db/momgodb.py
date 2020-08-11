from ..model.mongoCollection import mongoCollection
from .db import dbObject


class mongodb(dbObject):
    _name = "mongodb"

    def __init__(self,
                 host: str = None,
                 port: int = None,
                 username: str = None,
                 password: str = None,
                 db=None,
                 info: tuple = None):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._db = db
        self._info = info

    @property
    def _keyList(self):
        return self._db.list_collection_names()

    def __str__(self):
        baseStr = super().__str__()
        baseStr += "\ncollections:{}".format(str(self._keyList))
        return baseStr

    def __getitem__(self, key):
        key = super().__getitem__(key)
        if isinstance(key, str):
            return mongoCollection(self._db[key],
                                   key,
                                   host=self._host,
                                   port=self._port,
                                   username=self._username,
                                   password=self._password,
                                   info=self._info)
        elif isinstance(key, list):
            results = []
            for k in key:
                results.append(
                    mongoCollection(self._db[k],
                                    k,
                                    host=self._host,
                                    port=self._port,
                                    username=self._username,
                                    password=self._password,
                                    info=self._info))
            return results

    def __delitem__(self, key):
        result = super().__delitem__(key)
        if isinstance(result, str):
            self._db.drop_collection(key)
        else:
            raise KeyError("key must be the name of keys in database")

    def __setitem__(self, key, value):
        """
        Initialize database
        :param key: the name of collection
        :param value: a non-empty list to initialize database
        """
        if not isinstance(key, str):
            raise KeyError("key must be a str")
        if key in self._keyList:
            raise KeyError("key had exists")
        if not isinstance(value, list) or len(value) == 0:
            raise TypeError("value must be a no-empty list")
        db = mongoCollection(self._db[key],
                             key,
                             host=self._host,
                             port=self._port,
                             username=self._username,
                             password=self._password,
                             info=self._info)
        db.extend(value)
        return db
