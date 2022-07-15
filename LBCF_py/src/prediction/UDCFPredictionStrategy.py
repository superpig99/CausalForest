
# 依赖类：PredictionValues、ObjectiveBayesDebiaser

####### 所有矩阵的维度都需要做检查!!!!!!!!!!!!!!!!!!!!!!!!!

import numpy as np

class UDCFPredictionStrategy:
# public:
    def __init__(self,num_treatments,num_outcomes):
        self._num_treatments = num_treatments
        self._num_outcomes = num_outcomes
        self._num_types = num_treatments * (num_treatments + num_outcomes + 1) + num_outcomes + 1
        self._weight_index = 0
        self._Y_index = 1
        self._W_index = self._Y_index + num_outcomes
        self._YW_index = self._W_index + num_treatments
        self._WW_index = self._YW_index + num_treatments *  num_outcomes
        self._bayes_debiaser = ObjectiveBayesDebiaser()
    
    def prediction_length(self):
        return self._num_treatments * self._num_outcomes
    
    def predict(self,average):
        weight_bar = average[self._weight_index]
        Y_bar = ??? # 由于不知道average存储的数据长什么样，这里的赋值初始化无法确定
        W_bar = ???
        YW_bar = ???
        WW_bar = ???

        theta = np.linalg.inv(WW_bar * weight_bar - W_bar * W_bar.T) * (YW_bar * weight_bar - W_bar * Y_bar.T)

        return theta[:self.prediction_length()]
    
    def compute_variance(self,average,leaf_values,ci_group_size):
        if self._num_outcomes > 1:
            raise ValueError("Pointwise variance estimates are only implemented for one outcome.")
        
        weight_bar = average[self._weight_index]
        Y_bar = average[self._Y_index]
        W_bar = ???
        YW_bar = ???
        WW_bar = ???

        theta = np.linalg.inv(WW_bar * weight_bar - W_bar * W_bar.T) * (YW_bar * weight_bar - Y_bar * W_bar)
        main_effect = (Y_bar - theta.T * W_bar) / weight_bar

        k = weight_bar - W_bar.T * np.linalg.inv(WW_bar) * W_bar
        term1 = np.linalg.inv(WW_bar) + 1 / k * np.linalg.inv(WW_bar) * W_bar * W_bar.T * np.linalg.inv(WW_bar)
        term2 = 1 / k * np.linalg.inv(WW_bar) * W_bar

        num_good_groups = 0
        rho_squared = np.zeros(self._num_treatments)
        rho_grouped_squared = np.zeros(self._num_treatments)

        group_rho = np.zeros(self._num_treatments)
        psi_1 = np.zeros(self._num_treatments)
        rho = np.zeros(self._num_treatments)
        for group in range(int(leaf_values.get_num_nodes() / ci_group_size)):
            good_group = True
            for j in range(ci_group_size):
                if leaf_values.empty(group * ci_group_size + j):
                    good_group = False
            
            if not good_group:
                continue
            
            num_good_groups += 1
            group_rho[:] = 0

            for j in range(ci_group_size):
                i = group * ci_group_size + j
                leaf_value = leaf_values.get_values(i)
                leaf_weight = leaf_value[self._weight_index]
                leaf_Y = leaf_value[self._Y_index]
                leaf_W = ???
                leaf_YW = ???
                leaf_WW = ???

                psi_1 = leaf_YW - leaf_WW * theta - leaf_W * main_effect
                psi_2 = leaf_Y - leaf_W.T * theta - leaf_weight * main_effect

                rho = term1 * psi_1 - term2 * psi_2
                rho_squared += rho**2 # 这里需要确认
                group_rho += rho
            
            group_rho /= ci_group_size
            rho_grouped_squared += group_rho**2
        
        var_between = rho_grouped_squared / num_good_groups
        var_total = rho_squared / (num_good_groups * ci_group_size)

        group_noise = (var_total - var_between) / (ci_group_size - 1)

        var_debiased = np.zeros(self._num_treatments)
        for i in range(self._num_treatments):
            var_debiased[i] = self._bayes_debiaser.debias(var_between[i],group_noise[i],num_good_groups)
        
        return var_debiased
    
    def prediction_value_length(self):
        return self._num_types
    
    def precompute_prediction_values(self,leaf_samples,data):
        num_leaves = len(leaf_samples)
        values = np.zeros(num_leaves) # 这里的定义有待确认

        for i in range(len(leaf_samples)):
            num_samples = len(leaf_samples[i])

            if num_samples == 0:
                continue
            
            sum_Y = np.zeros(self._num_outcomes)
            sum_W = np.zeros(self._num_treatments)
            sum_YW = np.zeros((self._num_treatments,self._num_outcomes))
            sum_WW = np.zeros((self._num_treatments,self._num_treatments))
            sum_weight = 0.0
            for sample in leaf_samples[i]:
                weight = data.get_weight(sample)
                outcome = data.get_outcomes(sample)
                treatment = data.get_treatments(sample)
                sum_Y += weight * outcome
                sum_W += weight * treatment
                sum_YW += weight * treatment * outcome.T # 这里有待确认
                sum_WW += weight * treatment * treatment.T
                sum_weight += weight
            
            if abs(sum_weight) <= 1e-16:
                continue
            
            value = values[i] # 指向values[i]

            value.append(sum_weight / num_samples)
            for j in range(self._num_outcomes):
                value.append(sum_Y[j]/num_samples)
            
            for j in range(self._num_treatments):
                value.append(sum_W[j] / num_samples)
            
            for j in range(self._num_treatments * self._num_outcomes):
                value.append(sum_YW[j]/num_samples)
            
            for j in range(self._num_treatments * self._num_treatments):
                value.append(sum_WW[j]/num_samples)

        return PredictionValues(values,num_samples)
    
    def compute_error(self,sample,average,leaf_values,data):
        return [None,None] # ????不确定




# private: 全是成员变量