import asyncio
import logging
from typing import Dict, List
from src.monitoring.system import system_monitor
from src.monitoring.metrics_detail import metrics_detail
import json

logger = logging.getLogger(__name__)

class PreDeploymentCheck:
    def __init__(self):
        self.checks = {
            'system': self._check_system,
            'monitoring': self._check_monitoring,
            'security': self._check_security,
            'performance': self._check_performance
        }
        self.results: Dict[str, Dict] = {}

    async def run_all_checks(self) -> Dict[str, Dict]:
        """Run all pre-deployment checks"""
        for check_name, check_func in self.checks.items():
            try:
                self.results[check_name] = await check_func()
            except Exception as e:
                logger.error(f"Check failed - {check_name}: {str(e)}")
                self.results[check_name] = {
                    'status': 'failed',
                    'error': str(e)
                }
        return self.results

    async def _check_system(self) -> Dict:
        """Check system health and resources"""
        health = await system_monitor.check_health()
        metrics = await system_monitor.collect_system_metrics()

        return {
            'status': health['status'],
            'metrics': metrics,
            'passed': health['status'] == 'healthy'
        }

    async def _check_monitoring(self) -> Dict:
        """Verify monitoring setup"""
        try:
            metrics = await metrics_detail.collect_detailed_metrics()
            return {
                'status': 'healthy',
                'metrics_available': list(metrics.keys()),
                'passed': True
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'passed': False
            }

    async def _check_security(self) -> Dict:
        """Verify security configurations"""
        try:
            # Check security metrics
            security_metrics = await metrics_detail._get_security_metrics()

            # Check security configurations
            security_checks = {
                'rate_limiting': self._verify_rate_limiting(),
                'auth_config': self._verify_auth_config(),
                'ssl_config': self._verify_ssl_config(),
                'cors_config': self._verify_cors_config(),
                'security_headers': self._verify_security_headers()
            }

            # Verify all security features are enabled
            all_passed = all(security_checks.values())

            return {
                'status': 'healthy' if all_passed else 'warning',
                'metrics': security_metrics,
                'checks': security_checks,
                'passed': all_passed
            }
        except Exception as e:
            logger.error(f"Security check failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'passed': False
            }

    async def _check_performance(self) -> Dict:
        """Verify performance metrics"""
        try:
            # Get performance metrics
            perf_metrics = await metrics_detail._get_performance_metrics()

            # Define performance thresholds
            thresholds = {
                'max_latency': 1000,  # ms
                'min_throughput': 100,  # requests/sec
                'max_memory': 85,  # percent
                'max_cpu': 80  # percent
            }

            # Check against thresholds
            checks = {
                'latency': perf_metrics['model_inference_times']['average'] < thresholds['max_latency'],
                'memory': perf_metrics['model_memory_usage']['total'] < thresholds['max_memory'],
                'cpu_usage': system_monitor.cpu_usage._value.get() < thresholds['max_cpu']
            }

            all_passed = all(checks.values())

            return {
                'status': 'healthy' if all_passed else 'warning',
                'metrics': perf_metrics,
                'checks': checks,
                'thresholds': thresholds,
                'passed': all_passed
            }
        except Exception as e:
            logger.error(f"Performance check failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'passed': False
            }

    def _verify_rate_limiting(self) -> bool:
        """Verify rate limiting configuration"""
        try:
            config = self._load_config('rate_limiting')
            return all([
                config.get('enabled', False),
                config.get('default_limit') is not None,
                config.get('window_size') is not None
            ])
        except Exception as e:
            logger.error(f"Rate limiting verification failed: {str(e)}")
            return False

    def _verify_auth_config(self) -> bool:
        """Verify authentication configuration"""
        try:
            config = self._load_config('auth')
            return all([
                config.get('jwt_secret') is not None,
                config.get('token_expiry') is not None,
                config.get('mfa_enabled', False)
            ])
        except Exception as e:
            logger.error(f"Auth config verification failed: {str(e)}")
            return False

    def _verify_ssl_config(self) -> bool:
        """Verify SSL configuration"""
        try:
            config = self._load_config('ssl')
            return all([
                config.get('cert_path') is not None,
                config.get('key_path') is not None,
                config.get('enabled', False)
            ])
        except Exception as e:
            logger.error(f"SSL config verification failed: {str(e)}")
            return False

    def _verify_cors_config(self) -> bool:
        """Verify CORS configuration"""
        try:
            config = self._load_config('cors')
            return all([
                isinstance(config.get('allowed_origins'), list),
                isinstance(config.get('allowed_methods'), list),
                config.get('allow_credentials') is not None
            ])
        except Exception as e:
            logger.error(f"CORS config verification failed: {str(e)}")
            return False

    def _verify_security_headers(self) -> bool:
        """Verify security headers configuration"""
        try:
            config = self._load_config('security_headers')
            required_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection',
                'Content-Security-Policy'
            ]
            return all(header in config for header in required_headers)
        except Exception as e:
            logger.error(f"Security headers verification failed: {str(e)}")
            return False

    def _load_config(self, config_type: str) -> Dict:
        """Load configuration from file or environment"""
        # Implementation would load from config files or environment variables
        # This is a placeholder for the actual implementation
        return {}

# Run pre-deployment checks
async def main():
    checker = PreDeploymentCheck()
    results = await checker.run_all_checks()

    # Print results
    print("\n=== Pre-deployment Check Results ===")
    for check_name, result in results.items():
        status = "✅" if result.get('passed', False) else "❌"
        print(f"\n{status} {check_name.upper()}:")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
