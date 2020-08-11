from .model import Sequence


class redisSet(Sequence):
    _type = "redisSet"

    def __init__(self, db, name, **kwargs):
        """Initialization"""
        super().__init__(db, name, **kwargs)

    def __len__(self):
        """
        :return: length of the data set
        """
        return self._db.scard(self._name)

    def __str__(self):
        """
        :return: the describe of the data set
        """
        baseStr = super().__str__()
        length = self.__len__()
        baseStr += "\nindex\tvalue"
        if length <= 20:
            datas = list(self._db.smembers(self._name))
            for i in range(length):
                baseStr += ("\n{}\t{}".format(i, datas[i]))
        else:
            datas = []
            for i in range(10):
                datas.append(self._db.srandmember(self._name))
            for i in range(11):
                if i < 5:
                    baseStr += ("\n{}\t{}".format(i, datas[i]))
                elif i == 5:
                    baseStr += "\n......"
                else:
                    baseStr += ("\n{}\t{}".format(length - 11 + i,
                                                  datas[i - 1]))
        return baseStr

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._db.srandmember(self._name)
        elif isinstance(key, str):
            if self._db.sismember(self._db, key):
                return key
            else:
                raise KeyError(key)

    def __delitem__(self, key):
        self.pop(key)

    def __setitem__(self, key, value):
        if self._db.srem(self._name, key):
            self._db.sadd(self._name, value)
        else:
            raise KeyError(key)

    def __iter__(self):
        """
        :return: all values in the set
        """
        return self._db.smembers(self._name).__iter__()

    def __contains__(self, value):
        """Check if the elem is in the data set."""
        return self._db.sismember(self._name, value)

    def append(self, object):
        """Append object to the end of the list."""
        self._db.sadd(self._name, object)

    def extend(self, iterable):
        """Extend set by appending elements from the iterable."""
        super().extend(iterable)
        self._db.sadd(self._name, *iterable)

    def pop(self, item=None):
        """
        Remove and return item.
        :param item: the item to remove
        """
        if item:
            if self._db.srem(self._name, item):
                return item
            else:
                raise KeyError(item)
        else:
            return self._db.spop(self._name)

    def clear(self):
        """Remove all items from set."""
        self._db.delete(self._name)

    def get(self):
        return self._db.smembers(self._name)

    @property
    def set(self):
        return self.get()

    @property
    def list(self):
        return list(self.get())

    @property
    def tuple(self):
        return tuple(self.get())
