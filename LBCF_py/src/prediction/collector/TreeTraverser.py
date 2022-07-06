###TreeTraverser类：
### 依赖类：
from ..forest.Forest import Forest
from ..tree.Tree import Tree
from ..commons.Data import Data
from ..commons.utility import *

class TreeTraverser:
# public:
    def __init__(self,num_threads):
        self._num_threads = num_threads
    
    def get_leaf_nodes(self,forest,data,oob_prediction):
        num_trees = len(forest.get_trees())
        leaf_nodes_by_tree = [0] * num_trees
        thread_ranges = []
        split_sequence(thread_ranges, 0, num_trees - 1, self._num_threads)
        ## 涉及到知识盲区了

        return leaf_nodes_by_tree
    
    def get_valid_trees_by_sample(self,forest,data,oob_prediction):
        num_trees = len(forest.get_trees())
        num_samples = data.get_num_rows()
        result = [[True]*num_trees]*num_samples ## 得核实一下我的理解是否正确
        if oob_prediction:
            for tree_idx in range(num_trees):
                for sample in forest.get_trees[tree_idx].get_drawn_samples(): # 这里绝对有问题
                    result[sample][tree_idx] = False
        return result

# private: 
    def _get_leaf_node_batch(self,start,num_trees,forest,data,oob_prediction):
        num_samples = data.get_num_rows()
        all_leaf_nodes = [0]*num_trees
        for i in range(num_trees):
            tree = forest.get_trees()[start+i]
            valid_samples = self._get_valid_samples(num_samples,tree,oob_prediction)
            leaf_nodes = tree.find_leaf_nodes(data,valid_samples) # 这里的引用得核实，主要是核实tree的数据类型
            all_leaf_nodes[i] = leaf_nodes
        return all_leaf_nodes
    
    def _get_valid_samples(self,num_samples,tree,oob_prediction):
        valid_samples = [True] * num_samples
        if oob_prediction:
            for sample in tree.get_drawn_samples(): # 这里的引用得核实
                valid_samples[sample] = False
        return valid_samples