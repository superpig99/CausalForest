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
#include <ctime>
#include <future>
#include <stdexcept>
#include <iostream>

#include "commons/utility.h"
#include "ForestTrainer.h"
#include "random/random.hpp"


namespace grf {

ForestTrainer::ForestTrainer(std::unique_ptr<RelabelingStrategy> relabeling_strategy,
                             std::unique_ptr<SplittingRuleFactory> splitting_rule_factory,
                             std::unique_ptr<OptimizedPredictionStrategy> prediction_strategy) :
    tree_trainer(std::move(relabeling_strategy), //这里是调用了tree_trainer的构造函数
                 std::move(splitting_rule_factory),
                 std::move(prediction_strategy)) {}

Forest ForestTrainer::train(const Data& data, const ForestOptions& options) const {
  std::vector<std::unique_ptr<Tree>> trees = train_trees(data, options); //train_trees是ForestTrainer的私有成员函数；

  size_t num_variables = data.get_num_cols() - data.get_disallowed_split_variables().size();
  //std::cout << "data.get_num_cols()=" << data.get_num_cols() << std::endl;
  //std::cout << "data.get_disallowed_split_variables().size()=" << data.get_disallowed_split_variables().size() << std::endl;
  size_t ci_group_size = options.get_ci_group_size();
  return Forest(trees, num_variables, ci_group_size);
}

// train_trees函数的定义：
std::vector<std::unique_ptr<Tree>> ForestTrainer::train_trees(const Data& data,
                                                              const ForestOptions& options) const {
  size_t num_samples = data.get_num_rows();
  uint num_trees = options.get_num_trees();

  // Ensure that the sample fraction is not too small and honesty fraction is not too extreme.
  // 判断sample分割是否合理
  const TreeOptions& tree_options = options.get_tree_options();
  bool honesty = tree_options.get_honesty();
  double honesty_fraction = tree_options.get_honesty_fraction();
  //std::cout << "options.get_sample_fraction()=" << options.get_sample_fraction() << std::endl; 
  if ((size_t) num_samples * options.get_sample_fraction() < 1) {
    throw std::runtime_error("The sample fraction is too small, as no observations will be sampled.");
  } else if (honesty && ((size_t) num_samples * options.get_sample_fraction() * honesty_fraction < 1
             || (size_t) num_samples * options.get_sample_fraction() * (1-honesty_fraction) < 1)) {
    throw std::runtime_error("The honesty fraction is too close to 1 or 0, as no observations will be sampled.");
  }
  //----------------------------------------------------------------------
  
  //为什么要把树分成若干group？？
  uint num_groups = (uint) num_trees / options.get_ci_group_size();

  //split_sequence的作用是将thread_ranges进行赋值
  std::vector<uint> thread_ranges;
  split_sequence(thread_ranges, 0, num_groups - 1, options.get_num_threads());
  
  //回调函数，在split_sequence执行完成之后进行
  std::vector<std::future<std::vector<std::unique_ptr<Tree>>>> futures;
  futures.reserve(thread_ranges.size());
  //-------------------------------------
  //先定义trees，等到train_batch训练好之后，会汇总到trees下
  std::vector<std::unique_ptr<Tree>> trees;
  trees.reserve(num_trees);

  // thread_ranges是split_sequence函数运行后的结果，定义了每个线程上tree的数量
  for (uint i = 0; i < thread_ranges.size() - 1; ++i) {
    size_t start_index = thread_ranges[i];
    size_t num_trees_batch = thread_ranges[i + 1] - start_index; //每个线程上tree的数量

    futures.push_back(std::async(std::launch::async, // 启动一个新的线程调用Fn
                                 &ForestTrainer::train_batch, //执行train_batch这个函数
                                 this, //this是指当前的实例自身，表明是当前实例在调用train_batch
                                 start_index,//以下全都是是train_batch的参数，
                                 num_trees_batch,
                                 std::ref(data),
                                 options));
  }
  //-----------------------------------------
  //将训练好的tree都放到trees里
  for (auto& future : futures) {
    std::vector<std::unique_ptr<Tree>> thread_trees = future.get(); //从futures中取train_batch运行后的结果
    trees.insert(trees.end(),
                 std::make_move_iterator(thread_trees.begin()),
                 std::make_move_iterator(thread_trees.end())); //插入到trees的末尾
  }

  return trees;
}
//-------------------------------------------------------
// train_batch
std::vector<std::unique_ptr<Tree>> ForestTrainer::train_batch(
    size_t start,
    size_t num_trees,
    const Data& data,
    const ForestOptions& options) const {
  size_t ci_group_size = options.get_ci_group_size();
  
  //随机数生成器
  std::mt19937_64 random_number_generator(options.get_random_seed() + start);
  nonstd::uniform_int_distribution<uint> udist; //均匀分布
  std::vector<std::unique_ptr<Tree>> trees; //先声明train_batch的返回值
  trees.reserve(num_trees * ci_group_size); //申请大小

  // 以下是构建num_trees棵树的过程
  for (size_t i = 0; i < num_trees; i++) {
    uint tree_seed = udist(random_number_generator); //生成满足均匀分布的随机数
    RandomSampler sampler(tree_seed, options.get_sampling_options());//定义了RandomSampler类的实例，等价写法是RandomSampler sampler=RandomSampler(tree_seed, options.get_sampling_options());
    //以下是分情况进行训练，重点就是 train_tree 和 train_ci_group
    if (ci_group_size == 1) {
      std::unique_ptr<Tree> tree = train_tree(data, sampler, options);
      trees.push_back(std::move(tree));
    } else {
      std::vector<std::unique_ptr<Tree>> group = train_ci_group(data, sampler, options);
      trees.insert(trees.end(),
          std::make_move_iterator(group.begin()),
          std::make_move_iterator(group.end()));
    }
  }
  return trees;
}
//-----------------------------------------------
// 构建一棵树
std::unique_ptr<Tree> ForestTrainer::train_tree(const Data& data,
                                                RandomSampler& sampler,
                                                const ForestOptions& options) const {
  std::vector<size_t> clusters;
  //sample_clusters是随机选取部分数据，赋值到clusters变量
  sampler.sample_clusters(data.get_num_rows(), options.get_sample_fraction(), clusters);
  //std::cout << "ForestTrainer.cpp 132 clusters.size()=" << clusters.size() << std::endl;
  // 所以tree的训练是在TreeTrainer类下定义的
  return tree_trainer.train(data, sampler, clusters, options.get_tree_options()); //由于train_tree是ForestTrainer的private成员函数，所以可以调用ForestTrainer类的成员函数
}

std::vector<std::unique_ptr<Tree>> ForestTrainer::train_ci_group(const Data& data,
                                                                 RandomSampler& sampler,
                                                                 const ForestOptions& options) const {
  std::vector<std::unique_ptr<Tree>> trees;

  std::vector<size_t> clusters;
  sampler.sample_clusters(data.get_num_rows(), 0.5, clusters);

  double sample_fraction = options.get_sample_fraction();
  for (size_t i = 0; i < options.get_ci_group_size(); ++i) {
    std::vector<size_t> cluster_subsample;
    sampler.subsample(clusters, sample_fraction * 2, cluster_subsample);

    std::unique_ptr<Tree> tree = tree_trainer.train(data, sampler, cluster_subsample, options.get_tree_options());
    trees.push_back(std::move(tree));
  }
  return trees;
}

} // namespace grf
