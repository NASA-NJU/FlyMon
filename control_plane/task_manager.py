from flymonlib.resource import *
from flymonlib.flymon_task import FlyMonTask
from resource_manager import ResourceManager
from data_collector import DataCollector

class TaskManager:
    def __init__(self):
        self.active_tasks={
            # tasi_id : (task_instance, [resource_list], data_querier)
        }
        self.idle_tasks={
            # tasi_id : (task_instance, [resource_list], data_querier)
        }
        self.TASK_INC = 0

    def register_task(self, key, attribute, mem_size, mem_num):
        """
        Input a task tuple (key, attribute(param), memory_size, memory_num).
        Return:
         - A task object with resource lists and data querier.
        """
        task_id = self.TASK_INC + 1
        self.TASK_INC += 1
        task = FlyMonTask(task_id, key, attribute, mem_size, mem_num)
        
        
        self.idle_tasks[task_id] = (task, resource_list)
        return task_id, task_instance, 


    def query_task(self, task_id, query_key):
        return 0

    def temp_data(self):
        return 
