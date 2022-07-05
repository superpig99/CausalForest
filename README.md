> ref:
> GRF-github: https://github.com/grf-labs/grf
> LBCF-github: https://github.com/www2022paper/WWW-2022-PAPER-SUPPLEMENTARY-MATERIALS

# CausalForest

## LBCF实现逻辑说明

### LBCF的train逻辑：
`mian.cpp`中`udcf_trainer`函数初始化了ForestTrainer类的实例，该实例用于构建Forest，实现逻辑如下：
#### ForestTrainer类train方法的调用逻辑：
ForestTrainer类的pulic成员函数train调用ForestTrainer类的private成员函数train_trees；而train_trees调用ForestTrainer类的private成员函数train_batch；而train_batch调用ForestTrainer类的private成员函数train_tree或train_ci_group；而train_tree调用ForestTrainer类的private成员变量tree_trainer的train方法，而tree_trainer实际上是TreeTrainer类的实例；综上，ForestTrainer类是依靠TreeTrainer类来实现树的构造的；

#### TreeTrainer类train方法的实现逻辑：
树的构造（分裂）实际是在TreeTrainer类的train方法实现的，该方法的实现逻辑如下：

1. 准备父节点数据集：这里会判断是否采用honest构造方式，若honest，则会将待分裂数据集随机采样分成tree_growing_clusters和new_leaf_clusters两部分，前者用于分裂节点（给到父节点nodes[0]），后者用于评估结果；
2. 指定分裂规则splitting_rule，`\UDCF_Synthetic\core\src\splitting\factory`路径下包含多种分裂规则，而本次main函数通过调用udcf_trainer指明了采用UDCFSplittingRuleFactory，




##### 参数说明：
- mtry是LBCF论文里的超参m！
- num_treatments是treatment的维度【作为treatment字段的个数】
- 同理，num_outcomes是outcome的维度【作为outcome字段的个数】