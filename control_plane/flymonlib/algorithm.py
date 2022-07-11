import abc 
from enum import Enum
from flymonlib.operation import *
from flymonlib.resource import Resource, ResourceType, ResourceNode
from flymonlib.param import *
from flymonlib.utils import *

class Algorithm(metaclass=abc.ABCMeta):
    """
    Abstract class for sketching algorithm.
    """
    @abc.abstractmethod 
    def param2(self):
        """Param2 is used as a feature of different algorithms.
        """
        pass

    @abc.abstractmethod 
    def cmu_num(self):
        """How many CMU used in this algorithm.
        """
        pass

    @abc.abstractmethod 
    def analyze(self, datas):
        """ Parse attribute data.
            datas: is an list of data list (according to cmu_num).
        """
        pass
    
    @abc.abstractmethod
    def __str__(self):
        """Return the name of this algorithm.
        """
        pass

    @abc.abstractmethod
    def param_mapping(self):
        """Some algorithm needs param mapping in the preparation stage.
        """
        pass

    @abc.abstractmethod
    def operation(self):
        pass

    @abc.abstractmethod 
    def resource_graph(self):
        """Return resource usage with linked resource nodes.
        """
        pass


class CountMin(Algorithm):
    """
    Implementation of CMS.
    """
    def __init__(self, d=3):
        self._rows = d

    @property
    def param2(self):
        """Param2 is used as a feature of different algorithms.
        """
        return Param(ParamType.Const, 65535)

    @property
    def cmu_num(self):
        """How many CMU used in this algorithm.
        """
        return self._rows

    @property 
    def analyze(self, datas):
        """ Parse attribute data.
            datas: is an list of data list (according to cmu_num).
        """
        return min(datas)
    
    def __str__(self):
        """Return the name of this algorithm.
        """
        return "Count Min Sketch"

    def param_mapping(self):
        """Some algorithm needs param mapping in the preparation stage.
        """
        return { 
            # key : param
            # val : code
        }

    def operation(self):
        return OperationType.CondADD

    def resource_graph(self):
        """Return resource usage with linked resource nodes.
        """
        graph = []
        for _ in range(self._rows):
            #                         Key   Param1            KeyMap                                     Mem div
            graph.append([ResourceNode(None, None, self.param2, None, self.param_mapping, self.operation, 1/self.cmu_num)])
        return graph