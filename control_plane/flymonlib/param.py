from enum import Enum

class Param(Enum):
    """
    A class to represent params in FlyMon.
    """
    Const = 1
    CompressedKey = 2
    Timestamp = 3
    PacketSize = 4
    QueueLen = 5

class ConstParam:
    def __init__(self, const_val):
        self.content = const_val

    @property
    def type(self):
        return Param.Const
    
    @property
    def content(self):
        return self.content

class CompressedKeyParam:
    def __init__(self, flow_key):
        self.content = flow_key

    @property
    def type(self):
        return Param.CompressedKey
    
    @property
    def content(self):
        return self.StdMeta

class TimestampParam:
    def __init__(self):
        self.content = "timestamp"

    @property
    def type(self):
        return Param.Timestamp
    
    @property
    def content(self):
        return self.content

class PktSizeParam:
    def __init__(self):
        self.content = "pkt_size"

    @property
    def type(self):
        return Param.PacketSize
    
    @property
    def content(self):
        return self.content

class QueueLenParam:
    def __init__(self):
        self.content = "queue_size"

    @property
    def type(self):
        return Param.QueueLen
    
    @property
    def content(self):
        return self.content