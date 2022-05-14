# -*- coding:UTF-8 -*-

from enum import Enum
from bitstring import BitArray, BitStream

class FlowKey:
    """Flow key definition"""
    def __init__(self, ipsrc, ipdst, sport, dport, protocol):
        """
        all the args are in hex string format (w/o '0x').
        """
        # All key are regarded as 5-tuple with a mask.
        self.key = BitArray(int=0, length=104)
        ipsrc =    BitArray( '0x'              + ipsrc + '0'*((104-32)/4) ) 
        ipdst =    BitArray( '0x' + '0'*(32/4) + ipdst + '0'*((104-64)/4) ) 
        sport =    BitArray( '0x' + '0'*(64/4) + sport + '0'*((104-80)/4) )
        dport =    BitArray( '0x' + '0'*(80/4) + dport + '0'*((104-96)/4) )
        protocol = BitArray( '0x' + '0'*(96/4) + protocol )
        self.key = self.key | ipsrc | ipdst | sport | dport | protocol
        pass
    
    def to_match_obj(self):
        pass

class FlowAttribute(Enum):
    frequency   = 1
    distinct_sk = 2
    distinct_mk = 3
    maximum     = 4
    exist       = 5

class FlyMonTask:
    """ Task instance in FlyMon """
    def __init__(self, task_id, flow_key, flow_attr, mem_size):
        self.id = task_id
        self.key = key
        self.attribute = attribute
        self.mem_size = mem_size
        self.data = []
        pass

    def query(self, key):
        return 0
    
    def install(self, resource_list):
        pass
