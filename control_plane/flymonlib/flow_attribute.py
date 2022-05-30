from enum import Enum
from flymonlib.operation import *
from flymonlib.param import *

class AttributeType(Enum):
    """
    A enum class for flow attributes
    """
    Frequency = 1
    SingleKeyDistinct  = 2
    MultiKeyDistinct  = 2
    Existence = 3
    Max = 4 


class Attribute():

    def __ 

class Frequency:
    def __init__(self, param_str):
        if param_name == 'pkt_size':
            self.param1 = PktSizeParam()
        else:
            try:
                self.param1 = ConstParam(int(param_str))
            except Exception as e:
                print(f"{e} when set a const param for the frequency attribute.")
                print(f"WARN: Set the param to Frequency(1).")
                self.param1 = ConstParam(1)
        pass
    @property
    def type(self):
        return FlowAttribute.Frequency

    @property
    def memory_num(self):
        return 3
    
    @property
    def param1(self):
        return self.param1
    
    @property
    def param2(self):
        return ConstParam(65535)

    @property
    def operation(self):
        return Operation.CondADD

    def __str__(self):
        return f"frequency({self.param1})"