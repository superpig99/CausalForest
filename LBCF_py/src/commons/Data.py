### Data类：
### 依赖类：ThirdParty

import numpy as np
import pandas as pd

class Data:
# public:
    # ----------Data初始化--------------------
    def __init__(self,
                data,
                num_rows,
                num_cols):
        self._data = data # 数据
        self._num_rows = num_rows # 数据行数
        self._num_cols = num_cols # 字段个数
        self._disallowed_split_variables = []
        return

    # 和init合并
    # @classmethod
    # def get_data_vector(cls, data, num_rows, num_cols):
    #     return cls(data, num_rows, num_cols)
    
    # 配合load_data的输出
    @classmethod
    def get_data_pair(cls, data_pair):
        return cls(data_pair[0], data_pair[1][0], data_pair[1][1])
    # ----------data初始化完成-------------------
    
    def set_outcome_index(self,index): # c++存在两种写法，可合并
        if type(index) == int: # 这个地方其实有漏洞，只处理了int型
            index = [index]
        self._outcome_index = index
        self._disallowed_split_variables += index

    def set_treatment_index(self,index): # c++存在两种写法，可合并
        if type(index) == int: # 这个地方其实有漏洞，只处理了int型
            index = [index]
        self._treatment_index = index
        self._disallowed_split_variables += index

    def set_instrument_index(self,index):
        self._instrument_index = index # 注意，这里的index是int型
        self._disallowed_split_variables.append(index)

    def set_weight_index(self,index):
        self._weight_index = index # 注意，这里的index是int型
        self._disallowed_split_variables.append(index)

    def set_causal_survival_numerator_index(self,index): # numerator：分子
        self._causal_survival_numerator_index = index # 注意，这里的index是int型
        self._disallowed_split_variables.append(index)

    def set_causal_survival_denominator_index(self,index): # denominator：分母
        self._causal_survival_denominator_index = index # 注意，这里的index是int型
        self._disallowed_split_variables.append(index)

    def set_censor_index(self,index):
        self._censor_index = index # 注意，这里的index是int型
        self._disallowed_split_variables.append(index)

    def get_all_values(self,all_values,sorted_samples,samples,var):
        '''
        函数说明：
        该函数的目的是得到并返回all_values，而all_values是用于分裂的所有样本；
        sorted_samples是对all_values排序（升序）之后的结果
        参数说明：
        all_values存储用于分裂的样本
        sorted_samples存储排序好的用户分裂的样本
        samples是传进来的 用于分裂的样本的所在行【index
        var指示用户分裂的列/字段/特征
        '''
        # 一次性获取samples所对应的所有数据，但注意数据类型的转变
        if len(samples)==0:
            raise ValueError('No data for splitting!')
        elif len(samples)==1:
            all_values = self.get(samples,var)
        else:
            all_values = self.get(samples,var).values # 这种情形下，all_values是np.array类型数据

        # index 但是这里没有办法处理空值
        index = np.argsort(all_values) # 得到all_values的argsort
        all_values = np.sort(all_values) # 对all_values排序

        # 生成sorted_values
        sorted_samples = [samples[i] for i in index]

        # 还差一步去除空值

        # all_values去重
        all_values = np.unique(all_values) # 不支持None，得先去除空值

        return index

    def get_num_cols(self):
        return self._num_cols

    def get_num_rows(self):
        return self._num_rows

    def get_num_outcomes(self):
        return len(self._outcome_index)

    def get_num_treatments(self):
        return len(self._treatment_index)

    def get_disallowed_split_variables(self):
        return self._disallowed_split_variables

    ## inline
    def get_outcome(self,row):
        # 适用于只有一列outcome的情形
        return self.get(row,self._outcome_index[0])

    def get_outcomes(self,row):
        # 适用于有多列outcome的情形
        return self.get(row,self._outcome_index).values

    def get_treatment(self,row):
        # 适用于只有一列treatment的情形
        return self.get(row,self._treatment_index[0])

    def get_treatments(self,row):
        # 适用于有多列treatment的情形
        return self.get(row,self._treatment_index).values # 得检验返回的values的维度

    def get_instrument(self,row):
        return self.get(row,self._instrument_index)

    def get_weight(self,row):
        return self.get(row,self._weight_index)

    def get_causal_survival_numerator(self,row):
        return self.get(row,self._causal_survival_numerator_index)

    def get_causal_survival_denominator(self,row):
        return self.get(row,self._causal_survival_denominator_index)

    def is_failure(self,row):
        return self.get(row,self._censor_index) > 0.0

    def get(self,row,col): # cpp里的data是按列存储的
        return self._data.iloc[row,col] # 这里是按pandas来写的
        # 按照这种写法，row和col可以是list类型，一次性取出多个数据