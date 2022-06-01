class Location:
    '''
    A read-only Class store the location information of a deployed task
    '''
    def __init__(self, location_list):
        # parse the location list
        self._group_id = location_list[0]
        self._group_type = location_list[1]
        self._hkeys = location_list[2]
        self._cmu_id = location_list[3]
        self._memory_type = location_list[4]
        self._memory_idx = location_list[5]
        
    @property
    def group_id(self):
        return self._group_id

    @property
    def group_type(self):
        return self._group_type
    
    @property
    def hkeys(self):
        return self._hkeys
    
    @property
    def cmu_id(self):
        return self._cmu_id
    
    @property
    def memory_type(self):
        return self._memory_type
    
    @property
    def memory_idx(self):
        return self._memory_idx

    # def __str__(self):
    #     return str(self._content)
