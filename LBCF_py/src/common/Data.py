### Data类：
### 依赖类：ThirdParty

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
        return cls(data_pair[0], data_pair[0][0], data_pair[0][1])
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
        pass

    def get_num_cols(self):
        pass

    def get_num_rows(self):
        pass

    def get_num_outcomes(self):
        pass

    def get_num_treatments(self):
        pass

    def get_disallowed_split_variables(self):
        pass

    ## inline
    def get_outcome(self,row):
        pass

    def get_outcomes(self,row):
        pass

    def get_treatment(self,row):
        pass

    def get_treatments(self,row):
        pass

    def get_instrument(self,row):
        pass

    def get_weight(self,row):
        pass

    def get_causal_survival_numerator(self,row):
        pass

    def get_causal_survival_denominator(self,row):
        pass

    def is_failure(self,row):
        pass

    def get(self,row,col):
        pass