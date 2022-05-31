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
    def __init__(self, type, content):
        self._type = type
        self._content = content
    
    @property
    def content(self):
        return self._content

    @property
    def type(self):
        return self._type
    
    @content.setter
    def content(self, content):
        self._content = content

    @type.setter
    def type(self, type):
        self._type = type
        pass

    def __str__(self):
        return f"[ResourceType: {self._type.name}, Content: {str(self.content)}]"