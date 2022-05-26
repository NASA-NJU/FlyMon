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
    def __init__(self, content):
        return self.content = content
    
    @property
    def content(self):
        return self.content

    @property
    def resource_type(self):
        pass

    def __str__(self):
        return str(self.content)

class ConstParam(Param):
    def __init__(self, const_val):
         super(ConstParam, self).__init__(const_val)

    @property
    def resource_type(self):
        return ParamType.Const

class CompressedKeyParam:
    def __init__(self, key_name):
         super(CompressedKeyParam, self).__init__(key_name)

    @property
    def resource_type(self):
        return ParamType.CompressedKey

class TimestampParam:
    def __init__(self):
         super(TimestampParam, self).__init__("timestamp")

    @property
    def resource_type(self):
        return ParamType.Timestamp
    
class PktSizeParam:
    def __init__(self):
         super(PktSizeParam, self).__init__("pkt_size")

    @property
    def resource_type(self):
        return ParamType.PacketSize

class QueueLenParam:
    def __init__(self):
         super(QueueLenParam, self).__init__("queue_size")

    @property
    def resource_type(self):
        return ParamType.QueueLen