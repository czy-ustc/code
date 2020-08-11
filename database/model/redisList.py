from .model import Sequence


class redisList(Sequence):
    _type = "redisList"

    def __init__(self, db, name, **kwargs):
        """Initialization"""
        super().__init__(db, name, **kwargs)

    def __len__(self):
        """
        :return: length of the data set
        """
        return self._db.llen(self._name)

    def __str__(self):
        """
        :return: the describe of the data set
        """
        baseStr = super().__str__()
        length = self.__len__()
        baseStr += "\nindex\tvalue"
        if length <= 20:
            datas = self._db.lrange(self._name, 0, length - 1)
            for i in range(length):
                baseStr += ("\n{}\t{}".format(i, datas[i]))
        else:
            datas = self._db.lrange(self._name, 0, 4) + self._db.lrange(
                self._name, length - 5, length - 1)
            for i in range(11):
                if i < 5:
                    baseStr += ("\n{}\t{}".format(i, datas[i]))
                elif i == 5:
                    baseStr += "\n......"
                else:
                    baseStr += ("\n{}\t{}".format(length - 11 + i,
                                                  datas[i - 1]))
        return baseStr

    def __getitem__(self, key: str):
        """
        :param key: index of list
        """
        length = self.__len__()
        if isinstance(key, int):
            if key < 0:
                key += length
            if not 0 <= key < length:
                raise IndexError("list index out of range")
            return self._db.lindex(self._name, key)
        elif isinstance(key, slice):
            if key.start:
                start = key.start if key.start >= 0 else key.start + length
            else:
                start = 0
            if key.stop:
                stop = (key.stop if key.stop >= 0 else key.stop + length) - 1
            else:
                stop = length
            step = key.step
            return self._db.lrange(self._name, start, stop)[::step]
        else:
            raise TypeError(
                "list indices must be integers or slices, not {}".format(
                    key.__class__.__name__))

    def __delitem__(self, key):
        """
        :param key: index of list
        """
        length = self.__len__()
        if isinstance(key, int):
            if key < 0:
                key += length
            if not 0 <= key < length:
                raise IndexError("list index out of range")
            if key == 0:
                return self._db.lpop(self._name)
            elif key == length - 1:
                return self._db.rpop(self._name)
            tail = self._db.lrange(self._name, key, length - 1)
            result = tail.pop(0)
            self._db.ltrim(self._name, 0, key - 1)
            self._db.rpush(self._name, *tail)
            return result
        elif isinstance(key, slice):
            if key.start:
                start = key.start if key.start >= 0 else key.start + length
            else:
                start = 0
            if key.stop:
                stop = (key.stop if key.stop >= 0 else key.stop + length) - 1
            else:
                stop = length
            step = key.step
            if not step or step == 1:
                tail = self._db.lrange(self._name, stop, length - 1)
                self._db.ltrim(self._name, 0, start - 1)
                self._db.rpush(self._name, *tail)
            else:
                datas = self._db.lrange(self._name, 0, length - 1)[key]
                self._db.rpush(self._name, *datas)
                self._db.ltrim(self._name, length, length + len(datas) - 1)
        else:
            raise TypeError(
                "list indices must be integers or slices, not {}".format(
                    key.__class__.__name__))

    def __setitem__(self, key, value):
        """
        :param key: index of list
        :param value: new value
        """
        if key < 0:
            key += self.__len__()
        self._db.lset(self._name, key, value)

    def __iter__(self):
        """
        :return: all values in the list
        """
        return self._db.lrange(self._name, 0, self.__len__() - 1).__iter__()

    def __contains__(self, elem):
        """Check if the elem is in the data set."""
        return elem in self._db.lrange(self._name, 0, self.__len__() - 1)

    def append(self, object):
        """Append object to the end of the list."""
        self._db.rpush(self._name, object)

    def extend(self, iterable):
        """Extend list by appending elements from the iterable."""
        super().extend(iterable)
        self._db.rpush(self._name, *iterable)

    def pop(self, index=-1):
        """Remove and return item at index (default last)."""
        if index == -1:
            return self._db.rpop(self._name)
        elif index == 0:
            return self._db.lpop(self._name)
        else:
            return self.__delitem__(index)

    def clear(self):
        """Remove all items from list."""
        self._db.delete(self._name)

    def get(self):
        """Get all values in the data set."""
        return self._db.lrange(self._name, 0, self.__len__() - 1)

    @property
    def list(self):
        return self.get()

    @property
    def tuple(self):
        return tuple(self.get())

    @property
    def set(self):
        return set(self.get())
