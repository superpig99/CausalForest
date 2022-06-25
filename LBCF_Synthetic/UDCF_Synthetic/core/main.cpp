#include <iostream>


#include <string>

#include <unistd.h>

#include "tree/Tree.h"

#include "prediction/DefaultPredictionStrategy.h"
#include "commons/utility.h"
#include "forest/ForestPredictor.h"
#include "forest/ForestTrainer.h"
#include "utilities/FileTestUtilities.h"
#include "utilities/ForestTestUtilities.h"

#include "forest/ForestTrainers.h"
#include "forest/ForestPredictors.h"
using namespace grf;

void update_predictions_file(const std::string& file_name,
                             const std::vector<Prediction>& predictions) {
  std::vector<std::vector<double>> values;
  values.reserve(predictions.size()); //reverse指定vector能存储的数据个数； size返回vector元素个数
  for (const auto& prediction : predictions) { // 只读取predictions中的元素，ref：https://blog.csdn.net/yiti8689/article/details/108277295
    values.push_back(prediction.get_predictions());
  }
  FileTestUtilities::write_csv_file(file_name, values);
  std::cout << "success! predictions dump to " << file_name << std::endl;
}

int main()
{
    
    char tmp[256];
    getcwd(tmp, 256); //getcwd 方法会将当前工作目录（working directory）的绝对路径复制到参数 tmp 所指的内存空间中，而参数 256 是 tmp 所指的空间大小。
    std::cout << "Current working directory: " << tmp << std::endl;
    // /UDCF/core/build  
    for( int j = 5; j <= 20;j = j + 5 ){ // 针对每一组noise数据进行预测
        auto data_vec = load_data("../../../data/train_data_"+std::to_string(j)+"uw.csv"); //train data
        Data data(data_vec);
        data.set_outcome_index(4);
        data.set_treatment_index({5,6,7});


        auto data_vec2 = load_data("../../../data/test_data_"+std::to_string(j)+"uw.csv"); //test data
        Data data2(data_vec2);
        data2.set_outcome_index(4);
        data2.set_treatment_index({5});
        size_t num_treatments = 3;   

        ForestTrainer trainer = udcf_trainer(num_treatments, 1, true);   
        ForestOptions options = ForestTestUtilities::default_options(true,1);
        Forest forest = trainer.train(data, options);
        ForestPredictor predictor = udcf_predictor(1, num_treatments, 1);  
        std::vector<Prediction> predictions = predictor.predict(forest, data, data2, false);
        update_predictions_file("../../../output/UDCF_uplift_"+std::to_string(j)+"uw.csv", predictions);
    }
    
    return 0;
}
