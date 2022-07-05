### RandomSampler类：
### 依赖于：SamplingOptions

class RandomSampler:
# public:
    def __init__(self,seed,options) -> None:
        pass ## 两个私有成员变量在此被初始化

    def sample_clusters(self,num_rows,sample_fraction,samples):
        pass

    def sample_from_clusters(self, clusters, samples):
        pass

    def get_samples_in_clusters(self,clusters,samples):
        pass

    def sample(self,num_samples,sample_fraction,samples):
        pass

    def subsample(self,samples,sample_fraction,subsamples,oob_samples,if_oob): # 注意，该函数有两种写法，此处将其合并
        pass

    def subsample_with_size(samples,subsample_size,subsamples):
        pass

    def draw(self,result,max_n,skip,num_samples):
        pass

    def sample_poisson(self,mean):
        pass

# private:
    def _shuffle_and_split(self,samples,n_all,size):
        pass

    def _draw_simple(self,result,max_n,skip,num_samples):
        pass

    def _draw_fisher_yates(self,result,max_n,skip,num_samples):
        result = np.arange(max_n)
        for i in skip:
            if 
