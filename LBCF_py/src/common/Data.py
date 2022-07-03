### Data类：
### 依赖类：ThirdParty

class Data:
# public:
    def __init__(self,
                data_ptr,
                num_rows,
                num_cols) -> None:
        pass

    @classmethod
    def get_data_vector(cls, data, num_rows, num_cols):
        return cls(data, num_rows, num_cols) # 未写完！！！
    
    @classmethod
    def get_data_pair(cls, data):
        return cls() # 未写完！！！
    
    def set_outcome_index(self,index): # c++存在两种写法，可合并
        pass

    def set_treatment_index(self,index): # c++存在两种写法，可合并
        pass

    def set_instrument_index(self,index):
        pass

    def set_weight_index(self,index):
        pass

    def set_causal_survival_numerator_index(self,index):
        pass

    def set_causal_survival_denominator_index(self,index):
        pass

    def set_censor_index(self,index):
        pass

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