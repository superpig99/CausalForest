### TreeTrainer类：
### 依赖于：Data, RandomSampler, TreeOptions, Tree, SplittingRule
### disallowed_split_variables该私有成员变量没有被定义

from ..sampleing.RandomSampler import RandomSampler
from TreeOptions import TreeOptions

class TreeTrainer:
# public:
    def __init__(self,
                relabeling_strategy,
                splitting_rule_factory, # cpp里该变量是指针，
                prediction_strategy) -> None:
        pass # 三个私有成员变量在此赋值

    def train(self, data, sampler, clusters, options):
        child_nodes = [[],[]]
        nodes = [] # cpp里定义的是个二维向量，但初始化的时候没有指明？？？？
        split_vars = []
        split_values = []
        send_missing_left = []
        self._create_empty_node(child_nodes, nodes, split_vars, split_values, send_missing_left)

        if options.get_honesty():
            tree_growing_clusters = []
            new_leaf_clusters = []
            sampler.subsample(clusters,options.get_honesty_fraction(), tree_growing_clusters, new_leaf_clusters)
            sampler.sample_from_clusters(tree_growing_clusters, nodes[0]) # 注意这里的nodes[0]写法是否有误
            sampler.sample_from_clusters(new_leaf_clusters, new_leaf_samples)
        else:
            sampler.sample_from_clusters(clusters, nodes[0])
        
        splitting_rule = 


# private
    def _create_empty_node(self, child_nodes, samples, split_vars, split_values, send_missing_left):
        child_nodes[0].append(0)
        child_nodes[1].append(0)
        samples.append(0)
        split_vars.append(0)
        split_values.append(0)
        send_missing_left.append(True)

    def _repopulate_leaf_nodes(self, tree, data, leaf_samples, honesty_prune_leaves):
        pass

    def _create_split_variable_subset(self, result, sampler, data, mtry):
        pass

    def _split_node(self,
                    node,
                    data,
                    splitting_rule,
                    sampler,
                    child_nodes,
                    samples,
                    split_vars,
                    split_values,
                    send_missing_left,
                    responses_by_sample, # third party
                    options):
        pass

    def _split_node_internal(self,
                            node,
                            data,
                            splitting_rule,
                            possible_split_vars,
                            samples,
                            split_vars,
                            split_values,
                            send_missing_left,
                            responses_by_sample, # third party
                            min_node_size):
        pass