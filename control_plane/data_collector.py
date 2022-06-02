from flymonlib.flymon_task import FlyMonTask
from flymonlib.flymon_runtime import FlyMonRuntime_BfRt


class DataCollector:

    def __init__(self, runtime:FlyMonRuntime_BfRt, cmug_configs):
        self.runtime = runtime
        pass

    def read(self, task_instance:FlyMonTask):
        data = []
        for loc in task_instance.locations:
            data.append(self.runtime.read(loc.group_id, loc.group_type, loc._cmu_id, 0, 16384))
        return data
