from ..model.mysqlTable import mysqlTable
from .db import dbObject


class mysqldb(dbObject):
    _name = "mysqldb"

    def __init__(self,
                 host: str = None,
                 port: int = None,
                 username: str = None,
                 password: str = None,
                 db=None,
                 info: tuple = None):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._db = db
        self._info = info

    @property
    def _keyList(self):
        sql = "show tables"
        self._db.execute(sql)
        tables = [db[0] for db in self._db.fetchall()]
        return tables

    def __str__(self):
        baseStr = super().__str__()
        baseStr += "\ntables:{}".format(str(self._keyList))
        return baseStr

    def __len__(self):
        sql = "show tables"
        return self._db.execute(sql)

    def __getitem__(self, key):
        key = super().__getitem__(key)
        if isinstance(key, str):
            return mysqlTable(self._db,
                              key,
                              host=self._host,
                              port=self._port,
                              username=self._username,
                              password=self._password,
                              info=self._info)
        elif isinstance(key, list):
            results = []
            for k in key:
                results.append(
                    mysqlTable(self._db,
                               k,
                               host=self._host,
                               port=self._port,
                               username=self._username,
                               password=self._password,
                               info=self._info))
            return results

    def __setitem__(self, key, value):
        """
        Initialize database
        :params key: name of table
        :params value: filed of the table
        """
        if not isinstance(key, str):
            raise KeyError("key must be a str")
        if key in self._keyList:
            raise KeyError("key had exists")
        if not isinstance(value, dict) or len(value) == 0:
            raise TypeError("value must be a non-empty dict")
        data_type = [
            "TINYINT", "SMALLINT", "MEDIUMINT", "INT", "INTEGER", "BIGINT",
            "FLOAT", "DOUBLE", "DECIMAL", "DATE", "TIME", "YEAR", "DATETIME",
            "TIMESTAMP", "CHAR", "VARCHAR", "TINYBLOB", "TINYTEXT", "BLOB",
            "TEXT", "MEDIUMBLOB", "MEDIUMTEXT", "LONGBLOB", "LONGTEXT"
        ]
        sql = "show tables"
        self._db.execute(sql)
        keys = [key[0] for key in self._db.fetchall()]
        if key not in keys:
            baseSql = "CREATE TABLE IF NOT EXISTS {}(_id INT UNSIGNED AUTO_INCREMENT,{}PRIMARY KEY (_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
            moreInfo = ""
            for _key, _value in value.items():
                if isinstance(_value, str):
                    if any([key in _value.upper() for key in data_type]):
                        moreInfo += "{} {} NOT NULL,".format(_key, _value)
                    else:
                        raise KeyError()
                else:
                    raise KeyError()
            sql = baseSql.format(key, moreInfo)
            self._db.execute(sql)
        else:
            raise KeyError("{} had existed".format(key))

    def __delitem__(self, key):
        result = super().__delitem__(key)
        if isinstance(result, str):
            sql = "show tables"
            self._db.execute(sql)
            keys = [key[0] for key in self._db.fetchall()]
            if key not in keys:
                raise KeyError()
            sql = "DROP tables {};".format(key)
            self._db.execute(sql)
        else:
            raise KeyError("key must be the name of keys in database")
