from enum import Enum
from flymonlib.resource import Resource, ResourceType
from flymonlib.operation import *
from flymonlib.param import *
from flymonlib.utils import *
from math import pow, log2

class AttributeType(Enum):
    """
    A enum class for flow attributes
    """
    Frequency = 1
    SingleKeyDistinct  = 2
    MultiKeyDistinct  = 2
    Existence = 3
    Max = 4
    FrequencySuMax = 5



class FlowAttribute():
    """
    This is an abstrace class!
    Do not use it.
    TODO: use a standard ABC defination.
    """
    def __init__(self, param_str):
        """
        Exception:
         - No exception.
        """
        self._param1 = parse_param(param_str)

    def analyze(self, datas):
        """ Parse attribute data.
        """
        return 0 # To be implemented by concreate attribute class.
    
    @property
    def type(self):
        return None

    @property
    def memory_num(self):
        return None
    
    @property
    def param1(self):
        return self._param1

    @param1.setter
    def param1(self, param):
        self._param1 = param

    @property
    def operation(self):
        return None

    @property
    def resource_list(self):
        resource_list = []
        if self._param1.type == ParamType.CompressedKey:
            resource_list.append(Resource(ResourceType.CompressedKey, self._param1.content))
        elif self._param1.type != ParamType.Const and self._param1.type != ParamType.Key:
            resource_list.append(Resource(ResourceType.StdParam, self._param1.content))
        return resource_list

    def __str__(self):
        return "Unknown"
    

class Frequency(FlowAttribute):
    def __init__(self, param_str):
        """
        Implement the built-in algorithm: Count-Min Sketch.
        Exception:
         - No exception.
        """
        super(Frequency, self).__init__(param_str)
        self._param2 = Param(ParamType.Const, 65535)

    def analyze(self, datas):
        """ Parse attribute data.
            datas: is an list of data list.
        """
        return min(datas)

    @property
    def type(self):
        return AttributeType.Frequency

    @property
    def param2(self):
        return self._param2

    @property
    def memory_num(self):
        return 3

    @property
    def param_mapping(self):
        return { 
            # key : param
            # val : code
        }

    @property
    def operation(self):
        return OperationType.CondADD

    def __str__(self):
        return f"frequency({self.param1})"


class FrequencySuMax(FlowAttribute):
    def __init__(self, param_str):
        """
        Implement the built-in algorithm: SuMax.
        Exception:
         - No exception.
        """
        super(FrequencySuMax, self).__init__(param_str)
        self._param2 = Param(ParamType.Const, 65535)

    def analyze(self, datas):
        """ Parse attribute data.
            datas: is an list of data list.
        """
        return min(datas)

    @property
    def type(self):
        return AttributeType.FrequencySuMax

    @property
    def param2(self):
        return self._param2

    @property
    def memory_num(self):
        return 1

    @property
    def param_mapping(self):
        return { 
            # key : param
            # val : code
        }

    @property
    def operation(self):
        return OperationType.CondADD

    def __str__(self):
        return f"frequency_sumax({self.param1})"

class SleKeyDistinct(FlowAttribute):
    def __init__(self):
        """
        Implement the built-in algorithm: HyperLogLog
        Exception:
         - No exception.
        """
        super(SleKeyDistinct, self).__init__("KEY")
        self._param2 = Param(ParamType.Const, 0) # No need

    @property
    def type(self):
        return AttributeType.SingleKeyDistinct

    @property
    def param2(self):
        return self._param2

    @property
    def memory_num(self):
        return 1

    @property
    def param_mapping(self):
        return { 
            # key : param
            # val : code
        }

    def analyze(self, datas):
        """ Parse attribute data.
            datas: is an list of data list.
        """
        datas = datas[0]        
        V = 0.0
        dZ = 0.0
        Z = 0.0   
        E = 0.0
        m = len(datas) * 1.0
        for bits in datas:
            if bits == 0:
                V+=1
            p = 16
            for i in range(15, -1, -1):
                bit = int(bits & (1<<i)) >> i
                if bit == 0:
                    p = (15 - i) + 1
                    break
            dZ += pow(2, -1*p) 
        Z = 1.0 / dZ
        E = 0.679 * pow(m, 2) * Z
        E_star = 0.0
        if E < 2.5*m:
            if V != 0:
                E_star = m * log2(m/V) 
            else:
                E_star = E
        pow232 = pow(2, 32)
        if E <= pow232/30:
            E_star = E 
        else: 
            E_star = -1*pow232*log2(1-E/pow232)
        return int(E_star)

    @property
    def operation(self):
        return OperationType.Max

    def __str__(self):
        return f"SK_Distinct(Key)"

