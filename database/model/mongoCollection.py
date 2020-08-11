from bson import ObjectId

from .model import Container


class mongoCollection(Container):
    _type = "mongoCollection"

    def __init__(self, db, name, **kwargs):
        super().__init__(db, name, **kwargs)

    def __len__(self):
        return self._db.count_documents({})

    def __str__(self):
        baseStr = super().__str__()
        length = self.__len__()
        baseStr += "\nindex\tvalue"
        if length <= 20:
            datas = [data for data in self._db.find()]
            for i in range(length):
                baseStr += ("\n{}\t{}".format(i, datas[i]))
        else:
            datas = []
            for data in self._db.find():
                datas.append(data)
                if len(datas) >= 10:
                    break
            for i in range(10):
                baseStr += ("\n{}\t{}".format(i, datas[i]))
            baseStr += "\n({} more items......)".format(length - 10)
        return baseStr

    def __getitem__(self, key):
        """
        :param key: query criteria
                    excepted: index: int
                              range: slice
                              expression: dict(condiction, offset, limit)
        """
        key = super().__getitem__(key)
        if isinstance(key, int):
            return mongoDict(self._db.find().sort("_id",
                                                  1).skip(key).limit(1)[0],
                             db=self._db)
        elif isinstance(key, dict):
            offset = key.pop("offset", 0)
            limit = key.pop("limit", None)
            if "_id" in key:
                _id = key["_id"]
                if isinstance(_id, str):
                    key["_id"] = ObjectId(_id)
                elif isinstance(_id, dict):
                    for k, v in _id.items():
                        _id[k] = ObjectId(v) if isinstance(v, str) else v
            if limit:
                return [
                    mongoDict(data, db=self._db)
                    for data in self._db.find(key).skip(offset).limit(limit)
                ]
            else:
                return [
                    mongoDict(data, db=self._db)
                    for data in self._db.find(key).skip(offset)
                ]
        elif isinstance(key, slice):
            start = key.start
            stop = key.stop
            step = key.step
            datas = self._db.find().sort("_id",
                                         1).skip(start).limit(stop - start)
            return [mongoDict(data, db=self._db) for data in datas][::step]

    def __delitem__(self, key):
        """
        :param key: expression: dict(condiction)
        """
        super().__delitem__(key)
        self._db.delete_many(key)

    def __setitem__(self, key, value):
        """
        :param key: expression: dict(condiction)
        """
        super().__setitem__(key, value)
        self._db.update_many(key, {"$set": value})

    def __iter__(self):
        return self

    def __next__(self):
        if not hasattr(self, "_result"):
            self._result = self._db.find()
        result = next(self._result, None)
        if result:
            return mongoDict(result, db=self._db)
        else:
            raise StopIteration()

    def __contains__(self, elem):
        """Check if the elem is in the data set."""
        return bool(self._db.count_documents(elem))

    def append(self, object):
        object = super().append(object)
        object.pop("_id", None)
        self._db.insert_one(object)
        object.pop("_id", None)

    def extend(self, iterable):
        iterable = super().extend(iterable)
        if iterable:
            value = [dict(v) for v in iterable]
            for v in value:
                v.pop("_id", None)
            self._db.insert_many(value)

    def pop(self, index: int = -1):
        data = self.__getitem__(index)
        if isinstance(data, list):
            data = data[0]
        result = dict(data)
        data.clear()
        return result

    def clear(self):
        self._db.delete_many({})

    def get(self):
        return [mongoDict(data, db=self._db) for data in self._db.find()]

    @property
    def list(self):
        return self.get()

    @property
    def tuple(self):
        return tuple(self.get())


class mongoDict(dict):
    def __init__(self, *args, db=None):
        self._db = db
        self._id = args[0].pop("_id")
        dict.__init__(self, *args)

    def clear(self):
        self._db.delete_one({"_id": self._id})
        super().clear()

    def pop(self, key, *default):
        if default:
            result = super().pop(key, default[0])
        else:
            result = super().pop(key)
        self._db.update({"_id": self._id}, self)
        return result

    def popitem(self):
        item = super().popitem()
        self._db.update({"_id": self._id}, self)
        return item

    def setdefault(self, key, default):
        value = super().setdefault(key, default)
        self._db.update_one({"_id": self._id}, {"$set": {key: value}})
        return value

    def update(self, d):
        super().update(d)
        self._db.update_one({"_id": self._id}, {"$set": d})

    def __delitem__(self, key):
        super().__delitem__(key)
        self._db.update({"_id": self._id}, self)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._db.update_one({"_id": self._id}, {"$set": {key: value}})
