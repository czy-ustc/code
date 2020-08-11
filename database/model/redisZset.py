from .model import Sequence


class redisZset(Sequence):
    _type = "redisZset"

    def __init__(self, db, name, **kwargs):
        """Initialization"""
        super().__init__(db, name, **kwargs)

    def __len__(self):
        """
        :return: length of the data set
        """
        return self._db.zcard(self._name)

    def __str__(self):
        """
        :return: the describe of the data set
        """
        baseStr = super().__str__()
        length = self.__len__()
        baseStr += "\nindex\tvalue\tcount"
        if length <= 20:
            datas = self._db.zrevrange(self._name,
                                       0,
                                       length - 1,
                                       withscores=True)
            for i in range(length):
                baseStr += ("\n{}\t{}\t{}".format(i, datas[i][0], datas[i][1]))
        else:
            datas = self._db.zrevrange(
                self._name, 0, 4, withscores=True) + self._db.zrevrange(
                    self._name, length - 5, length - 1, withscores=True)
            for i in range(11):
                if i < 5:
                    baseStr += ("\n{}\t{}\t{}".format(i, datas[i][0],
                                                      datas[i][1]))
                elif i == 5:
                    baseStr += "\n......"
                else:
                    baseStr += ("\n{}\t{}\t{}".format(i + length - 11,
                                                      datas[i - 1][0],
                                                      datas[i - 1][1]))
        return baseStr

    def __getitem__(self, key):
        """
        :param key: index: int
                    name: str
                    rank: slice
                    range: tuple
        """
        length = self.__len__()
        if isinstance(key, int):
            if key < 0:
                key += length
            if not 0 <= key < length:
                raise IndexError("list index out of range")
            return self._db.zrevrange(self._name, key, key, withscores=True)[0]
        elif isinstance(key, slice):
            start = key.start
            stop = key.stop
            step = key.step
            start = start or 0
            stop = stop or -1
            map(lambda x: x if x >= 0 else x + length, [start, stop])
            return self._db.zrevrange(self._name,
                                      start,
                                      stop - 1,
                                      withscores=True)[::step]
        elif isinstance(key, str):
            if self._db.zrank(self._name, key) is not None:
                return (key, self._db.zincrby(self._name, 0, key))
            else:
                raise KeyError(key)
        elif isinstance(key, tuple):
            result = self._db.zrangebyscore(self._name,
                                            key[0],
                                            key[1],
                                            withscores=True)
            result.reverse()
            return result

    def __delitem__(self, key):
        """
        :param key: index: int
                    name: str
                    rank: slice
                    range: tuple
        """
        length = self.__len__()
        if isinstance(key, int):
            if key < 0:
                key += length
            if not 0 <= key < length:
                raise IndexError("list index out of range")
            self._db.zremrangebyscore(self._name, key, key)
        elif isinstance(key, slice):
            start = key.start
            stop = key.stop
            step = key.step
            start = start or 0
            stop = stop or -1
            map(lambda x: x if x >= 0 else x + length, [start, stop])
            if not step:
                self._db.zremrangebyrank(self._name, length - stop,
                                         length - start - 1)
            else:
                datas = self._db.zrevrange(self._name, 0, length - 1)[key]
                self._db.zrem(self._name, *datas)
        elif isinstance(key, str):
            self._db.zrem(self._name, key)
        elif isinstance(key, tuple):
            return self._db.zremrangebyscore(self._name, key[0], key[1])

    def __setitem__(self, key, value):
        """
        :param key: index: int
                    name: str
        :param value: new value
        """
        if isinstance(key, int):
            k = self.__getitem__(key)[0]
            self._db.zadd(self._name, {k: value})
        elif isinstance(key, str):
            self._db.zadd(self._name, {key: value})

    def __iter__(self):
        """
        :return: all values in the zset
        """
        return self._db.zrevrange(self._name,
                                  0,
                                  self.__len__() - 1,
                                  withscores=True).__iter__()

    def __contains__(self, elem):
        """Check if the elem is in the data set."""
        return not self._db.zrank(self._name, elem) is None

    def append(self, object):
        """Append object to the end of the zset."""
        if isinstance(object, dict):
            self._db.zadd(self._name, object)
        if isinstance(object, tuple):
            self._db.zadd(self._name, {object[0]: object[1]})

    def extend(self, iterable):
        """Extend zset by appending elements from the iterable."""
        super().extend(iterable)
        if isinstance(iterable, dict):
            self._db.zadd(self._name, iterable)
        else:
            self._db.zadd(self._name, dict(iterable))

    def pop(self, index=-1):
        """Remove and return item at index (default last)."""
        key = self.__getitem__(index)
        self._db.zrem(self._name, key[0])
        return key

    def clear(self):
        """Remove all items from list."""
        self._db.delete(self._name)

    def get(self):
        """Get all values in the data set."""
        return tuple(
            self._db.zrevrange(self._name,
                               0,
                               self.__len__() - 1,
                               withscores=True))

    @property
    def tuple(self):
        return self.get()

    @property
    def dict(self):
        return dict(self.get())

    @property
    def list(self):
        return [
            list(d) for d in self._db.zrevrange(
                self._name, 0, self.__len__() - 1, withscores=True)
        ]

    @property
    def set(self):
        return set(self.get())
