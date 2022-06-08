from flymonlib.cmu_group import MemoryType
from flymonlib.flow_key import FlowKey



class Location:
    '''
    A read-only Class store the location information of a deployed task
    '''
    def __init__(self, location_list, hasher):
        # parse the location list
        self._group_id = location_list[0]
        self._group_type = location_list[1]
        self._hkeys = location_list[2]
        self._cmu_id = location_list[3]
        self._memory_type = location_list[4]
        self._memory_idx = location_list[5]

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
    def hkeys(self):
        return self._hkeys
    
    @hkeys.setter
    def hkeys(self, hkeys):
        self._hkeys = hkeys
    
    @property
    def cmu_id(self):
        return self._cmu_id
    
    @property
    def memory_type(self):
        return self._memory_type
    
    @property
    def memory_idx(self):
        return self._memory_idx

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

    @init_rules.setter
    def init_rules(self, rule_list):
        self._init_rules = rule_list
    
    @prep_rules.setter
    def prep_rules(self, rule_list):
        self._prep_rules = rule_list

    @oper_rules.setter
    def oper_rules(self, rule_list):
        self._oper_rules = rule_list

    @hash.setter
    def hash(self, hash_obj):
        self._hash = hash_obj

    def __str__(self) -> str: 
        memory_type = MemoryType(self.memory_type)
        info = f"group_id={self._group_id}, group_type={self._group_type}, hkeys={self._hkeys}, cmu_id={self._cmu_id}, memory_type:{memory_type.name} offset:{self._memory_idx}"
        return info