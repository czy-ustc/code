from .model import Sequence


class redisHash(Sequence):
    _type = "redisHash"

    def __init__(self, db, name, **kwargs):
        """Initialization"""
        super().__init__(db, name, **kwargs)

    def __len__(self):
        """
        :return: length of the data set
        """
        return self._db.hlen(self._name)

    def __str__(self):
        """
        :return: the describe of the data set
        """
        baseStr = super().__str__()
        length = self.__len__()
        baseStr += "\nkey\tvalue"
        if length <= 20:
            datas = self._db.hgetall(self._name)
            for k, v in datas.items():
                baseStr += ("\n{}\t{}".format(k, v))
        else:
            keys = self._db.hkeys(self._name)[:10]
            values = self._db.hmget(self._name, keys)
            for k, v in zip(keys, values):
                baseStr += ("\n{}\t{}".format(k, v))
            baseStr += "\n({} more items......)".format(length - 10)
        return baseStr

    def __getitem__(self, key):
        """
        :param key: index of list
        """
        result = self._db.hget(self._name, key)
        if not result:
            raise KeyError(key)
        return result

    def __delitem__(self, key):
        """
        :param key: index of list
        """
        super().__delitem__(key)
        self._db.hdel(self._name, key)

    def __setitem__(self, key, value):
        """
        :param key: index of list
        :param value: new value
        """
        self._db.hset(self._name, key, value)

    def __iter__(self):
        """
        :return: all values in the hash
        """
        return self._db.hgetall(self._name).items().__iter__()

    def __contains__(self, elem):
        """Check if the elem is in the data set."""
        return elem in self._db.hkeys(self._name)

    def append(self, object):
        """Append object to the end of the hash."""
        for k, v in object.items():
            self._db.hset(self._name, k, v)

    def extend(self, iterable):
        """Extend hash by appending elements from the iterable."""
        super().extend(iterable)
        self._db.hmset(self._name, iterable)

    def pop(self, key):
        """Remove and return item."""
        result = self._db.hget(self._name, key)
        if result:
            self._db.hdel(self._name, key)
        return result

    def clear(self):
        """Remove all items from list."""
        self._db.delete(self._name)

    def get(self):
        """Get all values in the data set."""
        return self._db.hgetall(self._name)

    @property
    def dict(self):
        return self.get()

    @property
    def tuple(self):
        return tuple(self._db.hgetall(self._name).items())

    @property
    def list(self):
        return [list(data) for data in self._db.hgetall(self._name).items()]

    @property
    def set(self):
        return set(self._db.hgetall(self._name).items())
