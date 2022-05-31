from flymonlib.resource import ResourceType
from flymonlib.cmu_group import CMU_Group

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
    
    def allocate_resources(self, task_id, resource_list, mode=1):
        """
        Dynamic allocate resources for a task.
        Args: 
         - A list of resource object.
         - task_id : used for mark the memory.
        Returns:
         - [locations] : a list of (group_id, group_type, cmu_id, memory_type, memory_idx)
         - mem_idx is offset on the type of memory, for example ,if the type is 2(HALF)
         - the mem_idx should be 1 or 2.
        --------------------------------------------------------------------------------
        Current Strategy: 
            a) Try to allocate them in a CMU-Group.
            b) Iterate all CMU-Group one by one.
                b1) Check Key Resources
                b2) Check Param Resources.
                c) If b1 && b2 are satisfied, inerate alls CMU in this group one by one:
                    c1) Read a memory resource, if the CMU has enough memory, append 
                        (group_id, group_type, cmu_id, memory_type, memory_idx) to locations.
                        then remove the memory resource.
                d) If all the memory resources are removed: return locations.
                e) Else, iterate the next CMU-Group.
            f) If don't have enough memory for all CMU-Groups. Release Resources and Return None.
        --------------------------------------------------------------------------------
        TODO: Implement a Smarter Allocation strategy. 
        For example, we need to carefully allocate compressed keys to save hash resources.
         - If the required compressed key can be generated from XOR from existing keys, we should also reuse the hash results.
         - How to efficient allocate the memory (I mean, improved memory utilization)?
        """
        locations = []
        if resource_list is None:
            return locations
        required_keys = []
        required_params = []
        required_memorys = []
        for resource in resource_list:
            if resource.type == ResourceType.Memory:
                required_memorys.append(resource)
            elif resource.type == ResourceType.CompressedKey:
                required_keys.append(resource)
            elif resource.type == ResourceType.StdParam:
                required_params.append(resource)

        for cmug in self.cmu_groups:
            if cmug.check_compressed_keys(required_keys) and cmug.check_parameters(required_params):
                # TODO: we only support alloclate the same memory for many times.
                for idx, required_memory in enumerate(list(required_memorys)): # shallow copy
                        # TODO: Here are some problems.
                        cmu_id = idx + 1
                        re = cmug.allocate_memory(cmu_id, task_id, required_memory.content, mode=1)
                        if re is not None:
                            memory_type = re[0]
                            memory_idx = re[1]
                            locations.append((cmug.group_id, cmug.group_type, cmu_id, memory_type, memory_idx))
                            required_memorys.remove(required_memory)
                if len(required_memorys) == 0:
                    return locations
        if len(required_memorys) != 0:
            # Allocation Failed. Need to recycle the memory.
            for location in locations:
                group_id = location[0]
                memory_type = location[3]
                self.cmu_groups[group_id-1].release_memory(task_id, memory_type)
            return None
        else:
            # Finally, allocate the keys.
            for location in locations:
                group_id = location[0]
                self.cmu_groups[group_id-1].allocate_compressed_keys(required_keys)
            return locations

    def release_task(self, task):
        """
        Dynamic release memorys for a task.
        TODO: Implement 
        """
        pass