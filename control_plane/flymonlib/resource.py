from enum import Enum

class Resource(Enum):
    """
    A class to represent resource in FlyMon DataPlane.
    """
    CompressedKey = 1
    Memory = 2
    StdParam = 3 # Not every CMU-Groups support all standard metadata.

class CompressedKeyResource:
    def __init__(self, flow_key):
        self.content = flow_key

    @property
    def type(self):
        return Resource.CompressedKey
    
    @property
    def content(self):
        return self.content

class MemoryResource:
    def __init__(self, size):
        self.content = size

    @property
    def type(self):
        return Resource.Memory
    
    @property
    def content(self):
        return self.content
    
class ParamResource:
    def __init__(self, param_name):
        self.content = param_name

    @property
    def type(self):
        return Resource.StdParam
    
    @property
    def content(self):
        return self.content