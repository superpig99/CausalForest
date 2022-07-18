### TreeOptions类：

class TreeOptions:
# public:
    def __init__(self,
                mtry:int,
                min_node_size:int,
                honesty:bool,
                honesty_fraction:float,
                honesty_prune_leaves:bool,
                alpha:float,
                imbalance_penalty:float) -> None:
        self._mtry = mtry
        self._min_node_size = min_node_size
        self._honesty = honesty
        self._honesty_fraction = honesty_fraction
        self._honesty_prune_leaves = honesty_prune_leaves
        self._alpha = alpha
        self._imbalance_penalty = imbalance_penalty
    
    def get_mtry(self):
        return self._mtry

    def get_min_node_size(self):
        return self._min_node_size

    def get_honesty(self):
        return self._honesty
    
    def get_honesty_fraction(self):
        return self._honesty_fraction
    
    def get_honesty_prune_leaves(self):
        return self._honesty_prune_leaves
    
    def get_alpha(self):
        return self._alpha
    
    def get_imbalance_penalty(self):
        return self._imbalance_penalty