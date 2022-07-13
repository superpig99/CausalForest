
#include "commons/utility.h"
#include "relabeling/UDCFRelabelingStrategy.h"

namespace grf {

UDCFRelabelingStrategy::UDCFRelabelingStrategy(size_t response_length) :
  response_length(response_length) {}

// relabel实现！！计算theta、Ap和rho
bool UDCFRelabelingStrategy::relabel(
    const std::vector<size_t>& samples,
    const Data& data,
    Eigen::ArrayXXd& responses_by_sample) const {

  // Prepare the relevant averages.
  size_t num_samples = samples.size();
  size_t num_treatments = data.get_num_treatments();
  size_t num_outcomes = data.get_num_outcomes();
  
  if (num_samples <= num_treatments) {
    return true;
  }

  Eigen::MatrixXd Y_centered = Eigen::MatrixXd(num_samples, num_outcomes); //定义矩阵，Y的残差
  Eigen::MatrixXd W_centered = Eigen::MatrixXd(num_samples, num_treatments); //定义矩阵，W的残差
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
    Y_mean += weight * outcome; // weight是权重alpha
    W_mean += weight * treatment;
    sum_weight += weight;
  }
  Y_mean /= sum_weight;
  W_mean /= sum_weight;
  
  Y_centered.rowwise() -= Y_mean.transpose(); // 得到残差
  W_centered.rowwise() -= W_mean.transpose();
  
  if (std::abs(sum_weight) <= 1e-16) {
    return true;
  }

  
  Eigen::MatrixXd WW_bar = W_centered.transpose() * weights.asDiagonal() * W_centered; // [num_treatments X num_treatments]
  
  if (equal_doubles(WW_bar.determinant(), 0.0, 1.0e-10)) {
    return true;
  }

  Eigen::MatrixXd A_p_inv = WW_bar.inverse();
  Eigen::MatrixXd beta = A_p_inv * W_centered.transpose() * weights.asDiagonal() * Y_centered; // [num_treatments X num_outcomes]，这里beta就是theta_p，父节点的最优解

  Eigen::MatrixXd rho_weight = W_centered * A_p_inv.transpose(); // [num_samples X num_treatments]，对应于LBCF论文算法1里的Q

  Eigen::MatrixXd residual = Y_centered - W_centered * beta; // [num_samples X num_outcomes]，对应于LBCF论文算法1里的R

  
  for (size_t i = 0; i < num_samples; i++) {
    size_t sample = samples[i];
    size_t j = 0;
    for (size_t outcome = 0; outcome < num_outcomes; outcome++) {
      for (size_t treatment = 0; treatment < num_treatments; treatment++) {
        responses_by_sample(sample, j) = rho_weight(i, treatment) * residual(i, outcome); // rho_ij
        j++;
      }
    }
  }
  return false;
}
//======================================================

size_t UDCFRelabelingStrategy::get_response_length() const {
  return response_length;
}

} // namespace grf
