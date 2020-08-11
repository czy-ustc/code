from .utils.log import setFile, setLevel
from .utils.setting import setting


class Database(object):
    def __init__(self):
        self._dbList = ["redis", "mongo", "mysql"]

    def __len__(self):
        return len(self._dbList)

    def __str__(self):
        return '<Database{}>'.format(str(self._dbList))

    def __getitem__(self, value):
        if value not in self._dbList:
            raise KeyError(value)
        if value == "redis":
            from .connect.redisConn import redisConn
            return redisConn()
        elif value == "mongo":
            from .connect.mongoConn import mongoConn
            return mongoConn()
        elif value == "mysql":
            from .connect.mysqlConn import mysqlConn
            return mysqlConn()

    def __getattr__(self, value):
        return self.__getitem__(value)

    def __iter__(self):
        return self._dbList.__iter__()

    def set_temporary(self, conf):
        setting.update_temporary(conf)

    def set_permanent(self, conf):
        setting.update_permanent(conf)

    @property
    def logLevel(self):
        return setting["conf"]["logLevel"]

    @logLevel.setter
    def logLevel(self, level):
        setLevel(level)

    @property
    def logFile(self):
        return setting["conf"]["logLevel"]

    @logFile.setter
    def logFile(self, filename):
        setFile(filename)


class File(object):
    def __getitem__(self, key):
        if "json" in key:
            from .file.jsonFile import jsonFile
            return jsonFile(key.replace("json", "").replace(".", ""))
        elif "txt" in key:
            from .file.txtFile import txtFile
            return txtFile(key.replace("txt", "").replace(".", ""))
        elif "csv" in key:
            from .file.csvFile import csvFile
            return csvFile(key.replace("csv", "").replace(".", ""))
