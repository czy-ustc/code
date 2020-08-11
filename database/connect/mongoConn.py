from pymongo import MongoClient

from ..db.momgodb import mongodb
from .connect import dbConn


class mongoConn(dbConn):
    _name = "mongo"

    def __init__(self, host=None, port=None, username=None, password=None):
        super().__init__(host=host,
                         port=port,
                         username=username,
                         password=password)

    @property
    def _dbDict(self):
        if not hasattr(self, "_db") or not hasattr(self, "_dbList"):
            self._db = MongoClient(host=self._host,
                                   port=self._port,
                                   username=self._username,
                                   password=self._password)
            database_names = self._db.list_database_names()
            database_names.sort()
            self._dbList = database_names
        baseDict = {}
        for i in range(len(self._dbList)):
            baseDict[i] = self._dbList[i]
        if "dbNames" in self._setting[self._name][self._host]:
            for k, v in self._setting[self._name][
                    self._host]["dbNames"].items():
                for _k, _v in baseDict.items():
                    if k == _v:
                        baseDict[_k] = v
        return baseDict

    def _connect(self):
        if not hasattr(self, "_db"):
            self._db = MongoClient(host=self._host,
                                   port=self._port,
                                   username=self._username,
                                   password=self._password)

    def __len__(self):
        if not hasattr(self, "_db") or not hasattr(self, "_dbList"):
            self._db = MongoClient(host=self._host,
                                   port=self._port,
                                   username=self._username,
                                   password=self._password)
            database_names = self._db.list_database_names()
            database_names.sort()
            self._dbList = database_names
        return len(self._dbList)

    def __str__(self):
        baseStr = super().__str__()
        baseStr += "\nindex\tname"
        for k, v in self._dbDict.items():
            baseStr += ("\n{}\t{}".format(k, v))
        return baseStr

    def __getitem__(self, value):
        k, v = super().__getitem__(value)
        return mongodb(host=self._host,
                       port=self._port,
                       password=self._password,
                       db=self._db[v],
                       info=(k, v))

    def __delitem__(self, value):
        result = super().__delitem__(value)
        if result:
            k, v = super().__getitem__(value)
            self._connect()
            self._db.drop_database(v)

    def __setitem__(self, key, value):
        k = super().__setitem__(key, value)[0]
        v = self._dbList[k]
        if "dbNames" in self._setting[self._name][self._host]:
            if v != value:
                self._setting[self._name][self._host]["dbNames"][v] = value
            else:
                self._setting[self._name][self._host]["dbNames"].pop(v, None)
                if len(self._setting[self._name][self._host]["dbNames"]) == 0:
                    self._setting[self._name][self._host].pop("dbNames", None)
        else:
            if v != value:
                self._setting[self._name][self._host]["dbNames"] = {v: value}
        self._setting._rewrite_conf_file()

    def __iter__(self):
        dbs = []
        for k, v in self._dbDict.items():
            dbs.append(
                mongodb(host=self._host,
                        port=self._port,
                        password=self._password,
                        db=self._db[v],
                        info=(k, v)))
        return dbs.__iter__()

    def __call__(self, host=None, port=None, username=None, password=None):
        return mongoConn(host=host,
                         port=port,
                         username=username,
                         password=password)
