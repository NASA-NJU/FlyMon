# -*- coding:UTF-8 -*-
from __future__ import print_function 
import math
from flymonlib.resource import *
from flymonlib.utils import PerfectBinaryTree
from flymonlib.flow_key import FlowKey

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
        self.mem_tree = PerfectBinaryTree()
        for i in range(self.max_type + 1):
            for j in range(2**i):
                # (type, type_idx/mem_idx, task_id)
                #  - type is 1,2,3,...,MIX_DIV
                #  - mem_idx is offset on the type of memory, for example ,if the type is 2(HALF), the mem_idx should be 1 or 2.
                #  - task_id, who uses this memory block?
                self.mem_tree.append([i+1, j, 0]) 
               
    
    def alloc_memory(self, type, task_id):
        """
        Allocate memory for task_id with memory type.
        Valid memory types are listed in MemoryType.
        Here we only consider memory fractions. The absolute memory size should
             be considered in resource manager.
        The memory are tagged with the task id and should be checked 
        when call the `show_memory()'
        -------------------------------------------------------------
        Input: Memory Type Enum, and Task ID (Type is always right). 
        Output: Memory Idx based on the input memory type.
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
                    for snode in sub_nodes:
                        snode.data[2] = task_id
                    return node.data[1]
        return 0
    
    def release_memory(self, task_id):
        """ Release the memory of a given task_id.
        Args:
            task_id: measurement task_id.
        Returns:
            True/False: is there a memory for the task_id?
        """
        re = False
        root = self.mem_tree.root()
        nodes = self.mem_tree.inorderTraversal(root)
        for node in nodes:
            if node.data[1] == task_id:
                node.data[1] = 0
                re = True
        return re

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
    def __init__(self, group_id, group_type, cmu_num, memory_size, stage_start, candidate_key_list, std_params):
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
        self._cmu_num = cmu_num
        self._memory_size = memory_size
        self._stage_start = stage_start

        ## Param Resources.
        self._std_params = []
        for param_name in std_params.keys():
            # param_str to Param Resources.
            self._std_params.append(Resource(ResourceType.StdParam, param_name))

        ## Compressed Key Resources.
        key_template = FlowKey(candidate_key_list)
        if group_type == 1:
            self._compressed_keys = [[Resource(ResourceType.CompressedKey, key_template), 16,  []] for _ in range(3)]  # key, bitw, tasks.
        else:
            self._compressed_keys = [ [Resource(ResourceType.CompressedKey, key_template), 32, []], 
                                      [Resource(ResourceType.CompressedKey, key_template), 16, []] ] 
        
        ## CMU and Memory Resources.
        self._cmus = [[CMU(), self._memory_size] for i in range(self._cmu_num)]  # Currently we only support 32 divisions.
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



    def show_status(self):
        """
        show current status of CMU-Group.
        """
        LINE_LEN = 60
        print('-'*LINE_LEN)
        print("Status of CMU-Group {}".format(self._group_id).center(LINE_LEN))
        print('-'*LINE_LEN)
        for idx, ck in enumerate(self._compressed_keys):
            if str(ck[0].content) == "":
                print("Compressed Key {} ({}b): Empty".format(idx+1, ck[1]))
            else:
                print("Compressed Key {} ({}b): {}".format(idx+1, ck[1], str(ck[0].content)))
        print('-'*LINE_LEN)
        for idx, (cmu, rest_mem) in enumerate(self._cmus):
            print("CMU-{} Rest Memory: {}".format(idx+1, rest_mem))
            # cmu.show_memory()
        print('-'*LINE_LEN)
    
    def check_parameters(self, required_param_list):
        """
        Check if the params are avaliable in this CMU-Group. 
        """
        for required_param in required_param_list:
            ok = False
            for p in self._std_params:
                if required_param == p:
                    ok = True
            if not ok:
                return False
        return True

    def check_compressed_keys(self, required_key_list):
        """
        Check if there are avaliable key resources.
        Empty or Equal key are valid.
        """
        for required_key in required_key_list:
            ok = False
            for ck, _, tasks in self._compressed_keys:
                if len(tasks) == 0:
                    ok = True
                else:
                    # The key as already be allocated.
                    # Check if it is a valid key?
                    if ck == required_key:
                        ok = True
            if not ok:
                return False
        return True

    def allocate_compressed_keys(self, task_id, required_key_list):
        """
        The required_key should be a flow_key object.
        TODO: need to consider bit size of key (for measurement accuracy reason)
        """
        hkey_list = []
        for required_key in required_key_list:
            ok = False
            for idx in range(len(self._compressed_keys)):
                task_list = self._compressed_keys[idx][2]
                if len(task_list) == 0:
                    hkey_list.append(idx+1)
                    ok = True
                    break
                else:
                    # The key as already be allocated.
                    if self.group_type == 2 and self._compressed_keys[idx][0] == required_key:
                        # If the CMU-Group is located in Egress Pipeline
                        # Then the hash bits should be reused.
                        hkey_list.append(idx+1)
                        ok = True
                        break
                    elif self.group_type == 1 and self._compressed_keys[idx][0] == required_key and task_id not in task_list:
                        ok = True
                        hkey_list.append(idx+1)
                        break
                    # TODO: support XOR in Ingress Pipeline.
            if not ok:
                return None
        for hkey_id in hkey_list:
            idx = hkey_id - 1
            self._compressed_keys[idx][0].content.set(required_key.content)
            self._compressed_keys[idx][2].append(task_id)
        return hkey_list

    def allocate_memory(self, cmu_id, task_id, mem_size, mode=1):
        """ Try to allocate memory for a specific task.
        Args:
            - cmu_id, need to larger than zero, that is, 1, 2, 3, ...

        Returns : 
        (memory_type, memory_idx) Or None (no enough memory)
            - mem_idx is offset on the type of memory, for example ,if the type is 2(HALF)
            - the mem_idx should be 1 or 2.
        ------------------------------------------------------
        If the memory list cannot be allocated all, it will return False and nothing will changed.
        mode=1 : accurate.
        mode=2 : efficient.
        """
        if mem_size > self._memory_size: 
            print("Invalid memory size : {}".format(mem_size))
            return None
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
        id = cmu_id - 1
        cmu = self._cmus[id][0]
        if self._cmus[id][1] < mem_size:
            return None
        memory_idx = cmu.alloc_memory(memory_type, task_id)
        if memory_idx >= 0:
            self._cmus[id][1] = self._cmus[id][1] - int(self._memory_size/memory_type)
            return memory_type, memory_idx
        return None

    def release_memory(self, task_id, memory_type):
        """
        Release memory for task_id.
        """
        for idx in range(len(self._cmus)):
            re = self._cmus[idx][0].release_memory(task_id)
            if re:
                self._cmus[idx][1] += int(self._memory_size/memory_type)
        pass

    def release_compressed_keys(self, task_id, hkeys):
        """
        Release compressed keys.
        """
        if hkeys is None:
            return 
        for hkey in hkeys:
            idx = hkey - 1
            if task_id not in self._compressed_keys[idx][2]:
                continue
            self._compressed_keys[idx][2].remove(task_id)