from enum import Enum
from flymonlib.operation import *
from flymonlib.param import *
from flymonlib.utils import *
from flymonlib.algorithm import *
from math import pow, log2

# Input your attribute like:
# -a frequency(param=1, algorithm=cms)

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

    @abc.abstractmethod
    def getalg(self, alg_name):
        """get algorithm object by name. NOTE: You must return an object for the default alg_name.
        Exception:
            Return -1 if the alg_name not exists and print avalible algorithms.
        """
        pass

class Frequency(FlowAttribute):
    """
    A frequency attribute.
    """
    ALGORITHMS = {
        "default" : CountMin(d=3),
        "cms" : CountMin(d=3),
        # "sumax" : SuMax(),
        # "mrac" : MRAC(),
        # "tower" : TowerSketch(),
        # "counter braids" : CountBraids()
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

    def getalg(self, alg_name):
        """Set algorithm.
        Return: If invalid, return None. If valid, return object.
        """
        if alg_name not in self.ALGORITHMS.keys():
            print(f"Invalid algorithm name, available algorithms are:\n   {str(self.ALGORITHMS.keys())}")
            return None
        else:
            return self.ALGORITHMS[alg_name]

# class FrequencySuMax(FlowAttribute):
#     def __init__(self, param_str):
#         """
#         Implement the built-in algorithm: SuMax.
#         Exception:
#          - No exception.
#         """
#         super(FrequencySuMax, self).__init__(param_str)
#         self._param2 = Param(ParamType.Const, 65535)

#     def analyze(self, datas):
#         """ Parse attribute data.
#             datas: is an list of data list.
#         """
#         return min(datas)

#     @property
#     def type(self):
#         return AttributeType.FrequencySuMax

#     @property
#     def param2(self):
#         return self._param2

#     @property
#     def memory_num(self):
#         return 1

#     @property
#     def param_mapping(self):
#         return { 
#             # key : param
#             # val : code
#         }

#     @property
#     def operation(self):
#         return OperationType.CondADD

#     def __str__(self):
#         return f"frequency_sumax({self.param1})"

# class SleKeyDistinct(FlowAttribute):
#     def __init__(self):
#         """
#         Implement the built-in algorithm: HyperLogLog
#         Exception:
#          - No exception.
#         """
#         super(SleKeyDistinct, self).__init__("KEY")
#         self._param2 = Param(ParamType.Const, 0) # No need

#     @property
#     def type(self):
#         return AttributeType.SingleKeyDistinct

#     @property
#     def param2(self):
#         return self._param2

#     @property
#     def memory_num(self):
#         return 1

#     @property
#     def param_mapping(self):
#         return { 
#             # key : param
#             # val : code
#         }

#     def analyze(self, datas):
#         """ Parse attribute data.
#             datas: is an list of data list.
#         """
#         datas = datas[0]        
#         V = 0.0
#         dZ = 0.0
#         Z = 0.0   
#         E = 0.0
#         m = len(datas) * 1.0
#         for bits in datas:
#             if bits == 0:
#                 V+=1
#             p = 16
#             for i in range(15, -1, -1):
#                 bit = int(bits & (1<<i)) >> i
#                 if bit == 0:
#                     p = (15 - i) + 1
#                     break
#             dZ += pow(2, -1*p) 
#         Z = 1.0 / dZ
#         E = 0.679 * pow(m, 2) * Z
#         E_star = 0.0
#         if E < 2.5*m:
#             if V != 0:
#                 E_star = m * log2(m/V) 
#             else:
#                 E_star = E
#         pow232 = pow(2, 32)
#         if E <= pow232/30:
#             E_star = E 
#         else: 
#             E_star = -1*pow232*log2(1-E/pow232)
#         return int(E_star)

#     @property
#     def operation(self):
#         return OperationType.Max

#     def __str__(self):
#         return f"SK_Distinct(Key)"

# class MulKeyDistinct(FlowAttribute):
#     def __init__(self, param_str):
#         """
#         Implement the built-in algorithm: BeauCoup.
#         Exception:
#          - No exception.
#         """
#         super(MulKeyDistinct, self).__init__(param_str)
#         self._param2 = Param(ParamType.Const, 0)

#     @property
#     def type(self):
#         return AttributeType.MultiKeyDistinct

#     @property
#     def param2(self):
#         return self._param2

#     @property
#     def memory_num(self):
#         return 3

#     @property
#     def param_mapping(self):
#         param_mapping = {
#             # a dict of mappings.
#             # key : (param, mask)
#             # val : code
#         }
#         mask_value = int('1'*4, base=2) << 12
#         for i in range(16):
#             param = i << 12
#             code = 1 << i
#             param_mapping[(param, mask_value)] = code
#         return param_mapping

#     @property
#     def operation(self):
#         return OperationType.Max

#     def __str__(self):
#         return f"MK_Distinct({self.param1})"


# class Existence(FlowAttribute):
#     def __init__(self):
#         """
#         Implement the built-in algorithm: BloomFilter.
#         Exception:
#          - No exception.
#         """
#         super(Existence, self).__init__("KEY")
#         self._param2 = Param(ParamType.Const, 0)

#     @property
#     def type(self):
#         return AttributeType.Existence

#     @property
#     def param2(self):
#         return self._param2

#     @property
#     def memory_num(self):
#         return 1

#     @property
#     def param_mapping(self):
#         param_mapping = {
#             # a dict of mappings.
#             # key : (param, mask)
#             # val : code
#         }
#         mask_value = int('1'*4, base=2) << 12
#         for i in range(16):
#             param = i << 12
#             code = 1 << i
#             param_mapping[(param, mask_value)] = code
#         return param_mapping

#     @property
#     def operation(self):
#         return OperationType.Max

#     def __str__(self):
#         return f"Existence(Key)"


# class Max(FlowAttribute):
#     def __init__(self, param_str):
#         """
#         Implement the built-in algorithm: SuMax.
#         Exception:
#          - No exception.
#         """
#         super(Max, self).__init__(param_str)
#         self._param2 = Param(ParamType.Const, 0)

#     def analyze(self, datas):
#         """ Parse attribute data.
#             datas: is an list of data list.
#         """
#         return min(datas)

#     @property
#     def type(self):
#         return AttributeType.Max

#     @property
#     def param2(self):
#         return self._param2

#     @property
#     def memory_num(self):
#         return 3

#     @property
#     def param_mapping(self):
#         return { 
#             # key : param
#             # val : code
#         }

#     @property
#     def operation(self):
#         return OperationType.Max

#     def __str__(self):
#         return f"Max({self.param1})"


def parse_attribute(attribute_str):
    # attribute = None
    try:
        re = match_format_string("{attr_name}({param})", attribute_str)
    except Exception as e:
        raise RuntimeError(f"Invalid attribute format {attribute_str}")
    if re['attr_name'] == 'frequency':
        return Frequency(re['param'])
    # elif re['attr_name'] == 'frequency_sumax':
    #     return FrequencySuMax(re['param'])
    # elif re['attr_name'] == "distinct":
    #     if re['param'] == "":
    #         return SleKeyDistinct() ## 
    #     else:
    #         return MulKeyDistinct(re['param'])
    # elif re['attr_name'] == "max":
    #     return Max(re['param'])
    # elif re['attr_name'] == "existence":
    #     return Existence()
    # else:
    #     raise RuntimeError(f"Invalid attribute name {re['attr_name']}")



