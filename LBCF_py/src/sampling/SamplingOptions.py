### SamplingOptions类：

class SamplingOptions:
# public:
    def __init__(self,samples_per_cluster=0,sample_clusters=0) -> None: # 两种写法已合并
        self._num_samples_per_cluster = samples_per_cluster
        if sample_clusters==0:
            self._clusters = []
        else:
            cluster_ids = {}
            for cluster in sample_clusters:
                if cluster not in cluster_ids.keys():
                    cluster_id = len(cluster_ids)
                    cluster_ids[cluster] = cluster_id
            
            self._clusters = [[]]*len(cluster_ids)
            for sample in range(len(sample_clusters)):
                cluster = sample_clusters[sample]
                cluster_id = cluster_ids[cluster]
                self._clusters[cluster_id].append(sample) # self._clusters是List[List[int]]类型


    def get_clusters(self):
        return self._clusters
    
    def get_samples_per_cluster(self):
        return self._num_samples_per_cluster