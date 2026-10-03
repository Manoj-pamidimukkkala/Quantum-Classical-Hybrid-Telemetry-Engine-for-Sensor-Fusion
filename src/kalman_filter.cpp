#include "kalman_filter.hpp"
#include <stdexcept>

namespace telemetry {

void ExtendedKalmanFilter::process_batch(
    std::span<const double> measurements,
    std::span<double> filtered_output
) {
    if (measurements.size() != filtered_output.size()) {
        throw std::invalid_argument("Input and output buffer sizes must match.");
    }

    size_t n = measurements.size();
    for (size_t i = 0; i < n; ++i) {
        p_ = p_ + q_;
        double k = p_ / (p_ + r_);
        x_ = x_ + k * (measurements[i] - x_);
        p_ = (1.0 - k) * p_;
        filtered_output[i] = x_;
    }
}

} // namespace telemetry
