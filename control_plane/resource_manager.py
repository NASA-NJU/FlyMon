from flymonlib.resource import ResourceType
from flymonlib.cmu_group import CMU_Group
import json

class ResourceManager():
    """
    ResourceManager manage all hardware resources.
    """
    def __init__(self, cmug_configs):
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
            return
        self.cmu_groups[group_id-1].show_status()
    
    def allocate_resources(self, resource_list, mode=1):
        """
        Dynamic allocate resources for a task.
        Input: 
         - A list of resource object.
        Return:
         - [locations] : a list of (group_type, group_id, cmu_id, segment_type, segment_id)
        --------------------------------------------------------------------------------
        Current Strategy: 
            a) Try to allocate them in a CMU-Group.
            b) Iterate all CMU-Group one by one.
                b1) Check Key Resources
                b2) Check Param Resources.
                c) If b1 && b2 are satisfied, inerate alls CMU in this group one by one:
                    c1) Read a memory resource, if the CMU has enough memory, append 
                        (group_id, group_type, cmu_id, segment_type, segment_id) to locations.
                        then remove the memory resource.
                d) If all the memory resources are removed: return locations.
                e) Else, iterate the next CMU-Group.
        --------------------------------------------------------------------------------
        TODO: Implement a Smarter Allocation strategy. 
        For example, we need to carefully allocate compressed keys to save hash resources.
         - If the required compressed key can be generated from XOR from existing keys, we should also reuse the hash results.
         - How to efficient allocate the memory (I mean, improved memory utilization)?
        """
        locations = []
        if resource_list is None:
            return locations
        required_key = []
        required_param = []
        required_memory = []
        for resource in resource_list:
            if resource.type == ResourceType.Memory:
                required_memory.append(resource)
            elif resource.type == ResourceType.CompressedKey:
                required_key.append(resource)
            elif resource.type == ResourceType.StdParam:
                required_param.append(resource)
                
        for cmug in self.cmu_groups:
            if cmug.allocat

                resource.type == ResourceType.CompressedKey:

                elif resource.type == ResourceType.StdParam:
                    print("Need a StdParam")
            break

        # task_id = task.get_id()
        # key = task.get_flowkey()
        # memory_size, memory_num = task.get_memory()

        pass

    def release_task(self, task):
        """
        Dynamic release memorys for a task.
        TODO: Implement 
        """
        pass