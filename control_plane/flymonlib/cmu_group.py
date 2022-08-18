# -*- coding:UTF-8 -*-
from __future__ import print_function 
import math
from flymonlib.resource import *
from flymonlib.utils import PerfectBinaryTree
from flymonlib.flow_key import FlowKey
from flymonlib.param import *
import ipaddress

class MemoryType(Enum):
    """
    A class to represent memory types for each CMU.
    """
    WHOLE       = 1      #  1
    HALF        = 2      #  1/2
    QUARTAR     = 3      #  1/4
    EIGHTH      = 4      #  1/8
    SIXTEENTH   = 5      #  1/16
    THIRTY      = 6      #  1/32

MAX_DIV = 32

class CMU:
    """
    A register memory in FlyMon is mananged by a binary tree.
    """
    def __init__(self, max_div=MAX_DIV):
        """
        max_div is the maximum memory divisions of a CMU, 32 is the default.
        """
        self.max_type = int(math.log(max_div, 2)) # maximum divisions : 2**types
        self.filter_set = []
        self.mem_tree = PerfectBinaryTree()
        for i in range(self.max_type + 1):
            for j in range(2**i):
                # (type, type_idx/mem_idx, task_id)
                #  - type is 1,2,3,...,MIX_DIV
                #  - mem_idx is offset on the type of memory, for example ,if the type is 2(HALF), the mem_idx should be 1 or 2.
                #  - task_id, who uses this memory block?
                self.mem_tree.append([i+1, j, 0]) 



    def check_memory(self, type):
        """Only check but not allocate.
        """
        root = self.mem_tree.root()
        nodes = self.mem_tree.inorderTraversal(root)
        for node in nodes:
            # Z the node's size suitable and the node is available
            if node.data[0] == type and node.data[2] == 0:
                sub_nodes = self.mem_tree.inorderTraversal(node)
                is_ok = True
                # Z check if all the subnode is available
                for snode in sub_nodes:
                    if snode.data[2] != 0:
                        is_ok = False
                if is_ok:
                    # for snode in sub_nodes:
                    #     snode.data[2] = task_id
                    return node.data[1]
        return 0

    def alloc_memory(self, task_id, memory_type, type_idx):
        """
        Allocate memory for task_id with memory type and memory index.
        """
        root = self.mem_tree.root()
        nodes = self.mem_tree.inorderTraversal(root)
        for node in nodes:
            # Z the node's size suitable and the node is available
            if node.data[0] == memory_type and node.data[1] == type_idx:
                sub_nodes = self.mem_tree.inorderTraversal(node)
                is_ok = True
                # Z check if all the subnode is available
                for snode in sub_nodes:
                    if snode.data[2] != 0:
                        is_ok = False
                if is_ok:
                    for snode in sub_nodes:
                        snode.data[2] = task_id
                    return 0
                else:
                    raise RuntimeError("Faild to allocate memory in CMU.")
    
    def release_memory(self, task_id):
        """ Release the memory of a given task_id.
        Args:
            task_id: measurement task_id.
        Returns:
            memory type.
        """
        memory_type = 0
        root = self.mem_tree.root()
        nodes = self.mem_tree.inorderTraversal(root)
        for node in nodes:
            if node.data[2] == task_id:
                node.data[2] = 0
                if node.data[0] >= memory_type:
                    # the largest memory type is the true type of the task.
                    # smaller is used to indicate the node has been occupied.
                    memory_type = node.data[0]
        return memory_type

    def show_memory(self):
        """
        Show the memory in line style. There are 'max_div' parts, 
        where a running task are tagged.
        """
        root = self.mem_tree.root()
        nodes = self.mem_tree.inorderTraversal(root)
        leaf_nodes = []
        for node in nodes:
            if node.data[0] == self.max_type:
                leaf_nodes.append(node)
        for node in leaf_nodes:
            print("|{:^4}".format(node.data[1]), end = '')
        print('|')



