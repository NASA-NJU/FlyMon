from enum import Enum
from flymonlib.flow_key import *

class ParamType(Enum):
    """
    A class to represent params in FlyMon.
    """
    Const = 1
    CompressedKey = 2
    StdParam = 3
    Key = 4 # The same with key.

class Param:
    def __init__(self, type, content=""):
        self._type = type
        self._content = content
    
    @property
    def content(self):
        return self._content

    @content.setter
    def content(self):
        return self._content

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    def __str__(self):
        return str(self._content)

    def __eq__(self, another):
        return self._type == another._type and self._content == another._content


def parse_param(param_str):
    """
    param string to param object.
    """
    param = None
    if 'hdr' in param_str:
        # Don't check the validity here.
        # Check it in Resource Manager when allocating resources.
        try:
            param = Param(ParamType.CompressedKey, parse_key(param_str))
        except Exception as e:
            print(f"{e} when parse the param_str for the attribute.")
            print(f"WARN: Set the param to Const 1.")
            param = Param(ParamType.Const, 1)
    elif param_str == "KEY":
        param = Param(ParamType.Key) # Special treatment, set to the same as Key
    elif param_str == 'pkt_size':
        param = Param(ParamType.StdParam, "pkt_size")
    elif param_str == 'timestamp':
        param = Param(ParamType.StdParam, "timestamp")
    elif param_str == 'queue_size':
        param = Param(ParamType.StdParam, "queue_size")
    else: # Must be a const.
        try:
            param = Param(ParamType.Const, int(param_str))
        except Exception as e:
            print(f"{e} when set a const param for the frequency attribute.")
            print(f"WARN: Set the param to Const 1.")
            param = Param(ParamType.Const, 1)
    return param