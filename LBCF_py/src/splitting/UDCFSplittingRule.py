# UDCFSplittingRule类:
# 依赖类：

import numpy as np

class UDCFSplittingRule:
# public:
'''
private vars:
  size_t* counter;
  double* weight_sums;
  Eigen::ArrayXXd sums;
  Eigen::ArrayXXi num_small_w;
  Eigen::ArrayXXd sums_w;
  Eigen::ArrayXXd sums_w_squared;

  uint min_node_size;
  double alpha;
  double imbalance_penalty;
  size_t response_length;
  size_t num_treatments;
'''
    def __init__(self
                ,max_num_unique_values
                ,min_node_size
                ,alpha
                ,imbalance_penalty
                ,response_length
                ,num_treatments):
        self._min_node_size = min_node_size
        self._alpha = alpha
        self._imbalance_penalty = imbalance_penalty
        self._response_length = response_length
        self._num_treatments = num_treatments
        self._counter = [0]*max_num_unique_values
        self._weight_sums = [0]*max_num_unique_values
        self._sums = np.zeros((max_num_unique_values,response_length))
        self._num_small_w = np.zeros((max_num_unique_values,num_treatments))
        self._sums_w = np.zeros((max_num_unique_values,num_treatments))
        self._sums_w_squared = np.zeros((max_num_unique_values,num_treatments))
    
    def find_best_split(self
                        ,data
                        ,node
                        ,possible_split_vars
                        ,responses_by_sample
                        ,samples
                        ,split_vars
                        ,split_values
                        ,send_missing_left):
        num_samples = len(samples[node])

        weight_sum_node = 0.0
        sum_node = np.zeros(response_length)
        sum_node_w = np.zeros(num_treatments)
        sum_node_w_squared = np.zeros(num_treatments)

        treatments = np.zeros((num_samples,num_treatments))
        for i in range(num_samples):
            sample = samples[node][i] # samples里存储的是下标
            sample_weight = data.get_weight(sample) # 这一步有什么意义

            sample_weight = 1
            weight_sum_node += sample_weight
            sum_node += sample_weight * responses_by_sample[sample]

            treatments[i] = data.get_treatments(sample)

            sum_node_w += sample_weight * treatments[i]
            sum_node_w_squared += sample_weight * np.square(treatments[i])
        
        size_node = sum_node_w_squared - np.square(sum_node_w)/weight_sum_node

        min_child_size = size_node * self._alpha

        mean_w_node = sum_node_w / weight_sum_node

        num_node_small_w = np.zeros(num_treatments)

        for i in range(num_samples):
            num_node_small_w += (treatments[i] < mean_w_node).astype(int)
        

        best_var = []
        best_value = []
        best_decrease = []
        best_send_missing_left = []
        for var in possible_split_vars:
            self._find_best_split_value(data, node, var, num_samples, num_samples, sum_node, mean_w_node, num_node_small_w,
                                        sum_node_w, sum_node_w_squared, min_child_size, treatments, best_value,
                                        best_var, best_decrease, best_send_missing_left, responses_by_sample, samples)
        
        if len(best_decrease) == 0:
            return True
        
        best_decrease_copy = best_decrease[:]
        num_decrease = len(best_decrease)
        best_decrease.sort()
        N = max(int(num_decrease*0.05),1)

        decrease_threshold = 0
        for decrease in best_decrease:
            N -= 1
            if N==0:
                decrease_threshold = decrease
                break
        
        intra_split_value = []
        intra_split_var = []
        intra_missing_left = []
        for i in range(num_decrease):
            if best_decrease_copy[i] >= decrease_threshold:
                intra_split_value.append(best_value[i])
                intra_split_var.append(best_var[i])
                intra_missing_left.append(best_send_missing_left[i])
        
        num_intra = len(intra_split_value)
        max_var = 0.0
        for i in range(num_intra):
            split_var = intra_split_var[i]
            split_value = intra_split_value[i]
            send_na_left = intra_missing_left[i]
            samples_left = []
            samples_right = []
            for sample in samples[node]:
                value = data.get(sample,split_var)
                if (value <= split_value) or (send_na_left and (value is None)) or ((split_value is None) and (value is None)):
                    samples_left.append(sample)
                else:
                    samples_right.append(sample)
            
            theta_left = np.zeros((num_treatments,num_outcomes)) # theta_left的具体维度是根据_relabel_child函数的实现来敲定的
            theta_right = np.zeros((num_treatments,num_outcomes))
            if self._relabel_child(samples_left,data,theta_left) or self._relabel_child(samples_right,data,theta_right):
                continue
            
            theta_left_mean = np.mean(theta_left)
            theta_right_mean = np.mean(theta_right)

            theta_left_var = np.var(theta_left)
            theta_right_var = np.var(theta_right)

            if theta_left_var + theta_right_var > max_var:
                split_vars[node] = split_var
                split_values[node] = split_value
                send_missing_left[node] = send_na_left
                max_var = theta_left_var + theta_right_var
        
        return False

    
