# 依赖类：ForestTrainer、UDCFRelabelingStrategy、UDCFSplittingRuleFactory、UDCFPredictionStrategy
# 也许依赖的类：MultiRegressionSplittingRuleFactory


from .ForestTrainer import ForestTrainer
from ..relabeling.UDCFRelabelingStrategy import UDCFRelabelingStrategy
from ..splitting.factory.UDCFSplittingRuleFactory import UDCFSplittingRuleFactory
from ..prediction.UDCFPredictionStrategy import UDCFPredictionStrategy

def instrumental_trainer(reduced_form_weight,stabilize_splits):
    pass

def udcf_trainer(num_treatments,num_outcomes,stabilize_splits):
    response_length = num_treatments * num_outcomes

    relabeling_strategy = UDCFRelabelingStrategy(response_length)
    splitting_rule_factory = UDCFSplittingRuleFactory(response_length,num_treatments) if stabilize_splits else MultiRegressionSplittingRuleFactory(response_length)
    prediction_strategy = UDCFPredictionStrategy(num_treatments,num_outcomes)

    return ForestTrainer(relabeling_strategy,splitting_rule_factory,prediction_strategy)

def quantile_trainer(quantiles):
    pass

def probability_trainer(num_classes):
    pass

def regression_trainer():
    pass

def multi_regression_trainer(num_outcomes):
    pass

def ll_regression_trainer(split_lambda,weight_penalty,overall_beta,ll_split_cutoff,ll_split_variables):
    pass

def survival_trainer():
    pass

def causal_survival_trainer(stabilize_splits):
    pass