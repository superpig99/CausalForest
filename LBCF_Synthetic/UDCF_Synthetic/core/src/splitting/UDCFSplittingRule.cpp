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
#include <iostream>
#include "commons/utility.h"
#include "UDCFSplittingRule.h"
#include <math.h>
#include <algorithm>

namespace grf {

UDCFSplittingRule::UDCFSplittingRule(size_t max_num_unique_values,
                                                   uint min_node_size,
                                                   double alpha,
                                                   double imbalance_penalty,
                                                   size_t response_length,
                                                   size_t num_treatments):
    min_node_size(min_node_size),
    alpha(alpha),
    imbalance_penalty(imbalance_penalty),
    response_length(response_length),
    num_treatments(num_treatments) {
  this->counter = new size_t[max_num_unique_values];
  this->weight_sums = new double[max_num_unique_values];
  this->sums = Eigen::ArrayXXd(max_num_unique_values, response_length);
  this->num_small_w = Eigen::ArrayXXi(max_num_unique_values, num_treatments);
  this->sums_w = Eigen::ArrayXXd(max_num_unique_values, num_treatments);
  this->sums_w_squared = Eigen::ArrayXXd(max_num_unique_values, num_treatments);
}

UDCFSplittingRule::~UDCFSplittingRule() {
  if (counter != nullptr) {
    delete[] counter;
  }
  if (weight_sums != nullptr) {
    delete[] weight_sums;
  }
}

bool UDCFSplittingRule::relabel_child(const std::vector<size_t>& samples,const Data& data, Eigen::MatrixXd &theta)
{
  // Prepare the relevant averages.
  size_t num_samples = samples.size();
  size_t num_treatments = data.get_num_treatments();
  size_t num_outcomes = data.get_num_outcomes();
  if (num_samples <= num_treatments) {
    return true;
  }

  Eigen::MatrixXd Y_centered = Eigen::MatrixXd(num_samples, num_outcomes);
  Eigen::MatrixXd W_centered = Eigen::MatrixXd(num_samples, num_treatments);
  Eigen::VectorXd weights = Eigen::VectorXd(num_samples);
  Eigen::VectorXd Y_mean = Eigen::VectorXd::Zero(num_outcomes);
  Eigen::VectorXd W_mean = Eigen::VectorXd::Zero(num_treatments);
  double sum_weight = 0;
  for (size_t i = 0; i < num_samples; i++) {
    size_t sample = samples[i];
    double weight = data.get_weight(sample);
    Eigen::VectorXd outcome = data.get_outcomes(sample);
    Eigen::VectorXd treatment = data.get_treatments(sample);
    Y_centered.row(i) = outcome;
    W_centered.row(i) = treatment;
    weights(i) = weight;
    Y_mean += weight * outcome;
    W_mean += weight * treatment;
    sum_weight += weight;
   }
  Y_mean /= sum_weight;
  W_mean /= sum_weight;
  Y_centered.rowwise() -= Y_mean.transpose();
  W_centered.rowwise() -= W_mean.transpose();

  if (std::abs(sum_weight) <= 1e-16) {
    return true;
   }

  Eigen::MatrixXd WW_bar = W_centered.transpose() * weights.asDiagonal() * W_centered; // [num_treatments X num_treatments]
  // Calculate the treatment effect.
  // This condition number check works fine in practice - there may be more robust ways.
  if (equal_doubles(WW_bar.determinant(), 0.0, 1.0e-10)) {
    return true;
  }

  Eigen::MatrixXd A_p_inv = WW_bar.inverse();
  theta = A_p_inv * W_centered.transpose() * weights.asDiagonal() * Y_centered; // [num_treatments X num_outcomes]
  return false;
        
}
    
bool UDCFSplittingRule::find_best_split(const Data& data,
                                               size_t node,
                                               const std::vector<size_t>& possible_split_vars,
                                               const Eigen::ArrayXXd& responses_by_sample,
                                               const std::vector<std::vector<size_t>>& samples,
                                               std::vector<size_t>& split_vars,
                                               std::vector<double>& split_values,
                                               std::vector<bool>& send_missing_left) {
  size_t num_samples = samples[node].size();
  
  double weight_sum_node = 0.0;
  Eigen::ArrayXd sum_node = Eigen::ArrayXd::Zero(response_length);
  Eigen::ArrayXd sum_node_w = Eigen::ArrayXd::Zero(num_treatments);
  Eigen::ArrayXd sum_node_w_squared = Eigen::ArrayXd::Zero(num_treatments);
  //
  
  Eigen::ArrayXXd treatments = Eigen::ArrayXXd(num_samples, num_treatments);
  for (size_t i = 0; i < num_samples; i++) {
    size_t sample = samples[node][i];
    double sample_weight = data.get_weight(sample);
    
    sample_weight = 1;
    weight_sum_node += sample_weight;
    sum_node += sample_weight * responses_by_sample.row(sample);
    
    treatments.row(i) = data.get_treatments(sample);
    
    sum_node_w += sample_weight * treatments.row(i);
    sum_node_w_squared += sample_weight * treatments.row(i).square();
  }
  
 

  Eigen::ArrayXd size_node = sum_node_w_squared - sum_node_w.square() / weight_sum_node;
 
  Eigen::ArrayXd min_child_size = size_node * alpha;
  

  Eigen::ArrayXd mean_w_node = sum_node_w / weight_sum_node;
  
  Eigen::ArrayXi num_node_small_w = Eigen::ArrayXi::Zero(num_treatments);
  
  for (size_t i = 0; i < num_samples; i++) {
    
    num_node_small_w += (treatments.row(i).transpose() < mean_w_node).cast<int>();
  }
  
    
  std::vector<size_t> best_var;
  std::vector<double> best_value;
  std::vector<double> best_decrease;
  std::vector<bool> best_send_missing_left;  
  
  for (auto& var : possible_split_vars) {
    
    find_best_split_value(data, node, var, num_samples, weight_sum_node, sum_node, mean_w_node, num_node_small_w,
                          sum_node_w, sum_node_w_squared, min_child_size, treatments, best_value,
        
                          best_var, best_decrease, best_send_missing_left, responses_by_sample, samples);
    
  }
  
  if (best_decrease.size() == 0) {
      
  
    return true;
  }
  
  std::vector<double> best_decrease_copy(best_decrease);
  size_t num_descrease = best_decrease_copy.size();
  std::sort(best_decrease.rbegin(), best_decrease.rend()); 
  size_t N = std::max(int(num_descrease*0.05),1);
  
  double decrease_threshold = 0;
  for (auto& decrease : best_decrease)
  {
    N--;
    if(N==0)
    {
      decrease_threshold = decrease;
      break;
    }
  }    
  std::vector<double> intra_split_value;
  std::vector<size_t> intra_split_var;
  std::vector<bool> intra_missing_left;  
  for (size_t i = 0; i < num_descrease; i++)
  {
    if(best_decrease_copy[i] >= decrease_threshold)
    {
       intra_split_value.push_back(best_value[i]);
       intra_split_var.push_back(best_var[i]);
       intra_missing_left.push_back(best_send_missing_left[i]);
       //std::cout << "i=" << i << ";best_value[i]=" << best_value[i] << ";best_var[i]"<< best_var[i]<< std::endl;
    }
  }
    
  size_t num_intra = intra_split_value.size();  
  double max_var = 0.0;
  for (size_t i = 0; i < num_intra; i++)
  {
    size_t split_var = intra_split_var[i];
    double split_value = intra_split_value[i];
    bool send_na_left = intra_missing_left[i];  
    std::vector<size_t> samples_left;
    std::vector<size_t> samples_right;  
    for (auto& sample : samples[node]) 
    {
     //std::cout << "TreeTrainer.cpp sample=" << sample << std::endl; 
     double value = data.get(sample, split_var);
    if (
        (value <= split_value) || // ordinary split
        (send_na_left && std::isnan(value)) || // are we sending NaN left
        (std::isnan(split_value) && std::isnan(value)) // are we splitting on NaN, then always send NaNs left
      ) {
      samples_left.push_back(sample);
    } else {
      samples_right.push_back(sample);
    }
   }
   // calculate \theta c_left  and \theta c_right
   Eigen::MatrixXd theta_left;
   Eigen::MatrixXd theta_right;  
    
   if(relabel_child(samples_left, data, theta_left) || relabel_child(samples_right, data, theta_right))
   {
      continue;
   }
  
   std::vector<double> theta_left_vect(theta_left.data(), theta_left.data() + theta_left.rows() * theta_left.cols());
   std::vector<double> theta_right_vect(theta_right.data(), theta_right.data() + theta_right.rows() * theta_right.cols());
   double theta_left_mean = 0.0;
   double theta_right_mean = 0.0;   
   
   for (size_t i = 0; i < num_treatments; i++)
   {
      theta_left_mean += theta_left_vect[i];
      theta_right_mean += theta_right_vect[i];
   }
   theta_left_mean /= num_treatments;
   theta_right_mean /= num_treatments; 
   
   double theta_left_var = 0.0;
   double theta_right_var = 0.0; 
   for (size_t i = 0; i < num_treatments; i++)
   {
      theta_left_var += std::pow(theta_left_vect[i] - theta_left_mean,2);
      theta_right_var += std::pow(theta_right_vect[i] - theta_right_mean,2);
      
   }
   if (theta_left_var + theta_right_var > max_var)
   {
      split_vars[node] = split_var;
      split_values[node] = split_value;
      send_missing_left[node] = send_na_left;   
      max_var = theta_left_var + theta_right_var;
   }
  }
 
  return false;
}


    
void UDCFSplittingRule::find_best_split_value(const Data& data,
                                                     size_t node,
                                                     size_t var,
                                                     size_t num_samples,
                                                     double weight_sum_node,
                                                     const Eigen::ArrayXd& sum_node,
                                                     const Eigen::ArrayXd& mean_node_w,
                                                     const Eigen::ArrayXi& num_node_small_w,
                                                     const Eigen::ArrayXd& sum_node_w,
                                                     const Eigen::ArrayXd& sum_node_w_squared,
                                                     const Eigen::ArrayXd& min_child_size,
                                                     const Eigen::ArrayXXd& treatments,
                                                     std::vector<double>& best_value,
                                                     std::vector<size_t>& best_var,
                                                     std::vector<double>& best_decrease,
                                                     std::vector<bool>& best_send_missing_left,
                                                     const Eigen::ArrayXXd& responses_by_sample,
                                                     const std::vector<std::vector<size_t>>& samples) {
  std::vector<double> possible_split_values;
  std::vector<size_t> sorted_samples;
  std::vector<size_t> index = data.get_all_values(possible_split_values, sorted_samples, samples[node], var);
  
  // Try next variable if all equal for this
  if (possible_split_values.size() < 2) {
    return;
  }

  size_t num_splits = possible_split_values.size() - 1;

  std::fill(counter, counter + num_splits, 0);
  std::fill(weight_sums, weight_sums + num_splits, 0);
  
  sums.topRows(num_splits).setZero();
  
    
  num_small_w.topRows(num_splits).setZero();
  sums_w.topRows(num_splits).setZero();
  sums_w_squared.topRows(num_splits).setZero();
  size_t n_missing = 0;
  double weight_sum_missing = 0;
  Eigen::ArrayXd sum_missing = Eigen::ArrayXd::Zero(response_length);
  Eigen::ArrayXd sum_w_missing = Eigen::ArrayXd::Zero(num_treatments);
  Eigen::ArrayXd sum_w_squared_missing = Eigen::ArrayXd::Zero(num_treatments);
  Eigen::ArrayXi num_small_w_missing = Eigen::ArrayXi::Zero(num_treatments);

  size_t split_index = 0;
  for (size_t i = 0; i < num_samples - 1; i++) {
    size_t sample = sorted_samples[i];
    size_t next_sample = sorted_samples[i + 1];
    size_t sort_index = index[i];
    double sample_value = data.get(sample, var);
    double sample_weight = data.get_weight(sample);
    // add
    sample_weight = 1;

    if (std::isnan(sample_value)) {
      weight_sum_missing += sample_weight;
      sum_missing += sample_weight * responses_by_sample.row(sample);
      ++n_missing;

      sum_w_missing += sample_weight * treatments.row(sort_index);
      sum_w_squared_missing += sample_weight * treatments.row(sort_index).square();
      num_small_w_missing += (treatments.row(sort_index).transpose() < mean_node_w).cast<int>();
    } else {
      weight_sums[split_index] += sample_weight;
      sums.row(split_index) += sample_weight * responses_by_sample.row(sample);
      ++counter[split_index];

      sums_w.row(split_index) += sample_weight * treatments.row(sort_index);
      sums_w_squared.row(split_index) += sample_weight * treatments.row(sort_index).square();
      num_small_w.row(split_index) += (treatments.row(sort_index).transpose() < mean_node_w).cast<int>();
      
    }

    double next_sample_value = data.get(next_sample, var);
    
    if (sample_value != next_sample_value && !std::isnan(next_sample_value)) {
      ++split_index;
    }
  }
  
  size_t n_left = n_missing;
  double weight_sum_left = weight_sum_missing;
  Eigen::Ref<Eigen::ArrayXd> sum_left = sum_missing;
  Eigen::Ref<Eigen::ArrayXd> sum_left_w = sum_w_missing;
  // add
  Eigen::ArrayXd sum_right_w = Eigen::ArrayXd::Zero(num_treatments);
  Eigen::Ref<Eigen::ArrayXd> sum_left_w_squared = sum_w_squared_missing;
  Eigen::Ref<Eigen::ArrayXi> num_left_small_w = num_small_w_missing;
 
  for (bool send_left : {true, false}) {
    if (!send_left) {
      // A normal split with no NaNs, so we can stop early.
      if (n_missing == 0) {
        break;
      }
      
      n_left = 0;
      weight_sum_left = 0;
      sum_left.setZero();
      sum_left_w.setZero();
      sum_left_w_squared.setZero();
      num_left_small_w.setZero();
    }

    for (size_t i = 0; i < num_splits; ++i) {
      // not necessary to evaluate sending right when splitting on NaN.
      if (i == 0 && !send_left) {
        continue;
      }

      n_left += counter[i];
      weight_sum_left += weight_sums[i];
      num_left_small_w += num_small_w.row(i);
      sum_left += sums.row(i);
      sum_left_w += sums_w.row(i);
      sum_left_w_squared += sums_w_squared.row(i);
      
      if ((num_left_small_w < min_node_size).any() || (n_left - num_left_small_w < min_node_size).any()) {
        continue;
      }

      
      size_t n_right = num_samples - n_left;
      
      if ((num_node_small_w - num_left_small_w < min_node_size).any() ||
          (n_right - num_node_small_w + num_left_small_w < min_node_size).any()) {
        break;
      }

      
      if ((sum_left_w_squared - sum_left_w.square() / weight_sum_left < min_child_size).any() ||
          (imbalance_penalty > 0.0 && (sum_left_w_squared - sum_left_w.square() / weight_sum_left == 0).all())) {
        continue;
      }

     
      double weight_sum_right = weight_sum_node - weight_sum_left;
     
      if ((sum_node_w_squared - sum_left_w_squared - (sum_node_w - sum_left_w).square() / weight_sum_right < min_child_size).any() ||
          (imbalance_penalty > 0.0 && (sum_node_w_squared - sum_left_w_squared - (sum_node_w - sum_left_w).square() / weight_sum_right == 0).all())) {
        continue;
      }
  
      double decrease = sum_left.square().sum() / weight_sum_left +
                        (sum_node - sum_left).square().sum() / weight_sum_right;
      
      double penalty_edge = imbalance_penalty * (1.0 / n_left + 1.0 / n_right);
      decrease -= penalty_edge;
     
      
      if (decrease > 0)
      {
          best_value.push_back(possible_split_values[i]);
          best_var.push_back(var);
          best_decrease.push_back(decrease);
          best_send_missing_left.push_back(send_left);         
      }
      
          
     
    }
  }
}

} // namespace grf
