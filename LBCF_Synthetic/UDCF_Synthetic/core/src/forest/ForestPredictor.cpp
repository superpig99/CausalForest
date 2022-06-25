/*-------------------------------------------------------------------------------
  This file is part of generalized random forest (grf).

  grf is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  grf is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with grf. If not, see <http://www.gnu.org/licenses/>.
 #-------------------------------------------------------------------------------*/

#include <stdexcept>

#include "forest/ForestPredictor.h"
#include "prediction/collector/OptimizedPredictionCollector.h"
#include "prediction/collector/DefaultPredictionCollector.h"
#include "commons/utility.h"

namespace grf {

ForestPredictor::ForestPredictor(uint num_threads,
                                 std::unique_ptr<DefaultPredictionStrategy> strategy) :
    tree_traverser(num_threads) {
  this->prediction_collector = std::unique_ptr<PredictionCollector>(
        new DefaultPredictionCollector(std::move(strategy), num_threads));
}

ForestPredictor::ForestPredictor(uint num_threads,
                                 std::unique_ptr<OptimizedPredictionStrategy> strategy) :
    tree_traverser(num_threads) {
  this->prediction_collector = std::unique_ptr<PredictionCollector>(
      new OptimizedPredictionCollector(std::move(strategy), num_threads));
}


std::vector<Prediction> ForestPredictor::predict(const Forest& forest,
                                                 const Data& train_data,
                                                 const Data& data,
                                                 bool estimate_variance) const {
  return predict(forest, train_data, data, estimate_variance, false);
}

std::vector<Prediction> ForestPredictor::predict_oob(const Forest& forest,
                                                     const Data& data,
                                                     bool estimate_variance) const {
  return predict(forest, data, data, estimate_variance, true);
}

std::vector<Prediction> ForestPredictor::predict(const Forest& forest,
                                                 const Data& train_data,
                                                 const Data& data,
                                                 bool estimate_variance,
                                                 bool oob_prediction) const {
  if (estimate_variance && forest.get_ci_group_size() <= 1) {
    throw std::runtime_error("To estimate variance during prediction, the forest must"
       " be trained with ci_group_size greater than 1.");
  }

    
  std::vector<std::vector<size_t>> leaf_nodes_by_tree = tree_traverser.get_leaf_nodes(forest, data, oob_prediction);
  //std::cout <<"leaf_nodes_by_tree total size=" << leaf_nodes_by_tree.size() << std::endl;
  /*  
  for (int i = 0; i < leaf_nodes_by_tree.size(); i++)
  {
    std::cout << "i=" << i << ";leaf_nodes_by_tree size=" << leaf_nodes_by_tree[i].size() << std::endl;
    for (int j = 0; j < leaf_nodes_by_tree[i].size(); j++)
    {
       if(j < 990)
       {
           continue;
       }
       std::cout << "node=" << j << ";every node is =" << leaf_nodes_by_tree[i][j] << std::endl;
       
    }
  }
  */
  std::vector<std::vector<bool>> trees_by_sample = tree_traverser.get_valid_trees_by_sample(forest, data, oob_prediction);
  //std::cout <<"trees_by_sample total size=" << trees_by_sample.size() << std::endl;
  /*
  for (int i = 0; i < trees_by_sample.size(); i++)
  {
    if(i < 990)
    {
      continue;
    }
    std::cout << "i=" << i << ";trees_by_sample size=" << trees_by_sample[i].size() << std::endl;
  }
  */
  return prediction_collector->collect_predictions(forest, train_data, data,
      leaf_nodes_by_tree, trees_by_sample,
      estimate_variance, oob_prediction);
}

} // namespace grf
