#!/usr/bin/env python3
"""
Automated Monitoring Runner for AI Tutor Application
Continuously monitors all services and generates real-time reports
"""

import asyncio
import signal
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import logging

# Add the project root to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from monitoring.core_monitor import AITutorMonitor
from monitoring.dashboard_generator import DashboardGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/logs/runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MonitoringRunner:
    """Main monitoring runner that orchestrates all monitoring activities"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.running = False
        self.monitor = None
        self.dashboard_generator = DashboardGenerator()
        
        # Ensure directories exist
        Path('monitoring/logs').mkdir(parents=True, exist_ok=True)
        Path('monitoring/reports').mkdir(parents=True, exist_ok=True)
        Path('monitoring/dashboards').mkdir(parents=True, exist_ok=True)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def start_monitoring(self):
        """Start the continuous monitoring process"""
        logger.info("🚀 Starting AI Tutor Monitoring System")
        logger.info(f"📊 Check interval: {self.check_interval} seconds")
        logger.info("📁 Logs: monitoring/logs/")
        logger.info("📈 Reports: monitoring/reports/")
        logger.info("🌐 Dashboard: monitoring/dashboards/index.html")
        
        self.running = True
        cycle_count = 0
        
        async with AITutorMonitor() as monitor:
            self.monitor = monitor
            
            while self.running:
                try:
                    cycle_count += 1
                    logger.info(f"\n{'='*60}")
                    logger.info(f"🔍 MONITORING CYCLE #{cycle_count}")
                    logger.info(f"{'='*60}")
                    
                    # Run monitoring cycle
                    await monitor.run_monitoring_cycle()
                    
                    # Generate and save reports every 5 cycles (or every ~2.5 minutes with 30s interval)
                    if cycle_count % 5 == 0:
                        monitor.save_metrics_report()
                    
                    # Generate real-time dashboard
                    await self._update_dashboard(monitor)
                    
                    # Log cycle completion
                    logger.info(f"✅ Cycle #{cycle_count} completed successfully")
                    
                    # Wait for next cycle
                    if self.running:
                        logger.info(f"⏳ Waiting {self.check_interval} seconds until next check...")
                        await asyncio.sleep(self.check_interval)
                        
                except KeyboardInterrupt:
                    logger.info("Monitoring interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"Error in monitoring cycle: {e}")
                    logger.info(f"Continuing monitoring in {self.check_interval} seconds...")
                    if self.running:
                        await asyncio.sleep(self.check_interval)
        
        logger.info("🛑 Monitoring system stopped")
    
    async def _update_dashboard(self, monitor: AITutorMonitor):
        """Update the real-time dashboard"""
        try:
            # Prepare metrics data for dashboard
            metrics_data = {
                'timestamp': datetime.now().isoformat(),
                'services': {},
                'system': None,
                'workflows': [],
                'summary': monitor.generate_summary()
            }
            
            # Add latest service metrics
            for service_name in monitor.services.keys():
                if monitor.metrics_history[service_name]:
                    latest_metrics = monitor.metrics_history[service_name][-1]
                    metrics_data['services'][service_name] = {
                        'name': latest_metrics.name,
                        'status': latest_metrics.status,
                        'response_time': latest_metrics.response_time,
                        'uptime_percentage': latest_metrics.uptime_percentage,
                        'success_count': latest_metrics.success_count,
                        'error_count': latest_metrics.error_count,
                        'last_error': latest_metrics.last_error
                    }
            
            # Add latest system metrics
            if monitor.system_metrics_history:
                latest_system = monitor.system_metrics_history[-1]
                metrics_data['system'] = {
                    'cpu_usage': latest_system.cpu_usage,
                    'memory_usage': latest_system.memory_usage,
                    'disk_usage': latest_system.disk_usage,
                    'network_io': latest_system.network_io
                }
            
            # Add recent workflow metrics
            if monitor.workflow_metrics_history:
                recent_workflows = monitor.workflow_metrics_history[-5:]  # Last 5 workflows
                for workflow in recent_workflows:
                    metrics_data['workflows'].append({
                        'workflow_name': workflow.workflow_name,
                        'total_time': workflow.total_time,
                        'success': workflow.success,
                        'steps': workflow.steps,
                        'timestamp': workflow.timestamp.isoformat(),
                        'error_message': workflow.error_message
                    })
            
            # Generate and save dashboard
            dashboard_path = self.dashboard_generator.save_dashboard(metrics_data)
            logger.info(f"📊 Dashboard updated: {dashboard_path}")
            
            # Also save latest metrics as JSON for API access
            json_path = Path('monitoring/dashboards/latest_metrics.json')
            with open(json_path, 'w') as f:
                json.dump(metrics_data, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
    
    def run_single_check(self):
        """Run a single monitoring check (for testing)"""
        logger.info("Running single monitoring check...")
        asyncio.run(self._run_single_check_async())
    
    async def _run_single_check_async(self):
        """Async version of single check"""
        async with AITutorMonitor() as monitor:
            await monitor.run_monitoring_cycle()
            await self._update_dashboard(monitor)
            logger.info("Single check completed")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Tutor Monitoring System')
    parser.add_argument(
        '--interval', 
        type=int, 
        default=30, 
        help='Check interval in seconds (default: 30)'
    )
    parser.add_argument(
        '--single', 
        action='store_true', 
        help='Run a single check and exit'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    runner = MonitoringRunner(check_interval=args.interval)
    
    if args.single:
        runner.run_single_check()
    else:
        try:
            asyncio.run(runner.start_monitoring())
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
