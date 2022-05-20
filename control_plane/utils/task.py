# -*- coding:UTF-8 -*-

from enum import Enum
from bitstring import BitArray, BitStream

class FlowKey:
    """Flow key definition"""
    def __init__(self, candidate_key_list):
        """
        Initially are key are not enabled.
        self.status: True -> Availiable
        """
        self.key_list = dict(candidate_key_list)
        for key in self.key_list.keys():
            bits = self.key_list[key]
            self.key_list[key] = (bits, BitArray(int=0, length=bits))
        self.status = True
    

    def set_mask(self, key_name, mask):
        """
        Set a mask to one of the candidate key.
        """
        if mask[0:2] != "0x":
            print("Invalid mask without leading '0x' or invalid mask length.") 
            return False
        origin_bits, _ = self.key_list[key_name]
        if len(mask[2:]) != origin_bits/4:
            print("Expected length: {}, given: {}.".format(origin_bits), len(mask[2:])*4)
            return False
        self.key_list[key_name] = (origin_bits, BitArray(mask))
        self.status = False
        return True

    def get_status(self):
        return self.status

    def reset(self):
        """
        Reset a compressed key.
        """
        for key in self.key_list.keys():
            bits,_ = self.key_list[key]
            self.key_list[key] = (bits, BitArray(int=0, length=bits))
        self.status = True

    def to_string(self):
        """
        Formally return a string of the key. Only the enabled key are listed,
        """
        key_string = " - ".join(["{}({})".format(key, self.key_list[key][1]) for key in self.key_list])
        return key_string

    def to_match_obj(self):
        """
        TODO: Return a BFRT object to configure the hash calculation unit.
        """
        return None

class FlowAttribute():
    """
    The base class of flow attributes.
    """
    def __init__(self):
        pass

class FlyMonTask:
    """ Task instance in FlyMon """
    def __init__(self, task_id, flow_key, flow_attr, mem_size):
        self.id = task_id
        self.key = flow_key
        self.attribute = flow_attr
        self.mem_size = mem_size
        pass

    def query(self, key):
        """
        Query the key according to the attribute.
        """
        return self.attribute.query(key)
    
    def install(self, resource_list):
        """
        Transform flow task into runtime rules.
        1. In initialization stage, it needs to select right key and params.
        2. In preprocessing stage, it needs to install how to pre-process parameters.
        3. In operation stage, it needs to install how to perform the statful operation.
        Please note that:
        a) the compressed keys are pre-configured by flymon manager.
        b) the address-translation are also implemented by the flymon manager. 
        The args are:
         - resource_list: a list of (CMU-Group ID, CMU ID).
        """
        for cmug_id, cmu_id in resource_list:
            pass
        pass
