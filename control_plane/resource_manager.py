from __future__ import annotations
from flymonlib.param import ParamType
from flymonlib.hash import HASHES_16, HASHES_32
from flymonlib.flymon_runtime import FlyMonRuntime_BfRt
from flymonlib.location import Location
from flymonlib.flymon_task import FlyMonTask
from flymonlib.cmu_group import CMU_Group
from flymonlib.utils import calc_keymapping

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
            next_group = cmug["next_group"]
            key_bitw = cmug["key_bitw"]
            id = cmug["id"]
            self.cmu_groups.append(CMU_Group(group_id=id, 
                                             group_type=type, 
                                             cmu_num=cmu_num, 
                                             key_bitw = key_bitw,
                                             memory_size=cmu_size, 
                                             stage_start=mau_start, 
                                             candidate_key_list=candidate_key_list, 
                                             std_params=std_params,
                                             next_group=next_group))
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
    
    def check_cmug(self, cmu_group, annotation, resource_node):
        """Judge if there is a cmu meets the resource_list requirements.
        Args:
            @cmu_group: CMU Group object.
            @annotation: The task already used Resources.
                            [
                                [DHASH IDs], [CMU IDs]
                            ]
            @resource_list: Resource List.
        Return:
            Valid Location or None.
        """
        # We get avalible keys here. But the task may already use the keys.
        # We should note that 32-bit keys can be reused by different CMU of a CMU Group.
        # According to the annnotation, we can efficiently allocate the CMUs.
        location = Location(cmu_group.group_id, cmu_group.group_type, None, None, None, None, None, resource_node, None)
        if resource_node.param1.type == ParamType.StdParam:
            has_param = cmu_group.check_parameter(resource_node.param1.content)
            if has_param is False:
                return None
        if resource_node.param1.type == ParamType.CompressedKey:
            avalible_hparams = cmu_group.check_compressed_key(resource_node.param1.content)
            if len(avalible_hparams) <= 0:
                return None
            for hparam in avalible_hparams.keys():
                if hparam not in annotation[0] and avalible_hparams[hparam] != 32:
                    # key and param can not select the same dhash currently.
                    # we prefer use 32-bit key as flow key, not param.
                    annotation[0].append(hparam)
                    # print(hparam)
                    location.dhash_param = hparam
                    # print(location.dhash_param)
                    break
            if location.dhash_param is None:
                return None

        avalible_hkeys = cmu_group.check_compressed_key(resource_node.key)
        for used_key in annotation[0]:
            # prefer to use already-in-use 32-bit keys.
            if used_key in avalible_hkeys.keys():
                if avalible_hkeys[used_key] == 32:
                    # can be reused.
                    location.dhash_key = used_key
                    break
        if location.dhash_key is None:
            # need to occupy a new avalible compressed key.
            for selected_key in avalible_hkeys.keys():
                if selected_key not in annotation[0]:
                    # can not reuse 16-bit keys.    
                    annotation[0].append(selected_key)
                    location.dhash_key = selected_key
                    break
        if location.dhash_key is None:
            return None 

        avalible_cmus = cmu_group.check_memory(resource_node.memory)
        for cmu_id in avalible_cmus.keys():
            if cmu_id not in annotation[1]:
                # a task can only use a CMU once.
                annotation[1].append(cmu_id)
                location.cmu_id = cmu_id
                location.memory_type = avalible_cmus[cmu_id][1]
                location.memory_idx = avalible_cmus[cmu_id][2]
                break
        if location.cmu_id is None:
            return None
        return location

    def allocate_resources(self, task_id, attribute, resource_graph, mode=1):
        """Dynamic allocate resources for a task.
        Args:
            @task_id.
            @resource graph. Each node represents resources of a CMU.
                each edge between two nodes represents the connection demand of two CMUs.
                e.g., [ [ [resource_list1], [resource_list2] ], [ [resource_list3] ] ] require 3 CMU,
                    CMU1 and CMU2 needs to be adjacent, while CMU3 does not.
            @mode. TODO. Memory Allocation Mode.
        Return:
            A set of Locations whicn can directly used to install rules in the data plane.
            Otherwise, None
        """
        priority_cmug_list = self.cmu_groups
        if len(resource_graph) > 1 and attribute.cmu_num > 1:
            priority_cmug_list = sorted(self.cmu_groups, key=lambda x: -x.group_type)
        # Annotations is used to help CMU Group's mark which Groups are used for this task to facilitate better use of resources.
        # It records which CMUs of each Group were used for this task.
        annotations = {}
        for cmu_group in priority_cmug_list:
            annotations[cmu_group.group_id] = [[], []]   
        final_locations = []
        for nodes in resource_graph:
            locations = []
            chain_len = len(nodes)
            if chain_len > 3:
                print("Cannot support chain length larger than 3!")
                return None
            for i in range(len(priority_cmug_list) - (chain_len - 1)):
                all_ok = True
                # get a valid chain (non-overlab CMU Groups)
                chain_of_groups = [priority_cmug_list[i]]
                head = chain_of_groups[0]
                while head.next_group != 0:
                    chain_of_groups.append(self.cmu_groups[head.next_group-1])
                    head = self.cmu_groups[head.next_group-1]
                # done
                for j in range(chain_len):
                    cmu_group = chain_of_groups[j]
                    location = self.check_cmug(cmu_group, annotations[cmu_group.group_id], nodes[j])
                    if location is None:
                        all_ok = False
                        break
                    # calc key mapping.
                    location.resource_node.key_mapping = calc_keymapping(self.cmu_groups[location.group_id-1].key_bitw, 
                                                                         location.memory_type, 
                                                                         location.memory_idx)
                    # set hasher
                    location.hash = self.dhashes[(location.group_id, location.dhash_key)]
                    locations.append(location)
                if all_ok:
                    final_locations += locations
                    break
                else:
                    locations = []
        if final_locations is not None:
            # allocate it.
            self.allocate_locations(task_id, final_locations)
        return final_locations

    def allocate_locations(self, task_id, locations):
        """
        Allocate a list of locations.
        """
        for loc in locations:
            required_keys = [] # [(dhash_id, flowkeyobj)]
            required_keys.append([loc.dhash_key, loc.resource_node.key])
            if loc.resource_node.param1.type == ParamType.CompressedKey:
                required_keys.append([loc.dhash_param, loc.resource_node.param1.content])
            group_id = loc.group_id
            self.cmu_groups[group_id-1].allocate_compressed_keys(task_id, required_keys)
            self.cmu_groups[group_id-1].allocate_memory(task_id, loc.cmu_id, loc.memory_type, loc.memory_idx)

    def release_task(self, task_instance: FlyMonTask):
        """
        Dynamic release memorys and compressed keys for a task.
        """
        for loc in task_instance.locations:
            group_id = loc.group_id
            self.cmu_groups[group_id-1].release_memory(task_instance.id)
            self.cmu_groups[group_id-1].release_compressed_keys(task_instance.id)
        pass