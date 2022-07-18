### TreeTrainer类：
### 依赖于：Data, RandomSampler, TreeOptions, Tree, SplittingRule
### disallowed_split_variables该私有成员变量没有被定义

from typing import List
from LBCF_py.src.prediction.PredictionValues import PredictionValues
import numpy as np

from ..relabeling.UDCFRelabelingStrategy import UDCFRelabelingStrategy
from ..splitting.factory.UDCFSplittingRuleFactory import UDCFSplittingRuleFactory
from ..splitting.UDCFSplittingRule import UDCFSplittingRule
from ..prediction.UDCFPredictionStrategy import UDCFPredictionStrategy
from ..commons.Data import Data
from ..sampling.RandomSampler import RandomSampler
from .TreeOptions import TreeOptions
from .Tree import Tree

class TreeTrainer:
# public:
    def __init__(self,
                relabeling_strategy:UDCFRelabelingStrategy,
                splitting_rule_factory:UDCFSplittingRuleFactory, # cpp里该变量是指针，
                prediction_strategy:UDCFPredictionStrategy) -> None:
        # 三个私有成员变量在此赋值
        self._relabeling_strategy = relabeling_strategy
        self._splitting_rule_factory = splitting_rule_factory
        self._prediction_strategy = prediction_strategy

    def train(self, data:Data, sampler:RandomSampler, clusters:List[int], options:TreeOptions):
        child_nodes = [[],[]]
        nodes = [] # cpp里定义的是个二维向量，但初始化的时候没有指明？？？？
        split_vars = []
        split_values = []
        send_missing_left = []
        self._create_empty_node(child_nodes, nodes, split_vars, split_values, send_missing_left)

        new_leaf_samples = []

        if options.get_honesty():
            tree_growing_clusters = []
            new_leaf_clusters = []
            sampler.subsample(clusters,options.get_honesty_fraction(), tree_growing_clusters, new_leaf_clusters)
            sampler.sample_from_clusters(tree_growing_clusters, nodes[0]) # 注意这里的nodes[0]写法是否有误
            sampler.sample_from_clusters(new_leaf_clusters, new_leaf_samples)
        else:
            sampler.sample_from_clusters(clusters, nodes[0])
        
        splitting_rule = self._splitting_rule_factory.create(len(nodes[0]),options)

        num_open_nodes = 1
        i = 0
        responses_by_sample = np.zeros((data.get_num_rows(),self._relabeling_strategy.get_response_length()))

        while num_open_nodes > 0:
            is_leaf_node = self._split_node(i,data,splitting_rule,sampler,child_nodes,nodes,split_vars,split_values,send_missing_left,responses_by_sample,options)
            if is_leaf_node:
                num_open_nodes -= 1
            else:
                nodes[i] = []
                num_open_nodes += 1
            i+=1
        
        drawn_samples = []
        sampler.get_samples_in_clusters(clusters,drawn_samples)

        tree = Tree(0,child_nodes,nodes,split_vars,split_values,drawn_samples,send_missing_left,PredictionValues())

        if len(new_leaf_samples)!=0:
            self._repopulate_leaf_nodes(tree,data,new_leaf_samples,options.get_honesty_prune_leaves())

        prediction_values = PredictionValues()

        if self._prediction_strategy is not None:
            prediction_values = self._prediction_strategy.precompute_prediction_values(tree.get_leaf_samples(),data)
        
        tree.set_prediction_values(prediction_values)

        return tree


# private
    def _create_empty_node(self, child_nodes, samples, split_vars, split_values, send_missing_left):
        child_nodes[0].append(0)
        child_nodes[1].append(0)
        samples.append([])
        split_vars.append(0)
        split_values.append(0)
        send_missing_left.append(True)

    def _repopulate_leaf_nodes(self, tree:Tree, data:Data, leaf_samples:List[int], honesty_prune_leaves:bool):
        num_nodes = len(tree.get_leaf_samples())
        new_leaf_nodes = [[]]*num_nodes

        leaf_nodes = tree.find_leaf_nodes(data, leaf_samples)

        for sample in leaf_samples:
            leaf_node = leaf_nodes[sample]
            new_leaf_nodes[leaf_node].append(sample)
        
        tree.set_leaf_samples(new_leaf_nodes)
        if honesty_prune_leaves:
            tree.honesty_prune_leaves()
        

    def _create_split_variable_subset(self, result:List[int], sampler:RandomSampler, data:Data, mtry:int):
        num_independent_variables = data.get_num_cols() - data.get_disallowed_split_variables()
        mtry_sample = sampler.sample_poisson(mtry)
        split_mtry = max(min(mtry_sample,num_independent_variables),1)

        sampler.draw(result,data.get_num_cols(),data.get_disallowed_split_variables(),split_mtry)


    def _split_node(self,
                    node:int,
                    data:Data,
                    splitting_rule:UDCFSplittingRule,
                    sampler:RandomSampler,
                    child_nodes:List[List[int]],
                    samples:List[List[int]],
                    split_vars:List[int],
                    split_values:List[float],
                    send_missing_left:List[bool],
                    responses_by_sample:np.ndarray, # third party
                    options:TreeOptions):
        possible_split_vars = []
        self._create_split_variable_subset(possible_split_vars,sampler,data,options.get_mtry())

        stop = self._split_node_internal(node,data,splitting_rule,possible_split_vars,samples,split_vars,split_values,send_missing_left,responses_by_sample,options.get_min_node_size())
        if stop:
            return True
        
        split_var = split_vars[node]
        split_value = split_values[node]
        send_na_left = send_missing_left[node]

        left_child_node = len(samples)
        child_nodes[0][node] = left_child_node
        self._create_empty_node(child_nodes,samples,split_vars,split_values,send_missing_left)

        right_child_node = len(samples)
        child_nodes[1][node] = right_child_node
        self._create_empty_node(child_nodes,samples,split_vars,split_values,send_missing_left)

        for sample in samples[node]:
            value = data.get(sample,split_var)
            if (value <= split_value) or (send_na_left and (value is None)) or ((split_value is None) and (value is None)):
                samples[left_child_node].append(sample)
            else:
                samples[right_child_node].append(sample)
        
        return False

    def _split_node_internal(self,
                            node:int,
                            data:Data,
                            splitting_rule:UDCFSplittingRule,
                            possible_split_vars:List[int],
                            samples:List[List[int]],
                            split_vars:List[int],
                            split_values:List[float],
                            send_missing_left:List[bool],
                            responses_by_sample:np.ndarray, # third party
                            min_node_size:int):
        if len(samples[node]) <= min_node_size:
            split_values[node] = -1.0
            return True
        
        stop = self._relabeling_strategy.relabel(samples[node],data,responses_by_sample)

        if stop or splitting_rule.find_best_split(data,node,possible_split_vars,responses_by_sample,samples,split_vars,split_values,send_missing_left):
            split_values[node] = -1.0
            return True
        
        return False
    