from enum import Enum

class ResourceNode:
    """A set of resources used in a CMU.
    """
    def __init__(self, key, param1, param2, key_mapping, param_mapping, operation, memory_size):
        self._key = key
        self._param1 = param1    # it will be post-processed by task object.
        self._param2 = param2
        self._key_map = key_mapping
        self._param_map = param_mapping
        self._operation = operation
        self._memsize = memory_size  # attribute set it as proportion, it will be 
                                     # post-processed to real size in task resource_graph func.
        pass

    @property
    def key(self):
        return self._key
    @key.setter
    def key(self, key):
        self._key = key

    @property
    def param1(self):
        return self._param1

    @param1.setter
    def param1(self, param1):
        self._param1 = param1

    @property
    def param2(self):
        return self._param2
    @property
    def key_mapping(self):
        return self._key_map
    @property
    def param_mapping(self):
        return self._param_map
    @property
    def operation(self):
        return self._operation
    @property
    def memory(self):
        return self._memsize

    @memory.setter
    def memory(self, memory):
        self._memsize = memory

    def __str__(self):
        return f"key={self.key}, param1={self.param1}, param2={self.param2}, operation={self.operation.name}"