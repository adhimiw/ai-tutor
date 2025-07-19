#!/bin/bash

# DSPy AI Tutor Integration Setup Script
# This script sets up the DSPy service and integrates it with your existing AI tutor app

set -e  # Exit on any error

echo "🚀 DSPy AI Tutor Integration Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if running from correct directory
if [ ! -f "package.json" ] || [ ! -d "backend" ] || [ ! -d "src" ]; then
    print_error "Please run this script from the root of your AI tutor app directory"
    exit 1
fi

print_info "Setting up DSPy integration for AI Tutor App..."

# Step 1: Check prerequisites
echo -e "\n${BLUE}Step 1: Checking prerequisites...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python 3 found: $PYTHON_VERSION"
else
    print_error "Python 3 is required but not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_status "Node.js found: $NODE_VERSION"
else
    print_error "Node.js is required but not found."
    exit 1
fi

# Check if Google API key is available
if [ -f "backend/.env" ]; then
    if grep -q "GOOGLE_API_KEY=" backend/.env; then
        print_status "Google API key configuration found"
    else
        print_warning "Google API key not found in backend/.env"
    fi
else
    print_warning "Backend .env file not found"
fi

# Step 2: Set up Python virtual environment
echo -e "\n${BLUE}Step 2: Setting up Python environment...${NC}"

cd dspy-service

if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
print_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_status "Python dependencies installed"

# Step 3: Configure DSPy service
echo -e "\n${BLUE}Step 3: Configuring DSPy service...${NC}"

if [ ! -f ".env" ]; then
    print_info "Creating DSPy service configuration..."
    cp .env.example .env
    print_status "DSPy .env file created"
    
    # Try to copy Google API key from backend if available
    if [ -f "../backend/.env" ]; then
        GOOGLE_KEY=$(grep "GOOGLE_API_KEY=" ../backend/.env | cut -d'=' -f2)
        if [ ! -z "$GOOGLE_KEY" ]; then
            sed -i "s/your_google_api_key_here/$GOOGLE_KEY/" .env
            print_status "Google API key copied from backend configuration"
        fi
    fi
else
    print_status "DSPy .env file already exists"
fi

# Create necessary directories
mkdir -p logs cache
print_status "Created logs and cache directories"

# Step 4: Test DSPy service
echo -e "\n${BLUE}Step 4: Testing DSPy service...${NC}"

# Check if Google API key is set
if grep -q "your_google_api_key_here" .env; then
    print_warning "Please edit dspy-service/.env and add your Google API key before continuing"
    print_info "You can continue the setup after adding the API key"
else
    print_info "Running DSPy service initialization test..."
    if python start.py --test 2>/dev/null; then
        print_status "DSPy service initialization test passed"
    else
        print_warning "DSPy service test failed - please check your Google API key"
    fi
fi

cd ..

# Step 5: Configure Node.js backend
echo -e "\n${BLUE}Step 5: Configuring Node.js backend...${NC}"

cd backend

if [ ! -f ".env" ]; then
    print_info "Creating backend configuration..."
    cp .env.example .env
    print_status "Backend .env file created"
else
    print_status "Backend .env file already exists"
fi

# Check if DSPy integration is enabled
if grep -q "ENABLE_DSPY_INTEGRATION=true" .env; then
    print_status "DSPy integration is enabled in backend"
else
    print_info "Enabling DSPy integration in backend..."
    echo "" >> .env
    echo "# DSPy Integration" >> .env
    echo "ENABLE_DSPY_INTEGRATION=true" >> .env
    echo "DSPY_SERVICE_URL=http://localhost:8001" >> .env
    echo "DSPY_FALLBACK_TO_GEMINI=true" >> .env
    echo "DSPY_REQUEST_TIMEOUT=30000" >> .env
    print_status "DSPy integration configuration added"
fi

cd ..

# Step 6: Create startup scripts
echo -e "\n${BLUE}Step 6: Creating startup scripts...${NC}"

# Create start-dspy.sh
cat > start-dspy.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting DSPy AI Tutor Service..."
cd dspy-service
source venv/bin/activate
python start.py
EOF

chmod +x start-dspy.sh
print_status "Created start-dspy.sh script"

# Create start-all.sh
cat > start-all.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting AI Tutor App with DSPy Integration..."

# Function to cleanup background processes
cleanup() {
    echo "Stopping services..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT

# Start DSPy service in background
echo "Starting DSPy service..."
cd dspy-service
source venv/bin/activate
python start.py &
DSPY_PID=$!
cd ..

# Wait for DSPy service to start
echo "Waiting for DSPy service to initialize..."
sleep 5

# Start backend
echo "Starting Node.js backend..."
cd backend
npm start &
BACKEND_PID=$!
cd ..

# Start frontend
echo "Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ All services started!"
echo "- DSPy Service: http://localhost:8001"
echo "- Backend API: http://localhost:5000"
echo "- Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for any process to exit
wait
EOF

chmod +x start-all.sh
print_status "Created start-all.sh script"

# Create test script
cat > test-dspy.sh << 'EOF'
#!/bin/bash
echo "🧪 Testing DSPy Integration..."
cd dspy-service
source venv/bin/activate
python test_service.py
EOF

chmod +x test-dspy.sh
print_status "Created test-dspy.sh script"

# Step 7: Final instructions
echo -e "\n${GREEN}🎉 DSPy Integration Setup Complete!${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your Google API key:"
echo "   - Edit dspy-service/.env and add your GOOGLE_API_KEY"
echo "   - Edit backend/.env and add your GOOGLE_API_KEY (if not already done)"
echo ""
echo "2. Start the services:"
echo "   - Start DSPy service only: ./start-dspy.sh"
echo "   - Start all services: ./start-all.sh"
echo ""
echo "3. Test the integration:"
echo "   - Test DSPy service: ./test-dspy.sh"
echo "   - Use your frontend to test enhanced AI responses"
echo ""
echo "4. Monitor the integration:"
echo "   - DSPy service logs: dspy-service/logs/"
echo "   - Backend will automatically use DSPy when available"
echo "   - Look for 'enhanced: true' in API responses"
echo ""
echo "Service URLs:"
echo "- DSPy Service: http://localhost:8001"
echo "- Backend API: http://localhost:5000"
echo "- Frontend: http://localhost:3000"
echo ""
print_info "For detailed documentation, see dspy-service/README.md"

echo -e "\n${BLUE}Happy tutoring with DSPy! 🎓${NC}"
