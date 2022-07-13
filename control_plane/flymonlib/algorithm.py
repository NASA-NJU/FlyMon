import abc 
from enum import Enum
from flymonlib.operation import *
from flymonlib.resource import ResourceNode
from flymonlib.param import *
from flymonlib.utils import *
from math import pow, log2

class Algorithm(metaclass=abc.ABCMeta):
    """
    Abstract class for sketching algorithm.
    """
    @property
    @abc.abstractmethod 
    def param2(self):
        """Param2 is used as a feature of different algorithms.
        """
        pass

    @property
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

    @property
    @abc.abstractmethod
    def param_mapping(self):
        """Some algorithm needs param mapping in the preparation stage.
        """
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

    def analyze(self, datas):
        """ Parse attribute data.
            datas: is an list of data list (according to cmu_num).
        """
        return min(datas)
    
    def __str__(self):
        """Return the name of this algorithm.
        """
        return "CMS"

    @property
    def param_mapping(self):
        """Some algorithm needs param mapping in the preparation stage.
        """
        return { 
            # key : param
            # val : code
        }

    def resource_graph(self):
        """Return resource usage with linked resource nodes.
        """
        graph = []
        for _ in range(self._rows):
            #                         Filter, Tid, Key   Param1            KeyMap                                     Mem div
            graph.append([ResourceNode(None, None, None, None, self.param2, None, self.param_mapping, OperationType.CondADD, 1/self.cmu_num)])
        return graph
    
    
class MRAC(Algorithm):
    """
    Implementation of MRAC.
    """
    def __init__(self):
        pass

    @property
    def param2(self):
        """Param2 is used as a feature of different algorithms.
        """
        return Param(ParamType.Const, 65535)

    @property
    def cmu_num(self):
        """How many CMU used in this algorithm.
        """
        return 1

    def analyze(self, datas):
        """ Parse attribute data.
            datas: is an list of data list (according to cmu_num).
        """
        print("Query of BeauCoup is not implemented now.")
        pass
    
    def __str__(self):
        """Return the name of this algorithm.
        """
        return "MRAC"

    @property
    def param_mapping(self):
        """Some algorithm needs param mapping in the preparation stage.
        """
        return { 
            # key : param
            # val : code
        }

    def resource_graph(self):
        """Return resource usage with linked resource nodes.
        """
        graph = []
        for _ in range(self._rows):
            #                         Filter, Tid, Key   Param1            KeyMap                                     Mem div
            graph.append([ResourceNode(None, None, None, None, self.param2, None, self.param_mapping, OperationType.CondADD, 1/self.cmu_num)])
        return graph
    
    
class SUMax(Algorithm):
    """
    Implementation of SuMax(Sum).
    """
    def __init__(self):
        pass

    @property
    def param2(self):
        """Param2 is used as a feature of different algorithms.
        """
        return Param(ParamType.Const, 65535)

    @property
    def cmu_num(self):
        """How many CMU used in this algorithm.
        """
        return 3

    def analyze(self, datas):
        """ Parse attribute data.
            datas: is an list of data list (according to cmu_num).
        """
        return min(datas)
    
    def __str__(self):
        """Return the name of this algorithm.
        """
        return "SuMax"

    @property
    def param_mapping(self):
        """Some algorithm needs param mapping in the preparation stage.
        """
        return { 
            # key : param
            # val : code
        }

    def resource_graph(self):
        """Return resource usage with linked resource nodes.
        """
        graph = []
        graph.append(ResourceNode(None, None, None, None, self.param2, None, self.param_mapping, OperationType.CondADD, 1/3))
        # current min is output to param2 in the data plane.
        graph.append(ResourceNode(None, None, None, None,        None, None, self.param_mapping, OperationType.CondADD, 1/3))
        # current min is output to param2 in the data plane.
        graph.append(ResourceNode(None, None, None, None,        None, None, self.param_mapping, OperationType.CondADD, 1/3))
        return [graph] # Sumax is different from CMS, it needs 3 chained CMU Groups.
    
