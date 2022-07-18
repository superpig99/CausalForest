
import os
from typing import List
import pandas as pd

from .src.tree.Tree import Tree # not finished

# from .src.prediction.DefaultPredictionStrategy
from .src.commons.utility import *
from .src.commons.Data import Data
from .src.prediction.Prediction import Prediction

from .src.forest.ForestPredictor import ForestPredictor # not finished
from .src.forest.ForestTrainer import ForestTrainer # not finished

# from .src.utilities.FileTestUtilities import FileTestUtilities
from .src.utilities.ForestTestUtilities import ForestTestUtilities

from .src.forest.ForestTrainers import * # not finished
from .src.forest.ForestPredictors import * # not finished


def update_predictions_file(file_name:str,predictions:List[Prediction]):
    # 还没搞清楚Prediction类的构造，但不妨碍该函数的进行
    df_pred = pd.DataFrame(predictions) # columns暂不确定
    df_pred.tocsv(file_name)
    print("success! predictions dump to " + file_name)


def main(file_to_train:str,file_to_test:str,file_to_save:str,outcome_index:List[int],treatment_index:List[int]):
    print("Current working directory: ",os.getcwd())
    ### 从文件读取train data【也提供了从pyspark读取数据的方式，到时候按需更改
    train_data_vec = load_data(file_to_train) # load_data的返回值是[data,[row_num,col_num]]
    data_to_train = Data.get_data_pair(train_data_vec) # data_to_train是Data类实例
    # data_to_train = Data(data_vec[0],data_vec[1][0],data_vec[1][1]) # 这个写法也ok
    data_to_train.set_outcome_index(outcome_index)
    data_to_train.set_treatment_index(treatment_index)

    ### 从文件读取test data
    test_data_vec = load_data(file_to_test)
    data_to_test = Data.get_data_pair(test_data_vec)
    data_to_test.set_outcome_index(outcome_index)
    data_to_test.set_treatment_index(treatment_index)

    num_treatments = 1 if type(treatment_index) == int else len(treatment_index)
    num_outcomes = 1 if type(outcome_index) == int else len(outcome_index)

    trainer = udcf_trainer(num_treatments,num_outcomes,True) # trainer是ForestTrainer的实例
    options = ForestTestUtilities.default_options(True,1) # options是ForestOptions的实例，在ForestTestUtilities里进行调参，这里采用了诚实分裂
    forest = trainer.train(data_to_train,options) # forest是Forest类的实例
    predictor = udcf_predictor(1,num_treatments,num_outcomes) # predictor是ForestPredictor类的实例
    predictions = predictor.predict(forest,data_to_train,data_to_test,False) # predictions是向量，其元素是Prediction类的实例
    ### 也许还可以加一些其他操作？ATE、CATE之类的
    update_predictions_file(file_to_save,predictions)

if __name__ == '__init__':
    file_to_train = ''
    file_to_test = ''
    file_to_save = ''
    outcome_index = []
    treatment_index = []
    main(file_to_train,file_to_test,file_to_save,outcome_index,treatment_index)