from redis import StrictRedis

from ..db.redisdb import redisdb
from .connect import dbConn


class redisConn(dbConn):
    _name = "redis"

    def __init__(self, host=None, port=None, username=None, password=None):
        super().__init__(host=host,
                         port=port,
                         username=username,
                         password=password)

    @property
    def _dbDict(self):
        if not hasattr(self, "_db") or not hasattr(self, "_dbcount"):
            self._db = StrictRedis(host=self._host,
                                   port=self._port,
                                   password=self._password,
                                   decode_responses=True)
            self._dbcount = int(
                self._db.execute_command("config get databases")[-1])
        baseDict = {db: "db{}".format(db) for db in range(self._dbcount)}
        if "dbNames" in self._setting[self._name][self._host]:
            for k, v in self._setting[self._name][
                    self._host]["dbNames"].items():
                baseDict[int(k)] = v
        return baseDict

    def _connect(self):
        if not hasattr(self, "_db"):
            self._db = StrictRedis(host=self._host,
                                   port=self._port,
                                   password=self._password,
                                   decode_responses=True)

    def __len__(self):
        if not hasattr(self, "_db") or not hasattr(self, "_dbcount"):
            self._db = StrictRedis(host=self._host,
                                   port=self._port,
                                   password=self._password,
                                   decode_responses=True)
            self._dbcount = int(
                self._db.execute_command("config get databases")[-1])
        return self._dbcount

    def __str__(self):
        baseStr = super().__str__()
        baseStr += "\nindex\tname"
        for k, v in self._dbDict.items():
            baseStr += ("\n{}\t{}".format(k, v))
        return baseStr

    def __getitem__(self, value):
        k, v = super().__getitem__(value)
        self._db = StrictRedis(host=self._host,
                               port=self._port,
                               password=self._password,
                               decode_responses=True,
                               db=k)
        return redisdb(host=self._host,
                       port=self._port,
                       password=self._password,
                       db=self._db,
                       info=(k, v))

    def __delitem__(self, value):
        result = super().__delitem__(value)
        if result:
            k, v = super().__getitem__(value)
            self._db = StrictRedis(host=self._host,
                                   port=self._port,
                                   password=self._password,
                                   decode_responses=True,
                                   db=k)
            redisdb(host=self._host,
                    port=self._port,
                    password=self._password,
                    db=self._db,
                    info=(k, v))._db.flushdb()

    def __setitem__(self, key, value):
        key = super().__setitem__(key, value)[0]
        if "dbNames" in self._setting[self._name][self._host]:
            self._setting[self._name][self._host]["dbNames"][str(key)] = value
        else:
            self._setting[self._name][self._host]["dbNames"] = {
                str(key): value
            }
        self._setting._rewrite_conf_file()

    def __iter__(self):
        dbs = []
        for k, v in self._dbDict.items():
            dbs.append(
                redisdb(host=self._host,
                        port=self._port,
                        password=self._password,
                        db=self._db,
                        info=(k, v)))
        return dbs.__iter__()

    def __call__(self, host=None, port=None, username=None, password=None):
        return redisConn(host=host,
                         port=port,
                         username=username,
                         password=password)
