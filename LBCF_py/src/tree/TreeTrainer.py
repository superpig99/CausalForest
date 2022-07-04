### TreeTrainer类：
### 依赖于：Data, RandomSampler, TreeOptions, Tree, SplittingRule
### disallowed_split_variables该私有成员变量没有被定义

class TreeTrainer:
# public:
    def __init__(self,
                relabeling_strategy,
                splitting_rule_factory,
                prediction_strategy) -> None:
        pass # 三个私有成员变量在此赋值

    def train(self, data, sampler, clusters, options):
        pass

# private
    def _create_empty_node(self, child_nodes, samples, split_vars, split_values, send_missing_left):
        pass

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