class HyperLogLog(Algorithm):
    """
    Implementation of HyperLogLog.
    """
    def __init__(self):
        pass

    @property
    def param2(self):
        """Param2 is used as a feature of different algorithms.
        """
        return Param(ParamType.Const, 65535) # Unused.

    @property
    def cmu_num(self):
        """How many CMU used in this algorithm.
        """
        return 1
    
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
    
    def __str__(self):
        """Return the name of this algorithm.
        """
        return "HLL"

    @property
    def param_mapping(self):
        """Some algorithm needs param mapping in the preparation stage.
        """
        return { 
            # key : param
            # val : code
        }

    def resource_graph(self):
        """Return resource usage with linked resource nodes.
        """
        #                   Filter, Tid,  Key  Param1            KeyMap                                  Mem div
        return [[ResourceNode(None, None, None, None, self.param2, None, self.param_mapping, OperationType.Max, 1)]]
    
    
class BeauCoup(Algorithm):
    """
    Implementation of BeauCoup.
    """
    def __init__(self):
        pass

    @property
    def param2(self):
        """Param2 is used as a feature of different algorithms.
        """
        return Param(ParamType.Const, 0) # Unused.

    @property
    def cmu_num(self):
        """How many CMU used in this algorithm.
        """
        return 3
    
    def analyze(self, datas):
        """ Parse attribute data.
            datas: is an list of data list.
        """
        # TODO: parse BeauCoup results.
        print("Query of BeauCoup is not implemented now.")
        pass
    
    def __str__(self):
        """Return the name of this algorithm.
        """
        return "BeauCoup"

    @property
    def param_mapping(self):
        """Some algorithm needs param mapping in the preparation stage.
        """
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

    def resource_graph(self):
        """Return resource usage with linked resource nodes.
        """
        graph = []
        for _ in range(self.cmu_num):
            #                         Filter, Tid, Key   Param1            KeyMap                                     Mem div
            graph.append([ResourceNode(None, None, None, None, self.param2, None, self.param_mapping, OperationType.AndOr, 1/self.cmu_num)])
        return graph
    

class BloomFilter(Algorithm):
    """
    Implementation of BloomFilter.
    """
    def __init__(self):
        pass

    @property
    def param2(self):
        """Param2 is used as a feature of different algorithms.
        """
        return Param(ParamType.Const, 0) # Unused.

    @property
    def cmu_num(self):
        """How many CMU used in this algorithm.
        """
        return 1
    
    def analyze(self, datas):
        """ Parse attribute data.
            datas: is an list of data list.
        """
        print("Query of Bloomfilter is not implemented now.")
        pass
    
    def __str__(self):
        """Return the name of this algorithm.
        """
        return "BloomFilter"

    @property
    def param_mapping(self):
        """Some algorithm needs param mapping in the preparation stage.
        """
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

    def resource_graph(self):
        """Return resource usage with linked resource nodes.
        """
        graph = []
        for _ in range(self.cmu_num):
            #                         Filter, Tid, Key   Param1            KeyMap                                     Mem div
            graph.append([ResourceNode(None, None, None, None, self.param2, None, self.param_mapping, OperationType.AndOr, 1/self.cmu_num)])
        return graph
    
class suMAX(Algorithm):
    """
    Implementation of SumMax(Max).
    """
    def __init__(self):
        pass

    @property
    def param2(self):
        """Param2 is used as a feature of different algorithms.
        """
        return Param(ParamType.Const, 0) # Unused.

    @property
    def cmu_num(self):
        """How many CMU used in this algorithm.
        """
        return 3
    
    def analyze(self, datas):
        """ Parse attribute data.
            datas: is an list of data list.
        """
        return min(datas)
    
    def __str__(self):
        """Return the name of this algorithm.
        """
        return "SuMax"

    @property
    def param_mapping(self):
        """Some algorithm needs param mapping in the preparation stage.
        """
        param_mapping = {
            # a dict of mappings.
            # key : (param, mask)
            # val : code
        }
        return param_mapping

    def resource_graph(self):
        """Return resource usage with linked resource nodes.
        """
        graph = []
        for _ in range(self.cmu_num):
            #                         Filter, Tid, Key   Param1            KeyMap                                     Mem div
            graph.append([ResourceNode(None, None, None, None, self.param2, None, self.param_mapping, OperationType.Max, 1/self.cmu_num)])
        return graph