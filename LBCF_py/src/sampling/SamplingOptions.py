### SamplingOptions类：

class SamplingOptions:
# public:
    def __init__(self,samples_per_cluster=0,sample_clusters=0) -> None: # 两种写法已合并
        self._num_samples_per_cluster = samples_per_cluster
        if sample_clusters==0:
            self._clusters = [0]
        else:
            pass
            ### 不太理解这个函数的作用


    def get_clusters(self):
        return self._clusters
    
    def get_samples_per_cluster(self):
        return self._num_samples_per_cluster