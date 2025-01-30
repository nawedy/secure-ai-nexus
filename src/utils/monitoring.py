from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
REQUEST_COUNT = Counter(
    'model_request_total',
    'Total number of requests',
    ['model_name', 'status']
)

REQUEST_LATENCY = Histogram(
    'model_request_latency_seconds',
    'Request latency in seconds',
    ['model_name'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Resource metrics
GPU_MEMORY_USAGE = Gauge(
    'gpu_memory_usage_bytes',
    'GPU memory usage in bytes',
    ['device', 'model_name']
)

MODEL_LOAD_TIME = Histogram(
    'model_load_time_seconds',
    'Time taken to load model',
    ['model_name']
)

class MetricsManager:
    @staticmethod
    def record_request(model_name: str, status: str, duration: float):
        REQUEST_COUNT.labels(model_name=model_name, status=status).inc()
        REQUEST_LATENCY.labels(model_name=model_name).observe(duration)
    
    @staticmethod
    def update_gpu_memory(model_name: str, device: str, memory_bytes: int):
        GPU_MEMORY_USAGE.labels(device=device, model_name=model_name).set(memory_bytes)
    
    @staticmethod
    def record_model_load_time(model_name: str, duration: float):
        MODEL_LOAD_TIME.labels(model_name=model_name).observe(duration) 