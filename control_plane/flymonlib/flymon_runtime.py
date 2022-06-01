# -*- coding:UTF-8 -*-

from numpy import mat
from flow_key import FlowKey
import bfrt_grpc.client as client
from work_space.FlyMon.control_plane.flymonlib.flymon_task import FlyMonTask

class FlyMonRuntime_Base:
    """
    A base class for configuring CMU-Group tables.
    NOTE: This is a abstract class, used as a template for different runtime environments.
    In particular, Barefoot Runtime is an implementation of this base class. 
    """
    def __init__(self):
        pass

    def compression_stage_config(self, group_id, dhash_id, hash_mask):
        pass

    def initialization_stage_add(self, group_id, cmu_id, filter, task_id, key, param1, param2):
        pass

    def initialization_stage_del(self, group_id, cmu_id, filter):
        pass

    def preprocessing_stage_add(self, group_id, cmu_id, task_id, key_match, param_match, new_key, new_param):
        pass

    def preprocessing_stage_del(self, group_id, cmu_id, task_id):
        pass

    def operation_stage_add(self, group_id, cmu_id, task_id, operation_type):
        pass

    def operation_stage_del(self, group_id, cmu_id, task_id):
        pass
    
class FlyMonRuntime_BfRt(FlyMonRuntime_Base):
    """
    A reference implementation of CMU Runtime based on Barefoot Runtime and Tofino.
    """
    def __init__(self, conn, context):
        super.__init__(self)
        self.conn = conn
        self.context = context
        pass
    
    def install(self, task_instance : FlyMonTask):
        """
        Install a task into the data plane
        """
        # 1. allocate the memory space
        for l in task_instance.locations:
            # ZTODO 
            self.preprocessing_stage_add(l.group_id, l.group_type, l.cmu_id, task_instance.id, [], [])

    def compression_stage_config(self, group_id, group_type, dhash_id, flow_key):
        """
        Set hash unit mask portion of the fields.
         - group_id: CMU-Group ID.
         - dhash_id: hash unit ID.
         - flow_key: FlowKey object in utils/flow_key.py
        """
        hash_configure_table = ""
        if group_type == 1:
            hash_configure_table = self.context.table_get(f"FlyMonIngress.cmu_group{group_id}.hash_unit{dhash_id}.configure")
        else:
            hash_configure_table = self.context.table_get(f"FlyMonEgress.cmu_group{group_id}.hash_unit{dhash_id}.configure")
        key_configs = flow_key.to_config_dict()
        target_config_list = []
        for key in key_configs.keys():
            inner_tuple = [] # inner tupples for a specific key container.
            # TODO: we can shuffle keys here to generate different hash values.
            for idx, (start_bit, bit_len) in key_configs[key]:
                inner_tuple.append(
                    { 
                      "order": client.DataTuple("order", idx),
                      "start_bit": client.DataTuple("start_bit", start_bit),
                      "length": client.DataTuple("length", bit_len)
                    }
                )
            target_config_list.append(client.DataTuple(key, container_arr_val = inner_tuple))
        data = hash_configure_table.make_data(target_config_list)
        hash_configure_table.default_entry_set(self.conn, data)
        pass

    def initialization_stage_add(self, group_id, group_type, cmu_id, filter, task_id, key, param1, param2):
        """
        Match fields:
         - filter: [(ipsrc, mask1), (ipdst, mask2)]
        Action fields:
         - task id: used as the match fields in other fields.
         - key : one of ['hkey1', 'hkey2'] for group type 1. ['hkey1', 'hkey2', 'hkey12', 'hkey3'] for group type 2.
         - param1 : (type, value), types are in ['cparam', 'hparam', 'std']
                - for cparam, value should be a constant value.
                - for hparam, value should in [1, 2] in group type1, [1, 2, 3] in group type2.
                - for std, value should in ['timestamp'], ['queue_length', 'queue_size', 'pktsize'] for group type2.
         - param2 : a const value
        Reutrn:
         - Return match key list as rule handler (usded for deleting)

        NOTE: Currently, I don't implement correctness checks of params. May be it can be implemented in the flymon manager.
        """
        prefix = ""
        if group_type == 1:
            prefix = f"FlyMonIngress.cmu_group{group_id}"
        else:
            prefix = f"FlyMonEgress.cmu_group{group_id}"
        initialization_table = self.context.table_get(prefix+f".tbl_cmu{cmu_id}_initialization")

        match = initialization_table.make_key([client.KeyTuple(f'hdr.ipv4.src_addr', filter[0][0], filter[0][1]),
                                               client.KeyTuple(f'hdr.ipv4.dst_addr', filter[1][0], filter[1][1])])
        action = None
        if param1[0] == 'cparam':
            action = initialization_table.make_data([ client.DataTuple('task_id', task_id),
                                                      client.conn.DataTuple('param1', param1[1]),
                                                      client.conn.DataTuple('param2', param2),], 
                                                    prefix + f".set_cmu{cmu_id}_{key}_cparam")
        elif param1[0] == 'hparam':
            action = initialization_table.make_data([ client.conn.DataTuple('task_id', task_id),
                                                      client.DataTuple('param2', param2),], 
                                                    prefix + f".set_cmu{cmu_id}_{key}_hparam{param1[1]}")
        else: ## std param
            action = initialization_table.make_data([ client.DataTuple('task_id', task_id),
                                                      client.DataTuple('param2', param2),], 
                                                    prefix + f".set_cmu{cmu_id}_{key}_{param1[1]}")
        initialization_table.entry_add(self.conn, [match], [action])
        return [match] # a key list. 

    def initialization_stage_del(self, group_id, group_type, cmu_id, key_list):
        """
        key_list: match key list return from initialization_stage_add. It should be maintained by task manager.
        """
        prefix = ""
        if group_type == 1:
            prefix = f"FlyMonIngress.cmu_group{group_id}"
        else:
            prefix = f"FlyMonEgress.cmu_group{group_id}"
        initialization_table = self.context.table_get(prefix+f".tbl_cmu{cmu_id}_initialization")
        initialization_table.entry_del(self.conn, key_list)
        pass

    def preprocessing_stage_add(self, group_id, group_type, cmu_id, task_id, key_mappings, param_mappings):
        """
         task_id: which task to match.
         key_mappings: used to implement address translation. e.g., [(key1, mask1, key_offset)]
         param_mappings: used to encode the params. e.g., [(param1, mask1, new param)]
        """
        prefix = ""
        if group_type == 1:
            prefix = f"FlyMonIngress.cmu_group{group_id}"
        else:
            prefix = f"FlyMonEgress.cmu_group{group_id}"
        perprocessing_table = self.context.table_get(prefix+f".tbl_cmu{cmu_id}_preprocessing")
        entry_dict = {}
        for key_tuple in key_mappings.keys():
            for param_tuple in param_mappings.keys():
                match = perprocessing_table.make_key([client.KeyTuple(f'meta.cmu_group{group_id}.cmu{cmu_id}.task_id', task_id),
                                                      client.KeyTuple(f'meta.cmu_group{group_id}.cmu{cmu_id}.key', key_tuple[0], key_tuple[1]),
                                                      client.KeyTuple(f'meta.cmu_group{group_id}.cmu{cmu_id}.param1', param_tuple[0], param_tuple[1])])
                action = perprocessing_table.make_data([ client.DataTuple('offset', key_tuple[2]),
                                                         client.DataTuple('code', param_tuple[2]),], 
                                                        prefix + f".process_cmu{cmu_id}_key_param")
                entry_dict[match] = action
                perprocessing_table.entry_add(self.conn, [match], [action])
        return entry_dict.keys() # a key list. 

    def preprocessing_stage_del(self, group_id, group_type, cmu_id, key_list):
        """
        key_list: match key list return from initialization_stage_add. It should be maintained by task manager.
        """
        prefix = ""
        if group_type == 1:
            prefix = f"FlyMonIngress.cmu_group{group_id}"
        else:
            prefix = f"FlyMonEgress.cmu_group{group_id}"
        perprocessing_table = self.context.table_get(prefix+f".tbl_cmu{cmu_id}_preprocessing")
        perprocessing_table.entry_del(self.conn, key_list)
        pass

    def operation_stage_add(self, group_id, group_type, cmu_id, task_id, operation_type):
        """
         task_id: which task to match.
         operation_type: in ['cond_add', 'max', 'and_or']
        """
        prefix = ""
        if group_type == 1:
            prefix = f"FlyMonIngress.cmu_group{group_id}"
        else:
            prefix = f"FlyMonEgress.cmu_group{group_id}"
        operation_table = self.context.table_get(prefix+f".tbl_cmu{cmu_id}_operation")
        match = operation_table.make_key([client.KeyTuplle(f'meta.cmu_group{group_id}.cmu{cmu_id}.task_id', task_id)])
        action = operation_table.make_data([], prefix + f"op_cmu{cmu_id}_.{operation_type}")
        operation_table.entry_add(self.conn, [match], [action])
        return [match] # a key list. 

    def operation_stage_del(self, group_id, group_type, cmu_id, key_list):
        prefix = ""
        if group_type == 1:
            prefix = f"FlyMonIngress.cmu_group{group_id}"
        else:
            prefix = f"FlyMonEgress.cmu_group{group_id}"
        operation_table = self.context.table_get(prefix+f".tbl_cmu{cmu_id}_operation")
        operation_table.entry_del(self.conn, key_list)

    def read(self, group_id, group_type, cmu_id, begin, end):
        """
        read memories in [begin, end)
        """
        memory_size = end-begin
        prefix = ""
        if group_type == 1:
            prefix = f"FlyMonIngress.cmu_group{group_id}"
        else:
            prefix = f"FlyMonEgress.cmu_group{group_id}"
        register_table = self.context.table_get(prefix + f".cmu{cmu_id}_buckets")
        buf = [0] * (end-begin)
        for register_idx in range(begin, end):
            resp = register_table.entry_get(
                    self.target,
                    [register_table.make_key([client.KeyTuple('$REGISTER_INDEX', register_idx)])],
                    {"from_hw": True})
            data, _ = next(resp)
            data_dict = data.to_dict()
            ## first is lo, second is hi.
            # print(data_dict)
            value_lo = data_dict[prefix + f".cmu{cmu_id}_buckets.f1"][0]
            buf[register_idx] = value_lo
        return buf