#!/bin/bash

# AI Tutor Application - Comprehensive Monitoring Startup Script
# This script starts all monitoring services and provides real-time system oversight

set -e  # Exit on any error

echo "🚀 AI Tutor Application - Comprehensive Monitoring System"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo -e "${PURPLE}🔍 $1${NC}"
}

# Check if running from correct directory
if [ ! -f "package.json" ] || [ ! -d "backend" ] || [ ! -d "src" ]; then
    print_error "Please run this script from the root of your AI tutor app directory"
    exit 1
fi

print_info "Starting comprehensive monitoring system..."

# Step 1: Check prerequisites
print_header "Step 1: Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python 3 found: $PYTHON_VERSION"
else
    print_error "Python 3 is required but not found."
    exit 1
fi

# Check if monitoring dependencies are installed
print_info "Installing monitoring dependencies..."
pip3 install aiohttp psutil --quiet

# Step 2: Create monitoring directories
print_header "Step 2: Setting up monitoring infrastructure..."

mkdir -p monitoring/logs
mkdir -p monitoring/reports
mkdir -p monitoring/dashboards
print_status "Monitoring directories created"

# Step 3: Check if services are running
print_header "Step 3: Checking service availability..."

# Check DSPy service
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    print_status "DSPy service is running (port 8001)"
else
    print_warning "DSPy service not detected on port 8001"
    print_info "You may need to start it with: ./start-dspy.sh"
fi

# Check Backend API
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    print_status "Backend API is running (port 5000)"
else
    print_warning "Backend API not detected on port 5000"
    print_info "You may need to start it with: cd backend && node server.js"
fi

# Check Frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    print_status "Frontend is running (port 3000)"
else
    print_warning "Frontend not detected on port 3000"
    print_info "You may need to start it with: npm run client:dev"
fi

# Step 4: Run initial monitoring check
print_header "Step 4: Running initial system check..."

python3 monitoring/monitor_runner.py --single
print_status "Initial monitoring check completed"

# Step 5: Display monitoring information
print_header "Step 5: Monitoring System Information"

echo ""
echo "📊 MONITORING DASHBOARD LOCATIONS:"
echo "   • Real-time Dashboard: file://$(pwd)/monitoring/dashboards/index.html"
echo "   • Latest Metrics JSON: $(pwd)/monitoring/dashboards/latest_metrics.json"
echo "   • Detailed Logs: $(pwd)/monitoring/logs/"
echo "   • Historical Reports: $(pwd)/monitoring/reports/"
echo ""

echo "🔧 MONITORING COMMANDS:"
echo "   • Start continuous monitoring: python3 monitoring/monitor_runner.py"
echo "   • Run single check: python3 monitoring/monitor_runner.py --single"
echo "   • Custom interval: python3 monitoring/monitor_runner.py --interval 60"
echo "   • Verbose mode: python3 monitoring/monitor_runner.py --verbose"
echo ""

echo "📈 WHAT'S BEING MONITORED:"
echo "   • DSPy Service (http://localhost:8001) - Health, response times, errors"
echo "   • Backend API (http://localhost:5000) - Performance, integration status"
echo "   • Frontend (http://localhost:3000) - Availability, connectivity"
echo "   • System Resources - CPU, memory, disk usage"
echo "   • End-to-End Workflows - Complete user interaction testing"
echo "   • Google API Usage - Quota monitoring and error tracking"
echo ""

echo "⚠️  ALERT THRESHOLDS:"
echo "   • Response Time: > 5 seconds"
echo "   • CPU Usage: > 80%"
echo "   • Memory Usage: > 85%"
echo "   • Service Uptime: < 95%"
echo ""

# Step 6: Ask user what to do next
echo "🚀 NEXT STEPS:"
echo ""
echo "1. View Real-time Dashboard:"
echo "   Open: file://$(pwd)/monitoring/dashboards/index.html"
echo ""
echo "2. Start Continuous Monitoring:"
echo "   python3 monitoring/monitor_runner.py"
echo ""
echo "3. Monitor in Background:"
echo "   nohup python3 monitoring/monitor_runner.py > monitoring/logs/background.log 2>&1 &"
echo ""

read -p "Would you like to start continuous monitoring now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Starting continuous monitoring..."
    print_info "Press Ctrl+C to stop monitoring"
    print_info "Dashboard will auto-refresh every 30 seconds"
    echo ""
    
    # Open dashboard in browser if possible
    if command -v xdg-open &> /dev/null; then
        xdg-open "file://$(pwd)/monitoring/dashboards/index.html" 2>/dev/null &
        print_status "Dashboard opened in browser"
    elif command -v open &> /dev/null; then
        open "file://$(pwd)/monitoring/dashboards/index.html" 2>/dev/null &
        print_status "Dashboard opened in browser"
    else
        print_info "Open this URL in your browser: file://$(pwd)/monitoring/dashboards/index.html"
    fi
    
    # Start monitoring
    python3 monitoring/monitor_runner.py
else
    print_info "Monitoring setup complete. Run 'python3 monitoring/monitor_runner.py' when ready."
fi

echo ""
print_status "Monitoring system setup completed successfully!"
echo ""
echo "📚 For more information:"
echo "   • Check monitoring/logs/ for detailed logs"
echo "   • View monitoring/reports/ for historical data"
echo "   • Monitor monitoring/dashboards/index.html for real-time status"
echo ""
print_info "Happy monitoring! 🎓✨"
