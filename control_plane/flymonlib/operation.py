from enum import Enum

class Operation(Enum):
    """
    A class to represent operations in FlyMon.
    """
    CondADD = 1
    Max     = 2
    And     = 3
    Or      = 4