### ForestTrain类：
### 依赖类：RelabelingStrategy，SplittingRuleFactory，OptimizedPredictionStrategy
### 依赖类： Data，ForestOptions，Tree，RandomSampler,TreeTrainer, utility

class ForestTrain:
## public:
    def __init__(self,
                relabeling_strategy,
                splitting_rule_factory,
                prediction_strategy):
        # 实例化了私有成员变量tree_trainer
        self._tree_trainer = TreeTrainer(relabeling_strategy,splitting_rule_factory,prediction_strategy)

    def train(self,data,options):
        trees = self._train_trees(data,options)

        num_variables = data.get_num_cols() - len(data.get_disallowed_split_variables())
        ci_group_size = options.get_ci_group_size()
        return Forest(trees,num_variables,ci_group_size)
    
## private:
    def _train_trees(self,data,options):
        num_samples = data.get_num_rows()
        num_trees = options.get_num_trees()

        tree_options = options.get_tree_options()
        honesty = tree_options.get_honesty()
        honesty_fraction = tree_options.get_honesty_fraction()

        if num_samples * options.get_sample_fraction() < 1:
            raise ValueError("The sample fraction is too small, as no observations will be sampled.")
        elif honesty and ((num_samples * options.get_sample_fraction() * honesty_fraction < 1) or (num_samples * options.get_sample_fraction() * (1-honesty_fraction)<1)):
            raise ValueError("The honesty fraction is too close to 1 or 0, as no observations will be sampled.")
        
        num_groups = num_trees / options.get_ci_group_size()

        thread_ranges = []
        split_sequence(thread_ranges,0,num_groups-1,options.get_num_threads())

        ####### 这个future确实不会。。。。

        return trees


    def _train_batch(self,start,num_trees,data,options):
        ci_group_size = options.get_ci_group_size()

        np.random.seed(options.get_random_seed() + start)
        trees = [0] * (num_trees * ci_group_size)

        for i in range(num_trees):
            tree_seed = np.random.uniform(0,np.ramdom.random(),1) # (low,high,size) ???????这里存在不确定，待排查
            sampler = RandomSampler(tree_seed,options.get_sampling_options())

            if ci_group_size == 1:
                tree = self._train_tree(data,sampler,options)
                trees.append(tree)
            else:
                group = self._train_ci_group(data,sampler,options)
                trees += group
        
        return trees


    def _train_tree(self,data,sampler,options):
        clusters = []
        sampler.sample_clusters(data.get_num_rows(),options.get_sample_fraction(),clusters)

        return self._tree_trainer.train(data,sampler,clusters,options.get_tree_options())

    def _train_ci_group(self,data,sampler,options):
        trees = []

        clusters = []
        sampler.sample_clusters(data.get_num_rows(),0.5,clusters)

        sample_fraction = options.get_sample_fraction()
        for i in range(options.get_ci_group_size()):
            cluster_subsample = []
            sampler.subsample(clusters, sample_fraction * 2, cluster_subsample)

            tree = self._tree_trainer.train(data,sampler,cluster_subsample,options.get_tree_options())
            trees.append(tree)
        
        return trees