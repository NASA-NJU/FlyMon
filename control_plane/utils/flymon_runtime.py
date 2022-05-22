# -*- coding:UTF-8 -*-

class FlyMonRuntime_Base:
    """
    A base class for configuring CMU-Group tables.
    NOTE: This is a abstract class, used as a template for different runtime environments.
    In particular, Barefoot Runtime is an implementation of this base class. 
    """
    def __init__(self):
        pass

    def compression_stage_config(self, group_id, dhash_id, hash_mask):
        pass

    def initialization_stage_add(self, group_id, cmu_id, filter, task_id, key, param1, param2):
        pass

    def initialization_stage_del(self, group_id, cmu_id, filter):
        pass

    def preprocessing_stage_add(self, group_id, cmu_id, task_id, key_match, param_match, new_key, new_param):
        pass

    def preprocessing_stage_del(self, group_id, cmu_id, task_id):
        pass

    def operation_stage_add(self, group_id, cmu_id, task_id, operation_type):
        pass

    def operation_stage_del(self, group_id, cmu_id, task_id):
        pass
    
def FlyMonRuntime_BfRt(CMU_Runtime_Base):
    """
    A reference implementation of CMU Runtime based on Barefoot Runtime and Tofino.
    """
    def __init__(self, conn):
        CMU_Runtime_Base.__init__(self)
        self.conn = conn
        pass
    
    def compression_stage_config(self, group_id, dhash_id, hash_mask):
        hash_configure = "pipe.FlyMonIngress.cmu_group{}.hash_unit{}.$CONFIGURE"
        hash_compute = "pipe.FlyMonIngress.cmu_group{}.hash_unit{}.$CONFIGURE"
        pass

    def initialization_stage_add(self, group_id, cmu_id, filter, task_id, key, param1, param2):
        pass

    def initialization_stage_del(self, group_id, cmu_id, filter):
        pass

    def preprocessing_stage_add(self, group_id, cmu_id, task_id, key_match, param_match, new_key, new_param):
        pass

    def preprocessing_stage_del(self, group_id, cmu_id, task_id):
        pass

    def operation_stage_add(self, group_id, cmu_id, task_id, operation_type):
        pass

    def operation_stage_del(self, group_id, cmu_id, task_id):
        pass
    
 
