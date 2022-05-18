# -*- coding:UTF-8 -*-

from enum import Enum
from bitstring import BitArray, BitStream


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
