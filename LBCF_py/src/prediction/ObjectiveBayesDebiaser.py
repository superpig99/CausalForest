
import numpy as np
import math

class ObjectiveBayesDebiaser:
    def __init__(self):
        self._ONE_over_SQRT_TWO_PI = 0.3989422804
        self._ONE_over_SQRT_TWO = 0.70710678118
    
    def debias(self,var_between,group_noise,num_good_groups):
        initial_estimate = var_between - group_noise
        initial_se = max(var_between,group_noise) * (2.0 / num_good_groups)**0.5
        if abs(initial_se) <= 1.0e-10:
            return 0.0
        
        ratio = initial_estimate / initial_se

        numerator = np.exp(-ratio*ratio/2) * self._ONE_over_SQRT_TWO_PI

        denominator = 0.5 * math.erfc(-ratio * self._ONE_over_SQRT_TWO)

        bayes_correction = initial_se * numerator / denominator
        return initial_estimate + bayes_correction