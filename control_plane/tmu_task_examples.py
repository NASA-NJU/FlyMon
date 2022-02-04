from tmu_utils import *

# TaskInstance
# value = (["const" / "hash"], value_content)
# memory = (memory_num, memory_type)
# stateless_op = ("no_action", "one_hot")
# stateful_op =  ("op_add", "op_max", "op_set", "op_and")
g_task_id = 0

def get_task_cmsketch_five_tuple(threshold= 1024, num_rows=4, memory_type_per_row=1):
    global g_task_id
    g_task_id += 1
    key_five_tuple = []
    key_five_tuple.append(HashFieldSlice(name="hdr.ipv4.src_addr",                        order=1))
    key_five_tuple.append(HashFieldSlice(name="hdr.ipv4.dst_addr",                        order=2))
    key_five_tuple.append(HashFieldSlice(name="ig_md.elements.src_port",                  order=3))
    key_five_tuple.append(HashFieldSlice(name="ig_md.elements.dst_port",                  order=4))
    key_five_tuple.append(HashFieldSlice(name="hdr.ipv4.protocol",                        order=5))
    task_instance = TaskInstance(task_id=g_task_id, 
                                    key=key_five_tuple, 
                                    value=("const", 1), 
                                    memory=(num_rows, memory_type_per_row),
                                    stateless_op="no_action",
                                    stateful_op="op_add",
                                    threshold=threshold)
    return task_instance

# used to test dyn hashing.
def get_task_cmsketch_ip_pair(threshold=1024, num_rows=4, memory_type_per_row=1):
    # temporarily removed.
    pass