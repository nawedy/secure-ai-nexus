# Performance Tuning Guide

## Overview

This guide provides detailed instructions for optimizing the performance of the SecureAI Platform's restore system.

## System Performance Baselines

### Resource Utilization Targets
```yaml
CPU:
  Idle: < 30%
  Normal Load: 30-70%
  Peak Load: < 85%

Memory:
  Available: > 25%
  Cache Hit Rate: > 90%
  Swap Usage: < 5%

Storage:
  IOPS: < 80% of provisioned
  Latency: < 10ms
  Throughput: > 100MB/s

Network:
  Bandwidth Utilization: < 70%
  Latency: < 5ms
  Packet Loss: < 0.1%
```

## Database Optimization

### PostgreSQL Configuration
```ini:postgresql.conf
# Memory Configuration
shared_buffers = 4GB                  # 25% of total RAM
effective_cache_size = 12GB           # 75% of total RAM
maintenance_work_mem = 1GB            # For maintenance operations
work_mem = 32MB                       # Per-operation memory

# Parallel Query Tuning
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
parallel_leader_participation = on

# I/O Configuration
effective_io_concurrency = 200        # For SSDs
random_page_cost = 1.1               # For SSDs
seq_page_cost = 1.0

# WAL Configuration
wal_buffers = 16MB
wal_writer_delay = 200ms
wal_writer_flush_after = 1MB

# Query Planning
default_statistics_target = 100
```

### Restore Operation Optimization
```python
class RestoreOptimizer:
    def __init__(self):
        self.pg_config = {
            'maintenance_work_mem': '2GB',
            'checkpoint_timeout': '1h',
            'max_wal_size': '4GB',
            'restore_command_threads': 4
        }

    async def optimize_for_restore(self, db_size: int):
        """Optimize database settings for restore operation"""
        # Calculate optimal settings based on database size
        memory_settings = self._calculate_memory_settings(db_size)
        worker_settings = self._calculate_worker_settings(db_size)

        # Apply optimized settings
        await self._apply_settings({**memory_settings, **worker_settings})

        return self._generate_restore_command(db_size)

    def _calculate_memory_settings(self, db_size: int) -> dict:
        """Calculate optimal memory settings"""
        total_memory = psutil.virtual_memory().total
        return {
            'maintenance_work_mem': min(total_memory * 0.25, 2 * 1024**3),
            'work_mem': min(total_memory * 0.05, 64 * 1024**2),
        }

    def _calculate_worker_settings(self, db_size: int) -> dict:
        """Calculate optimal worker settings"""
        cpu_count = psutil.cpu_count()
        return {
            'max_parallel_workers': max(4, min(cpu_count - 1, 8)),
            'max_parallel_maintenance_workers': max(2, min(cpu_count // 2, 4))
        }
```

## Storage Optimization

### I/O Tuning
```python
class StorageOptimizer:
    def __init__(self):
        self.io_config = {
            'read_ahead_kb': 1024,
            'nr_requests': 256,
            'scheduler': 'mq-deadline'
        }

    async def optimize_storage(self):
        """Optimize storage settings"""
        device = self._get_storage_device()

        # Set I/O scheduler
        await self._set_scheduler(device)

        # Set read-ahead
        await self._set_read_ahead(device)

        # Adjust I/O queue
        await self._adjust_queue(device)

    async def monitor_io_performance(self):
        """Monitor I/O performance metrics"""
        stats = {
            'iops': self._get_iops(),
            'latency': self._get_latency(),
            'throughput': self._get_throughput()
        }

        if not self._meets_requirements(stats):
            await self._adjust_settings(stats)
```

## Network Optimization

### Network Configuration
```yaml:k8s/network/network-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: network-optimization
  namespace: secureai
data:
  sysctl-settings: |
    net.core.somaxconn=65535
    net.core.netdev_max_backlog=16384
    net.ipv4.tcp_max_syn_backlog=8192
    net.ipv4.tcp_slow_start_after_idle=0
    net.ipv4.tcp_tw_reuse=1
    net.ipv4.ip_local_port_range=1024 65535
```

