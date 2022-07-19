# UDCFSplittingRuleFactory类：
# 依赖于：TreeOptions、UDCFSplittingRule

from ...tree.TreeOptions import TreeOptions
from ..UDCFSplittingRule import UDCFSplittingRule

class UDCFSplittingRuleFactory:
# public:
    def __init__(self, response_length:int, num_treatments:int):
        self._response_length = response_length
        self._num_treatments = num_treatments

    def create(self, max_num_unique_values:int, options:TreeOptions):
        return UDCFSplittingRule(max_num_unique_values,
                                options.get_min_node_size(),
                                options.get_alpha(),
                                options.get_imbalance_penalty(),
                                self._response_length,
                                self._num_treatments)

# private:全是成员变量