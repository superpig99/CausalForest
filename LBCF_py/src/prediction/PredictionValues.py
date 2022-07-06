### PredictionValues类
### 依赖类：

class PredictionValues:
# public:
    def __init__(self,values=0,num_types=0):
        self._values = values
        if values == 0:
            self._num_nodes = 0
        else:
            self._num_nodes = len(values) # c++的size对于二维vector的返回值是什么？？？
        self._num_types = num_types
    
    def get(self,node,type):
        return self._values[node][type]
    
    def get_values(self,node):
        return self._values[node]

    def empty(self,node):
        return len(self._values[node])==0
    
    def get_all_values(self):
        return self._values
    
    def get_num_nodes(self):
        return self._num_nodes
    
    def get_num_types(self):
        return self._num_types

# private: all variables