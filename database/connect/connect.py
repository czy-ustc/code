import msvcrt
import time

from ..utils.log import logger
from ..utils.setting import setting


class dbConn(object):
    _name = "database"

    def __init__(self, host=None, port=None, username=None, password=None):
        _setting = setting._update_setting(host=host,
                                           port=port,
                                           username=username,
                                           password=password,
                                           name=self._name)
        self._host = _setting["host"]
        self._port = _setting["port"]
        self._username = _setting["username"]
        self._password = _setting["password"]
        self._setting = setting

    @property
    def _dbDict(self):
        """
        :return: the index and name of databases
        """
        return {}

    def _connect(self):
        """
        the method of connection
        """
        return True if hasattr(
            self, "_is_connected") and self._is_connected else False

    def __len__(self):
        self._connect()
        return 0

    def __str__(self):
        self._connect()
        host = '"{}"'.format(self._host)
        user = '"{}"'.format(self._username)
        baseStr = "<{}(host={} port={} user={})>".format(
            self._name, host, self._port, user)
        return baseStr

    def __getitem__(self, value):
        """
        :param value: value must be int(index of database) or str(name of database)
        :return (index, value)
        """
        if isinstance(value, int):
            if value < 0:
                value += self.__len__()
            if not 0 <= value < self.__len__():
                raise IndexError("database index out of range")
            return value, self._dbDict[value]
        elif isinstance(value, str):
            for k, v in self._dbDict.items():
                if v == value:
                    return k, v
            return self.__len__(), value
        else:
            raise KeyError(
                "value must be int(index of database) or str(name of database)"
            )

    _getitem = __getitem__

    def __delitem__(self, value):
        """
        flush the database
        :param value: value must be int(index of database) or str(name of database)
        :return True: Can flush the database.
                False: Can't flush the database.
        """
        k, v = self._getitem(value)
        logger.warning("Try to flush database({}:{})!".format(k, v))
        start_time = time.time()
        print("Please press any key to continue.")
        wait_input = ""
        while True:
            if msvcrt.kbhit():
                wait_input = msvcrt.getche()
            if len(wait_input) != 0 or (time.time() - start_time) > 10:
                break
        if len(wait_input) > 0:
            password = input(
                "please input the password of the database if you want to flush the database:"
            )
            if not self._password or password == self._password:
                logger.warning("Succeed to flush database({}:{})!".format(
                    k, v))
                return True
        logger.warning("Failed to flush database({}:{})!".format(k, v))
        return False

    def __setitem__(self, key, value):
        """
        rename the database
        :param key: value must be int(index of database) or str(name of database)
        :param value: the new name of the database
        """
        if not isinstance(value, str):
            raise KeyError("the new name of the database must be a str")
        k, v = self._getitem(key)
        if k == self.__len__():
            raise IndexError("database index out of range")
        if value in self._dbDict.values():
            raise KeyError("The name is already in use.")
        return k, v

    def __iter__(self):
        return self._dbDict.__iter__()

    def __call__(self, host=None, port=None, username=None, password=None):
        return dbConn(host=host,
                      port=port,
                      username=username,
                      password=password)
