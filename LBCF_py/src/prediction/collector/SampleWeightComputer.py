from tkinter import W
from typing import List

from ...forest.Forest import Forest

class SampleWeightComputer:
# public:
    def compute_weights(self, sample:int, forest:Forest, leaf_nodes_by_tree:List[List[int]], valid_trees_by_sample:List[List[bool]]):
        weights_by_sample = {}

        for tree_index in range(0,len(forest.get_trees())):
            if not valid_trees_by_sample[sample][tree_index]:
                continue

            leaf_nodes = leaf_nodes_by_tree[tree_index]
            node = leaf_nodes[sample]

            tree = forest.get_trees()[tree_index]
            samples = tree.get_leaf_samples()[node]
            if not samples.empty():
                self._add_sample_weights(samples,weights_by_sample)
            
            self._normalize_sample_weights(weights_by_sample)
            return weights_by_sample
    
# private:
    def _add_sample_weights(self, samples:List[int], weights_by_sample:dict):
        sample_weight = 1.0 / len(samples)

        for sample in samples:
            if sample not in weights_by_sample.keys():
                weights_by_sample[sample] = sample_weight
            else:
                weights_by_sample[sample] += sample_weight        
    
    def _normalize_sample_weights(self, weights_by_sample:dict):
        total_weight = 0.0
        for entry in weights_by_sample.values():
            total_weight += entry
        
        for sample in weights_by_sample.keys():
            weights_by_sample[sample] /= total_weight