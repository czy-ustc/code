import atexit

from pymysql import connect
from pymysql.err import InternalError

from ..db.mysqldb import mysqldb
from .connect import dbConn

dbList = []


class mysqlConn(dbConn):
    _name = "mysql"

    def __init__(self, host=None, port=None, username=None, password=None):
        super().__init__(host=host,
                         port=port,
                         username=username,
                         password=password)

    @property
    def _dbDict(self):
        if not hasattr(self, "_db") or not hasattr(self, "_dbList"):
            self._connect()
            sql = "show databases"
            self._db.execute(sql)
            database_names = [db[0] for db in self._db.fetchall()]
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

    def _connect(self, key=None):
        if key or not hasattr(self, "_db"):
            if not key:
                self._conn = connect(host=self._host,
                                     port=self._port,
                                     user=self._username,
                                     password=self._password,
                                     charset='utf8')
            else:
                self._conn = connect(host=self._host,
                                     port=self._port,
                                     user=self._username,
                                     password=self._password,
                                     charset='utf8',
                                     db=key)
            self._db = self._conn.cursor()
            dbList.append(self._conn)
        return self._db

    def __len__(self):
        if not hasattr(self, "_db") or not hasattr(self, "_dbList"):
            self._connect()
        sql = "show databases"
        result = self._db.execute(sql)
        return result

    def __str__(self):
        baseStr = super().__str__()
        baseStr += "\nindex\tname"
        for k, v in self._dbDict.items():
            baseStr += ("\n{}\t{}".format(k, v))
        return baseStr

    def __getitem__(self, value):
        k, v = super().__getitem__(value)
        try:
            self._connect(v)
        except InternalError:
            sql = "CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET utf8mb4".format(
                v)
            self._connect()
            self._db.execute(sql)
            self._connect(v)
        return mysqldb(host=self._host,
                       port=self._port,
                       password=self._password,
                       db=self._db,
                       info=(k, v))

    def __delitem__(self, value):
        result = super().__delitem__(value)
        if result:
            k, v = super().__getitem__(value)
            self._connect()
            sql = "DROP DATABASE {}".format(v)
            self._db.execute(sql)

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
            self._connect(v)
            dbs.append(
                mysqldb(host=self._host,
                        port=self._port,
                        password=self._password,
                        db=self._db,
                        info=(k, v)))
        return dbs.__iter__()

    def __call__(self, host=None, port=None, username=None, password=None):
        return mysqlConn(host=host,
                         port=port,
                         username=username,
                         password=password)


@atexit.register
def close():
    for db in dbList:
        try:
            db.close()
        except Exception:
            pass