class CMU_Group():
    """Status of CMU_Group instance in control plane"""
    def __init__(self, group_id, group_type, meta_id, cmu_num, key_bitw, memory_size, stage_start, candidate_key_list, std_params, next_group):
        """
        There are properties and status of CMU_Group class.
        As for properties, it loads them from "cmu_groups.json" file generated from the "flymon_compiler.py".
        As for status, each CMU-Group has several members, including compressed keys and CMUs.
          - The compressed keys can be configured to generate specific hash values of particular flow keys.
          - The CMUs holds the memory informations.
        When allocate a task, flymon manager needs to check following things:
          - compressed keys
          - CMU memory
          - standard parameters
        """
        # Properties.
        self._group_id = group_id
        self._group_type = group_type
        self._meta_id = meta_id
        self._cmu_num = cmu_num
        self._key_bitw = key_bitw
        self._memory_size = memory_size
        self._stage_start = stage_start
        self._next_group = next_group

        ## Param Resources.
        self._std_params = []
        for param_name in std_params.keys():
            # param_str to Param Resources.
            self._std_params.append(Param(ParamType.StdParam, param_name))

        ## Compressed Key Resources.
        if group_type == 1:
            self._compressed_keys = [[FlowKey(candidate_key_list), 16,  []] for _ in range(3)]  # key, bitw, tasks.
        else:
            self._compressed_keys = [ [FlowKey(candidate_key_list), 32, []], 
                                      [FlowKey(candidate_key_list), 16, []] ] 
        
        ## CMU and Memory Resources.
        ###  #0 CMU Obj  #1 rest_memory  #2 existing filters
        self._cmus = [[CMU(), self._memory_size, []] for i in range(self._cmu_num)]  # Currently we only support 32 divisions.
        pass
        
    @property
    def cmu_num(self):
        return self._cmu_num
    
    @property
    def group_id(self):
        return self._group_id

    @property
    def group_type(self):
        return self._group_type

    @property
    def meta_id(self):
        return self._meta_id

    @property
    def key_bitw(self):
        return self._key_bitw

    @property
    def memory_size(self):
        return self._memory_size
    
    @property
    def next_group(self):
        return self._next_group

    def show_status(self):
        """
        show current status of CMU-Group.
        """
        LINE_LEN = 60
        print('-'*LINE_LEN)
        print("Status of CMU-Group {}".format(self._group_id).center(LINE_LEN))
        print('-'*LINE_LEN)
        for idx, ck in enumerate(self._compressed_keys):
            if str(ck[0]) == "":
                print("Compressed Key {} ({}b): Empty".format(idx+1, ck[1]))
            else:
                print("Compressed Key {} ({}b): {}".format(idx+1, ck[1], str(ck[0])))
        print('-'*LINE_LEN)
        for idx, (cmu, rest_mem, _) in enumerate(self._cmus):
            print("CMU-{} Rest Memory: {}".format(idx+1, rest_mem))
            # cmu.show_memory()
        print('-'*LINE_LEN)
    

    def check_compressed_key(self, required_key):
        """
        Check if the hkeys are avliable in this CMU Group.
        Return:
            hkey_dict: {DHASH ID : bit width}
        """
        # mirror the 32-bit keys because it can be used multiple times.
        hkey_dict = {}
        for idx in range(len(self._compressed_keys)):
            task_list = self._compressed_keys[idx][2]
            if len(task_list) != 0:
                # The key as already be allocated.
                if self._compressed_keys[idx][0] == required_key:
                    hkey_dict[idx+1] = self._compressed_keys[idx][1]
            else:
                hkey_dict[idx+1] = self._compressed_keys[idx][1]
        return hkey_dict

    def check_parameter(self, required_param):
        """
        Check if the params are avaliable in this CMU-Group. 
        """
        for param in self._std_params:
            if required_param == param.content:
                return True
        return False



    def check_filter_and_memory(self, task_filter, mem_size, mode=1):
        """Check if there are CMUs have traffic intersection and sufficient memory.
        Args:
            @filter: the new task's filter.
            @mem_size: required memory size.
            @mode: efficient(1) or accurate(2) mode?
        Return:
            a dict of usable CMUs. Resource manager needs to consider CMU repeation by itself.
            {
                CMU ID : {real size, memory type, type_index}
            }
            Otherwise, empty dict {}
        """
        cmu_dict = {}
        for idx in range(self._cmu_num):
            cmu_id = idx + 1
            # Check filter : Src Net and Dst Net
            # Currently, our filter is src_ip/prefix, dst_ip/prefix
            task_network_1 = ipaddress.ip_network(f"{task_filter[0][0]}/{task_filter[0][1]}")
            task_network_2 = ipaddress.ip_network(f"{task_filter[1][0]}/{task_filter[1][1]}")
            is_filter_ok = True
            for existing_filter in self._cmus[idx][2]:
                existing_network_1 = ipaddress.ip_network(f"{existing_filter[0][0]}/{existing_filter[0][1]}")
                existing_network_2 = ipaddress.ip_network(f"{existing_filter[1][0]}/{existing_filter[1][1]}")
                # Only when both src_net and dst_net have traffic intersection, the CMU cannot be used.
                if ( task_network_1.subnet_of(existing_network_1) or task_network_1.supernet_of(existing_network_1) ) and (task_network_2.subnet_of(existing_network_2) or task_network_2.supernet_of(existing_network_2)):
                    is_filter_ok = False
                    break
            if not is_filter_ok:
                # There is a traffic intersection, check next CMU.
                continue
            # Check memory
            if mem_size > self._memory_size: 
                print("Invalid memory size : {}".format(mem_size))
                return {}
            memory_type = int(math.log2(self._memory_size / mem_size)) + 1
            if memory_type < 1:
                print(f"No enough memory, allocated as the max : {self._memory_size}")
                memory_type = 1
            if memory_type > MAX_DIV:
                print(f"Too small memory, allocated as the min : {int(self._memory_size/MAX_DIV)}")
                memory_type = MAX_DIV
            if mode == 2:
                # TODO: need to implement a simple efficient mode.
                pass
            cmu = self._cmus[idx][0]
            if self._cmus[idx][1] < mem_size:
                continue
            memory_idx = cmu.check_memory(memory_type)
            if memory_idx >= 0:
                # self._cmus[idx][1] = self._cmus[id][1] - int(self._memory_size/memory_type)
                cmu_dict[cmu_id] = (int(self._memory_size/memory_type), memory_type, memory_idx)
        return cmu_dict

    def allocate_compressed_keys(self, task_id, hkeys):
        """ Allocate compressed keys for a specific task.
        Args:
            @task_id
            @hkeys: [(dhash_id, flowkeyobj)]
        """
        for hkey in hkeys:
            idx = hkey[0] - 1
            if len(self._compressed_keys[idx][2]) == 0:
                self._compressed_keys[idx][0].set(hkey[1])
            if task_id not in self._compressed_keys[idx][2]:
                self._compressed_keys[idx][2].append(task_id)

    def allocate_filter_and_memory(self, task_id, cmu_id, task_filter, memory_type, type_idx):
        """ Try to allocate memory for a specific task.
        Args:
            @task_id: task id
            @cmu_list: [cmu_id, memory_type, type_idx]
        Returns : 
            No return.
        """
        id = cmu_id - 1
        cmu = self._cmus[id][0]
        cmu.alloc_memory(task_id, memory_type, type_idx)
        self._cmus[id][1] -= int(self._memory_size/memory_type)
        self._cmus[id][2].append(task_filter)

    def release_filter_and_memory(self, task_id, task_filter):
        """
        Release memory for task_id.
        """
        for idx in range(len(self._cmus)):
            memory_type = self._cmus[idx][0].release_memory(task_id)
            if memory_type > 0:
                self._cmus[idx][1] += int(self._memory_size/memory_type)
                self._cmus[idx][2].remove(task_filter)
        pass

    def release_compressed_keys(self, task_id):
        """
        Release compressed keys.
        """
        # [FlowKey(candidate_key_list), 32, []
        for hkey, _, tasks in  self._compressed_keys:
            if task_id not in tasks:
                continue
            tasks.remove(task_id)
            if len(tasks) == 0:
                hkey.reset()
    