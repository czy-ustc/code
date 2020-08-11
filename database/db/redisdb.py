from ..model.redisHash import redisHash
from ..model.redisList import redisList
from ..model.redisSet import redisSet
from ..model.redisStr import redisStr
from ..model.redisZset import redisZset
from .db import dbObject


class redisdb(dbObject):
    _name = "redisdb"

    def __init__(self,
                 host=None,
                 port=None,
                 username=None,
                 password=None,
                 db=None,
                 info=None):
        super().__init__(host=host,
                         port=port,
                         username=username,
                         password=password,
                         db=db,
                         info=info)

    @property
    def _keyList(self):
        return self._db.keys("*")

    def __str__(self):
        baseStr = super().__str__()
        baseStr += "\nkeys:{}".format(str(self._keyList))
        return baseStr

    def __len__(self):
        return self._db.dbsize()

    def __getitem__(self, key):
        key = super().__getitem__(key)
        if isinstance(key, str):
            _type = self._db.type(key)
            if _type == "string":
                return redisStr(self._db,
                                key,
                                host=self._host,
                                port=self._port,
                                username=self._username,
                                password=self._password,
                                info=self._info)
            elif _type == "list":
                return redisList(self._db,
                                 key,
                                 host=self._host,
                                 port=self._port,
                                 username=self._username,
                                 password=self._password,
                                 info=self._info)
            elif _type == "set":
                return redisSet(self._db,
                                key,
                                host=self._host,
                                port=self._port,
                                username=self._username,
                                password=self._password,
                                info=self._info)
            elif _type == "zset":
                return redisZset(self._db,
                                 key,
                                 host=self._host,
                                 port=self._port,
                                 username=self._username,
                                 password=self._password,
                                 info=self._info)
            elif _type == "hash":
                return redisHash(self._db,
                                 key,
                                 host=self._host,
                                 port=self._port,
                                 username=self._username,
                                 password=self._password,
                                 info=self._info)
        elif isinstance(key, list):
            results = []
            for k in key:
                results.append(self.__getitem__(k))
            return results

    def __setitem__(self, key, value):
        """
        Initialize database
        :param key: the name of key
        :param value: a non-empty str(str,bytes,int,float) like "string"/b"bytes"/1/.0 -> string
                                  list like [1, 2, 3] -> list
                                  set like {1, 2, 3} -> set
                                  tuple like (("key", 100), ) -> zset
                                  dict like {key: value} -> hash
        """
        if not isinstance(key, str):
            raise KeyError("key must be a str")
        if key in self._keyList and not any(
            [value, isinstance(value, int),
             isinstance(value, float)]):
            raise KeyError("key had exists")
        if not any([value, isinstance(value, int), isinstance(value, float)]):
            raise TypeError("value must be non-empty")
        if any(
            [isinstance(value, _type) for _type in [str, bytes, int, float]]):
            self._db.set(key, value)
        elif isinstance(value, list):
            self._db.rpush(key, *value)
        elif isinstance(value, set):
            self._db.sadd(key, *value)
        elif isinstance(value, tuple):
            self._db.zadd(key, dict(value))
        elif isinstance(value, dict):
            self._db.hmset(key, value)

    def __delitem__(self, key):
        result = super().__delitem__(key)
        if isinstance(result, str):
            self._db.delete(key)
        else:
            raise KeyError("key must be the name of keys in database")
