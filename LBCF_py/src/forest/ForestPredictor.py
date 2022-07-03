###ForestPredictor类：
### 依赖类：PredictionCollector, Forest, Data, Prediction, TreeTraverser

class ForestPredictor:
# public:
    def __init__(self, num_threads,strategy) -> None: # strategy有两种策略可选
        pass # 这里包含了两个私有成员变量 tree_traverser，prediction_collector

    def predict(self,forest,train_data,data,estimate_variance):
        pass

    def predict_oob(self,forest,data,estimate_variance):
        pass

# private:
    def _predict(self,forest,train_data,data,estimate_variance,oob_prediction):
        pass