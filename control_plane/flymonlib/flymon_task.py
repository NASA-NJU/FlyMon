# -*- coding:UTF-8 -*-

import socket
import struct
from flymonlib.flow_key import FlowKey
from flymonlib.flow_attribute import *
from flymonlib.resource import *
from flymonlib.utils import match_format_string
from flymonlib.location import Location


def parse_filter(filter_str):
    """
    Args:
        filter_std: e.g., a.b.c.d/32,a.b.c.d/24
    Returns:
        [(a.b.c.d, 255.255.0.0), (0.0.0.0, 0.0.0.0)]
    """
    filters = ["src_filter",  "dst_filter"]
    results = []
    try:
        re_step1 = match_format_string("{src_filter},{dst_filter}", filter_str)
        for filter in filters:
            if re_step1[filter] == "*":
                results.append(("0.0.0.0", "0.0.0.0"))
            else:
                if '/' in re_step1[filter]:
                    re_step2 = match_format_string("{ip}/{prefix}", re_step1[filter])
                    ip = re_step2['ip']
                    prefix = int(re_step2['prefix'])
                    if prefix > 32 or prefix < 0 or len(ip)<7 or len(ip)>15:
                        raise RuntimeError()
                    mask = '1' * prefix + '0' * (32-prefix)
                    splt_mask = []
                    temp = ''
                    for idx, bit in enumerate(mask):
                        if idx != 0 and idx % 8 == 0:
                            splt_mask.append(temp)
                            temp = ''
                        else:
                            temp += bit
                    splt_mask.append(temp)
                    results.append((ip, f"{int(splt_mask[0], base=2)}.{int(splt_mask[1], base=2)}.{int(splt_mask[2], base=2)}.{int(splt_mask[3], base=2)}"))
                else:
                    results.append((re_step1[filter], "255.255.255.255"))
    except Exception as e:
        raise RuntimeError("Invalid filter format, example: 10.0.0.0/8,20.0.0.0/16 or 10.0.0.0/8,* or *,*")
    return results

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
        return self._attribute.memory_num
    
    def set_locations(self, locations):
        self._locations = locations
            
    @property
    def locations(self):
        return self._locations
    
    @locations.setter
    def locations(self, locations):
        self.set_locations(locations)
    
    
    def __str__(self) -> str:
        info = f"Filter= {self.filter}\nID = {self._id}\nKey = {str(self._key)}\nAttribute = {str(self._attribute)}\nMemory = {self.mem_size}({self.mem_num}*{int(self.mem_size/self.mem_num)})"
        info += "\nLocations:\n"
        for idx, loc in enumerate(self._locations):
            info += f" - loc{idx} = " + str(loc) + "\n"
        return info

    def resource_list(self):
        """
        The returned resources should be ordered:
            1. key resources from flow key.
            2. memory resources from cmu.
            3. other resources from attribute.
        """
        resource_list = []
        # Add key resource.
        for _ in range(self.mem_num):
            resource_list.append(Resource(ResourceType.CompressedKey, self.key))
        # Add memory resource.
        memory_num = self.mem_num
        for _ in range(memory_num):
            resource_list.append(Resource(ResourceType.Memory, int(self.mem_size/memory_num)))
        # Add attribute resource (param)
        resource_list.extend(self._attribute.resource_list)
        return resource_list


    def generate_key_bytes(self, key_str, candidate_key_set = ["src_addr", "dst_addr", "src_port", "dst_port", "protocol"]):
        """Parse key string to a flowKey object.
        Args:
            key_st : 10.0.0.0/24,*,*,*,*,
        Returns:
            bytes of the flow key
        """
        buf = b''
        full_name_dict = {
            "src_addr" : "hdr.ipv4.src_addr",
            "dst_addr" : "hdr.ipv4.dst_addr",
            "src_port" : "hdr.ports.src_port",
            "dst_port" : "hdr.ports.dst_port",
            "protocol" : "hdr.ipv4.protocol"
        }
        try:
            template = "{" + "},{".join(candidate_key_set) + "}"
            re_step1 = match_format_string(template, key_str)
            for key_name in candidate_key_set:
                if re_step1[key_name] == "*":
                    bytes_len = self.key.get_bytes_len(full_name_dict[key_name])
                    # buf += bytes([0 for _ in range(bytes_len)]) 
                    # No need to append zero bytes.
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
