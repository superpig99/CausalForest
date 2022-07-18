### forest类：
### 依赖类：Tree
from typing import List
from ..tree.Tree import Tree

class Forest:
# public:
    def __init__(self,trees:List[Tree], num_variables:int, ci_group_size:int):
        self._trees += trees # np.array不支持这个操作的！注意辨别
        self._num_variables = num_variables
        self._ci_group_size = ci_group_size

    @classmethod
    def ft_init(cls,forest):
        return cls(forest.trees,forest.num_variables,forest.ci_group_size)
    
    def get_trees(self): # 依赖类：Tree
        return self._trees

    def get_trees_(self):# 依赖类：Tree
        return self._trees

    def get_num_variables(self):
        return self._num_variables

    def get_ci_group_size(self):
        return self._ci_group_size

    def merge(self,forests):
        all_trees = []
        num_variables = forests[0].get_num_variables()
        ci_group_size = forests[0].get_ci_group_size()

        for forest in forests:
            trees = forest.get_trees_()
            all_trees += trees # np.array不支持！list可以

            if forest.get_ci_group_size() != ci_group_size:
                raise ValueError("All forests being merged must have the same ci_group_size.")
            
        return Forest(all_trees,num_variables,ci_group_size)

