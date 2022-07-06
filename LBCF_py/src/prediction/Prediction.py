### Prediction类：
### 依赖类：

class Prediction:
# public:
    def __init__(self,predictions,variance_estimates=0,error_estimates=0,excess_error_estimates=0):
        self._predictions = predictions
        self._variance_estimates = variance_estimates
        self._error_estimates = error_estimates
        self._excess_error_estimates = excess_error_estimates
    
    def get_predictions(self):
        return self._predictions
    
    def get_variance_estimates(self):
        return self._variance_estimates
    
    def get_error_estimates(self):
        return self._error_estimates
    
    def get_excess_error_estimates(self):
        return self._excess_error_estimates
    
    def contains_variance_estimates(self):
        # 有问题！！！？？？
        # _variance_estimates不一定是list，有可能是整数【初始化的时候就是整数】
        # return True if len(self._variance_estimates)>0 else False
        return len(self._variance_estimates)>0
    
    def contains_error_estimates(self):
        # 有问题！！！？？？
        # _variance_estimates不一定是list，有可能是整数【初始化的时候就是整数】
        return len(self._variance_estimates)>0
    
    def size(self):
        return len(self._predictions)
# private: all variables