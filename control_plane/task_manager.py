from flymonlib.resource import *
from flymonlib.flymon_task import FlyMonTask
from resource_manager import ResourceManager
from data_collector import DataCollector

class TaskManager:
    def __init__(self, runtime, cmug_configs):
        self.runtime = runtime
        self.tasks = {
            # key : task_id
            # val : [status, task_instance]
            #        status : True (Active) / False (Idle)
        }
        self.TASK_INC = 0

    def register_task(self, key, attribute, mem_size):
        """
        Input Example:
         - flow_key: hdr.ipv4.src_addr/24, hdr.ipv4.dst_addr/32
         - flow_attr: frequency(1)
         - memory_size: 65536
        Return:
         - A task object with resource lists and data querier.
        Exception:
         - may rase some exception.
        """
        task_id = self.TASK_INC + 1
        self.TASK_INC += 1
        task_instance = FlyMonTask(task_id, key, attribute, mem_size)
        self.tasks[task_id] = (False, task_instance)
        return task_instance
    
    def install_task(self, task_instance):
        """
        Setup a task instance.
        """
        

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
