
from concurrent.futures import thread
from typing import List
import numpy as np

from ..UDCFPredictionStrategy import UDCFPredictionStrategy
from ..PredictionValues import PredictionValues
from ..Prediction import Prediction
from ...forest.Forest import Forest
from ...commons.utility import *
from ...commons.Data import Data


class OptimizedPredictionCollector:
# public:
    def __init__(self, strategy:UDCFPredictionStrategy, num_threads:int) -> None:
        self._strategy = strategy
        self._num_threads = num_threads

    def collect_predictions(self,
                            forest:Forest,
                            train_data:Data,
                            data:Data,
                            leaf_nodes_by_tree:List[List[int]],
                            valid_trees_by_sample:List[List[bool]],
                            estimate_variance:bool,
                            estimate_error:bool) -> List[Prediction]:
        num_samples = data.get_num_rows()
        thread_ranges = []
        split_sequence(thread_ranges, 0, num_samples-1, self._num_threads)

        predictions = []
        for i in range(0,len(thread_ranges)-1):
            start_index = thread_ranges[i]
            num_samples_batch = thread_ranges[i+1] - start_index

            thread_predictions = self._collect_predictions_batch(forest,train_data,data,leaf_nodes_by_tree,valid_trees_by_sample,estimate_variance,estimate_error,start_index,num_samples_batch)
            predictions += thread_predictions

# private:
    def _collect_predictions_batch(self,
                                   forest:Forest,
                                   train_data:Data,
                                   data:Data,
                                   leaf_nodes_by_tree:List[List[int]],
                                   valid_trees_by_sample:List[List[bool]],
                                   estimate_variance:bool,
                                   estimate_error:bool,
                                   start:int,
                                   num_samples:int):
        num_trees = len(forest.get_trees())
        record_leaf_values = estimate_variance or estimate_error

        predictions = []

        for sample in range(start, num_samples + start):
            average_value = np.array([])
            leaf_values = np.array([])
            if record_leaf_values:
                leaf_values = np.zeros(num_trees.shape) # 有问题

            num_leaves = 0
            for tree_index in range(0,len(forest.get_trees())):
                if not valid_trees_by_sample[sample][tree_index]:
                    continue

                leaf_nodes = leaf_nodes_by_tree[tree_index]

                node = leaf_nodes[sample]

                tree = forest.get_trees()[tree_index]
                prediction_values = tree.get_prediction_values()

                if not prediction_values.empty(node):
                    num_leaves+=1
                    self._add_prediction_values(node,prediction_values,average_value)
                    if record_leaf_values:
                        leaf_values[tree_index] = prediction_values.get_values(node)
            
            if num_leaves == 0:
                nan = [None]*self._strategy.prediction_length()
                nan_error = [None]
                ######### 这里不确定
                continue
            
            self._normalize_prediction_values(num_leaves,average_value)
            point_prediction = self._strategy.predict(average_value)

            prediction_values(leaf_values,self._strategy.prediction_value_length())
            variance = self._strategy.compute_variance(average_value,prediction_values,forest.get_ci_group_size()) if estimate_variance else []

            mse = []
            mce = []
            if estimate_error:
                error = self._strategy.compute_error(sample,average_value,prediction_values,data)
                mse.append(error[0][0]) # compute_error还未确定，所以其返回值也待定
                mce.append(error[0][1])
            
            prediction = Prediction(point_prediction, variance, mse, mce)

            self._validate_prediction(sample,prediction)
            predictions.append(prediction)
        
        return predictions

    
    def _add_prediction_values(self, node:int, prediction_values:PredictionValues, combined_average:List[float]):
        if len(combined_average)==0:
            combined_average = [0.0]*prediction_values.get_num_types()
        
        for type in range(0,prediction_values.get_num_types()):
            combined_average[type] += prediction_values.get(node,type)
        

    def _normalize_prediction_values(self, num_leaves:int, combined_average:List[float]):
        for i in range(len(combined_average)): # 需要检查一下这里是否成功
            combined_average[i] /= num_leaves

    def _validate_prediction(self, sample:int, prediction:Prediction):
        prediction_length = self._strategy.prediction_length()
        if len(prediction.get_predictions()) != prediction_length: # 这里是按自己的理解写的，得确认一下是否成功
            raise ValueError("Prediction for sample " + str(sample) + " did not have the expected length.")

# 成员变量：strategy,num_threads