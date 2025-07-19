#!/usr/bin/env python3
"""
Real-time Dashboard Generator for AI Tutor Monitoring
Creates HTML dashboards with live metrics and charts
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class DashboardGenerator:
    """Generates real-time HTML dashboards for monitoring data"""
    
    def __init__(self):
        self.dashboard_dir = Path('monitoring/dashboards')
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_html_dashboard(self, metrics_data: Dict[str, Any]) -> str:
        """Generate complete HTML dashboard"""
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Tutor - System Monitor</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 20px;
        }
        .header {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        .header h1 {
            color: #2c3e50;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .status-overview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .status-card {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }
        .status-card:hover { transform: translateY(-5px); }
        .status-healthy { border-left: 5px solid #27ae60; }
        .status-degraded { border-left: 5px solid #f39c12; }
        .status-down { border-left: 5px solid #e74c3c; }
        .service-name { 
            font-size: 1.2em; 
            font-weight: bold; 
            margin-bottom: 10px;
            color: #2c3e50;
        }
        .metric { 
            display: flex; 
            justify-content: space-between; 
            margin: 5px 0;
            font-size: 0.9em;
        }
        .metric-label { color: #7f8c8d; }
        .metric-value { font-weight: bold; }
        .charts-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .chart-container {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        .chart-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #2c3e50;
            text-align: center;
        }
        .workflow-section {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            margin-bottom: 20px;
        }
        .workflow-step {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
            background: #f8f9fa;
        }
        .step-success { border-left: 4px solid #27ae60; }
        .step-failed { border-left: 4px solid #e74c3c; }
        .alerts-section {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        .alert {
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }
        .alert-critical {
            background: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }
        .timestamp {
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 20px;
        }
        .auto-refresh {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.9);
            padding: 10px 15px;
            border-radius: 25px;
            font-size: 0.9em;
            color: #27ae60;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="auto-refresh">🔄 Auto-refresh: 30s</div>
    
    <div class="container">
        <div class="header">
            <h1>🎓 AI Tutor System Monitor</h1>
            <div class="timestamp">Last Updated: {timestamp}</div>
        </div>
        
        <div class="status-overview">
            {service_cards}
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <div class="chart-title">Response Times (Last 10 Checks)</div>
                <canvas id="responseTimeChart" width="400" height="200"></canvas>
            </div>
            <div class="chart-container">
                <div class="chart-title">System Performance</div>
                <canvas id="systemChart" width="400" height="200"></canvas>
            </div>
        </div>
        
        <div class="workflow-section">
            <div class="chart-title">🔄 Latest End-to-End Workflow Test</div>
            {workflow_steps}
        </div>
        
        <div class="alerts-section">
            <div class="chart-title">⚠️ Active Alerts</div>
            {alerts}
        </div>
    </div>
    
    <script>
        // Response Time Chart
        const responseCtx = document.getElementById('responseTimeChart').getContext('2d');
        new Chart(responseCtx, {{
            type: 'line',
            data: {{
                labels: {response_time_labels},
                datasets: {response_time_datasets}
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'Response Time (seconds)' }}
                    }}
                }},
                plugins: {{
                    legend: {{ position: 'top' }}
                }}
            }}
        }});
        
        // System Performance Chart
        const systemCtx = document.getElementById('systemChart').getContext('2d');
        new Chart(systemCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['CPU Usage', 'Memory Usage', 'Available'],
                datasets: [{{
                    data: [{cpu_usage}, {memory_usage}, {available_resources}],
                    backgroundColor: ['#e74c3c', '#f39c12', '#27ae60'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
        
        // Auto-refresh every 30 seconds
        setTimeout(() => {{
            window.location.reload();
        }}, 30000);
    </script>
</body>
</html>
        """
        
        # Generate service cards
        service_cards = self._generate_service_cards(metrics_data.get('services', {}))
        
        # Generate workflow steps
        workflow_steps = self._generate_workflow_steps(metrics_data.get('workflows', []))
        
        # Generate alerts
        alerts = self._generate_alerts(metrics_data)
        
        # Generate chart data
        response_time_data = self._generate_response_time_data(metrics_data.get('services', {}))
        
        # System metrics
        system_data = metrics_data.get('system', {})
        cpu_usage = system_data.get('cpu_usage', 0)
        memory_usage = system_data.get('memory_usage', 0)
        available_resources = max(0, 100 - max(cpu_usage, memory_usage))
        
        return html_template.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            service_cards=service_cards,
            workflow_steps=workflow_steps,
            alerts=alerts,
            response_time_labels=json.dumps(response_time_data['labels']),
            response_time_datasets=json.dumps(response_time_data['datasets']),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            available_resources=available_resources
        )
    
    def _generate_service_cards(self, services: Dict[str, Any]) -> str:
        """Generate HTML for service status cards"""
        cards = []
        
        for service_name, metrics in services.items():
            status = metrics.get('status', 'unknown')
            status_class = f"status-{status}"
            
            card_html = f"""
            <div class="status-card {status_class}">
                <div class="service-name">{service_name.replace('_', ' ').title()}</div>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value">{status.upper()}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Response Time:</span>
                    <span class="metric-value">{metrics.get('response_time', 0):.2f}s</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Uptime:</span>
                    <span class="metric-value">{metrics.get('uptime_percentage', 0):.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Success/Error:</span>
                    <span class="metric-value">{metrics.get('success_count', 0)}/{metrics.get('error_count', 0)}</span>
                </div>
            </div>
            """
            cards.append(card_html)
        
        return '\n'.join(cards)
    
    def _generate_workflow_steps(self, workflows: List[Dict[str, Any]]) -> str:
        """Generate HTML for workflow steps"""
        if not workflows:
            return '<div class="workflow-step">No workflow data available</div>'
        
        latest_workflow = workflows[-1]
        steps = latest_workflow.get('steps', [])
        
        step_html = []
        for step in steps:
            success = step.get('success', False)
            step_class = 'step-success' if success else 'step-failed'
            status_icon = '✅' if success else '❌'
            
            html = f"""
            <div class="workflow-step {step_class}">
                <span>{status_icon} {step.get('name', 'Unknown Step').replace('_', ' ').title()}</span>
                <span>{step.get('duration', 0):.2f}s</span>
            </div>
            """
            step_html.append(html)
        
        return '\n'.join(step_html)
    
    def _generate_alerts(self, metrics_data: Dict[str, Any]) -> str:
        """Generate HTML for alerts"""
        alerts = []
        
        # Check service alerts
        services = metrics_data.get('services', {})
        for service_name, metrics in services.items():
            if metrics.get('status') == 'down':
                alerts.append(f"🔴 CRITICAL: {service_name} is DOWN")
            elif metrics.get('status') == 'degraded':
                alerts.append(f"🟡 WARNING: {service_name} is degraded")
            
            if metrics.get('response_time', 0) > 5.0:
                alerts.append(f"🟡 WARNING: {service_name} slow response ({metrics.get('response_time', 0):.2f}s)")
        
        # Check system alerts
        system = metrics_data.get('system', {})
        if system.get('cpu_usage', 0) > 80:
            alerts.append(f"🟡 WARNING: High CPU usage ({system.get('cpu_usage', 0):.1f}%)")
        if system.get('memory_usage', 0) > 85:
            alerts.append(f"🟡 WARNING: High memory usage ({system.get('memory_usage', 0):.1f}%)")
        
        # Check workflow alerts
        workflows = metrics_data.get('workflows', [])
        if workflows and not workflows[-1].get('success', True):
            alerts.append("🔴 CRITICAL: End-to-end workflow test failed")
        
        if not alerts:
            alerts.append("✅ All systems operating normally")
        
        alert_html = []
        for alert in alerts:
            alert_class = 'alert-critical' if '🔴 CRITICAL' in alert else 'alert'
            alert_html.append(f'<div class="{alert_class}">{alert}</div>')
        
        return '\n'.join(alert_html)
    
    def _generate_response_time_data(self, services: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart data for response times"""
        # For now, generate sample data - in a real implementation,
        # this would use historical data from the monitoring system
        
        labels = [f"Check {i+1}" for i in range(10)]
        datasets = []
        
        colors = {
            'dspy_service': '#3498db',
            'backend_api': '#e74c3c',
            'frontend': '#27ae60'
        }
        
        for service_name, metrics in services.items():
            # Generate sample historical data (in real implementation, use actual history)
            current_time = metrics.get('response_time', 1.0)
            sample_data = [
                max(0.1, current_time + (i * 0.1 - 0.5)) for i in range(10)
            ]
            
            datasets.append({
                'label': service_name.replace('_', ' ').title(),
                'data': sample_data,
                'borderColor': colors.get(service_name, '#95a5a6'),
                'backgroundColor': colors.get(service_name, '#95a5a6') + '20',
                'tension': 0.4,
                'fill': False
            })
        
        return {
            'labels': labels,
            'datasets': datasets
        }
    
    def save_dashboard(self, metrics_data: Dict[str, Any]) -> str:
        """Save dashboard to file and return file path"""
        html_content = self.generate_html_dashboard(metrics_data)
        
        dashboard_file = self.dashboard_dir / 'index.html'
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(dashboard_file)
