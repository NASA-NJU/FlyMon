# -*- coding:UTF-8 -*-
from __future__ import print_function 
import math
from xml.dom.minidom import parseString
from perfect_tree import PerfectBinaryTree
from bitstring import BitArray, BitStream

"""
This file define some basic components in Flymon.
Includes: CompressedKey, CMU, and CMU-Group.
"""

class CompressedKey:
    """Flow key definition"""
    def __init__(self, candidate_key_list):
        """
        Initially are key are not enabled.
        self.status: True -> Availiable
        """
        self.key_list = dict(candidate_key_list)
        for key in self.key_list.keys():
            bits = self.key_list[key]
            self.key_list[key] = (bits, BitArray(int=0, length=bits))
        self.status = True
    

    def set_mask(self, key_name, mask):
        """
        Set a mask to one of the candidate key.
        """
        if mask[0:2] != "0x":
            print("Invalid mask without leading '0x' or invalid mask length.") 
            return False
        origin_bits, _ = self.key_list[key_name]
        if len(mask[2:]) != origin_bits/4:
            print("Expected length: {}, given: {}.".format(origin_bits), len(mask[2:])*4)
            return False
        self.key_list[key_name] = (origin_bits, BitArray(mask))
        self.status = False
        return True

    def get_status(self):
        return self.status

    def reset(self):
        """
        Reset a compressed key.
        """
        for key in self.key_list.keys():
            bits,_ = self.key_list[key]
            self.key_list[key] = (bits, BitArray(int=0, length=bits))
        self.status = True

    def to_string(self):
        """
        Formally return a string of the key. Only the enabled key are listed,
        """
        key_string = " - ".join(["{}({})".format(key, self.key_list[key][1]) for key in self.key_list])
        return key_string

    def to_match_obj(self):
        """
        TODO: Return a BFRT object to configure the hash calculation unit.
        """
        return None

class CMU:
    """
    A register memory in FlyMon is mananged by a binary tree.
    Valid memory types.
    0 : 1/1 | 1 : 1/2 | 2 : 1/4 | 3 : 1/8 | 4 : 1/16 | 5 : 1/32
    """
    def __init__(self, max_div=32):
        """
        types = 1, 2, ...
        """
        self.max_type = int(math.log(max_div, 2)) # maximum divisions : 2**types
        self.mem_tree = PerfectBinaryTree()
        for i in range(self.max_type + 1):
            for j in range(2**i):
                self.mem_tree.append([i, 0]) # (type, status)
    
    def alloc_memory(self, type, task_id):
        if type < 0 or type > self.max_type:
            return False
        root = self.mem_tree.root()
        nodes = self.mem_tree.inorderTraversal(root)
        for node in nodes:
            if node.data[0] == type and node.data[1] == 0:
                sub_nodes = self.mem_tree.inorderTraversal(node)
                is_ok = True
                for snode in sub_nodes:
                    if snode.data[1] != 0:
                        is_ok = False
                if is_ok:
                    for snode in sub_nodes:
                        snode.data[1] = task_id
                    return True
        return False
    
    def release_memory(self, task_id):
        root = self.mem_tree.root()
        nodes = self.mem_tree.inorderTraversal(root)
        for node in nodes:
            if node.data[1] == task_id:
                node.data[1] = 0

    def show_memory(self):
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
        # Properties.
        self.group_id = group_id
        self.group_type = group_type
        self.cmu_num = cmu_num
        self.memory_size = memory_size
        self.stage_start = stage_start
        self.std_params = std_params

        # Member Status.
        if group_type == 1:
            self.compressed_keys = [(CompressedKey(candidate_key_list), 16)] * 3
        else:
            self.compressed_keys = [(CompressedKey(candidate_key_list), 32), (CompressedKey(candidate_key_list), 16)] 
        self.cmus = self.cmu_num * [CMU()]
    
    def show_status(self):
        """
        show current status of CMU-Group.
        """
        LINE_LEN = 80
        print('-'*LINE_LEN)
        print("Status of CMU-Group {}".format(self.group_id).center(LINE_LEN))
        print('-'*LINE_LEN)
        for idx, ck in enumerate(self.compressed_keys):
            print("Compressed Key {} ({}b): {}".format(idx+1, ck[1], ck[0].to_string()))
        print('-'*LINE_LEN)
        for idx, cmu in enumerate(self.cmus):
            print("Memory Status of CMU {}".format(idx+1))
            cmu.show_memory()
        print('-'*LINE_LEN)
    

    def allocate_compressed_key(self, key_list):
        """
        The key list should be a list of (key_name, mask_string).
        e.g., [("hdr.ipv4.src_addr", "0xffffffff"), ("hdr.ipv4.dst_addr", "0xffffffff")] is a valid key (IP Pair).
        """
        try:
            for ck in self.compressed_keys:
                if ck.get_status() == True:
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
        for cmu in self.cmus:
            if count < mem_num:
                re = cmu.alloc_memory(memory_type, task_id)
                if re is True:
                    count += 1
        if count < mem_num:
            print("No enough memory {}x{}".format(mem_num, mem_size))
            for cmu in self.cmus:
                cmu.release_memory(task_id)
            return False
        return True

    def release_memory(self, task_id):
        """
        Release memory for task_id.
        """
        for cmu in self.cmus:
                cmu.release_memory(task_id)
        pass