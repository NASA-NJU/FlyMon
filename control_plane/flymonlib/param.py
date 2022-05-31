from enum import Enum

class ParamType(Enum):
    """
    A class to represent params in FlyMon.
    """
    Const = 1
    CompressedKey = 2
    Timestamp = 3
    PacketSize = 4
    QueueLen = 5

class Param:
    def __init__(self, type, content=""):
        self._type = type
        self._content = content
    
    @property
    def content(self):
        return self._content

    @content.setter
    def content(self):
        return self._content

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    def __str__(self):
        return str(self._content)

    def __eq__(self, another):
        return self._type == another._type and self._content == another._content