#!/usr/bin/env python3
"""
AI Tutor Application - Comprehensive Monitoring System
Monitors all services, APIs, and workflows with real-time metrics
"""

import asyncio
import aiohttp
import time
import json
import logging
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/logs/monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceMetrics:
    """Metrics for a single service"""
    name: str
    url: str
    status: str  # 'healthy', 'degraded', 'down'
    response_time: float
    last_check: datetime
    error_count: int
    success_count: int
    uptime_percentage: float
    last_error: Optional[str] = None

@dataclass
class SystemMetrics:
    """System-wide performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    timestamp: datetime

@dataclass
class WorkflowMetrics:
    """End-to-end workflow performance"""
    workflow_name: str
    total_time: float
    steps: List[Dict[str, Any]]
    success: bool
    timestamp: datetime
    error_message: Optional[str] = None

class AITutorMonitor:
    """Comprehensive monitoring system for AI Tutor application"""
    
    def __init__(self):
        self.services = {
            'dspy_service': 'http://localhost:8001',
            'backend_api': 'http://localhost:5000',
            'frontend': 'http://localhost:3000'
        }
        
        self.metrics_history: Dict[str, List[ServiceMetrics]] = {
            service: [] for service in self.services.keys()
        }
        
        self.system_metrics_history: List[SystemMetrics] = []
        self.workflow_metrics_history: List[WorkflowMetrics] = []
        
        self.alert_thresholds = {
            'response_time': 5.0,  # seconds
            'error_rate': 0.1,     # 10%
            'cpu_usage': 80.0,     # percentage
            'memory_usage': 85.0,  # percentage
            'uptime': 95.0         # percentage
        }
        
        # Ensure monitoring directories exist
        Path('monitoring/logs').mkdir(parents=True, exist_ok=True)
        Path('monitoring/reports').mkdir(parents=True, exist_ok=True)
        Path('monitoring/dashboards').mkdir(parents=True, exist_ok=True)
        
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def check_service_health(self, service_name: str, base_url: str) -> ServiceMetrics:
        """Check health of a specific service"""
        start_time = time.time()
        
        try:
            # Determine health endpoint
            health_endpoints = {
                'dspy_service': '/health',
                'backend_api': '/api/health',
                'frontend': '/'
            }
            
            endpoint = health_endpoints.get(service_name, '/health')
            url = f"{base_url}{endpoint}"
            
            async with self.session.get(url) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    status = 'healthy'
                    error_msg = None
                elif response.status >= 500:
                    status = 'down'
                    error_msg = f"HTTP {response.status}"
                else:
                    status = 'degraded'
                    error_msg = f"HTTP {response.status}"
                    
                # Get previous metrics for this service
                prev_metrics = self.metrics_history[service_name]
                error_count = prev_metrics[-1].error_count if prev_metrics else 0
                success_count = prev_metrics[-1].success_count if prev_metrics else 0
                
                if status == 'healthy':
                    success_count += 1
                else:
                    error_count += 1
                
                # Calculate uptime percentage
                total_checks = error_count + success_count
                uptime_percentage = (success_count / total_checks * 100) if total_checks > 0 else 100
                
                return ServiceMetrics(
                    name=service_name,
                    url=base_url,
                    status=status,
                    response_time=response_time,
                    last_check=datetime.now(),
                    error_count=error_count,
                    success_count=success_count,
                    uptime_percentage=uptime_percentage,
                    last_error=error_msg
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            prev_metrics = self.metrics_history[service_name]
            error_count = (prev_metrics[-1].error_count if prev_metrics else 0) + 1
            success_count = prev_metrics[-1].success_count if prev_metrics else 0
            
            total_checks = error_count + success_count
            uptime_percentage = (success_count / total_checks * 100) if total_checks > 0 else 0
            
            return ServiceMetrics(
                name=service_name,
                url=base_url,
                status='down',
                response_time=response_time,
                last_check=datetime.now(),
                error_count=error_count,
                success_count=success_count,
                uptime_percentage=uptime_percentage,
                last_error=str(e)
            )

    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_io={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                },
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={'bytes_sent': 0, 'bytes_recv': 0},
                timestamp=datetime.now()
            )

    async def test_end_to_end_workflow(self) -> WorkflowMetrics:
        """Test complete user workflow from frontend to response"""
        workflow_start = time.time()
        steps = []
        
        try:
            # Step 1: Test DSPy service directly
            step_start = time.time()
            test_question = "What is 2+2?"
            
            async with self.session.post(
                'http://localhost:8001/chat',
                json={'message': test_question, 'subject': 'math'}
            ) as response:
                dspy_time = time.time() - step_start
                dspy_success = response.status == 200
                dspy_response = await response.text() if dspy_success else None
                
                steps.append({
                    'name': 'dspy_direct_test',
                    'duration': dspy_time,
                    'success': dspy_success,
                    'details': f"Status: {response.status}"
                })
            
            # Step 2: Test backend API
            step_start = time.time()
            async with self.session.post(
                'http://localhost:5000/api/chat',
                json={'message': test_question, 'files': []}
            ) as response:
                backend_time = time.time() - step_start
                backend_success = response.status == 200
                backend_response = await response.json() if backend_success else None
                
                steps.append({
                    'name': 'backend_api_test',
                    'duration': backend_time,
                    'success': backend_success,
                    'details': f"Status: {response.status}, Enhanced: {backend_response.get('enhanced', False) if backend_response else False}"
                })
            
            # Step 3: Check if response contains expected educational structure
            step_start = time.time()
            educational_check = False
            if backend_success and backend_response:
                response_text = backend_response.get('response', '')
                educational_indicators = ['Problem Analysis', 'Step-by-Step', 'Solution', 'Difficulty']
                educational_check = any(indicator in response_text for indicator in educational_indicators)
            
            educational_time = time.time() - step_start
            steps.append({
                'name': 'educational_quality_check',
                'duration': educational_time,
                'success': educational_check,
                'details': f"Educational structure detected: {educational_check}"
            })
            
            total_time = time.time() - workflow_start
            overall_success = all(step['success'] for step in steps)
            
            return WorkflowMetrics(
                workflow_name='end_to_end_user_interaction',
                total_time=total_time,
                steps=steps,
                success=overall_success,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            total_time = time.time() - workflow_start
            return WorkflowMetrics(
                workflow_name='end_to_end_user_interaction',
                total_time=total_time,
                steps=steps,
                success=False,
                timestamp=datetime.now(),
                error_message=str(e)
            )

    async def check_google_api_quota(self) -> Dict[str, Any]:
        """Monitor Google API usage and quota"""
        try:
            # Test Google API with a simple request
            start_time = time.time()
            async with self.session.post(
                'http://localhost:8001/chat',
                json={'message': 'Test quota check', 'subject': 'general'}
            ) as response:
                api_time = time.time() - start_time
                
                if response.status == 200:
                    return {
                        'status': 'healthy',
                        'response_time': api_time,
                        'quota_exceeded': False,
                        'last_check': datetime.now().isoformat()
                    }
                elif response.status == 429:
                    return {
                        'status': 'quota_exceeded',
                        'response_time': api_time,
                        'quota_exceeded': True,
                        'last_check': datetime.now().isoformat()
                    }
                else:
                    return {
                        'status': 'error',
                        'response_time': api_time,
                        'quota_exceeded': False,
                        'error': f"HTTP {response.status}",
                        'last_check': datetime.now().isoformat()
                    }
        except Exception as e:
            return {
                'status': 'error',
                'response_time': 0,
                'quota_exceeded': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }

    def generate_alerts(self, metrics: ServiceMetrics) -> List[str]:
        """Generate alerts based on metrics thresholds"""
        alerts = []
        
        if metrics.response_time > self.alert_thresholds['response_time']:
            alerts.append(f"HIGH RESPONSE TIME: {metrics.name} responding in {metrics.response_time:.2f}s")
        
        if metrics.uptime_percentage < self.alert_thresholds['uptime']:
            alerts.append(f"LOW UPTIME: {metrics.name} uptime is {metrics.uptime_percentage:.1f}%")
        
        if metrics.status == 'down':
            alerts.append(f"SERVICE DOWN: {metrics.name} is not responding")
        
        if metrics.status == 'degraded':
            alerts.append(f"SERVICE DEGRADED: {metrics.name} is experiencing issues")
        
        return alerts

    async def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        logger.info("Starting monitoring cycle...")
        
        # Check all services
        for service_name, base_url in self.services.items():
            metrics = await self.check_service_health(service_name, base_url)
            self.metrics_history[service_name].append(metrics)
            
            # Generate alerts
            alerts = self.generate_alerts(metrics)
            for alert in alerts:
                logger.warning(f"ALERT: {alert}")
        
        # Collect system metrics
        system_metrics = self.collect_system_metrics()
        self.system_metrics_history.append(system_metrics)
        
        # Test end-to-end workflow
        workflow_metrics = await self.test_end_to_end_workflow()
        self.workflow_metrics_history.append(workflow_metrics)
        
        # Check Google API quota
        quota_status = await self.check_google_api_quota()
        
        # Log summary
        logger.info(f"Monitoring cycle completed:")
        for service_name in self.services.keys():
            latest_metrics = self.metrics_history[service_name][-1]
            logger.info(f"  {service_name}: {latest_metrics.status} ({latest_metrics.response_time:.2f}s)")
        
        logger.info(f"  System: CPU {system_metrics.cpu_usage:.1f}%, Memory {system_metrics.memory_usage:.1f}%")
        logger.info(f"  Workflow: {'SUCCESS' if workflow_metrics.success else 'FAILED'} ({workflow_metrics.total_time:.2f}s)")
        logger.info(f"  Google API: {quota_status['status']}")

    def save_metrics_report(self):
        """Save detailed metrics report to file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'system': asdict(self.system_metrics_history[-1]) if self.system_metrics_history else None,
            'workflows': [asdict(wm) for wm in self.workflow_metrics_history[-10:]],  # Last 10 workflows
            'summary': self.generate_summary()
        }
        
        # Add service metrics
        for service_name in self.services.keys():
            if self.metrics_history[service_name]:
                latest = self.metrics_history[service_name][-1]
                report['services'][service_name] = asdict(latest)
        
        # Save to file
        report_file = f"monitoring/reports/metrics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Metrics report saved to {report_file}")

    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        summary = {
            'overall_health': 'healthy',
            'services_up': 0,
            'services_total': len(self.services),
            'average_response_time': 0.0,
            'workflow_success_rate': 0.0
        }
        
        # Service summary
        total_response_time = 0
        healthy_services = 0
        
        for service_name in self.services.keys():
            if self.metrics_history[service_name]:
                latest = self.metrics_history[service_name][-1]
                total_response_time += latest.response_time
                if latest.status == 'healthy':
                    healthy_services += 1
        
        summary['services_up'] = healthy_services
        summary['average_response_time'] = total_response_time / len(self.services) if self.services else 0
        
        if healthy_services < len(self.services):
            summary['overall_health'] = 'degraded' if healthy_services > 0 else 'critical'
        
        # Workflow success rate
        if self.workflow_metrics_history:
            recent_workflows = self.workflow_metrics_history[-20:]  # Last 20 workflows
            successful = sum(1 for wm in recent_workflows if wm.success)
            summary['workflow_success_rate'] = (successful / len(recent_workflows)) * 100
        
        return summary
