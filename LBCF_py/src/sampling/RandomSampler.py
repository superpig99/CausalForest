### RandomSampler类：
### 依赖于：SamplingOptions
import random
import math
import numpy as np

class RandomSampler:
# public:
    def __init__(self,seed,options) -> None:
        ## 两个私有成员变量在此被初始化
        self._options = options
        random.seed(seed) # 疑问：这里是否是全局有效

    def sample_clusters(self,num_rows,sample_fraction,samples):
        if self._options.get_clusters(): ## clusters的含义不清晰，这里的空值与否的判断需要检查
            num_samples = len(self._options.get_clusters) # c++里二维vector的size返回值是否为元素个数，待检查
            self.sample(num_rows,sample_fraction,samples)
        else:
            self.sample(num_rows,sample_fraction,samples)

    def sample_from_clusters(self, clusters, samples):
        if self._options.get_clusters():
            samples_by_cluster = self._options.get_clusters()
            for cluster in clusters:
                cluster_samples = samples_by_cluster[cluster]
                if len(cluster_samples) <= self._options.get_samples_per_cluster():
                    samples += cluster_samples # 假设samples是list类型
                    ## 如果samples是np.array类型，则需要以下写法：
                    ## samples = np.concatenate((samples,cluster_samples))
                else:
                    subsamples = [] # 目前暂定list类型
                    self.subsample_with_size(cluster_samples, self._options.get_samples_per_cluster(), subsamples)
                    samples += subsamples # samples是list类型
                    ## 如果samples是np.array类型，则需要以下写法：
                    ## samples = np.concatenate((samples,cluster_samples))
        else:
            samples = clusters

    def get_samples_in_clusters(self,clusters,samples):
        if self._options.get_clusters():
            for cluster in clusters:
                cluster_samples = self._options.get_clusters()[cluster]
                samples += cluster_samples
        else:
            samples = clusters

    def sample(self,num_samples,sample_fraction,samples):
        num_samples_inbag = int(num_samples * sample_fraction)
        self._shuffle_and_split(samples, num_samples, num_samples_inbag)

    def subsample(self,samples,sample_fraction,subsamples,oob_samples=[],if_oob=False): # 注意，该函数有两种写法，此处将其合并
        shuffled_sample = random.shuffle(samples)
        subsample_size = math.ceil(len(samples) * sample_fraction)
        subsamples = shuffled_sample[:subsample_size]
        if if_oob:
            oob_samples = shuffled_sample[subsample_size:]

    def subsample_with_size(samples,subsample_size,subsamples):
        shuffled_sample = random.shuffle(samples)
        subsamples = shuffled_sample[:subsample_size]

    def draw(self,result,max_n,skip,num_samples):
        if num_samples_inbag < max_n // 10:
            self._draw_simple(result,max_n,skip,num_samples) # result这个地址能传过去么？
        else:
            self._draw_fisher_yates(result,max_n,skip,num_samples)

    def sample_poisson(self,mean):
        pass # random模块并没有泊松分布，但treeTrainer用到了这里，所以待定

# private:
    def _shuffle_and_split(self,samples,n_all,size):
        # 待检查
        samples = random.shuffle(np.arange(n_all))
        samples = samples[:size] #???? size和n_all的大小关系是什么？？？

    def _draw_simple(self,result,max_n,skip,num_samples):
        result = [0]*num_samples
        temp = [False]*max_n
        for i in range(num_samples):
            while True:
                draw_n = random.uniform(0 , max_n - 1 - len(skip))
                for skip_value in skip:
                    if draw_n >= skip_value:
                        draw_n += 1
                if ~temp[draw_n]:
                    break
            temp[draw_n] = True
            result[i] = draw_n

    def _draw_fisher_yates(self,result,max_n,skip,num_samples):
        # 该函数并未被使用，暂时省略
        pass