### Network Performance Monitoring
```python
class NetworkOptimizer:
    def __init__(self):
        self.metrics = PrometheusClient()
        self.thresholds = {
            'latency_ms': 5,
            'packet_loss_percent': 0.1,
            'bandwidth_utilization': 0.7
        }

    async def monitor_network(self):
        """Monitor network performance"""
        while True:
            metrics = await self._collect_metrics()
            if self._requires_optimization(metrics):
                await self._optimize_network(metrics)
            await asyncio.sleep(60)

    async def _optimize_network(self, metrics: Dict[str, float]):
        """Apply network optimizations"""
        if metrics['latency_ms'] > self.thresholds['latency_ms']:
            await self._optimize_tcp_settings()

        if metrics['packet_loss_percent'] > self.thresholds['packet_loss_percent']:
            await self._adjust_network_qos()
```

## Memory Management

### Memory Optimization
```python
class MemoryOptimizer:
    def __init__(self):
        self.memory_config = {
            'vm.swappiness': 10,
            'vm.dirty_ratio': 40,
            'vm.dirty_background_ratio': 10,
            'vm.vfs_cache_pressure': 50
        }

    async def optimize_memory(self):
        """Optimize memory settings"""
        total_mem = psutil.virtual_memory().total

        # Calculate optimal settings
        settings = self._calculate_memory_settings(total_mem)

        # Apply settings
        await self._apply_memory_settings(settings)

        # Monitor and adjust
        asyncio.create_task(self._monitor_memory_usage())

    async def _monitor_memory_usage(self):
        """Monitor memory usage and adjust settings"""
        while True:
            usage = psutil.virtual_memory()
            if usage.percent > 85:
                await self._free_memory_pressure()
            await asyncio.sleep(30)
```

## Performance Monitoring

### Metrics Collection
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'restore_duration': Histogram(
                'restore_duration_seconds',
                'Time taken for restore operations',
                buckets=(60, 300, 600, 1800, 3600)
            ),
            'restore_size': Gauge(
                'restore_size_bytes',
                'Size of restore operation'
            ),
            'restore_rate': Gauge(
                'restore_rate_bytes_per_second',
                'Restore throughput'
            )
        }

    async def monitor_performance(self):
        """Monitor system performance metrics"""
        while True:
            metrics = await self._collect_metrics()
            await self._analyze_performance(metrics)
            await self._adjust_if_needed(metrics)
            await asyncio.sleep(60)
```

## Performance Tuning Procedures

### 1. Initial Assessment
- Baseline performance metrics
- Resource utilization analysis
- Bottleneck identification
- Performance requirements review

### 2. Database Tuning
- Query optimization
- Index management
- Connection pooling
- Vacuum and analyze scheduling

### 3. Storage Optimization
- I/O scheduling
- Buffer management
- Disk alignment
- RAID configuration

### 4. Network Tuning
- TCP optimization
- Buffer sizes
- QoS configuration
- Load balancing

### 5. Memory Management
- Buffer allocation
- Cache configuration
- Swap optimization
- Memory limits

## Monitoring & Alerting

### Performance Alerts
```yaml:k8s/monitoring/performance-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: performance-alerts
spec:
  groups:
  - name: performance.rules
    rules:
    - alert: SlowRestoreOperation
      expr: restore_duration_seconds > 3600
      labels:
        severity: warning
      annotations:
        summary: Restore operation taking too long

    - alert: HighResourceUtilization
      expr: system_resource_utilization > 0.85
      labels:
        severity: warning
      annotations:
        summary: High resource utilization detected
```

## Troubleshooting Performance Issues

### Common Issues and Solutions
1. **Slow Restore Operations**
   - Check I/O performance
   - Verify network bandwidth
   - Monitor memory usage
   - Analyze CPU utilization

2. **Resource Contention**
   - Adjust resource limits
   - Optimize scheduling
   - Review QoS settings
   - Implement rate limiting

3. **Network Bottlenecks**
   - Verify network configuration
   - Check for packet loss
   - Monitor latency
   - Optimize routing
