
class DataManager:
    """
    This class is dedicated for collecting and manage measurement datas.
    Specially, it needs to translate physical data address for each task's virtual address.
    """
    def __init__(self, bfrt_session):
        self.session = bfrt_session
        pass

    def sync(self):
        """
        Maybe it needs to be a thread function that running once periodly.
        """
        pass