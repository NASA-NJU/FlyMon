class FlowAttribute:
    """
    A base class for flow attributes
    NOTE: This is a abstract class, used as a template for different runtime environments.
    """
    def __init__(self):
        pass


    def install(self, runtime, task_id, resource_lists):
        """
        Given a runtime interfaces and resource lists, you need to install flow rules to CMU-Group(s)
        - resource_lists: [(group_id, group_type, cmu_id)]
        NOTE: how to resolve data address translation here?
        Answer: We need not to resolve data address translation here. This should be implemented in resource manager.
                Here we just modify [set params, preprocessing params, select operations]
        """
        pass

    def parse(self, data, flowkey):
        """
        You need to implement how to read the data according to the given flow key.
        """
        pass