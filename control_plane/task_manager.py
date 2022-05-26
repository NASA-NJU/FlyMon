from flymonlib.flymon_task import FlyMonTask
from resource_manager import ResourceManager
from data_collector import DataCollector

class TaskManager:
    def __init__(self):
        self.tasks={
            # tasi_id : (task_instance, [resource_list])
        }
        self.TASK_INC = 0
        self.rm = ResourceManager()

        # TODO: Implement a data collector.
        # Requirements:
        # - Running asynchronously
        # - provide query interfaces.
        # - ** provide virtual-to-physical translation**.
        self.dc = DataCollector() 
        
    def register_task(self, key, attribute, mem_size, mem_num):
        task_id = self.TASK_INC + 1
        self.TASK_INC += 1
        task = FlyMonTask(task_id, key, attribute, mem_size, mem_num)
        resource_list = self.rm.allocate_resources(task)
        self.tasks[task_id] = (task, resource_list)
        return task_id

    def query_task(self, task_id, query_key):
        return 0

    def temp_data(self):
        return 
