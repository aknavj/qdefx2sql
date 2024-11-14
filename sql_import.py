import abc
from abc import ABC, abstractmethod

# Import abstract class
class sql_import(ABC):

    @abstractmethod
    def loadFile(self, filename):
        pass

    @abstractmethod
    def saveFile(self, filename, content, ext):
        pass

    @abstractmethod
    def parseContent(self):
        pass

    @abstractmethod
    def saveSql(self, table, filename):
        pass
