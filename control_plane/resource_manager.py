from flymonlib.hash import HASHES_16, HASHES_32
from flymonlib.flymon_runtime import FlyMonRuntime_BfRt
from flymonlib.location import Location
from flymonlib.flymon_task import FlyMonTask
from flymonlib.resource import ResourceType
from flymonlib.cmu_group import CMU_Group

class ResourceManager():
    """
    ResourceManager manages all hardware resources.
    """
    def __init__(self, runtime : FlyMonRuntime_BfRt, cmug_configs):
        self.runtime = runtime
        self.cmu_groups = []
        self.dhashes = {
            # key : (group_id, dhash_id)
            # val : hasher object
        }
        ## TEMP hasher allocation id
        hash_16_id = 0
        hash_32_id = 0
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
            self.runtime.clear_all(id, type, cmu_num)
            # Setup Dashes.
            dhash_num = 0
            if type == 1:
                dhash_num = 3
            else:
                dhash_num = 2
            # print(f"Setup Hash Units for CMU-Group {id}")
            for idx in range(dhash_num):
                dhash_id = idx + 1
                if type == 2 and dhash_id == 1:
                    self.runtime.setup_dhash(id, type, dhash_id, HASHES_32[hash_32_id])
                    self.dhashes[(id, dhash_id)] = HASHES_32[hash_32_id]
                    hash_32_id += 1
                else:
                    self.runtime.setup_dhash(id, type, dhash_id, HASHES_16[hash_16_id])
                    self.dhashes[(id, dhash_id)] = HASHES_16[hash_16_id]       
                    hash_16_id += 1        

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
         - [locations] : a list of Location(group_id, group_type, (hkey1, ...), cmu_id, memory_type, memory_idx)
         - mem_idx is offset on the type of memory, for example ,if the type is 2(HALF)
         - the mem_idx should be 1 or 2.
         - (hkey1, ...) denotes the hash_ids that will be used by key and param1, respectively. 
        --------------------------------------------------------------------------------
        Current Strategy: 
            a) Try to allocate them in a CMU-Group.
            b) Iterate all CMU-Group one by one.
                b1) Check Key Resources
                b2) Check Param Resources.
                c) If b1 && b2 are satisfied, iterate alls CMU in this group one by one:
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
        
        priority_cmug_list = self.cmu_groups
        if len(required_memorys) > 1:
            # We favor group_type 2 for multi-row algorithms.
            priority_cmug_list = sorted(self.cmu_groups, key=lambda x: -x.group_type)
        for cmug in priority_cmug_list:
            # TODO: each cmug need not to have all required_keys, just at least one flowkey.
            hkeys = cmug.allocate_compressed_keys(task_id, required_keys) 
            has_param = cmug.check_parameters(required_params)
            if hkeys is not None and has_param:
                used_cmu = []
                for required_memory in list(required_memorys): # shallow copy
                    if len(used_cmu) == cmug.cmu_num : 
                        break
                    for id in range(cmug.cmu_num):
                        cmu_id = id + 1
                        if cmu_id not in used_cmu:
                            # Each task cannot use the same CMU twice.
                            re = cmug.allocate_memory(cmu_id, task_id, required_memory.content, mode=1)
                            if re is not None:
                                memory_type = re[0]
                                memory_idx = re[1]
                                hkeys_for_this_location = [hkeys[0]] + hkeys[len(required_memorys):]
                                flow_key = hkeys.pop(0) # use this hkey as flow key
                                locations.append(Location(                                
                                                           [cmug.group_id, cmug.group_type, hkeys_for_this_location, cmu_id, memory_type, memory_idx], 
                                                           hasher=self.dhashes[(cmug.group_id, flow_key)] 
                                                         )
                                                )
                                required_memorys.remove(required_memory)
                                required_keys.pop(0) # Dangers, remove a required flow/compressed key.
                                used_cmu.append(cmu_id)
                                break # To allocate the next required_memory
                            else:
                                # print("No enough memory")
                                pass
                # if len(hkeys) != 0:
                #     cmug.release_compressed_keys(task_id, hkeys) # release unused hkeys.
                if len(required_memorys) == 0:
                    break
        if len(required_memorys) != 0:
            # Allocation Failed. Need to recycle the memory.
            for location in locations:
                group_id = location.group_id
                memory_type = location.memory_type
                self.cmu_groups[group_id-1].release_memory(task_id, memory_type)
                self.cmu_groups[group_id-1].release_compressed_keys(task_id, location.hkeys)
            return None
        return locations

    def release_task(self, task_instance: FlyMonTask):
        """
        Dynamic release memorys and compressed keys for a task.
        """
        for location in task_instance.locations:
            group_id = location.group_id
            memory_type = location.memory_type
            self.cmu_groups[group_id-1].release_memory(task_instance.id, memory_type)
            self.cmu_groups[group_id-1].release_compressed_keys(task_instance.id, location.hkeys)
        pass