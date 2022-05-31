# -*- coding:UTF-8 -*-

from flymonlib.flow_key import FlowKey
from flymonlib.flow_attribute import *
from flymonlib.resource import *
from flymonlib.utils import match_format_string


def parse_key(key_str):
    key_template = {
        "hdr.ipv4.src_addr" : 32,
        "hdr.ipv4.dst_addr" : 32,
        "hdr.ports.src_port": 16,
        "hdr.ports.dst_port": 16,
        "hdr.ipv4.protocol" :  8
    }
    flow_key = FlowKey(key_template)
    try:
        key_list = key_str.split(',')
        for key in key_list:
            if '/' in key:
                k,m = key.split('/')
                if k not in key_template.keys():
                    raise RuntimeError(f"Invalid key format: {key_str}, example: hdr.ipv4.src_addr/<mask:int>, hdr.ports.src_port/<mask:int>")
                if int(m) < 0 or int(m) > key_template[k]:
                    raise RuntimeError(f"Invalid key mask: {m}, need >=0 and <= {key_template[k]}")
                re = flow_key.set_mask(k, int(m))
                if re is False:
                    raise RuntimeError(f"Set mask faild for the key {k}")
            else:
                flow_key.set_mask(key, 32)
    except Exception as e:
        raise e
    return flow_key

def parse_attribute(attribute_str):
    # attribute = None
    try:
        re = match_format_string("{attr_name}({param})", attribute_str)
    except Exception as e:
        raise RuntimeError(f"Invalid attribute format {attribute_str}")
    if re['attr_name'] == 'frequency':
        return Frequency(re['param'])
    else:
        raise RuntimeError(f"Invalid attribute name {re['attr_name']}")


class FlyMonTask:
    """ 
    Task instance in FlyMon 
    """
    def __init__(self, task_id, flow_key, flow_attr, mem_size):
        """
        Input examples:
        flow_key: hdr.ipv4.src_addr/<mask:int>, hdr.ipv4.dst_addr/<mask:int>
        flow_attr: frequency(1)
        memory_size: 65536
        """
        self._id = task_id
        self._key = parse_key(flow_key)
        self.attribute = parse_attribute(flow_attr)
        self.mem_size = mem_size
        pass
    
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        try:
            int_id = int(id)
            self_id = int_id
        except Exception as e:
            raise RuntimeError("Invalid id.")
        
    @property   
    def key(self):
        return self._key
    
    @key.setter
    def key(self, key):
        self._key = key
        
    @property
    def attribute(self):
        return self._attribute
    
    @attribute.setter
    def attribute(self, attr):
        self._attribute = attr
        
    @property
    def mem_size(self):
        return self._mem_size
    
    @mem_size.setter
    def mem_size(self, mem):
        self._mem_size = mem
    
    @property
    def mem_num(self):
        return self._attribute.memory_num
    
    def __str__(self) -> str:
        return f"ID = {self._id}\nKey = {str(self._key)}\nAttribute = {str(self._attribute)}\nMemory = {self.mem_size}({self.mem_num}*{int(self.mem_size/self.mem_num)})"
        
    def resource_list(self):
        resource_list = []
        resource_list.append(Resource(ResourceType.CompressedKey, self.key))
        memory_num = self.mem_num
        for _ in range(memory_num):
            resource_list.append(Resource(ResourceType.Memory, self.mem_size/memory_num))
        resource_list.append(Resource(ResourceType.StdParam, self.attribute.param1))
        return resource_list