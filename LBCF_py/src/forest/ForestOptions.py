### ForestOptions类：
### 依赖类：TreeOptions, SamplingOptions

class ForestOptions:
# public:
    def __init__(self,
                num_trees,
                ci_group_size,
                sample_fraction,
                mtry,
                min_node_size,
                honesty,
                honesty_fraction,
                honesty_prune_leaves,
                alpha,
                imbalance_penalty,
                num_threads,
                random_seed,
                sample_clusters,
                samples_per_cluster):
        pass

    def validate_num_threads(self,num_threads):
        pass

    def get_num_trees(self):
        return self._num_trees
    
    def get_ci_group_size(self):
        return self._ci_group_size

    def get_sample_fraction(self):
        return self._sample_fraction
    
    def get_tree_options(self):
        return self._tree_options # TreeOptions类的实例
    
    def get_sampling_options(self):
        return self._sampling_options # SamplingOptions类的实例
    
    def get_num_threads(self):
        return self._num_threads
    
    def get_random_seed(self):
        return self._random_seed