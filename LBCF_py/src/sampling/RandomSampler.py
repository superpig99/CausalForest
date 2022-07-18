### RandomSampler类：
### 依赖于：SamplingOptions

import math
import numpy as np
from typing import List

from .SamplingOptions import SamplingOptions

class RandomSampler:
# public:
    def __init__(self, seed:int, options:SamplingOptions) -> None:
        ## 两个私有成员变量在此被初始化
        self._options = options
        np.random.seed(seed) # 全局有效

    def sample_clusters(self, num_rows:int, sample_fraction:float, samples:List[int]):
        if len(self._options.get_clusters())==0:
            self.sample(num_rows,sample_fraction,samples)
        else:
            num_samples = len(self._options.get_clusters())
            self.sample(num_samples,sample_fraction,samples)

    def sample_from_clusters(self, clusters:List[int], samples:List[int]):
        if len(self._options.get_clusters())==0:
            samples = clusters
        else:
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

    def get_samples_in_clusters(self, clusters:List[int], samples:List[int]):
        if len(self._options.get_clusters())==0:
            samples = clusters # 这里是否需要深拷贝？
        else:
            for cluster in clusters:
                cluster_samples = self._options.get_clusters()[cluster]
                samples += cluster_samples

    def sample(self, num_samples:int, sample_fraction:float, samples:List[int]):
        num_samples_inbag = int(num_samples * sample_fraction)
        self._shuffle_and_split(samples, num_samples, num_samples_inbag)

    def subsample(self, samples:List[int], sample_fraction:float, subsamples:List[int], oob_samples=[],if_oob=False): # 注意，该函数有两种写法，此处将其合并
        shuffled_sample = samples[:]
        np.random.shuffle(shuffled_sample)
        subsample_size = math.ceil(len(samples) * sample_fraction)
        subsamples = shuffled_sample[:subsample_size]
        if if_oob:
            oob_samples = shuffled_sample[subsample_size:]

    def subsample_with_size(self, samples:List[int], subsample_size:int,subsamples:List[int]):
        shuffled_sample = samples[:]
        np.random.shuffle(shuffled_sample)
        subsamples = shuffled_sample[:subsample_size] # 目的是返回subsamples

    def draw(self, result:List[int], max_n:int, skip:set, num_samples:int):
        if num_samples < (max_n // 10):
            self._draw_simple(result,max_n,skip,num_samples)
        else:
            self._draw_fisher_yates(result,max_n,skip,num_samples)

    def sample_poisson(self,mean):
        return np.random.poisson(lam = mean, size = 1) # 返回的是np.array([val])

# private:
    def _shuffle_and_split(self, samples:List[int], n_all:int, size:int):
        samples = np.arange(n_all)
        np.random.shuffle(samples) # np.random.shuffle无返回值，在自身进行操作
        samples = samples.tolist()
        if size <= n_all:
            samples = samples[:size]
        else:
            samples += [0]*(size - n_all)

    def _draw_simple(self, result:List[int], max_n:int, skip:set, num_samples:int):
        result = [0]*num_samples
        temp = [False]*max_n
        for i in range(num_samples):
            while True:
                draw_n = int(np.random.uniform(0 , max_n - 1 - len(skip)))
                for skip_value in skip:
                    if draw_n >= skip_value:
                        draw_n += 1
                if not temp[draw_n]:
                    break
            temp[draw_n] = True
            result[i] = draw_n

    def _draw_fisher_yates(self, result:List[int], max_n:int, skip:set, num_samples:int):
        result = np.arange(max_n).tolist()
        for i in skip:
            if i in result: # 也许可以改为set操作进行加速
                result.remove(i)
        
        for i in range(len(result)-1,-1,-1):
            j = i + math.floor(np.random.uniform(0.0,1.0)*(max_n - len(skip) -i))
            result[i],result[j] = result[j],result[i]
        
        if num_samples>len(result):
            result += [0]*(num_samples - len(result))
        else:
            result = result[:num_samples]