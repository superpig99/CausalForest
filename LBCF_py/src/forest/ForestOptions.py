### ForestOptions类：
### 依赖类：TreeOptions, SamplingOptions

from typing import List
import random
import numpy as np

from ..tree.TreeOptions import TreeOptions
from ..sampling.SamplingOptions import SamplingOptions

DEFAULT_NUM_THREADS = 0

class ForestOptions:
# public:
    def __init__(self,
                num_trees:int,
                ci_group_size:int,
                sample_fraction:float,
                mtry:int,
                min_node_size:int,
                honesty:bool,
                honesty_fraction:float,
                honesty_prune_leaves:bool,
                alpha:float,
                imbalance_penalty:float,
                num_threads:int,
                random_seed:int,
                sample_clusters:List[int],
                samples_per_cluster:int):
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
            self._random_seed = random.getrandbits(32) # 生成32位的随机数


    def validate_num_threads(self,num_threads:int):
        if num_threads == DEFAULT_NUM_THREADS:
            return 4 # 这里的线程数是程序内还是本地全局的？？？ # 请教后得知随便设就行
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