class MulKeyDistinct(FlowAttribute):
    def __init__(self, param_str):
        """
        Implement the built-in algorithm: BeauCoup.
        Exception:
         - No exception.
        """
        super(MulKeyDistinct, self).__init__(param_str)
        self._param2 = Param(ParamType.Const, 0)

    @property
    def type(self):
        return AttributeType.MultiKeyDistinct

    @property
    def param2(self):
        return self._param2

    @property
    def memory_num(self):
        return 3

    @property
    def param_mapping(self):
        param_mapping = {
            # a dict of mappings.
            # key : (param, mask)
            # val : code
        }
        mask_value = int('1'*4, base=2) << 12
        for i in range(16):
            param = i << 12
            code = 1 << i
            param_mapping[(param, mask_value)] = code
        return param_mapping

    @property
    def operation(self):
        return OperationType.Max

    def __str__(self):
        return f"MK_Distinct({self.param1})"


class Existence(FlowAttribute):
    def __init__(self):
        """
        Implement the built-in algorithm: BloomFilter.
        Exception:
         - No exception.
        """
        super(Existence, self).__init__("KEY")
        self._param2 = Param(ParamType.Const, 0)

    @property
    def type(self):
        return AttributeType.Existence

    @property
    def param2(self):
        return self._param2

    @property
    def memory_num(self):
        return 1

    @property
    def param_mapping(self):
        param_mapping = {
            # a dict of mappings.
            # key : (param, mask)
            # val : code
        }
        mask_value = int('1'*4, base=2) << 12
        for i in range(16):
            param = i << 12
            code = 1 << i
            param_mapping[(param, mask_value)] = code
        return param_mapping

    @property
    def operation(self):
        return OperationType.Max

    def __str__(self):
        return f"Existence(Key)"


class Max(FlowAttribute):
    def __init__(self, param_str):
        """
        Implement the built-in algorithm: SuMax.
        Exception:
         - No exception.
        """
        super(Max, self).__init__(param_str)
        self._param2 = Param(ParamType.Const, 0)

    def analyze(self, datas):
        """ Parse attribute data.
            datas: is an list of data list.
        """
        return min(datas)

    @property
    def type(self):
        return AttributeType.Max

    @property
    def param2(self):
        return self._param2

    @property
    def memory_num(self):
        return 3

    @property
    def param_mapping(self):
        return { 
            # key : param
            # val : code
        }

    @property
    def operation(self):
        return OperationType.Max

    def __str__(self):
        return f"Max({self.param1})"


def parse_attribute(attribute_str):
    # attribute = None
    try:
        re = match_format_string("{attr_name}({param})", attribute_str)
    except Exception as e:
        raise RuntimeError(f"Invalid attribute format {attribute_str}")
    if re['attr_name'] == 'frequency':
        return Frequency(re['param'])
    elif re['attr_name'] == 'frequency_sumax':
        return FrequencySuMax(re['param'])
    elif re['attr_name'] == "distinct":
        if re['param'] == "":
            return SleKeyDistinct() ## 
        else:
            return MulKeyDistinct(re['param'])
    elif re['attr_name'] == "max":
        return Max(re['param'])
    elif re['attr_name'] == "existence":
        return Existence()
    else:
        raise RuntimeError(f"Invalid attribute name {re['attr_name']}")



