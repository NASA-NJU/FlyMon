# -*- coding:UTF-8 -*-

from enum import Enum
from bitstring import BitArray, BitStream
from flow_key import FlowKey
from flow_attr import FlowAttribute


def parse_key(key_str):
    return None

def parse_attribute(attribute_str):
    return None

class FlyMonTask:
    """ 
    Task instance in FlyMon 
    """
    def __init__(self, task_id, flow_key, flow_attr, mem_size):
        self.id = task_id
        self.key = parse_key(flow_key)
        self.attribute = parse_attribute(flow_attr)
        self.mem_size = mem_size
        pass

    def get_id(self):
        return self.id 
        
    def get_flowkey(self):
        return self.key

    def get_flowattribute(self):
        return self.attribute

    def get_memory(self):
        return (self.mem_size, self.mem_num)
    

