import traceback
from flymonlib.cmu_group import MemoryType
from flymonlib.param import ParamType
from flymonlib.resource import *
from flymonlib.flymon_task import FlyMonTask
from flymonlib.flymon_runtime import FlyMonRuntime_BfRt
from flymonlib.utils import calc_keymapping

class TaskManager:
    def __init__(self, runtime : FlyMonRuntime_BfRt, cmug_configs : dict):
        self.runtime = runtime
        self.cmug_bitw = {
            # key : cmu_group id
            # val : cmu_bitw (total_bits)
        }
        for cmug in cmug_configs:
            id = cmug["id"]
            cmu_bitw = cmug["key_bitw"]
            self.cmug_bitw[id] = cmu_bitw
        self.tasks = {
            # key : task_id
            # val : [status, task_instance, [init_rules], [preprocessing_rules], [operation_rules]]
            #        status : True (Active) / False (Idle)
        }
        self.TASK_INC = 0

    def register_task(self, filter, key, attribute, mem_size):
        """ Initial an idle FlyMonTask instance.
        Args:
            flow_key: hdr.ipv4.src_addr/24, hdr.ipv4.dst_addr/32
            flow_attr: frequency(1)
            memory_size: 65536
        Returns:
            A task object with resource lists and data querier.
        Exceptions:
            may rase some exception when generate a FlyMonTask object.
        """
        task_id = self.TASK_INC + 1
        self.TASK_INC += 1
        task_instance = FlyMonTask(task_id, filter, key, attribute, mem_size)
        self.tasks[task_id] = [False, task_instance] 
        return task_instance
    
    def install_task(self, task_id):
        """ Install rules for a task instance and make it active.
        Args:
            task_instace: a FlyMonTask object.
        Returns:
            install status? memory range?
        Exceptrions:
            may rasse some exceptions when install rules.
        ------------------------------------------------------------------
        Install Strategy:
            For each loation:
                1. install compressed keys if it is currently not enabled.
                2. install initialization stage rules according to location.hkeys (should in the order of key, param1) and attribute.param2.
                3. install preprocessing stage rules according to locations and attribute.param_mapping
                4. install operation stage rules according to attribute.operation
        """
        task_instance = self.tasks[task_id][1]
        try:
            for location in task_instance.locations:
                # Install the compression stage.
                # TODO: if the hash is already configured, do not configure again.
                self.runtime.compression_stage_config(location.group_id, location.group_type,
                                                      location.hkeys[0], task_instance.key)
                # Install the initialization stage.
                if task_instance.attribute.param1.type == ParamType.CompressedKey:
                    self.runtime.compression_stage_config(location.group_id, location.group_type,
                                                          location.hkeys[1], task_instance.attribute.param1.content)
                    location.init_rules = self.runtime.initialization_stage_add(location.group_id, location.group_type, location.cmu_id,
                                                            task_instance.filter, # Filter
                                                            task_instance.id,
                                                            location.hkeys[0],   # key
                                                            (task_instance.attribute.param1, location.hkeys[1]),
                                                            task_instance.attribute.param2)
                elif task_instance.attribute.param1.type == ParamType.Key:
                    self.runtime.compression_stage_config(location.group_id, location.group_type,
                                                          location.hkeys[1], task_instance.key)
                    location.init_rules = self.runtime.initialization_stage_add(location.group_id, location.group_type, location.cmu_id,
                                                            task_instance.filter, # Filter
                                                            task_instance.id,
                                                            location.hkeys[0],   # key
                                                            (task_instance.attribute.param1, location.hkeys[1]),
                                                            task_instance.attribute.param2)
                else:
                    location.init_rules = self.runtime.initialization_stage_add(location.group_id, location.group_type, location.cmu_id,
                                                            task_instance.filter, # Filter
                                                            task_instance.id,
                                                            location.hkeys[0],
                                                            (task_instance.attribute.param1, None),
                                                            task_instance.attribute.param2)
                # # Install the pre-processing stage.
                if location.memory_type != MemoryType.WHOLE.value or len(task_instance.attribute.param_mapping) != 0:
                    location.prep_rules = self.runtime.preprocessing_stage_add(location.group_id, location.group_type, location.cmu_id,
                                                        task_instance.id, 
                                                        calc_keymapping(self.cmug_bitw[location.group_id], 
                                                                        location.memory_type, 
                                                                        location.memory_idx),  # Key mappings.
                                                        task_instance.attribute.param_mapping) # Param1 mappings.
                # # Install the operation stage.
                location.oper_rules = self.runtime.operation_stage_add(location.group_id, location.group_type, location.cmu_id,
                                                       task_instance.id, task_instance.attribute.operation)
                # pass
            self.tasks[task_instance.id][0] = True
        except Exception as e:
            print(f"Failed! {e} when install rules for task {task_instance.id}")
            print(traceback.format_exc())
            # withdraw installed rules.
            self.uninstall_task(task_id)
            return False
        return True

    def uninstall_task(self, task_id):
        task_instance = self.tasks[task_id][1]
        for loc in task_instance.locations:
            self.runtime.initialization_stage_del(loc.group_id, loc.group_type, loc.cmu_id, loc.init_rules)
            loc.init_rules = []
            self.runtime.preprocessing_stage_del(loc.group_id, loc.group_type, loc.cmu_id, loc.prep_rules)
            loc.prep_rules = []
            self.runtime.operation_stage_del(loc.group_id, loc.group_type, loc.cmu_id, loc.oper_rules)
            loc.oper_rules = []
        self.tasks[task_instance.id][0] = False
    
    def show_tasks(self):
        """
        Show all tasks one by one.
        """
        for task_id in self.tasks.keys():
            self.show_task(task_id)
        
    def show_task(self, task_id):
        """ Print task infomation
        Args:
            task_id: the allocated task id.
        Returns:
            None
        """
        print(f"----------------------------------------------------")
        status = self.tasks[task_id][0]
        instance = self.tasks[task_id][1]
        if status is True:
            status = "Active Task"
        else:
            status = "Idle Task"
        print(f"[{status}] \n{str(instance)}")

    def query_task(self, task_id, query_key):
        return 0

    def temp_data(self):
        return 

    def get_instance(self, task_id):
        if task_id not in self.tasks.keys():
            return None
        return self.tasks[task_id][1]