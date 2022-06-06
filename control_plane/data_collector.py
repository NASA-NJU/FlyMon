from flymonlib.flow_key import FlowKey
from flymonlib.flymon_task import FlyMonTask
from flymonlib.flymon_runtime import FlyMonRuntime_BfRt


class DataCollector:

    def __init__(self, runtime:FlyMonRuntime_BfRt, cmug_configs):
        self.runtime = runtime
        self.cmug_bitw = {
            # key : cmu_group id
            # val : cmu_bitw (total_bits)
        }
        self.cmug_mem = {
            # key: cmu_group id
            # val : type, cmu_num, memory_size
        }
        for cmug in cmug_configs:
            id = cmug["id"]
            cmu_bitw = cmug["key_bitw"]
            cmu_num = cmug["cmu_num"]
            cmu_size = cmug["cmu_size"]
            group_type = cmug["type"]
            self.cmug_bitw[id] = cmu_bitw
            self.cmug_mem[id] = (group_type, cmu_num, cmu_size)


    def read_group(self, group_id):
        """Read all memory of a cmu group.
        Args:
            group_id
        Returns:
            a list of data array        
        """
        if group_id not in self.cmug_mem.keys():
            print(f"Invalid CMU-Group ID.")
            return None
        data = []
        group_type = self.cmug_mem[group_id][0]
        cmu_num = self.cmug_mem[group_id][1]
        cmu_size = self.cmug_mem[group_id][2]
        for idx in range(cmu_num):
            cmu_id = idx + 1
            low = 0
            high = cmu_size
            # actually read the data 
            data.append(self.runtime.read(group_id, group_type, cmu_id, low, high))
        return data

    def read_task(self, task_instance:FlyMonTask):
        data = []
        for loc in task_instance.locations:
            # first calc the memory range
            # the address width of this task
            key_bitw = self.cmug_bitw[loc.group_id] - loc.memory_type + 1  
            # the lowwer and higher bound of the memory range
            low = loc.memory_idx*(2**key_bitw)
            high = (loc.memory_idx+1)*(2**key_bitw)
            # actually read the data 
            data.append(self.runtime.read(loc.group_id, loc.group_type, loc.cmu_id, low, high))
        return data

    def query_task(self, task_instance:FlyMonTask, flow_key_bytes = None):
        data = []
        if flow_key_bytes is not None:
            """
            For multi-key tasks.
            """
            for loc in task_instance.locations:
                idx = loc.address_translate(self.cmug_bitw[loc.group_id], flow_key_bytes)
                data.append(self.runtime.read(loc.group_id, loc.group_type, loc.cmu_id, idx, idx + 1)[0])
        else:
            """
            For single-key tasks.
            """
            pass
        # print(data)
        print(task_instance.attribute.analyze(data))
        