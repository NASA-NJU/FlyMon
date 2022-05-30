from enum import Enum

class ResourceType(Enum):
    """
    A enum class to represent resource in FlyMon DataPlane.
    """
    CompressedKey = 1
    Memory = 2
    StdParam = 3 # Not every CMU-Groups support all standard metadata.

class Resource():
    """
    Base class for resources.
    """
    def __init__(self, content):
        self._content = content
    
    @property
    def content(self):
        return self._content
    
    @content.setter
    def content(self, content):
        self._content = content

    def __str__(self):
        return str(self.content)

class CompressedKeyResource(Resource):
    def __init__(self, flow_key):
         super(CompressedKeyResource, self).__init__(flow_key)

    @property
    def type(self):
        return Resource.CompressedKey

class MemoryResource(Resource):
    def __init__(self, size):
         super(MemoryResource, self).__init__(size)

    @property
    def type(self):
        return Resource.Memory

class ParamResource(Resource):
    def __init__(self, param_name):
        super(ParamResource, self).__init__(param_name)

    @property
    def type(self):
        return Resource.StdParam
    