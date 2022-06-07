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
            resource_list.append(Resource(ResourceType.CompressedKey, self._param1))
        elif self._param1.type != ParamType.Const:
            resource_list.append(Resource(ResourceType.StdParam, self._param1))
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
        # 	double estimate = 0;                
        V = 0
        dZ = 0
        Z = 0   
        E = 0
        m = len(datas)
        for bits in datas:
            if bits == 0:
                V+=1
            p = 0
            for i in range(15, -1, -1):
                bit = (bits & (1<<i)) >> i
                if bit == 0:
                    p = (15 - i) + 1
                    break
            dZ += pow(2, -1*p) 
        Z = 1.0 / dZ
        E = 0.679 * pow(m, 2) * Z
        E_star = 0
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
        return E_star

# uint32_t HyperLogLogCalc(const vector<uint16_t>& data){
# 	double estimate = 0;                
# 	double V = 0;
# 	double dZ = 0;
# 	double Z = 0;
# 	double E = 0;
# 	double m = data.size();
# 	for(auto& bits : data){
# 		if(bits == 0){
# 			V+=1;
# 		}
# 		int p = 0;
# 		for(int i = 15; i >= 0; --i){
# 			uint16_t bit = (bits & (1<<i)) >> i;
# 			if(bit == 0){
# 				p = (15 - i) + 1;
# 				break;
# 			}
# 		}
# 		dZ += pow(2, -1*p);
# 	}
# 	Z = 1.0 / dZ;
# 	E = 0.679 * pow(m, 2) * Z;
# 	double E_star = 0;
# 	if (E < 2.5*m){
# 		E_star = (V != 0)? m * log2(m/V) : E;
# 	}
# 	double pow232 = pow(2, 32);
# 	E_star = (E <= pow232/30)? E : -1*pow232*log2(1-E/pow232);
# 	return E_star;
# }


    @property
    def operation(self):
        return OperationType.Max

    def __str__(self):
        return f"sk_distinct({self.param1})"

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
        return 1

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
        return f"sk_distinct({self.param1})"


class Existence(FlowAttribute):
    def __init__(self, param_str):
        """
        Implement the built-in algorithm: BloomFilter.
        Exception:
         - No exception.
        """
        super(Existence, self).__init__(param_str)
        self._param2 = Param(ParamType.Const, 0)

    @property
    def type(self):
        return AttributeType.MultiKeyDistinct

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
        return OperationType.Max

    def __str__(self):
        return f"sk_distinct({self.param1})"


class Max(FlowAttribute):
    def __init__(self, param_str):
        """
        Implement the built-in algorithm: SuMax.
        Exception:
         - No exception.
        """
        super(Max, self).__init__(param_str)
        self._param2 = Param(ParamType.Const, 0)

    @property
    def type(self):
        return AttributeType.MultiKeyDistinct

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
        return OperationType.Max

    def __str__(self):
        return f"sk_distinct({self.param1})"


def parse_attribute(attribute_str):
    # attribute = None
    try:
        re = match_format_string("{attr_name}({param})", attribute_str)
    except Exception as e:
        raise RuntimeError(f"Invalid attribute format {attribute_str}")
    if re['attr_name'] == 'frequency':
        return Frequency(re['param'])
    if re['attr_name'] == "distinct":
        if re['param'] == "":
            return SleKeyDistinct() ## 
        else:
            return MulKeyDistinct(re['param'])
    else:
        raise RuntimeError(f"Invalid attribute name {re['attr_name']}")



