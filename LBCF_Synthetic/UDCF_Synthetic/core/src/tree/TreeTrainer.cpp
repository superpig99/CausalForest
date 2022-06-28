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

#include <algorithm>
#include <memory>

#include "commons/Data.h"
#include "tree/TreeTrainer.h"

namespace grf {
//TreeTrainer的构造函数
TreeTrainer::TreeTrainer(std::unique_ptr<RelabelingStrategy> relabeling_strategy,
                         std::unique_ptr<SplittingRuleFactory> splitting_rule_factory,
                         std::unique_ptr<OptimizedPredictionStrategy> prediction_strategy) :
    relabeling_strategy(std::move(relabeling_strategy)),
    splitting_rule_factory(std::move(splitting_rule_factory)),
    prediction_strategy(std::move(prediction_strategy)) {}

//TreeTrainer的成员函数--train
std::unique_ptr<Tree> TreeTrainer::train(const Data& data,
                                         RandomSampler& sampler,
                                         const std::vector<size_t>& clusters,
                                         const TreeOptions& options) const {
  std::vector<std::vector<size_t>> child_nodes;
  std::vector<std::vector<size_t>> nodes; // 父节点
  std::vector<size_t> split_vars;
  std::vector<double> split_values;
  std::vector<bool> send_missing_left;

  child_nodes.emplace_back(); //append空值，使得{}变成{{}}
  child_nodes.emplace_back(); //两次该操作，则child_nodes从{}变为{{},{}}
  create_empty_node(child_nodes, nodes, split_vars, split_values, send_missing_left);
  //经过该函数之后，各值变为child_nodes = {{0},{0}}, nodes={0}, split_vars={0},split_values={0},send_missing_left={True}

  std::vector<size_t> new_leaf_samples;
  
  // 先构建父节点nodes，直接将部分数据给到nodes，且这部分数据将用于后续的节点分裂
  if (options.get_honesty()) {
    std::vector<size_t> tree_growing_clusters; //如果是honest分裂，则cluster还得区分tree_growing_cluster和new_leaf_cluster，前者用于分裂节点，后者用于评估结果
    std::vector<size_t> new_leaf_clusters;
    sampler.subsample(clusters, options.get_honesty_fraction(), tree_growing_clusters, new_leaf_clusters); //subsample实现了tree_growing_cluster和new_leaf_cluster的划分

    sampler.sample_from_clusters(tree_growing_clusters, nodes[0]); //从clusters中将数据给到nodes[0]
    sampler.sample_from_clusters(new_leaf_clusters, new_leaf_samples);
  } else {
    //std::cout << "TreeTrainer.cpp not honesty" << std::endl;
    sampler.sample_from_clusters(clusters, nodes[0]);
  }
  /*  
  for(int i = 0; i<clusters.size();i++)
  {
    std::cout << "i=" << i << ";value=" << clusters[i] << std::endl;
  }
  */
  // nodes[0].size() is the number of samples subsampled for this tree.
  
  //splitting_rule_factory是TreeTrainer类的成员变量，是个指针，所以用->来调用方法
  //注意，main函数调用udcf_trainer来创建trainer实例，而udcf_trainer函数指明了splitting_rule_factory指向UDCFRelabelingStrategy
  std::unique_ptr<SplittingRule> splitting_rule = splitting_rule_factory->create(
      nodes[0].size(), options);
  //std::cout << " TreeTrainer.cpp nodes[0].size()" << nodes[0].size() << std::endl;
  size_t num_open_nodes = 1;
  size_t i = 0;
  Eigen::ArrayXXd responses_by_sample(data.get_num_rows(), relabeling_strategy->get_response_length());
  while (num_open_nodes > 0) {
    bool is_leaf_node = split_node(i,
                                   data,
                                   splitting_rule,
                                   sampler,
                                   child_nodes,
                                   nodes,
                                   split_vars,
                                   split_values,
                                   send_missing_left,
                                   responses_by_sample,
                                   options);
    if (is_leaf_node) {
      --num_open_nodes;
    } else {
      nodes[i].clear();
      ++num_open_nodes;
    }
    ++i;
  }

  std::vector<size_t> drawn_samples;
  sampler.get_samples_in_clusters(clusters, drawn_samples);

  std::unique_ptr<Tree> tree(new Tree(0, child_nodes, nodes,
      split_vars, split_values, drawn_samples, send_missing_left, PredictionValues()));

  if (!new_leaf_samples.empty()) {
    repopulate_leaf_nodes(tree, data, new_leaf_samples, options.get_honesty_prune_leaves());
  }

  PredictionValues prediction_values;
  if (prediction_strategy != nullptr) {
    //std::cout << " TreeTrainer.cpp prediction_strategy != nullptr" << std::endl;
    prediction_values = prediction_strategy->precompute_prediction_values(tree->get_leaf_samples(), data);
  }
  tree->set_prediction_values(prediction_values);

  return tree;
}
//----------------TreeTrainer::train函数结束--------------------------

void TreeTrainer::repopulate_leaf_nodes(const std::unique_ptr<Tree>& tree,
                                        const Data& data,
                                        const std::vector<size_t>& leaf_samples,
                                        const bool honesty_prune_leaves) const {
  size_t num_nodes = tree->get_leaf_samples().size();
  std::vector<std::vector<size_t>> new_leaf_nodes(num_nodes);

  std::vector<size_t> leaf_nodes = tree->find_leaf_nodes(data, leaf_samples);

  for (auto& sample : leaf_samples) {
    size_t leaf_node = leaf_nodes[sample];
    new_leaf_nodes[leaf_node].push_back(sample);
  }
  tree->set_leaf_samples(new_leaf_nodes);
  if (honesty_prune_leaves) {
    tree->honesty_prune_leaves();
  }
}

void TreeTrainer::create_split_variable_subset(std::vector<size_t>& result,
                                               RandomSampler& sampler,
                                               const Data& data,
                                               uint mtry) const {

  // Randomly select an mtry for this tree based on the overall setting.
  size_t num_independent_variables = data.get_num_cols() - data.get_disallowed_split_variables().size();
  size_t mtry_sample = sampler.sample_poisson(mtry);
  size_t split_mtry = std::max<size_t>(std::min<size_t>(mtry_sample, num_independent_variables), 1uL);

  sampler.draw(result,
               data.get_num_cols(),
               data.get_disallowed_split_variables(),
               split_mtry);
}

bool TreeTrainer::split_node(size_t node,
                             const Data& data,
                             const std::unique_ptr<SplittingRule>& splitting_rule,
                             RandomSampler& sampler,
                             std::vector<std::vector<size_t>>& child_nodes,
                             std::vector<std::vector<size_t>>& samples,
                             std::vector<size_t>& split_vars,
                             std::vector<double>& split_values,
                             std::vector<bool>& send_missing_left,
                             Eigen::ArrayXXd& responses_by_sample,
                             const TreeOptions& options) const {

  std::vector<size_t> possible_split_vars;
  create_split_variable_subset(possible_split_vars, sampler, data, options.get_mtry());
  
  bool stop = split_node_internal(node,
                                  data,
                                  splitting_rule,
                                  possible_split_vars,
                                  samples,
                                  split_vars,
                                  split_values,
                                  send_missing_left,
                                  responses_by_sample,
                                  options.get_min_node_size());
  if (stop) {
    return true;
  }

  size_t split_var = split_vars[node];
  double split_value = split_values[node];
  bool send_na_left = send_missing_left[node];

  size_t left_child_node = samples.size();
  child_nodes[0][node] = left_child_node;
  create_empty_node(child_nodes, samples, split_vars, split_values, send_missing_left);

  size_t right_child_node = samples.size();
  child_nodes[1][node] = right_child_node;
  create_empty_node(child_nodes, samples, split_vars, split_values, send_missing_left);

  //std::cout << "TreeTrainer.cpp left_child_node=" << left_child_node << std::endl;
  //std::cout << "TreeTrainer.cpp right_child_node=" << right_child_node << std::endl;  
  // For each sample in node, assign to left or right child
  // Ordered: left is <= splitval and right is > splitval
  for (auto& sample : samples[node]) {
     //std::cout << "TreeTrainer.cpp sample=" << sample << std::endl; 
     double value = data.get(sample, split_var);
    if (
        (value <= split_value) || // ordinary split
        (send_na_left && std::isnan(value)) || // are we sending NaN left
        (std::isnan(split_value) && std::isnan(value)) // are we splitting on NaN, then always send NaNs left
      ) {
      samples[left_child_node].push_back(sample);
    } else {
      samples[right_child_node].push_back(sample);
    }
  }

  // No terminal node
  return false;
}

bool TreeTrainer::split_node_internal(size_t node,
                                      const Data& data,
                                      const std::unique_ptr<SplittingRule>& splitting_rule,
                                      const std::vector<size_t>& possible_split_vars,
                                      const std::vector<std::vector<size_t>>& samples,
                                      std::vector<size_t>& split_vars,
                                      std::vector<double>& split_values,
                                      std::vector<bool>& send_missing_left,
                                      Eigen::ArrayXXd& responses_by_sample,
                                      uint min_node_size) const {
  // Check node size, stop if maximum reached
  if (samples[node].size() <= min_node_size) {
    split_values[node] = -1.0;
    return true;
  }

  bool stop = relabeling_strategy->relabel(samples[node], data, responses_by_sample);

  if (stop || splitting_rule->find_best_split(data,
                                              node,
                                              possible_split_vars,
                                              responses_by_sample,
                                              samples,
                                              split_vars,
                                              split_values,
                                              send_missing_left)) {
    split_values[node] = -1.0;
    return true;
  }

  return false;
}

// create_empty_node成员方法
void TreeTrainer::create_empty_node(std::vector<std::vector<size_t>>& child_nodes,
                                    std::vector<std::vector<size_t>>& samples,
                                    std::vector<size_t>& split_vars,
                                    std::vector<double>& split_values,
                                    std::vector<bool>& send_missing_left) const {
  child_nodes[0].push_back(0);
  child_nodes[1].push_back(0);
  samples.emplace_back();
  split_vars.push_back(0);
  split_values.push_back(0);
  send_missing_left.push_back(true);
}
//--------------------------------------
} // namespace grf
