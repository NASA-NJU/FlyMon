# -*- coding:UTF-8 -*-
import time
from numpy import mat
from flymonlib.operation import OperationType
from flymonlib.param import ParamType
from flymonlib.flow_key import FlowKey
import bfrt_grpc.client as client

class FlyMonRuntime_BfRt():
    """
    A reference implementation of CMU Runtime based on Barefoot Runtime and Tofino.
    """
    def __init__(self, conn, context):
        super(FlyMonRuntime_BfRt,self).__init__()
        self.conn = conn
        self.context = context
        pass

    def compression_stage_config(self, group_id, group_type, dhash_id, flow_key):
        """
        Set hash unit mask portion of the fields.
            group_id: CMU-Group ID.
            dhash_id: hash unit ID.
            flow_key: FlowKey object in utils/flow_key.py
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
            for idx, (start_bit, bit_len) in enumerate(key_configs[key]):
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
        return True

    def initialization_stage_add(self, group_id, group_type, cmu_id, filter, task_id, key, param1, param2):
        """
        Match fields:
            filter: [(ipsrc, mask1), (ipdst, mask2)]
        Action fields:
            task id: used as the match fields in other fields.
            key : one of [1, 2] for group type 1. [1, 2, 12, 3] for group type 2.
            param1 : a Param object and a potential hash unit ID (on valid for ParamType.CompressedKey)
                   for ParamType.Const
                   for ParamType.CompressedKey
                   for ParamType.Timestamp/PacketSize/QueueLen
                   for hparam, value should in [1, 2] in group type1, [1, 2, 3] in group type2.
                   for std, value should in ['timestamp'], ['queue_length', 'queue_size', 'pktsize'] for group type2.
            param2 : a const value
        Reutrns:
            Return match key list as rule handler (usded for deleting) / None for failed.
        """
        prefix = ""
        if group_type == 1:
            prefix = f"FlyMonIngress.cmu_group{group_id}"
        else:
            prefix = f"FlyMonEgress.cmu_group{group_id}"
        initialization_table = self.context.table_get(prefix+f".tbl_cmu{cmu_id}_initialization")
        initialization_table.info.key_field_annotation_add("hdr.ipv4.src_addr", "ipv4") 
        initialization_table.info.key_field_annotation_add("hdr.ipv4.dst_addr", "ipv4")
        match = initialization_table.make_key([client.KeyTuple(f'hdr.ipv4.src_addr', filter[0][0], filter[0][1]),
                                               client.KeyTuple(f'hdr.ipv4.dst_addr', filter[1][0], filter[1][1])])
        action = None
        if param1[0].type == ParamType.CompressedKey:
            action = initialization_table.make_data([ client.DataTuple('task_id', task_id),
                                                      client.DataTuple('param1', param1[1]),
                                                      client.DataTuple('param2', param2.content),], 
                                                      prefix + f".set_cmu{cmu_id}_hkey{key}_hparam{param1[1]}")
        elif param1[0].type == ParamType.Const:
            action = initialization_table.make_data([ client.DataTuple('task_id', task_id),
                                                      client.DataTuple('param1', param1[0].content),
                                                      client.DataTuple('param2', param2.content),], 
                                                      prefix + f".set_cmu{cmu_id}_hkey{key}_cparam")
        elif param1[0].type == ParamType.PacketSize:
            action = initialization_table.make_data([ client.DataTuple('task_id', task_id),
                                                      client.DataTuple('param2', param2.content)], 
                                                      prefix + f".set_cmu{cmu_id}_hkey{key}_pktsize")
        elif param1[0].type == ParamType.Timestamp:
            action = initialization_table.make_data([ client.DataTuple('task_id', task_id),
                                                      client.DataTuple('param2', param2.content)], 
                                                      prefix + f".set_cmu{cmu_id}_hkey{key}_timestamp")
        elif param1[0].type == ParamType.QueueLen:
            action = initialization_table.make_data([ client.DataTuple('task_id', task_id),
                                                      client.DataTuple('param2', param2.content)], 
                                                      prefix + f".set_cmu{cmu_id}_hkey{key}_queue_length")
        else:
            raise RuntimeError(f"Unkonwn ParamType of param 1.")
        initialization_table.entry_add(self.conn, [match], [action])
        return [match]

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
        # batch entries to make operations faster
        batch_match = []
        batch_action = []
        for key, mask in key_mappings.keys():
            if len(param_mappings) == 0:
                    match = perprocessing_table.make_key([client.KeyTuple(f'meta.cmu_group{group_id}.cmu{cmu_id}.task_id', task_id),
                                                        client.KeyTuple(f'meta.cmu_group{group_id}.cmu{cmu_id}.key', key, mask),
                                                        client.KeyTuple(f'meta.cmu_group{group_id}.cmu{cmu_id}.param1', 0, 0)])
                    action = perprocessing_table.make_data([ client.DataTuple('offset', key_mappings[(key, mask)])], 
                                                             prefix + f".process_cmu{cmu_id}_key")
                    entry_dict[match] = action
                    batch_match.append(match)
                    batch_action.append(action)
            else:
                for param_tuple in param_mappings:
                    match = perprocessing_table.make_key([client.KeyTuple(f'meta.cmu_group{group_id}.cmu{cmu_id}.task_id', task_id),
                                                        client.KeyTuple(f'meta.cmu_group{group_id}.cmu{cmu_id}.key', key, mask),
                                                        client.KeyTuple(f'meta.cmu_group{group_id}.cmu{cmu_id}.param1', param_tuple[0], param_tuple[1])])
                    action = perprocessing_table.make_data([ client.DataTuple('offset', key_mappings[(key, mask)]),
                                                            client.DataTuple('code', param_tuple[2]),], 
                                                            prefix + f".process_cmu{cmu_id}_key_param")
                    # Z what's it
                entry_dict[match] = action
                batch_match.append(match)
                batch_action.append(action)
        perprocessing_table.entry_add(self.conn, batch_match, batch_action)
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
        perprocessing_table.entry_del(self.conn, list(key_list))
        pass

    def operation_stage_add(self, group_id, group_type, cmu_id, task_id, operation_type):
        """
         task_id: which task to match.
        """
        prefix = ""
        if group_type == 1:
            prefix = f"FlyMonIngress.cmu_group{group_id}"
        else:
            prefix = f"FlyMonEgress.cmu_group{group_id}"
        operation_table = self.context.table_get(prefix+f".tbl_cmu{cmu_id}_operation")
        match = operation_table.make_key([client.KeyTuple(f'meta.cmu_group{group_id}.cmu{cmu_id}.task_id', task_id)])
        if operation_type == OperationType.AndOr:
            action = operation_table.make_data([], prefix + f".op_cmu{cmu_id}_and_or")
        elif operation_type == OperationType.CondADD:
            action = operation_table.make_data([], prefix + f".op_cmu{cmu_id}_cond_add")
        elif operation_table == OperationType.Max:
            action = operation_table.make_data([], prefix + f".op_cmu{cmu_id}_max")
        else:
            print("Invalid operation type when install runtime rules.")
            return None
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
        prefix = ""
        if group_type == 1:
            prefix = f"FlyMonIngress.cmu_group{group_id}"
        else:
            prefix = f"FlyMonEgress.cmu_group{group_id}"
        register_table = self.context.table_get(prefix + f".cmu{cmu_id}_buckets")
        # buf = [0] * (end-begin)
        buf = []
        # batch entries to read faster
        batch_key = []
        for register_idx in range(begin, end):
            batch_key.append(register_table.make_key([client.KeyTuple('$REGISTER_INDEX', register_idx)]))
        
        before_timestamp = time.time()
        resp = register_table.entry_get(
                self.conn,
                batch_key,
                {"from_hw": True})
        print(f"read lantency: {time.time() - before_timestamp}")
        
        for data, _ in resp:
        # data, _ = next(resp)
            data_dict = data.to_dict()
            ## first is lo, second is hi.
            # print(data_dict)
            value_lo = data_dict[prefix + f".cmu{cmu_id}_buckets.f1"][0]
            buf.append(value_lo)
        return buf