# UDCFRelabelingStrategy类：
# 依赖于：Data

import numpy as np
from ..commons.Data import Data


class UDCFRelabelingStrategy:
# public:
    def __init__(self,response_length):
        self._response_length = response_length
    
    def relabel(self,samples,data,responses_by_sample): # responses_by_sample得是np.array类型
        num_samples = len(samples)
        num_treatments = data.get_num_treatments()
        num_outcomes = data.get_num_outcomes

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

        beta = A_p_inv * W_centered.T * np.diag(weights) * Y_centered

        rho_weight = W_centered * A_p_inv.T

        residual = Y_centered - W_centered*beta

        for i in range(num_samples): # 可以转成矩阵操作么？？不然运行起来会很慢
            sample = samples[i]
            j = 0
            for outcome in range(num_outcomes):
                for treatment in range(num_treatments):
                    responses_by_sample[sample,j] = rho_weight[i,treatment] * residual[i,outcome]
                    j++
        
        return False

    
    def get_response_length(self):
        return self._response_length

# private:是成员变量
