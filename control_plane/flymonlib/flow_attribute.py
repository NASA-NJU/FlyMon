from enum import Enum
from flymonlib.operation import *
from flymonlib.param import *
from flymonlib.utils import *
from flymonlib.algorithm import *



class AttributeType(Enum):
    """
    A enum class for flow attributes
    """
    Frequency = 1
    Distinct  = 2
    Existence = 3
    Max = 4


class FlowAttribute(metaclass=abc.ABCMeta):
    """
    This is an abstrace class!
    Do not use it.
    """
    ALGORITHMS = {
        
    }
    def __init__(self, param_str, algorithm_str="default"):
        """
        Exception:
         - No exception.
        """
        self._param1 = parse_param(param_str)
        self._alg = self.getalg(algorithm_str)

    @property
    def algorithm(self):
        """Get algorithm.
        """
        return self._alg

    @property
    def param1(self):
        return self._param1

    @property
    def param2(self):
        if self.algorithm is None:
            return None
        return self.algorithm.param2

    @property
    def param_mapping(self):
        if self.algorithm is None:
            return None
        return self.algorithm.param_mapping

    @property
    def cmu_num(self):
        if self.algorithm is None:
            return None
        return self.algorithm.cmu_num

    def resource_graph(self):
        graph = self.algorithm.resource_graph()
        for nodes in graph:
            for node in nodes:
                node.param1 = self.param1
        return graph

    def analyze(self, datas):
        return self.algorithm.analyze(datas)

    def getalg(self, alg_name):
        """Set algorithm.
        Return: If invalid, return None. If valid, return object.
        """
        if alg_name not in self.ALGORITHMS.keys():
            print(f"Invalid algorithm name, available algorithms are:\n   {str(self.ALGORITHMS.keys())}")
            return None
        else:
            return self.ALGORITHMS[alg_name]

    # Below are method must be implemented.
    @property
    @abc.abstractmethod
    def type(self):
        """Return atrribute type.
        """
        pass
    
    @abc.abstractmethod
    def __str__(self):
        """Return attribute name.
        """
        pass


class Frequency(FlowAttribute):
    """
    A frequency attribute.
    """
    ALGORITHMS = {
        "default" : CountMin(d=3),
        "cms" : CountMin(d=3),
        "sumax" : SUMax(),
        "mrac" : MRAC(),
        # "tower" : TowerSketch(), # TODO
        # "counter braids" : CountBraids()  # TODO
    }
    def __init__(self, param_str, algorithm="default"):
        """
        Exception:
         - No exception.
        """
        super(Frequency, self).__init__(param_str, algorithm)

    def type(self):
        """Return atrribute type.
        """
        return AttributeType.Frequency

    def __str__(self):
        """Return attribute name.
        """
        return f"Frequency(param={str(self.param1)}, algorithm={str(self.algorithm)})"

        
class Distinct(FlowAttribute):
    """
    A distinct attribute.
    """
    ALGORITHMS = {
        "default" : HyperLogLog(),
        "hll" : HyperLogLog(),
        "beaucoup" : BeauCoup()
    }
    
    def __init__(self, param_str, algorithm="default"):
        """
        Exception:
         - No exception.
        """
        super(Distinct, self).__init__(param_str, algorithm)

    def type(self):
        """Return atrribute type.
        """
        return AttributeType.Distinct

    def __str__(self):
        """Return attribute name.
        """
        return f"Distinct(param={str(self.param1)}, algorithm={str(self.algorithm)})"

class Existence(FlowAttribute):
    """
    A distinct attribute.
    """
    ALGORITHMS = {
        "default" : BloomFilter(),
        "bloomfilter" : BloomFilter()
    }
    
    def __init__(self, param_str, algorithm="default"):
        """
        Exception:
         - No exception.
        """
        super(Existence, self).__init__(param_str, algorithm)

    def type(self):
        """Return atrribute type.
        """
        return AttributeType.Existence

    def __str__(self):
        """Return attribute name.
        """
        return f"Existence(param={str(self.param1)}, algorithm={str(self.algorithm)})"
    
class Max(FlowAttribute):
    """
    A distinct attribute.
    """
    ALGORITHMS = {
        "default" : suMAX(),
        "sumax" : suMAX()
    }
    
    def __init__(self, param_str, algorithm="default"):
        """
        Exception:
         - No exception.
        """
        super(Max, self).__init__(param_str, algorithm)

    def type(self):
        """Return atrribute type.
        """
        return AttributeType.Max

    def __str__(self):
        """Return attribute name.
        """
        return f"Max(param={str(self.param1)}, algorithm={str(self.algorithm)})"

def parse_attribute(attribute_str):
    try:
        re = match_format_string("{attr_name}({param},{algorithm})", attribute_str)
    except Exception as e:
        raise RuntimeError(f"Invalid attribute format {attribute_str}, valid examples: frequency(1,cms) or frequency(1,default), no spaces in '()'")
    if re['attr_name'] == 'frequency':
        return Frequency(re['param'], algorithm=re["algorithm"])
    elif re['attr_name'] == "distinct":
        return Distinct(re['param'], algorithm=re["algorithm"])
    elif re['attr_name'] == "max":
        return Max(re['param'])
    elif re['attr_name'] == "existence":
        return Existence(re['param'], algorithm=re["algorithm"])
    else:
        raise RuntimeError(f"Invalid attribute name {re['attr_name']}")



