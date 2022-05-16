from perfect_tree import PerfectBinaryTree
import math

class MemoryTree:
    """
    A register memory in FlyMon is mananged by a binary tree.
    Valid memory types.
    0 : 1/1
    1 : 1/2
    2 : 1/4
    3 : 1/8
    4 : 1/16
    5 : 1/32
    Others: Invalid.
    """
    def __init__(self, max_div=32):
        """
        types = 1, 2, ...
        """
        self.max_type = int(math.log(max_div, 2)) # maximum divisions : 2**types
        self.mem_tree = PerfectBinaryTree()
        for i in range(self.max_type + 1):
            for j in range(2**i):
                self.mem_tree.append([i, 1]) # (type, status)
    
    def alloc_memory(self, type):
        if type < 0 or type > self.max_type:
            return False
        root = self.mem_tree.root()
        nodes = self.mem_tree.inorderTraversal(root)
        for node in nodes:
            if node.data[0] == type and node.data[1] == 1:
                node.data[1] = 0 
                return True
        return False
    
    def release_memory(self, type):
        if type < 0 or type > self.max_type:
            return False
        root = self.mem_tree.root()
        nodes = self.mem_tree.inorderTraversal(root)
        for node in nodes:
            if node.data[0] == type and node.data[1] == 0:
                node.data[1] = 1
                return True
        return False

    def show_memory(self):
        self.mem_tree.show_tree()


class CMU:
    def __init__(self, max_div=32):
        self.memory = MemoryTree(max_div)
        pass
    
    def show_memory(self):
        self.memory.show_memory() 

class CMU_Group():
    """Status of CMU_Group instance in control plane"""
    def __init__(self, group_id, group_type, cmu_num, memory_size, stage_start, std_params):
        # Properties.
        self.group_id = group_id
        self.group_type = group_type
        self.cmu_num = cmu_num
        self.stage_start = stage_start
        self.std_params = std_params

        # Status.
        if group_type == 1:
            self.compressed_keys = [None] * 3
        else:
            self.compressed_keys = [None] * 3
        self.cmus = self.cmu_num * [CMU(memory_size, std_params)]

