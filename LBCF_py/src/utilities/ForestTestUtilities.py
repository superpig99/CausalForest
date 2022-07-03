### ForestTestUtilities类：
### 返回ForestOptions

from ..forest.ForestOptions import ForestOptions

class ForestTestUtilities:
    def __init__(self) -> None: # 该类的init方法为空
        pass

    def default_options(self,honesty=False,ci_group_size=1): # 已合并
        self.num_trees = 300
        self.ci_group_size = ci_group_size
        self.sample_fraction = 0.5
        self.mtry = 3
        self.min_node_size = 50
        self.honesty = honesty
        self.honesty_fraction = 0.5
        self.prune = True
        self.alpha = 0.05
        self.imbalance_penalty = 0.01
        self.num_threads = 40
        self.seed = 42
        self.empty_clusters = [] ## 这个变量如何初始化？？？
        self.samples_per_cluster = 0

        return ForestOptions(self.num_trees,
                self.ci_group_size,
                self.sample_fraction,
                self.mtry,
                self.min_node_size,
                self.honesty,
                self.honesty_fraction,
                self.prune,
                self.alpha,
                self.imbalance_penalty,
                self.num_threads,
                self.seed,
                self.empty_clusters,
                self.samples_per_cluster)
    
    def default_honest_options(self):
        return self.default_options(True,1)