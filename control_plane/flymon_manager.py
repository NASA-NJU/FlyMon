from cmu_group import CMU_Group
import json

class FlyMonManager():
    """
    FlyMonManager integrate the functions of Resource Manager and Task Manager
    """

    def __init__(self, config_file):
        cmug_configs = json.load(open(config_file, 'r'))
        self.cmu_groups = []
        for cmug in cmug_configs:
            cmu_num = cmug["cmu_num"]
            cmu_size = cmug["cmu_size"]
            mau_start = cmug["mau_start"]
            candidate_key_list = cmug["candidate_key_list"]
            std_params = cmug["std_params"]
            type = cmug["type"]
            id = cmug["id"]
            self.cmu_groups.append(CMU_Group(group_id=id, 
                                             group_type=type, 
                                             cmu_num=cmu_num, 
                                             memory_size=cmu_size, 
                                             stage_start=mau_start, 
                                             candidate_key_list=candidate_key_list, 
                                             std_params=std_params))
        pass


    def show_status(self, group_id):
        if group_id > len(self.cmu_groups):
            print("Invalid CMU-Group id: {}".format(group_id))
        self.cmu_groups[group_id-1].show_status()

    def add_task(self, key, attribute, params, mem_size):
        pass

    def del_task(self):

        return 0

    def query_task(self, task_id, key):

        return 0

    def __sync__(self):
        ## Do not read from hw.
        pass
