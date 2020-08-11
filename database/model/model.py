class Model(object):
    _type = "Model"

    def __init__(self, db, name, **kwargs):
        """
        **kwargs: host, port, username, password, info
        """
        self._db = db
        self._name = name
        self._objectInfo = kwargs

    @property
    def name(self):
        return self._name

    def __len__(self):
        pass

    def __str__(self):
        host = '"{}"'.format(self._objectInfo["host"])
        user = '"{}"'.format(self._objectInfo["username"]
                             ) if self._objectInfo["username"] else str(
                                 self._objectInfo["username"])
        baseStr = '<{}(host={} port={} user={} db={} key="{}")>'.format(
            self._type, host, self._objectInfo["port"], user,
            str(self._objectInfo["info"]), self._name)
        return baseStr
    
    __repr__ = __str__


class Pair(Model):
    def __init__(self, db, name, **kwargs):
        super().__init__(db, name, **kwargs)

    def __len__(self):
        return super().__len__()

    def __str__(self):
        return super().__str__()

    def get(self):
        pass

    def set(self, value):
        pass

    @property
    def str(self):
        pass

    @property
    def bytes(self):
        pass

    @property
    def int(self):
        pass

    @property
    def float(self):
        pass


class Sequence(Model):
    def __init__(self, db, name, **kwargs):
        super().__init__(db, name, **kwargs)

    def __len__(self):
        return super().__len__()

    def __str__(self):
        return super().__str__()

    def __getitem__(self, key):
        pass

    def __delitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def __contains__(self, value):
        pass

    def append(self, object):
        """Append object to the end of the list."""
        pass

    def extend(self, iterable):
        """Extend list by appending elements from the iterable."""
        if not hasattr(iterable, "__iter__"):
            raise TypeError("{} object is not iterable".format(
                iterable.__class__.__name__))

    def pop(self, *args):
        """Remove and return item at index (default last)."""
        pass

    def clear(self):
        """Remove all items from list."""
        pass

    def get(self):
        """Get all values in the data set."""
        pass


class Container(Model):
    def __init__(self, db, name, **kwargs):
        """Initialization"""
        super().__init__(db, name, **kwargs)

    def __len__(self):
        """Return the items count of the container."""
        return super().__len__()

    def __str__(self):
        """Return the description of the container."""
        return super().__str__()

    def __getitem__(self, key) -> list or dict:
        """Find all items that meet the criteria."""
        if isinstance(key, int):
            length = self.__len__()
            if key < 0:
                key += length
            if not 0 <= key < length:
                raise IndexError("list index out of range")
            return key
        elif isinstance(key, slice):
            length = self.__len__()
            start = key.start or 0
            stop = key.stop or length
            step = key.step or 1
            for i in [start, stop]:
                i = i if i >= 0 else i + length
            return slice(start, stop, step)
        elif isinstance(key, dict):
            offset = key.get("offset", 0)
            limit = key.get("limit", 0)
            for i in [offset, limit]:
                if not isinstance(i, int):
                    raise TypeError("{} must be an integer".format(i))
            return key
        else:
            raise TypeError(
                "list indices must be integers, slices or dicts, not {}".
                format(key.__class__.__name__))

    def __delitem__(self, key: dict):
        """Delete all items that meet the criteria."""
        if not isinstance(key, dict):
            raise TypeError("list indices must be dicts, not {}".format(
                key.__class__.__name__))

    def __setitem__(self, key: dict, value: dict):
        """Modify all items that meet the criteria."""
        if not isinstance(key, dict):
            raise TypeError("list indices must be dicts, not {}".format(
                key.__class__.__name__))
        if not isinstance(value, dict):
            raise TypeError("a dict needed to modify the items, not {}".format(
                key.__class__.__name__))

    def __iter__(self):
        """Return all items in the container."""
        pass

    def __next__(self):
        """Return the next item in the container."""
        pass

    def append(self, object: dict):
        """Append object to the end of the list."""
        if not isinstance(object, dict):
            raise TypeError("object must be a dict")
        return dict(object)

    def extend(self, iterable):
        """Extend list by appending elements from the iterable."""
        if not hasattr(iterable, "__iter__"):
            raise TypeError("{} object is not iterable".format(
                iterable.__class__.__name__))
        return [dict(i) for i in iterable]

    def pop(self, index: int = -1):
        """Remove and return item at index (default last)."""
        pass

    def clear(self):
        """Remove all items from list."""
        pass

    def get(self):
        """Get all values in the data set."""
        pass
