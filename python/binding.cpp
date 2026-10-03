#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "kalman_filter.hpp"
#include "lockfree_queue.hpp"

namespace py = pybind11;

PYBIND11_MODULE(telemetry_engine_cpp, m) {
    m.doc() = "C++20 High-Throughput Sensor Telemetry Engine with EKF";

    py::class_<telemetry::StateEstimate>(m, "StateEstimate")
        .def_readonly("timestamp_ns", &telemetry::StateEstimate::timestamp_ns)
        .def_readonly("estimated_value", &telemetry::StateEstimate::estimated_value)
        .def_readonly("covariance", &telemetry::StateEstimate::covariance)
        .def_readonly("processing_latency_ns", &telemetry::StateEstimate::processing_latency_ns);

    py::class_<telemetry::ExtendedKalmanFilter>(m, "ExtendedKalmanFilter")
        .def(py::init<double, double, double>(), 
             py::arg("process_noise"), py::arg("measurement_noise"), py::arg("initial_state") = 0.0)
        .def("update", &telemetry::ExtendedKalmanFilter::update)
        .def("process_batch", [](telemetry::ExtendedKalmanFilter& self, std::vector<double> measurements) {
            std::vector<double> output(measurements.size());
            self.process_batch(measurements, output);
            return output;
        });
}