# private:
    def _relabel_child(self,samples,data,theta):
        num_samples = len(samples)
        num_treatments = data.get_num_treatments()
        num_outcomes = data.get_num_outcomes()
        if num_samples <= num_treatments:
            return True
        
        Y_centered = np.zeros((num_samples,num_outcomes)) # 残差
        W_centered = np.zeros((num_samples,num_treatments))
        weights = np.zeros(num_samples) # 也可以改成随机数
        Y_mean = np.zeros(num_outcomes)
        W_mean = np.zeros(num_treatments)
        sum_weight = 0

        for i in range(num_samples):
            sample = samples[i]
            weight = data.get_weight(sample) # 留意哪一步训练过程会计算weight，按道理是会增加一列weight字段
            outcome = data.get_outcomes(sample) # 返回np.array类型
            treatment = data.get_treatments(sample) # 返回np.array类型
            Y_centered[i] = outcome
            W_centered[i] = treatment
            weights[i] = weight
            Y_mean += weight * outcome # 对于np.array类型来说，该操作是成立的
            W_mean += weight * treatment
            sum_weight += weight
        
        Y_mean /= sum_weight
        W_mean /= sum_weight

        Y_centered -= Y_mean  # 对于np.array类型来说，该操作是成立的
        W_centered -= W_mean

        if abs(sum_weight)<= 1e-16:
            return True
        
        WW_bar = W_centered.T * np.diag(weights) * W_centered

        if abs(np.linalg.det(WW_bar)-0.0) <= 1.0e-10:
            return True
        
        A_p_inv = np.linalg.inv(WW_bar)

        theta = A_p_inv * W_centered.T * np.diag(weights) * Y_centered
        
        return False
    
    def _find_best_split_value(self
                              ,data
                              ,node
                              ,var
                              ,num_samples
                              ,weight_sum_node
                              ,sum_node
                              ,mean_node_w
                              ,sum_node_small_w
                              ,sum_node_w
                              ,sum_node_w_squared
                              ,min_child_size
                              ,treatments
                              ,best_value
                              ,best_var
                              ,best_decrease
                              ,best_send_missing_left
                              ,responses_by_sample
                              ,samples):
        possible_split_values = []
        sorted_samples = []
        index = data.get_all_values(possible_split_values,sorted_samples,samples[node], var)

        if len(possible_split_values) < 2:
            return
        
        num_splits = len(possible_split_values) - 1

        self._counter[:num_splits] = 0
        self._weight_sums[:num_splits] = 0

        self._sums[:num_splits] = 0 # 该操作对np.array成立

        self._num_small_w[:num_splits] = 0
        self._sums_w[:num_splits] = 0
        self._sums_w_squared[:num_splits] = 0
        n_missing = 0
        weight_sum_missing = 0
        sum_missing = np.zeros(response_length)
        sum_w_missing = np.zeros(num_treatments)
        sum_w_squared_missing = np.zero(num_treatments)
        num_small_w_missing = np.zero(num_treatments)

        split_index = 0
        for i in range(num_samples - 1):
            sample = sorted_samples[i]
            next_sample = sorted_samples[i+1]
            sort_index = index[i]
            sample_value = data.get(sample,var)
            sample_weight = data.get_weight(sample) # 又来，这一步有什么用

            sample_weight = 1

            if sample_value is None:
                weight_sum_missing += sample_weight
                sum_missing += sample_weight * responses_by_sample[sample]
                n_missing += 1

                sum_w_missing += sample_weight * treatments[sort_index]
                sum_w_squared_missing += sample_weight * treatments



