# -*- coding:UTF-8 -*-

import socket
import struct
from flymonlib.flow_key import *
from flymonlib.flow_attribute import *
from flymonlib.resource import *
from flymonlib.utils import parse_filter


class FlyMonTask:
    """ 
    Task instance in FlyMon 
    """
    def __init__(self, task_id, filter, flow_key, flow_attr, mem_size):
        """
        Input examples:
        task filter: 10.0.0.1/255.0.0.0,0.0.0.0/0.0.0.0
        flow_key: hdr.ipv4.src_addr/<mask:int>, hdr.ipv4.dst_addr/<mask:int>
        flow_attr: frequency(1)
        memory_size: 65536
        """
        self._id = task_id
        self._filter = parse_filter(filter) # [(src_ip, src_mask), (dst_ip, dst_mask)] 
        self._key = parse_key(flow_key)
        self.attribute = parse_attribute(flow_attr)
        self.mem_size = mem_size
        self._locations = []
        pass
    
    @property
    def id(self):
        return self._id

    @property
    def filter(self):
        return self._filter
        
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
        return self._attribute.algorithm.cmu_num
            
    @property
    def locations(self):
        return self._locations
    
    @locations.setter
    def locations(self, locations):
        self._locations = locations
    
    def __str__(self) -> str:
        info = f"Filter= {self.filter}\nID = {self._id}\nKey = {str(self._key)}\nAttribute = {str(self._attribute)}\nMemory = {self.mem_size}({self.mem_num}*{int(self.mem_size/self.mem_num)})"
        info += "\nLocations:\n"
        for idx, loc in enumerate(self._locations):
            info += f" - loc{idx} = " + str(loc) + "\n"
        return info

    def resource_graph(self):
        """
        [[node1, node2] [node3]]
        """
        resource_graph = self._attribute.resource_graph()
        for nodes in resource_graph:
            for node in nodes:
                node.filter = self.filter
                node.task_id = self.id
                if self.key is None:
                    print("here")
                    node.key = self.attribute.param1.content
                else:
                    node.key = self.key
                node.memory = int(self.mem_size * node.memory)
        return resource_graph

    def generate_key_bytes(self, key_str, candidate_key_set = ["src_addr", "dst_addr", "src_port", "dst_port", "protocol"]):
        """Parse key string to a flowKey object.
        Args:
            key_st : 10.0.0.0/24,*,*,*,*,
        Returns:
            bytes of the flow key
        """
        buf = b''
        # full_name_dict = {
        #     "src_addr" : "hdr.ipv4.src_addr",
        #     "dst_addr" : "hdr.ipv4.dst_addr",
        #     "src_port" : "hdr.ports.src_port",
        #     "dst_port" : "hdr.ports.dst_port",
        #     "protocol" : "hdr.ipv4.protocol"
        # }
        try:
            template = "{" + "},{".join(candidate_key_set) + "}"
            re_step1 = match_format_string(template, key_str)
            for key_name in candidate_key_set:
                if re_step1[key_name] == "*":
                    # bytes_len = self.key.get_bytes_len(full_name_dict[key_name])
                    # buf += bytes([0 for _ in range(bytes_len)]) 
                    # No need to append zero bytes.
                    pass
                else:
                    if "/" in re_step1[key_name]:
                        raise("Currently, the query key masks are not supported.")
                        # re_step2 = match_format_string("{key}/{prefix}", re_step1[key_name])
                        # key = re_step2['key']
                        # prefix = int(re_step2['prefix'])
                        # if "ipv4" in key_name:
                        #     buf += socket.inet_aton(re_step1[key_name])
                        # elif "port" in key_name:
                        #     buf += struct.pack('!H', int(re_step1[key_name]))
                        # else:
                        #     buf += struct.pack('!B', int(re_step1[key_name]))             
                    else:
                        if "addr" in key_name:
                            buf += socket.inet_aton(re_step1[key_name])
                        elif "port" in key_name:
                            buf += struct.pack('!H', int(re_step1[key_name]))
                        else:
                            buf += struct.pack('!B', int(re_step1[key_name]))
        except Exception as e:
            raise RuntimeError("Invalid query key format, example: 10.0.0.0/24,*,*,*,*")
        return buf
