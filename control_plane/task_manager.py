import ResourceManager as RM


class TaskManager():

    def __init__(self):
        self.resource_manager = RM()
        self.task_dict = {}
        self.task_id = 0
        pass

    def add_task(self, key, attribute, params, mem_size):
        if attribute == "fr":
            cmu_num = 3
            resource_list = self.resource_manager.alloc_resouces(key, params, cmu_num, mem_size)
            self.task_id += 1
            task = Task(task_id, key, attribute, params, mem_size)
            self.task_dict.append(task)
            task.install()
        return self.task_id

    def del_task(self):

        return 0

    def query_task(self, task_id, key):

        return 0

    def __sync__(self):
        ## Do not read from hw.
        pass
    
    def read_data
