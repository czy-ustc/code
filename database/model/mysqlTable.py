from ..utils.log import logger
from .model import Container


class mysqlTable(Container):
    _type = "mysqlTablet"

    def __init__(self, db, name, **kwargs):
        super().__init__(db, name, **kwargs)

    def __len__(self):
        sql = "SELECT * FROM {}".format(self._name)
        num = self._db.execute(sql)
        return num

    def __str__(self):
        baseStr = super().__str__()
        length = self.__len__()
        fields = ["index"] + [filed[0] for filed in self._db.description]
        baseStr += ("\n" + "\t".join(["{:<10}".format(str(d))
                                      for d in fields]))
        if length <= 20:
            datas = self._db.fetchall()
            for i in range(length):
                data = [i]
                data.extend(datas[i])
                baseStr += ("\n" +
                            "\t".join(["{:<10}".format(str(d)) for d in data]))
        else:
            "LIMIT 3 OFFSET 1"
            sql = "SELECT * FROM {} LIMIT 5".format(str(self._name))
            self._db.execute(sql)
            datas = list(self._db.fetchall())
            sql = "SELECT * FROM {} LIMIT 5 OFFSET {}".format(
                str(self._name), length - 5)
            self._db.execute(sql)
            datas += list(self._db.fetchall())
            for i in range(11):
                if i < 5:
                    _data = [i]
                    _data.extend(datas[i])
                    baseStr += ("\n" + "\t".join(
                        ["{:<10}".format(str(data)) for data in _data]))
                elif i == 5:
                    baseStr += "\n......"
                else:
                    _data = [length - 11 + i]
                    _data.extend(datas[i - 1])
                    baseStr += ("\n" + "\t".join(
                        ["{:<10}".format(str(data)) for data in _data]))
        return baseStr

    def __getitem__(self, key):
        """
        :param key: query criteria
                        excepted: index: int
                                  range: slice
                                  expression: str
        """
        if not hasattr(self, "_fields"):
            sql = "SELECT * FROM {} LIMIT 1;".format(self._name)
            self._db.execute(sql)
            self._fields = [filed[0] for filed in self._db.description]
        key = super().__getitem__(key)
        if isinstance(key, int):
            sql = "SELECT * FROM {} LIMIT 1 OFFSET {}".format(self._name, key)
            self._db.execute(sql)
            result = self._db.fetchone()
            return mysqlDict(dict(zip(self._fields, result)),
                             db=self._db,
                             name=self._name)
        elif isinstance(key, slice):
            start = key.start
            stop = key.stop
            sql = "SELECT * FROM {} LIMIT {} OFFSET {}".format(
                self._name, stop - start, start)
            self._db.execute(sql)
            results = self._db.fetchall()[::key.step]
        elif isinstance(key, dict):
            sql = "SELECT * FROM {} ".format(self._name)
            for k, v in key.items():
                sql += "{} {}".format(k, v) if v else ""
            sql += ";"
            self._db.execute(sql)
            results = self._db.fetchall()
        _results = []
        for result in results:
            _results.append(dict(zip(self._fields, result)))
        return [
            mysqlDict(data, db=self._db, name=self._name) for data in _results
        ]

    def __delitem__(self, key):
        """
        :param key: expression: str
        """
        super().__delitem__(key)
        sql = "DELETE FROM {} ".format(self._name)
        for k, v in key.items():
            sql += "{} {}".format(k, v) if v else ""
        try:
            self._db.execute(sql)
            self._db.connection.commit()
        except Exception as e:
            logger.warning(e)
            self._db.connection.rollback()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        updateStr = ""
        for k, v in value.items():
            if isinstance(v, str):
                v = "'{}'".format(v)
            updateStr += "{}={},".format(k, v)
        updateStr = updateStr[:-1]
        sql = "UPDATE {} SET {} ".format(self._name, updateStr)
        for k, v in key.items():
            sql += "{} {}".format(k, v) if v else ""
        try:
            self._db.execute(sql)
            self._db.connection.commit()
        except Exception as e:
            logger.warning(e)
            self._db.connection.rollback()

    def __iter__(self):
        if not hasattr(self, "_fields"):
            sql = "SELECT * FROM {} LIMIT 1;".format(self._name)
            self._db.execute(sql)
            self._fields = [filed[0] for filed in self._db.description]
        sql = "SELECT * FROM {}".format(self._name)
        self._db.execute(sql)
        return self

    def __next__(self):
        row = self._db.fetchone()
        if row:
            return mysqlDict(dict(zip(self._fields, row)),
                             db=self._db,
                             name=self._name)
        raise StopIteration()

    def __contains__(self, elem):
        """Check if the elem is in the data set."""
        findStr = ""
        for k, v in elem.items():
            if isinstance(v, str):
                findStr += "{}='{}' AND ".format(k, v)
            elif isinstance(v, float):
                findStr += "ABS({} - {}) < 1e-5 AND ".format(k, v)
            else:
                findStr += "{}={} AND ".format(k, v)
        findStr = findStr[:-5]
        sql = "SELECT * FROM {} WHERE {}".format(self._name, findStr)
        return bool(self._db.execute(sql))

    def append(self, value: dict):
        value = super().append(value)
        keys, values = "", ""
        if not hasattr(self, "_fields"):
            sql = "SELECT * FROM {} LIMIT 1;".format(self._name)
            self._db.execute(sql)
            self._fields = [filed[0] for filed in self._db.description]
        for _key, _value in value.items():
            if _key not in self._fields:
                raise AttributeError("no attribute named {}".format(_key))
            keys += (_key + ",")
            if isinstance(_value, str):
                values += '"{}",'.format(_value)
            else:
                values += (str(_value) + ",")
        sql = "INSERT INTO {table}({keys}) VALUES ({values});".format(
            table=self._name, keys=keys, values=values).replace(",)", ")")
        try:
            if self._db.execute(sql):
                self._db.connection.commit()
        except Exception as e:
            logger.warning(e)
            self._db.connection.rollback()

    def extend(self, iterable):
        iterable = super().extend(iterable)
        for value in iterable:
            self.append(value)

    def pop(self, index=-1):
        index = super().__getitem__(index)
        result = self.__getitem__(index)
        _result = dict(result)
        result.clear()
        return _result

    def clear(self):
        sql = "TRUNCATE {}".format(self._name)
        try:
            if self._db.execute(sql):
                self._db.connection.commit()
        except Exception as e:
            logger.warning(e)
            self._db.connection.rollback()

    def get(self):
        if not hasattr(self, "_fields"):
            sql = "SELECT * FROM {} LIMIT 1;".format(self._name)
            self._db.execute(sql)
            self._fields = [filed[0] for filed in self._db.description]
        sql = "SELECT * FROM {}".format(self._name)
        self._db.execute(sql)
        results = self._db.fetchall()
        _results = []
        for result in results:
            _results.append(dict(zip(self._fields, result)))
        return [
            mysqlDict(data, db=self._db, name=self._name) for data in _results
        ]

    @property
    def list(self):
        return self.get()

    @property
    def dict(self):
        if not hasattr(self, "_fields"):
            sql = "SELECT * FROM {} LIMIT 1;".format(self._name)
            self._db.execute(sql)
            self._fields = [filed[0] for filed in self._db.description]
        sql = "SELECT * FROM {}".format(self._name)
        self._db.execute(sql)
        results = self._db.fetchall()
        dict_result = {}
        for i in range(len(self._fields)):
            dict_result[self._fields[i]] = [r[i] for r in results]
        dict_result.pop("_id", None)
        return dict_result

    @property
    def tuple(self):
        sql = "SELECT * FROM {}".format(self._name)
        self._db.execute(sql)
        return tuple([tuple(filed[0] for filed in self._db.description)] +
                     list(self._db.fetchall()))

    @property
    def set(self):
        return set(self.tuple)


