class CompressedKeyResource:
    """
    A class to represent resource in FlyMon DataPlane.
    """
    def __init__(self, type, content_dict):
        self.type = type
        self.content_dict = content_dict