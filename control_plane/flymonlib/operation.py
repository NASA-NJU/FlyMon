from enum import Enum

class OperationType(Enum):
    """
    A class to represent operations in FlyMon.
    """
    CondADD = 1
    Max     = 2
    AndOr   = 3