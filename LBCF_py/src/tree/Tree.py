### Tree类：
### 依赖于：PredictionValues, Data

class Tree:
# public:
    def __init__(self,
                root_node,
                child_nodes,
                leaf_samples,
                split_vars,
                split_values,
                drawn_samples,
                send_missing_left,
                prediction_values) -> None:
        self._root_node = root_node
        self._child_nodes = child_nodes
        self._leaf_samples = leaf_samples
        self._split_vars = split_vars
        self._split_values = split_values
        self._drawn_samples = drawn_samples
        self._send_missing_left = send_missing_left
        self._prediction_values = prediction_values # 可以这样初始化么？？？

    def find_leaf_nodes(self,data,samples): # 两种写法，注意合并
        pass

    def honesty_prune_leaves(self): # 依赖于private prune_node函数
        pass

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
    
    def is_leaf(self,node):
        return (self._child_nodes[0][node]==0) and (self._child_nodes[1][node]==0)
    
    def set_leaf_samples(self,leaf_samples):
        self._leaf_samples = leaf_samples
    
    def set_prediction_values(self,prediction_values):
        self._prediction_values = prediction_values # 可以这样初始化么？？？

# private:
    def _find_leaf_node(self, data, sample):
        pass

    def _prune_node(self,node):
        pass

    def _is_empty_leaf(self, node):
        pass

