from flymonlib.cmu_group import CMU_Group
import json

class ResourceManager():
    """
    ResourceManager manage all hardware resources.
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
    
    def allocate_resources(self, resource_list, mode=1):
        """
        Dynamic allocate resources for a task.
        TODO: Implement Smart Allocation strategy. 
        For example, we need to carefully allocate compressed keys to save hash resources.
         - If the compressed keys already exists in a CMU-Group, we need to allocate the task to the CMU-Group.
         - If the required compressed key can be generated from XOR from existing keys, we should also reuse the hash results.
        return:
        [resource_list], each resource includes:
         -  type : ['compressed_key', 'hash_param', 'std_param', 'memory']
         -  content : 
        """
        # task_id = task.get_id()
        # key = task.get_flowkey()
        # memory_size, memory_num = task.get_memory()
        # for cmug in self.cmu_groups:
        #     if False == cmug.allocate_memory(task_id, memory_size, memory_num):
        #         continue
        #     if False == cmug.allocate_compressed_key(key.to_config_dict()):
        #         cmug.release_memory(task_id)
        #         continue
        #     break
        pass

    def release_task(self, task):
        """
        Dynamic release memorys for a task.
        TODO: Implement 
        """
        pass