class mysqlDict(dict):
    def __init__(self, *args, db=None, name=None):
        self._db = db
        self._name = name
        self._id = args[0].pop("_id", None)
        dict.__init__(self, *args)

    def clear(self):
        findStr = ""
        if self._id:
            findStr += "_id={} AND ".format(self._id)
        for k, v in self.items():
            if isinstance(v, str):
                findStr += "{}='{}' AND ".format(k, v)
            elif isinstance(v, float):
                findStr += "ABS({} - {}) < 1e-5 AND ".format(k, v)
            else:
                findStr += "{}={} AND ".format(k, v)
        findStr = findStr[:-5]
        sql = "DELETE FROM {} WHERE {} LIMIT 1".format(self._name, findStr)
        try:
            self._db.execute(sql)
            self._db.connection.commit()
        except Exception as e:
            logger.warning(e)
            self._db.connection.rollback()
        super().clear()

    def setdefault(self, key, default):
        value = super().setdefault(key, default)
        findStr = ""
        if self._id:
            findStr += "_id={} AND ".format(self._id)
        for k, v in self.items():
            if isinstance(v, str):
                findStr += "{}='{}' AND ".format(k, v)
            elif isinstance(v, float):
                findStr += "ABS({} - {}) < 1e-5 AND ".format(k, v)
            else:
                findStr += "{}={} AND ".format(k, v)
        findStr = findStr[:-5]
        if isinstance(value, str):
            value = "'{}'".format(value)
        sql = "UPDATE {} SET {}={} WHERE {} LIMIT 1".format(
            self._name, key, value, findStr)
        try:
            self._db.execute(sql)
            self._db.connection.commit()
        except Exception as e:
            logger.warning(e)
            self._db.connection.rollback()
        return value

    def update(self, d):
        updateStr = ""
        for k, v in d.items():
            if isinstance(v, str):
                updateStr += "{}='{}',".format(k, v)
            else:
                updateStr += "{}={},".format(k, v)
        updateStr = updateStr[:-1]
        findStr = ""
        if self._id:
            findStr += "_id={} AND ".format(self._id)
        for k, v in self.items():
            if isinstance(v, str):
                findStr += "{}='{}' AND ".format(k, v)
            elif isinstance(v, float):
                findStr += "ABS({} - {}) < 1e-5 AND ".format(k, v)
            else:
                findStr += "{}={} AND ".format(k, v)
        findStr = findStr[:-5]
        sql = "UPDATE {} SET {} WHERE {} LIMIT 1".format(
            self._name, updateStr, findStr)
        try:
            self._db.execute(sql)
            self._db.connection.commit()
            super().update(d)
        except Exception as e:
            logger.warning(e)
            self._db.connection.rollback()

    def __setitem__(self, key, value):
        findStr = ""
        if self._id:
            findStr += "_id={} AND ".format(self._id)
        for k, v in self.items():
            if isinstance(v, str):
                findStr += "{}='{}' AND ".format(k, v)
            elif isinstance(v, float):
                findStr += "ABS({} - {}) < 1e-5 AND ".format(k, v)
            else:
                findStr += "{}={} AND ".format(k, v)
        findStr = findStr[:-5]
        findStr = findStr.replace("''", "'")
        if isinstance(value, str):
            value = "'{}'".format(value)
        sql = "UPDATE {} SET {}={} WHERE {} LIMIT 1".format(
            self._name, key, value, findStr)
        try:
            self._db.execute(sql)
            self._db.connection.commit()
            super().__setitem__(key, value)
        except Exception as e:
            logger.warning(e)
            self._db.connection.rollback()
