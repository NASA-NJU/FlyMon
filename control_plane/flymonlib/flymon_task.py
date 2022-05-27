# -*- coding:UTF-8 -*-

from enum import Enum
from bitstring import BitArray, BitStream
from flow_key import FlowKey
from flow_attr import FlowAttribute


def parse_key(key_str):
    key_list = key_str.split(',')
    flow_key = None
    # TODO: parse key.


    flow_key = {
        "hdr.ipv4.src_addr" : 32,
        "hdr.ipv4.dst_addr" : 32,
        "hdr.ports.src_port": 16,
        "hdr.ports.dst_port": 16,
        "hdr.ipv4.protocol" :  8
    }
    flow_key.set_mask("hdr.ipv4.src_addr", 32)
    return FlowKey(flow_key)

def parse_attribute(attribute_str):
    attribute = None
    # TODO: parse attribute


    attribute = Frequency(1)
    return attribute

class FlyMonTask:
    """ 
    Task instance in FlyMon 
    """
    def __init__(self, task_id, flow_key, flow_attr, mem_size):
        """
        Input examples:
        flow_key: SrcIP/<mask:int>, DstIP/<mask:int>
        flow_attr: Frequency(1)
        memory_size: 65536
        """
        self.id = task_id
        self.key = parse_key(flow_key)
        self.attribute = parse_attribute(flow_attr)
        self.mem_size = mem_size
        pass
    
    @property
    def id(self):
        return self.id 
        
    @property   
    def key(self):
        return self.key
        
    @property
    def attribute(self):
        return self.attribute
        
    @property
    def memory(self):
        return self.mem_size
    
    def resource_list(self):
        resource_list = []
        resource_list.append(CompressedKeyResource(self.key))
        memory_num = self.attribute.memory_num
        for i in range(mem_num):
            resource_list.append(MemoryResource(self.mem_size/memory_num))
        if self.attribute.param1.param_type == ParamType.CompressedKey:
            resource_list.append(ParamResource(self.key))
        elif self.attribute.param1.param_type == ParamType.CompressedKey:
        pass
    
    def querier(self, key, memories):
        """
        Given a list of memory block, return a result according to underlayer algorithms.
        """
        # TODO: currently, only print all the data.
        for buckets in memories:
            print(buckets)
        pass

