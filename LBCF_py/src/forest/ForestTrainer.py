### ForestTrain类：
### 依赖类：RelabelingStrategy，SplittingRuleFactory，OptimizedPredictionStrategy
### 依赖类： Data，ForestOptions，Tree，RandomSampler,TreeTrainer, utility

import imp
import numpy as np
from ..sampling.RandomSampler import RandomSampler
from ..commons.Data import Data
from ..commons.utility import *
from ..tree.TreeTrainer import TreeTrainer
from .Forest import Forest
from .ForestOptions import ForestOptions
from ..relabeling.UDCFRelabelingStrategy import UDCFRelabelingStrategy
from ..splitting.factory.UDCFSplittingRuleFactory import UDCFSplittingRuleFactory
from ..prediction.UDCFPredictionStrategy import UDCFPredictionStrategy


class ForestTrainer:
## public:
    def __init__(self,
                relabeling_strategy:UDCFRelabelingStrategy,
                splitting_rule_factory:UDCFSplittingRuleFactory,
                prediction_strategy:UDCFPredictionStrategy):
        # 实例化了私有成员变量tree_trainer
        self._tree_trainer = TreeTrainer(relabeling_strategy,splitting_rule_factory,prediction_strategy)

    def train(self, data:Data, options:ForestOptions):
        trees = self._train_trees(data,options)

        num_variables = data.get_num_cols() - len(data.get_disallowed_split_variables())
        ci_group_size = options.get_ci_group_size()
        return Forest(trees,num_variables,ci_group_size)
    
## private:
    def _train_trees(self, data:Data, options:ForestOptions):
        num_samples = data.get_num_rows()
        num_trees = options.get_num_trees()

        tree_options = options.get_tree_options()
        honesty = tree_options.get_honesty()
        honesty_fraction = tree_options.get_honesty_fraction()

        if num_samples * options.get_sample_fraction() < 1:
            raise ValueError("The sample fraction is too small, as no observations will be sampled.")
        elif honesty and ((num_samples * options.get_sample_fraction() * honesty_fraction < 1) or (num_samples * options.get_sample_fraction() * (1-honesty_fraction)<1)):
            raise ValueError("The honesty fraction is too close to 1 or 0, as no observations will be sampled.")
        
        num_groups = num_trees / options.get_ci_group_size()

        thread_ranges = []
        split_sequence(thread_ranges,0,num_groups-1,options.get_num_threads())

        trees = []
        for i in range(len(thread_ranges)-1):
            start_index = thread_ranges[i]
            num_tress_batch = thread_ranges[i+1]-start_index

            thread_trees = self._train_batch(start_index,num_tress_batch,data,options)
            trees += thread_trees

        return trees


    def _train_batch(self, start:int, num_trees:int, data:Data, options:ForestOptions):
        ci_group_size = options.get_ci_group_size()

        np.random.seed(options.get_random_seed() + start)
        
        trees = []
        for i in range(num_trees):
            tree_seed = np.random.uniform(0,np.ramdom.random(),1) # ???????这里存在不确定，待排查
            sampler = RandomSampler(tree_seed,options.get_sampling_options())

            if ci_group_size == 1:
                tree = self._train_tree(data,sampler,options)
                trees.append(tree)
            else:
                group = self._train_ci_group(data,sampler,options) # group是List[Tree]类型
                trees += group
        
        return trees


    def _train_tree(self, data:Data, sampler:RandomSampler, options:ForestOptions):
        clusters = []
        sampler.sample_clusters(data.get_num_rows(), options.get_sample_fraction(), clusters) # 填充clusters

        return self._tree_trainer.train(data,sampler,clusters,options.get_tree_options())

    def _train_ci_group(self,data,sampler,options):
        trees = []

        clusters = []
        sampler.sample_clusters(data.get_num_rows(),0.5,clusters)

        sample_fraction = options.get_sample_fraction()
        for i in range(options.get_ci_group_size()):
            cluster_subsample = []
            sampler.subsample(clusters, sample_fraction * 2, cluster_subsample)

            tree = self._tree_trainer.train(data,sampler,cluster_subsample,options.get_tree_options())
            trees.append(tree)
        
        return trees