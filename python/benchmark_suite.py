import time
import numpy as np
import matplotlib.pyplot as plt

# Import native C++ module
import telemetry_engine_cpp

class PurePythonEKF:
    def __init__(self, process_noise, measurement_noise, initial_state=0.0):
        self.q = process_noise
        self.r = measurement_noise
        self.x = initial_state
        self.p = 1.0

    def update(self, measurement):
        self.p += self.q
        k = self.p / (self.p + self.r)
        self.x += k * (measurement - self.x)
        self.p = (1.0 - k) * self.p
        return self.x

def run_benchmarks():
    print("=== Quantum-Classical Hybrid Telemetry Engine Benchmark ===")
    
    # 1. Setup Parameters & Simulated Sensor Noise Stream
    n_samples = 500_000
    process_noise = 1e-5
    measurement_noise = 1e-2
    
    true_signal = np.sin(np.linspace(0, 100, n_samples))
    sensor_noise = np.random.normal(0, np.sqrt(measurement_noise), n_samples)
    raw_stream = true_signal + sensor_noise
    
    print(f"Ingested {n_samples:,} simulated quantum sensor packets.")
    
    # 2. Latency Benchmarking (Python vs C++ Engine)
    py_filter = PurePythonEKF(process_noise, measurement_noise)
    cpp_filter = telemetry_engine_cpp.ExtendedKalmanFilter(process_noise, measurement_noise, 0.0)

    # Measure Python per-packet latency
    py_latencies = []
    t_start = time.perf_counter_ns()
    for val in raw_stream[:10_000]:
        t0 = time.perf_counter_ns()
        _ = py_filter.update(val)
        py_latencies.append((time.perf_counter_ns() - t0) / 1e3) # µs

    # Measure C++ Engine per-packet latency
    cpp_latencies = []
    for i, val in enumerate(raw_stream[:10_000]):
        t0 = time.perf_counter_ns()
        _ = cpp_filter.update(i * 1000, val)
        cpp_latencies.append((time.perf_counter_ns() - t0) / 1e3) # µs

    p95_py = np.percentile(py_latencies, 95)
    p99_py = np.percentile(py_latencies, 99)
    
    p95_cpp = np.percentile(cpp_latencies, 95)
    p99_cpp = np.percentile(cpp_latencies, 99)

    print("\n--- Latency Performance Statistics ---")
    print(f"Pure Python Engine -> p95: {p95_py:.3f} µs | p99: {p99_py:.3f} µs")
    print(f"C++20 Native Engine -> p95: {p95_cpp:.3f} µs | p99: {p99_cpp:.3f} µs")
    print(f"Speedup Factor      -> p95: {p95_py/p95_cpp:.2f}x | p99: {p99_py/p99_cpp:.2f}x")

    # 3. Batch Vector Filtering Evaluation
    t0 = time.perf_counter()
    filtered_cpp = cpp_filter.process_batch(raw_stream)
    batch_time = (time.perf_counter() - t0) * 1e3
    
    throughput = (n_samples / (batch_time / 1000)) / 1e6
    print(f"\nBatch Processing Time for {n_samples:,} samples: {batch_time:.2f} ms ({throughput:.2f} Million samples/sec)")

    # 4. Generate Latency & Signal Reconstruction Plot
    plt.figure(figsize=(12, 5))

    # Signal Reconstruction Subplot
    plt.subplot(1, 2, 1)
    sample_window = 300
    plt.plot(raw_stream[:sample_window], label="Raw Noise Stream", color="gray", alpha=0.5)
    plt.plot(true_signal[:sample_window], label="True Signal", color="blue", linestyle="--")
    plt.plot(filtered_cpp[:sample_window], label="Filtered State (EKF)", color="crimson")
    plt.title("Sensor Noise Filtering & State Estimation")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    # Latency Percentile Histogram Subplot
    plt.subplot(1, 2, 2)
    plt.hist(cpp_latencies, bins=50, color="teal", alpha=0.7, label="C++20 Engine Latency")
    plt.axvline(p95_cpp, color="orange", linestyle="--", label=f"p95 ({p95_cpp:.2f} µs)")
    plt.axvline(p99_cpp, color="red", linestyle=":", label=f"p99 ({p99_cpp:.2f} µs)")
    plt.title("Per-Packet Processing Latency Distribution")
    plt.xlabel("Latency (microseconds)")
    plt.ylabel("Packet Count")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig("telemetry_benchmark_results.png", dpi=300)
    print("Benchmark complete. Results saved to 'telemetry_benchmark_results.png'.")

if __name__ == '__main__':
    run_benchmarks()
