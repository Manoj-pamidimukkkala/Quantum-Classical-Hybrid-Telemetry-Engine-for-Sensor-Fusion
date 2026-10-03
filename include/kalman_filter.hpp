#pragma once

#include <cstdint>
#include <cmath>
#include <span>
#include <vector>

namespace telemetry {

struct StateEstimate {
    uint64_t timestamp_ns;
    double estimated_value;
    double covariance;
    uint64_t processing_latency_ns;
};

class ExtendedKalmanFilter {
public:
    ExtendedKalmanFilter(double process_noise, double measurement_noise, double initial_state = 0.0)
        : q_(process_noise), r_(measurement_noise), x_(initial_state), p_(1.0) {}

    // Process a single scalar sensor packet in real time
    StateEstimate update(uint64_t timestamp_ns, double measurement) {
        // Predict step
        p_ = p_ + q_;

        // Update step (Kalman Gain)
        double k = p_ / (p_ + r_);
        x_ = x_ + k * (measurement - x_);
        p_ = (1.0 - k) * p_;

        return StateEstimate{
            .timestamp_ns = timestamp_ns,
            .estimated_value = x_,
            .covariance = p_,
            .processing_latency_ns = 0
        };
    }

    // SIMD vector processing pass over array spans
    void process_batch(
        std::span<const double> measurements,
        std::span<double> filtered_output
    );

private:
    double q_; // Process noise covariance
    double r_; // Measurement noise covariance
    double x_; // Estimated state
    double p_; // Estimate error covariance
};

} // namespace telemetry
