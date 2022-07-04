### ForestTrain类：
### 依赖类：RelabelingStrategy，SplittingRuleFactory，OptimizedPredictionStrategy
### 依赖类： Data，ForestOptions，Tree，RandomSampler

class ForestTrain:
## public:
    def __init__(self,
                relabeling_strategy,
                splitting_rule_factory,
                prediction_strategy):
        pass # 实例化了私有成员变量tree_trainer

    def train(self,data,options):
        pass
    
## private:
    def _train_trees(self,data,options):
        pass

    def _train_batch(self,start,num_trees,data,options):
        pass

    def _train_tree(self,data,sampler,options):
        pass

    def _train_ci_group(self,data,sampler,options):
        pass