### forest类：
### 依赖类：Tree

class Forest:
# public:
    def __init__(self,trees,num_variables,ci_group_size):
        ## self.__trees 依赖于Tree类
        self.__num_variables = num_variables
        self.__ci_group_size = ci_group_size

    @classmethod
    def ft_init(cls,forest):
        return cls(forest.trees,forest.num_variables,forest.ci_group_size)
    
    def get_trees(self): # 依赖类：Tree
        pass

    def get_trees_(self):# 依赖类：Tree
        pass

    def get_num_variables(self):
        pass

    def get_ci_group_size(self):
        pass

    def merge(self,forests):
        pass

