from flymonlib.cmu_group import MemoryType
from flymonlib.flow_key import FlowKey

class Location:
    '''
    A read-only Class store the location information of a deployed task.
    A task may contain multiple locations (in different CMUs)
    A location represents a CMU info about the task.
    '''
    def __init__(self, 
                 group_id, group_type, key_dhash, param_dhash,
                 cmu_id, memory_type, memory_idx, 
                 resource_node, hasher):

        # location info, used to specify table.
        self._group_id = group_id
        self._group_type = group_type
        self._dhash_key = key_dhash
        self._dhash_param = param_dhash
        self._cmu_id = cmu_id
        self._memory_type = memory_type
        self._memory_idx = memory_idx

        # resource info, used to install rules.
        self._resource_node = resource_node

        # Maintain stateful rules.
        self._init_rules = []
        self._prep_rules = []
        self._oper_rules = []
    
        # Maintain hash handle
        self._hash = hasher
    
    def address_translate(self, phy_bitw, buf):
        """
        Args:
            Flow key to be hash and translate.
        Returns:
            Real memory address.
        """
        offset = 0
        if self.group_type == 2:
            offset = (self.cmu_id - 1) * 8
        mem_range = int( (2**phy_bitw)  /  (2**(self._memory_type-1)) )
        address_base = self._hash.compute(phy_bitw, buf, offset)
        current_idx = int(address_base / mem_range)
        offset = (self._memory_idx - current_idx) * mem_range
        # print(f"mem_range:{mem_range} current_idx: {current_idx}  current_idx:{current_idx}, offset:{offset}")
        # print(f"address_base:{address_base}, offset:{offset}, read:{address_base + offset}")
        return address_base + offset

    @property
    def group_id(self):
        return self._group_id

    @property
    def group_type(self):
        return self._group_type
    
    @property
    def dhash_key(self):
        return self._dhash_key
    
    @dhash_key.setter
    def dhash_key(self, hkey_id):
        self._dhash_key = hkey_id

    @property
    def dhash_param(self):
        return self._dhash_param
    
    @dhash_param.setter
    def dhash_param(self, hkey_id):
        self._dhash_param = hkey_id
    
    @property
    def cmu_id(self):
        return self._cmu_id

    @cmu_id.setter
    def cmu_id(self, cmu_id):
        self._cmu_id = cmu_id
    
    @property
    def memory_type(self):
        return self._memory_type

    @memory_type.setter
    def memory_type(self, memory_type):
        self._memory_type = memory_type
    
    @property
    def memory_idx(self):
        return self._memory_idx

    @memory_idx.setter
    def memory_idx(self, memory_idx):
        self._memory_idx = memory_idx

    @property
    def resource_node(self):
        return self._resource_node

    @property
    def init_rules(self):
        return self._init_rules
    
    @property
    def prep_rules(self):
        return self._prep_rules

    @property
    def oper_rules(self):
        return self._oper_rules
    
    @property
    def hash(self):
        return self._hash
    @hash.setter
    def hash(self, hash_obj):
        self._hash = hash_obj

    @init_rules.setter
    def init_rules(self, rule_list):
        self._init_rules = rule_list
    
    @prep_rules.setter
    def prep_rules(self, rule_list):
        self._prep_rules = rule_list

    @oper_rules.setter
    def oper_rules(self, rule_list):
        self._oper_rules = rule_list

    def __str__(self) -> str: 
        memory_type = MemoryType(self.memory_type)
        info = f"group_id={self.group_id}, hkey={self.dhash_key}, cmu_id={self.cmu_id}, memory_type:{memory_type.name} offset:{self.memory_idx}"
        return info