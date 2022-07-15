### ForestOptions类：
### 依赖类：TreeOptions, SamplingOptions

import numpy as np
DEFAULT_NUM_THREADS = 0

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
        self._ci_group_size = ci_group_size
        self._sample_fraction = sample_fraction
        self._tree_options = TreeOptions(mtry, min_node_size, honesty, honesty_fraction, honesty_prune_leaves, alpha, imbalance_penalty)
        self._sampling_options = SamplingOptions(samples_per_cluster,sample_clusters)

        self._num_threads = self.validate_num_threads(num_threads)

        self._num_trees = num_trees + (num_trees % ci_group_size)

        if (ci_group_size > 1) and (sample_fraction > 0.5):
            raise ValueError("When confidence intervals are enabled, the sampling fraction must be less than 0.5.")

        if random_seed != 0:
            self._random_seed = random_seed
        else:
            self._random_seed = np.random.randn() ### 这里不确定，待排查


    def validate_num_threads(self,num_threads):
        if num_threads == DEFAULT_NUM_THREADS:
            return ??? # 这里的线程数是程序内还是本地全局的？？？
        elif num_threads > 0:
            return num_threads
        else:
            raise ValueError("A negative number of threads was provided.")

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