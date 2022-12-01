from dataclasses import dataclass, field

import numpy as np

# node compatible with priority queue where path len is priority
@dataclass
class Node:
    matrix: np.ndarray
    path: list
    cost: float
    path_len: int = field(init=False)

    def __post_init__(self):
        self.path_len = len(self.path)

    def __lt__(self, other):
        return self.path_len > other.path_len

