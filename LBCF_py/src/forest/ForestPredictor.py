###ForestPredictor类：
### 依赖类：PredictionCollector, Forest, Data, Prediction, TreeTraverser

from ast import For
from ..commons.Data import Data
from .Forest import Forest
from ..prediction.collector.TreeTraverser import TreeTraverser
from ..prediction.collector.OptimizedPredictionCollector import OptimizedPredictionCollector
from ..prediction.UDCFPredictionStrategy import UDCFPredictionStrategy

class ForestPredictor:
# public:
    def __init__(self, num_threads:int, strategy: UDCFPredictionStrategy) -> None: # strategy有两种策略可选，但udcf_predictor在是现实，选择的是Optimized策略，所以这里只需要实现一个就可以
        # 这里包含了两个私有成员变量 tree_traverser，prediction_collector
        self._tree_traverser = TreeTraverser(num_threads)
        self._prediction_collector = OptimizedPredictionCollector(strategy,num_threads)

    def predict(self, forest:Forest, train_data:Data, data:Data, estimate_variance:bool):
        return self._predict(forest,train_data,data,estimate_variance,False)

    def predict_oob(self,forest:Forest, data:Data, estimate_variance:bool):
        return self._predict(forest, data, data, estimate_variance, True)

# private:
    def _predict(self,forest:Forest, train_data:Data, data:Data, estimate_variance:bool, oob_prediction:bool):
        if estimate_variance and (forest.get_ci_group_size()<=1):
            raise ValueError("To estimate variance during prediction, the forest must be trained with ci_group_size greater than 1.")

        leaf_nodes_by_tree = self._tree_traverser.get_leaf_nodes(forest, data, oob_prediction)

        trees_by_sample = self._tree_traverser.get_valid_trees_by_sample(forest, data, oob_prediction)

        return self._prediction_collector.collect_predictions(forest, train_data, data, leaf_nodes_by_tree, trees_by_sample, estimate_variance, oob_prediction)