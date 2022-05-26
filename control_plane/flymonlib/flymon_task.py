# -*- coding:UTF-8 -*-

from enum import Enum
from bitstring import BitArray, BitStream
from flow_key import FlowKey

class FlyMonTask:
    """ 
    Task instance in FlyMon 
    NOTE: Currently, we use a stupid param 'mem_num', which should not seen to users.
    TODO: make the mem_num (number of CMUs) transparent to users.
    """
    def __init__(self, task_id, flow_key, flow_attr, mem_size, mem_num=1):
        self.id = task_id
        self.key = flow_key
        self.attribute = flow_attr
        self.mem_size = mem_size
        self.mem_num = mem_num
        pass

    def get_id(self):
        return self.id 
        
    def get_flowkey(self):
        return self.key

    def get_flowattribute(self):
        return self.attribute

    def get_memory(self):
        return (self.mem_size, self.mem_num)
    

