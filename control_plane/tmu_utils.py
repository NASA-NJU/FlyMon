# -*- coding: UTF-8 -*-
import os
from ptf import config
from ptf.thriftutils import *
from ptf.testutils import *
from bfruntime_client_base_tests import BfRuntimeTest
import bfrt_grpc.client as client
from collections import namedtuple
import pprint as pp
import time
import crcmod
import sys
import numpy as np
sys.path.append("..")
from common import *
from enum import Enum
import math

HashFieldSlice = namedtuple('HashFieldSlice', 'name start_bit length order')
HashFieldSlice.__new__.__defaults__ = (None, None, 0)
# value = (value_type, value_content)
# memory = (memory_num, memory_type)
# stateless_op = ("no_action", "one_hot")
# stateful_op =  ("op_add", "op_max", "op_set", "op_and")
TaskInstance = namedtuple('TaskInstance', 'task_id, key, value, memory, stateless_op, stateful_op, threshold')

class TMU():
    def __init__(self, target, bfrt_info, tmu_config, cu_target_bits, memory_size):
        self.target = target
        self.bfrt_info = bfrt_info
        self.tmu_id = tmu_config["id"]
        self.cu_id = tmu_config["cu_id"]
        self.eu_ids = tmu_config["eu_list"]
        self.ru_id = tmu_config["ru_id"]
        self.memory_size = memory_size
        
        self.task_register_name = f"SwitchIngress.task_register_{self.tmu_id}"
        self.cu_name = f"SwitchIngress.cu_{self.cu_id}"
        self.cu_hash_tables_name = [f"{self.cu_name}.hash_unit{i}" for i in range(len(cu_target_bits))]
        self.eu_names = [f"SwitchIngress.eu_{eu_id}" for eu_id in self.eu_ids]
        self.task_register_table_name = f"{self.task_register_name}.tbl_set_task_id"
        self.eu_set_key_tables_name = [f"{eu_name}.tbl_set_key" for eu_name in self.eu_names]
        self.eu_set_val_tables_name = [f"{eu_name}.tbl_set_val" for eu_name in self.eu_names]
        self.eu_process_key_tables_name = [f"{eu_name}.tbl_process_key" for eu_name in self.eu_names]
        self.eu_process_val_tables_name = [f"{eu_name}.tbl_process_val" for eu_name in self.eu_names]
        self.eu_select_op_tables_name = [f"{eu_name}.tbl_select_op" for eu_name in self.eu_names]
        self.eu_register_tables_name = [f"{eu_name}.pages" for eu_name in self.eu_names]
        self.ru_name = f"SwitchIngress.ru_{self.ru_id}"
        self.reporter_table_name = f"{self.ru_name}.tbl_result_judge"

        self.task_register_table = self.bfrt_info.table_get(self.task_register_table_name)
        self.cu_hash_config_tables = [self.bfrt_info.table_get(f"{ht}.configure") for ht in self.cu_hash_tables_name]
        self.cu_hash_comput_tables = [self.bfrt_info.table_get(f"{ht}.compute") for ht in self.cu_hash_tables_name]
        self.eu_set_key_tables = [self.bfrt_info.table_get(tb) for tb in self.eu_set_key_tables_name]
        self.eu_set_val_tables = [self.bfrt_info.table_get(tb) for tb in self.eu_set_val_tables_name]
        self.eu_key_process_tables = [self.bfrt_info.table_get(tb) for tb in self.eu_process_key_tables_name]
        self.eu_val_process_tables = [self.bfrt_info.table_get(tb) for tb in self.eu_process_val_tables_name]
        self.eu_select_op_tables = [self.bfrt_info.table_get(tb) for tb in self.eu_select_op_tables_name]
        self.eu_register_tables = [self.bfrt_info.table_get(tb) for tb in self.eu_register_tables_name]
        self.reporter_table = self.bfrt_info.table_get(self.reporter_table_name)
        
        # Init resource manager.
        self.cu_status = [None for i in range(len(cu_target_bits))] # [slice_tuple_list]
        pass

    # =======================================
    # Register A Task.
    # =======================================
    def register_task(self, task_instance):
        task_id = task_instance.task_id
        task_key = task_instance.key
        task_val = task_instance.value                  # value = (value_type, value_content)
        task_memory_num = task_instance.memory[0]       # memory = (memory_num, memory_type)
        task_memory_type = task_instance.memory[1]
        # task_stateless_op = task_instance.stateless_op  # stateless_op = ("no_action", "one_hot")
        task_stateful_op = task_instance.stateful_op    # stateful_op =  ("op_add", "op_max", "op_set", "op_and")
        task_threshold = task_instance.threshold        
        
        hu_id = self.get_avaliable_hash_unit(task_key)
        if hu_id is None:
            print("No avaliable hash unit.")
            return -1
        self.config_hash_unit(hu_id, task_key)
        count = 0
        used_euit = []
        for eu_id in self.eu_ids:
            if count < task_memory_num:
                self.config_table_set_key(eu_id, task_id, hu_id)
                if task_val[0] == "const":
                    self.config_table_set_val_const(eu_id, task_id, task_val[1])
                else:
                    val_hu_id = self.get_avaliable_hash_unit(task_val[1])
                    self.config_table_set_val_hash(eu_id, task_id, val_hu_id)
                self.config_table_process_key(eu_id, task_id, task_memory_type)
                self.config_table_select_op(eu_id, task_id, task_stateful_op)
                used_euit.append(eu_id)
                count += 1
        self.config_table_report(task_id, task_memory_num, task_threshold)
        self.config_table_register_task(task_id, used_euit)

    def get_avaliable_hash_unit(self, key):
        for idx, k in enumerate(self.cu_status):
            if k is None or k == key:
                self.cu_status[idx] = key
                return idx
        return None

    # Todo, support part of eu list. 
    def config_table_register_task(self, task_id, eu_ids):
        self.task_register_table.info.key_field_annotation_add("hdr.ipv4.src_addr", "ipv4") # don't know...
        self.task_register_table.info.key_field_annotation_add("hdr.ipv4.dst_addr", "ipv4")
        match = self.task_register_table.make_key([client.KeyTuple('hdr.ipv4.src_addr', "0.0.0.0", "0.0.0.0"), 
                                                   client.KeyTuple('hdr.ipv4.dst_addr', "0.0.0.0", "0.0.0.0")])
        match.apply_mask()
        action = self.task_register_table.make_data([client.DataTuple(f'id{eu_id}', task_id) for eu_id in eu_ids]
                                                     + [client.DataTuple('end', 0)], f'{self.task_register_name}.set_task_id')
        self.task_register_table.entry_add(
            self.target,
            [match],
            [action]
        )

    ## Current only support use the all EUs (i.e., task_memory_num == EU_NUM_PER_TMU).
    ## TODO: impolement arbitrary task_memory_num and range.
    ## There is no difficulty in implementation, but it is more logical and needs to be handled.
    def config_table_report(self, task_id, task_memory_num, threshold):
        match = self.reporter_table.make_key( [client.KeyTuple(f'ig_md.eu_{i}.task_id', task_id) for i in range(task_memory_num)] 
                                            + [client.KeyTuple(f'ig_md.eu_{i}.val', threshold, threshold) for i in range(task_memory_num)])
        action = self.reporter_table.make_data([], f'{self.ru_name}.hit')
        self.reporter_table.entry_add(
            self.target,
            [match],
            [action]
        )

    def get_eu_idx(self, eu_id):
        return eu_id % len(self.eu_ids)

    def create_hash_data(self, table, slice_tuples):
        # temporarily removed.
        pass

    ## The slice_tuple_list is to define the fields properties to be hashed.
    def config_hash_unit(self, hash_id, slice_tuple_list):
        # temporarily removed.
        pass

    def config_table_set_key(self, eu_id, task_id, hash_id):
        T1 = time.time()
        eu_id = self.get_eu_idx(eu_id)
        self.eu_set_key_tables[eu_id].entry_add(
            self.target,
            [self.eu_set_key_tables[eu_id].make_key([client.KeyTuple(f'ig_md.eu_{eu_id}.task_id',
                                                     task_id)])],
            [self.eu_set_key_tables[eu_id].make_data([], f'{self.eu_names[eu_id]}.set_key_hash{hash_id}')] ## data plane begin from 1.
        )
        T2 = time.time()
        print("change key time: %s ms", ((T2 - T1)*1000))
        
    def config_table_set_val_hash(self, eu_id, task_id, hash_id):
        T1 = time.time()
        eu_id = self.get_eu_idx(eu_id)
        self.eu_set_val_tables[eu_id].entry_add(
            self.target,
            [self.eu_set_val_tables[eu_id].make_key([client.KeyTuple(f'ig_md.eu_{eu_id}.task_id',
                                                     task_id)])],
            [self.eu_set_val_tables[eu_id].make_data([], f'{self.eu_names[eu_id]}.set_val_hash{hash_id}')]
        )
        T2 = time.time()
        print("change val time: %s ms", ((T2 - T1)*1000))

    def config_table_set_val_const(self, eu_id, task_id, const_val):
        eu_id = self.get_eu_idx(eu_id)
        self.eu_set_val_tables[eu_id].entry_add(
            self.target,
            [self.eu_set_val_tables[eu_id].make_key([client.KeyTuple(f'ig_md.eu_{eu_id}.task_id',
                                                     task_id)])],
            [self.eu_set_val_tables[eu_id].make_data([client.DataTuple('const_val', const_val)], f'{self.eu_names[eu_id]}.set_val_const')]
        )

    # memory type : all(1) half(2) quartar(4) ...
    def config_table_process_key(self, eu_id, task_id, memory_type, memory_idx = 0):
        eu_id = self.get_eu_idx(eu_id)
        if memory_type == 1:
            return # no need to process key.
        if memory_type == 2:  
            mask_value = 1 << (int(math.log2(self.memory_size)) -1)
            hack_value = int(self.memory_size / 2)
            if memory_idx == 0:
                match_value = 1 << (int(math.log2(self.memory_size)) -1) # to fix key which is larger than a half of total memory.
                match = self.eu_key_process_tables[eu_id].make_key([client.KeyTuple(f'ig_md.eu_{eu_id}.task_id', task_id),
                                                                    client.KeyTuple(f'ig_md.eu_{eu_id}.key', match_value, mask_value)])
                action = self.eu_key_process_tables[eu_id].make_data([client.DataTuple('offset', hack_value)], f'{self.eu_names[eu_id]}.key_add_offset')
                self.eu_key_process_tables[eu_id].entry_add(self.target, [match], [action])
            else:
                match_value = 0 # to fix key which is smaller than a half of total memory.
                match = self.eu_key_process_tables[eu_id].make_key([client.KeyTuple(f'ig_md.eu_{eu_id}.task_id', task_id),
                                                                    client.KeyTuple(f'ig_md.eu_{eu_id}.key', match_value, mask_value)])
                action = self.eu_key_process_tables[eu_id].make_data([client.DataTuple('offset', hack_value)], f'{self.eu_names[eu_id]}.key_add_offset')
                self.eu_key_process_tables[eu_id].entry_add(self.target, [match], [action])
        ## currently only support memory_type all and half, quautar is easy to implement by referencing memory_type half.
        pass

    # opname: op_add, op_max, op_and, op_set.
    def config_table_select_op(self, eu_id, task_id, op_name):
        eu_id = self.get_eu_idx(eu_id)
        self.eu_select_op_tables[eu_id].entry_add(
            self.target,
            [self.eu_select_op_tables[eu_id].make_key([client.KeyTuple(f'ig_md.eu_{eu_id}.task_id',
                                                     task_id)])],
            [self.eu_select_op_tables[eu_id].make_data([], f'{self.eu_names[eu_id]}.{op_name}')]
        )

    def read_task_data(self, task_instance):
        datas = np.zeros((len(self.eu_ids), self.memory_size), dtype=np.int)
        for eu_id in self.eu_ids:
            data = self.read(eu_id)
            idx = self.get_eu_idx(eu_id)
            datas[idx] = data
        for data in datas:
            print(data)
    
    def read(self, eu_id):
        ## Todo, add partial read.
        memory_size = self.memory_size
        pipe_id = 0
        eu_id = self.get_eu_idx(eu_id)
        register_table = self.eu_register_tables[eu_id]
        buf = [0] * memory_size
        for register_idx in range(memory_size):
            resp = register_table.entry_get(
                    self.target,
                    [register_table.make_key([client.KeyTuple('$REGISTER_INDEX', register_idx)])],
                    {"from_hw": True})
            data, _ = next(resp)
            data_dict = data.to_dict()
            ## first is lo, second is hi.
            # print(data_dict)
            value_lo = data_dict[f'{self.eu_register_tables_name[eu_id]}.f1'][pipe_id]
            buf[register_idx] = value_lo
        return buf
        


    
    