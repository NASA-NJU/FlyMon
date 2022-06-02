from flymonlib.param import ParamType
from flymonlib.resource import *
from flymonlib.flymon_task import FlyMonTask
from flymonlib.flymon_runtime import FlyMonRuntime_BfRt

class TaskManager:
    def __init__(self, runtime : FlyMonRuntime_BfRt, cmug_configs : dict):
        self.runtime = runtime
        self.tasks = {
            # key : task_id
            # val : [status, task_instance]
            #        status : True (Active) / False (Idle)
        }
        self.TASK_INC = 0

    def register_task(self, key, attribute, mem_size):
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
        task_instance = FlyMonTask(task_id, None, key, attribute, mem_size)
        self.tasks[task_id] = [False, task_instance]
        return task_instance
    
    def install_task(self, task_instance : FlyMonTask):
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
        for location in task_instance.locations:
            # Install the compression stage.
            # TODO: if the hash is already configured, do not configure again.
            self.runtime.compression_stage_config(location.group_id, location.group_type,
                                                  location.hkeys[0], task_instance.key)
            # Install the initialization stage.
            if task_instance.attribute.param1.type == ParamType.CompressedKey:
                self.runtime.compression_stage_config(location.group_id, location.group_type,
                                                  location.hkeys[1], task_instance.attribute.param1)
            #     self.runtime.initialization_stage_add(location.group_id, location.group_type, location.cmu_id,
            #                                             task_instance.filter, # Filter
            #                                             task_instance.id,
            #                                             location.hkeys[0],
            #                                             location.hkeys[1],
            #                                             task_instance.attribute.param2)
            # else:
            #     self.runtime.initialization_stage_add(location.group_id, location.group_type, location.cmu_id,
            #                                             task_instance.filter, # Filter
            #                                             task_instance.id,
            #                                             location.hkeys[0],
            #                                             task_instance.attribute.param1,
            #                                             task_instance.attribute.param2)
            # # Install the pre-processing stage.
            # self.runtime.preprocessing_stage_add(location.group_id, location.group_type, location.cmu_id,
            #                                      task_instance.id, None, None) # Here I need two mappings.
            # # Install the operation stage.
            # self.runtime.operation_stage_add(location.group_id, location.group_type, location.cmu_id,
            #                                  task_instance.id, task_instance.attribute.operation)
            # pass

        self.tasks[task_instance.id][0] = True
    
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
        status = self.tasks[task_id][0]
        instance = self.tasks[task_id][1]
        if status is True:
            status = "Active"
        else:
            status = "Idle"
        print(f"[{status}] {str(instance)}")

    def query_task(self, task_id, query_key):
        return 0

    def temp_data(self):
        return 

    def get_instance(self, task_id):
        return self.tasks[task_id]