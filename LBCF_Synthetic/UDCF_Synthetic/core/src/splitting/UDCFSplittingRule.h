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

#ifndef GRF_UDCFSPLITTINGRULE_H
#define GRF_UDCFSPLITTINGRULE_H

#include "commons/Data.h"
#include "splitting/SplittingRule.h"

namespace grf {


class UDCFSplittingRule final: public SplittingRule {
public:
  UDCFSplittingRule(size_t max_num_unique_values,
                           uint min_node_size,
                           double alpha,
                           double imbalance_penalty,
                           size_t response_length,
                           size_t num_treatments);

  ~UDCFSplittingRule();

  bool find_best_split(const Data& data,
                       size_t node,
                       const std::vector<size_t>& possible_split_vars,
                       const Eigen::ArrayXXd& responses_by_sample,
                       const std::vector<std::vector<size_t>>& samples,
                       std::vector<size_t>& split_vars,
                       std::vector<double>& split_values,
                       std::vector<bool>& send_missing_left);

private:
  bool relabel_child(const std::vector<size_t>& samples,const Data& data, Eigen::MatrixXd &theta);
  void find_best_split_value(const Data& data,
                             size_t node,
                             size_t var,
                             size_t num_samples,
                             double weight_sum_node,
                             const Eigen::ArrayXd& sum_node,
                             const Eigen::ArrayXd& mean_node_w,
                             const Eigen::ArrayXi& sum_node_small_w,
                             const Eigen::ArrayXd& sum_node_w,
                             const Eigen::ArrayXd& sum_node_w_squared,
                             const Eigen::ArrayXd& min_child_size,
                             const Eigen::ArrayXXd& treatments,
                             std::vector<double>& best_value,
                             std::vector<size_t>& best_var,
                             std::vector<double>& best_decrease,
                             std::vector<bool>& best_send_missing_left,
                             const Eigen::ArrayXXd& responses_by_sample,
                             const std::vector<std::vector<size_t>>& samples);

  size_t* counter;
  double* weight_sums;
  Eigen::ArrayXXd sums;
  Eigen::ArrayXXi num_small_w;
  Eigen::ArrayXXd sums_w;
  Eigen::ArrayXXd sums_w_squared;

  uint min_node_size;
  double alpha;
  double imbalance_penalty;
  size_t response_length;
  size_t num_treatments;

  DISALLOW_COPY_AND_ASSIGN(UDCFSplittingRule);
};

} // namespace grf

#endif //GRF_UDCFSPLITTINGRULE_H
