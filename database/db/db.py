import re

from ..utils.log import logger


class dbObject(object):
    _name = "dbObject"

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
        return []

    def keys(self, pattern=""):
        pattern = re.compile(pattern)
        result = []
        for key in self._keyList:
            if re.search(pattern, key) is not None:
                result.append(key)
        return result

    def __len__(self):
        return len(self._keyList)

    def __str__(self):
        host = '"{}"'.format(self._host)
        user = '"{}"'.format(self._username) if self._username else str(
            self._username)
        baseStr = "<{}(host={} port={} user={} db={})>".format(
            self._name, host, self._port, user, str(self._info))
        return baseStr

    def __getitem__(self, key: str):
        """
        :param key: name of database
                    pattern of database("$re pattern")
        :return: database(if name) databases(if pattern)
        """
        if key in self._keyList:
            return key
        if "$re" in key:
            key = key.replace("$re ", "")
            pattern = re.compile(key)
            result = []
            for v in self._keyList:
                if re.search(pattern, v) is not None:
                    result.append(v)
            return result
        else:
            raise KeyError(
                "key must be the name of the keys in database or a pattern like '$re pattern'"
            )

    _getitem = __getitem__

    def __delitem__(self, key):
        v = self._getitem(key)
        if v:
            logger.warning(
                "Try to delete the key/collection/table({})".format(v))
        return v

    def __setitem__(self, key, value):
        v = self._getitem(key)
        return v

    def __iter__(self):
        return self._keyList.__iter__()

    def __contains__(self, key):
        return key in self._keyList
