# 依赖类：ForestOptions、UDCFPredictionStrategy、ForestPredictor

from .ForestOptions import ForestOptions
from .ForestPredictor import ForestPredictor
from ..prediction.UDCFPredictionStrategy import UDCFPredictionStrategy

def instrumental_predictor(num_threads):
    pass

def udcf_predictor(num_threads,num_treatments,num_outcomes):
    num_threads = ForestOptions.validate_num_threads(num_threads)
    prediction_strategy = UDCFPredictionStrategy(num_treatments,num_outcomes)

    return ForestPredictor(num_threads,prediction_strategy)

def quantile_predictor(num_threads,quantiles):
    pass

def probability_predictor(num_threads,num_classes):
    pass

def regression_predictor(num_threads):
    pass

def multi_regression_predictor(num_threads,num_outcomes):
    pass

def ll_regression_predictor(num_threads,lambdas,weight_penalty,linear_correction_variables):
    pass

def ll_causal_predictor(num_threads,lambdas,weight_penalty,linear_correction_variables):
    pass

def survival_predictor(num_threads,num_failures,prediction_type):
    pass

def causal_survival_predictor(num_threads):
    pass