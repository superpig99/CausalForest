### Tree类：
### 依赖于：PredictionValues, Data

from operator import le
from typing import List

from ..commons.Data import Data
from ..prediction.PredictionValues import PredictionValues

class Tree:
# public:
    def __init__(self,
                root_node:int,
                child_nodes:List[List[int]],
                leaf_samples:List[List[int]],
                split_vars:List[int],
                split_values:List[float],
                drawn_samples:List[int],
                send_missing_left:List[bool],
                prediction_values:PredictionValues) -> None:
        self._root_node = root_node
        self._child_nodes = child_nodes
        self._leaf_samples = leaf_samples
        self._split_vars = split_vars
        self._split_values = split_values
        self._drawn_samples = drawn_samples
        self._send_missing_left = send_missing_left
        self._prediction_values = prediction_values # 可以这样初始化么？？？

    def find_leaf_nodes(self, data:Data, samples:List[int]): # 两种写法，注意合并
        prediction_leaf_nodes = [0]*data.get_num_rows()

        for sample in samples:
            node = self._find_leaf_node(data,sample)
            prediction_leaf_nodes[sample] = node
        
        return prediction_leaf_nodes
    
    def find_leaf_nodes_b(self, data:Data, valid_samples:List[bool]):
        num_samples = data.get_num_rows()

        prediction_leaf_nodes = [0]*data.get_num_rows()

        for sample in range(num_samples):
            if not valid_samples[sample]:
                continue

            node = self._find_leaf_node(data,sample)
            prediction_leaf_nodes[sample] = node
        
        return prediction_leaf_nodes

    def honesty_prune_leaves(self): # 依赖于private prune_node函数
        num_nodes = len(self._leaf_samples)
        for n in range(num_nodes,self._root_node,-1):
            node = n-1
            if self.is_leaf(node):
                continue
                
            left_child = self._child_nodes[0][node]
            if not self.is_leaf(left_child):
                self._prune_node(left_child)
            
            right_child = self._child_nodes[1][node]
            if not self.is_leaf(right_child):
                self._prune_node(right_child)
            
        self._prune_node(self._root_node)

    def get_root_node(self):
        return self._root_node
    
    def get_child_nodes(self):
        return self._child_nodes
    
    def get_leaf_samples(self):
        return self._leaf_samples
    
    def get_split_vars(self):
        return self._split_vars
    
    def get_split_values(self):
        return self._split_values
    
    def get_drawn_samples(self):
        return self._drawn_samples
    
    def get_send_missing_left(self):
        return self._send_missing_left
    
    def get_prediction_values(self):
        return self._prediction_values
    
    def is_leaf(self,node:int):
        return (self._child_nodes[0][node]==0) and (self._child_nodes[1][node]==0)
    
    def set_leaf_samples(self,leaf_samples:List[List[int]]):
        self._leaf_samples = leaf_samples
    
    def set_prediction_values(self,prediction_values:PredictionValues):
        self._prediction_values = prediction_values # 可以这样初始化么？？？

# private:
    def _find_leaf_node(self, data:Data, sample:int):
        node = self._root_node
        while True:
            if self.is_leaf(node):
                break

            split_var = self.get_split_vars()[node]
            split_val = self.get_split_values()[node]
            value = data.get(sample, split_var)
            send_na_left = self.get_send_missing_left()[node]
            if (value <= split_val) or (send_na_left and (value is None)) or ((split_val is None) and (value is None)):
                node = self._child_nodes[0][node]
            else:
                node = self._child_nodes[1][node]
        return node

    def _prune_node(self, node:int): ### 这个地方绝对有问题，node无法传回去，除非不用指针，直接返回值
        left_child = self._child_nodes[0][node]
        right_child = self._child_nodes[1][node]

        if self._is_empty_leaf(left_child) or self._is_empty_leaf(right_child):
            self._child_nodes[0][node] = 0
            self._child_nodes[1][node] = 0
        
        if not self._is_empty_leaf(left_child):
            node = left_child
        elif not self._is_empty_leaf(right_child):
            node = right_child

    def _is_empty_leaf(self, node:int):
        return (self.is_leaf(node) and (len(self._leaf_samples[node])==0))

