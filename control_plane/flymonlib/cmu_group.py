# -*- coding:UTF-8 -*-
from __future__ import print_function 
import math
from flymonlib.resource import *
from flymonlib.utils import PerfectBinaryTree
from flymonlib.flow_key import FlowKey


class CMU:
    """
    A register memory in FlyMon is mananged by a binary tree.
    """
    def __init__(self, max_div=32):
        """
        max_div is the maximum memory divisions of a CMU, 32 is the default.
        """
        self.max_type = int(math.log(max_div, 2)) # maximum divisions : 2**types
        self.mem_tree = PerfectBinaryTree()
        for i in range(self.max_type + 1):
            for j in range(2**i):
                self.mem_tree.append([i, 0]) # (type, status)
    
    def alloc_memory(self, type, task_id):
        """
        Allocate memory for task_id with memory type.
        Valid memory types are:
            0 : 1/1 | 1 : 1/2 | 2 : 1/4 | 3 : 1/8 | 4 : 1/16 | 5 : 1/32
        Here we only consider memory fractions. The absolute memory size should
        be considered in flymon manager.
        The memory are tagged with the task id and should be checked 
        when call the `show_memory()'
        """
        if type < 0 or type > self.max_type:
            return False
        root = self.mem_tree.root()
        nodes = self.mem_tree.inorderTraversal(root)
        for node in nodes:
            # Z the node's size suitable and the node is available
            if node.data[0] == type and node.data[1] == 0:
                sub_nodes = self.mem_tree.inorderTraversal(node)
                is_ok = True
                # Z check if all the subnode is available
                for snode in sub_nodes:
                    if snode.data[1] != 0:
                        is_ok = False
                if is_ok:
                    for snode in sub_nodes:
                        snode.data[1] = task_id
                    return True
        return False
    
    def release_memory(self, task_id):
        """
        Release the memory of a given task_id.
        """
        root = self.mem_tree.root()
        nodes = self.mem_tree.inorderTraversal(root)
        for node in nodes:
            if node.data[1] == task_id:
                node.data[1] = 0

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
        self.group_id = group_id
        self.group_type = group_type
        self.cmu_num = cmu_num
        self.memory_size = memory_size
        self.stage_start = stage_start

        ## Param Resources.
        self.std_params = []
        for param_name in std_params:
            # self.std_params.append()
            pass

        ## Compressed Key Resources.
        key_template = FlowKey(candidate_key_list)
        if group_type == 1:
            self.compressed_keys = [(Resource(ResourceType.CompressedKey, key_template), 16, True)] * 3   # key, bitw, status.
        else:
            self.compressed_keys = [(Resource(ResourceType.CompressedKey, key_template), 32, True), 
                                    (Resource(ResourceType.CompressedKey, key_template), 16, True)] 
        
        ## CMU and Memory Resources.
        self.cmus = self.cmu_num * [(CMU(), self.memory_size)]  # Currently we only support 32 divisions.
        pass
        

    def show_status(self):
        """
        show current status of CMU-Group.
        """
        LINE_LEN = 60
        print('-'*LINE_LEN)
        print("Status of CMU-Group {}".format(self.group_id).center(LINE_LEN))
        print('-'*LINE_LEN)
        for idx, ck in enumerate(self.compressed_keys):
            if str(ck[0].content) == "":
                print("Compressed Key {} ({}b): Empty".format(idx+1, ck[1]))
            else:
                print("Compressed Key {} ({}b): {}".format(idx+1, ck[1], str(ck[0].content)))
        print('-'*LINE_LEN)
        for idx, (cmu, rest_mem) in enumerate(self.cmus):
            print("CMU-{} Rest Memory: {}".format(idx+1, rest_mem))
            # cmu.show_memory()
        print('-'*LINE_LEN)
    

    def get_std_params(self):
        """
        Return support params.
        """
        
    
    def allocate_compressed_key(self, key_list):
        """
        The key list should be a list of (key_name, mask_string).
        e.g., [("hdr.ipv4.src_addr", "0xffffffff"), ("hdr.ipv4.dst_addr", "0xffffffff")] is a valid key (IP Pair).
        """
        try:
            for ck, _, status in self.compressed_keys:
                if status == True:
                    for key_name, key_mask in key_list:
                        re = ck.set_mask(key_name, key_mask)
                        if not re:
                            return False
        except Exception as e:
            print("Errors occur when allocate a compressed key {}", e)
            return False
        return True

    def allocate_memory(self, task_id, mem_size, mem_num, mode=1):
        """
        Try to allocate memory for a specific task.
        If the memory list cannot be allocated all, it will return False and nothing will changed.
        mode=1 : accurate.
        mode=2 : efficient.
        TODO: enable memory list with different size.
        """
        if mem_size > self.memory_size:
            print("Invalid memory size : {}".format(mem_size))
            return False
        if mem_num > self.cmu_num:
            print("Invalid memory num : {}".format(mem_num))
            return False
        memory_type = int(self.memory_size / mem_size) # default is a accurate mode.
        if mode == 2:
            # TODO: need to implement a simple efficient mode.
            pass
        count = 0
        for idx in range(len(self.cmus)):
            cmu = self.cmus[idx][0]
            if count < mem_num:
                re = cmu.alloc_memory(memory_type, task_id)
                if re is True:
                    count += 1
                    self.cmus[idx][1] -= (mem_size/memory_type)
        if count < mem_num:
            print("No enough memory {}x{}".format(mem_num, mem_size))
            for cmu in self.cmus:
                cmu.release_memory(task_id)
                self.cmus[idx][1] += (mem_size/memory_type)
            return False
        
        return True

    def release_memory(self, task_id):
        """
        Release memory for task_id.
        """
        for cmu in self.cmus:
            cmu.release_memory(task_id)
        pass