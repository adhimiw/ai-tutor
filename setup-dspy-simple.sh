#!/bin/bash

# Simple DSPy AI Tutor Integration Setup Script
# Lightweight version focusing on core functionality

set -e  # Exit on any error

echo "🚀 DSPy AI Tutor Integration Setup (Simplified)"
echo "=============================================="

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

print_info "Setting up DSPy integration for AI Tutor App (lightweight version)..."

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

# Install Python dependencies (lightweight)
print_info "Installing essential Python dependencies..."
pip install --upgrade pip

# Install packages one by one to avoid conflicts
print_info "Installing DSPy..."
pip install dspy-ai>=2.4.0

print_info "Installing Google Generative AI..."
pip install google-generativeai>=0.8.0

print_info "Installing FastAPI and web framework..."
pip install fastapi>=0.104.0 uvicorn>=0.24.0 pydantic>=2.0.0

print_info "Installing utilities..."
pip install python-dotenv>=1.0.0 requests>=2.31.0 loguru>=0.7.0

print_info "Installing basic data processing..."
pip install numpy>=1.24.0 scikit-learn>=1.3.0

print_status "Essential Python dependencies installed"

# Step 3: Configure DSPy service
echo -e "\n${BLUE}Step 3: Configuring DSPy service...${NC}"

if [ ! -f ".env" ]; then
    print_info "Creating DSPy service configuration..."
    cp .env.example .env
    print_status "DSPy .env file created"
    
    # Try to copy Google API key from backend if available
    if [ -f "../backend/.env" ]; then
        GOOGLE_KEY=$(grep "GOOGLE_API_KEY=" ../backend/.env | cut -d'=' -f2 2>/dev/null || echo "")
        if [ ! -z "$GOOGLE_KEY" ] && [ "$GOOGLE_KEY" != "your_google_api_key_here" ]; then
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

cd ..

# Step 4: Configure Node.js backend
echo -e "\n${BLUE}Step 4: Configuring Node.js backend...${NC}"

cd backend

if [ ! -f ".env" ]; then
    print_info "Creating backend configuration..."
    cp .env.example .env
    print_status "Backend .env file created"
else
    print_status "Backend .env file already exists"
fi

# Check if DSPy integration is enabled
if ! grep -q "ENABLE_DSPY_INTEGRATION=true" .env 2>/dev/null; then
    print_info "Enabling DSPy integration in backend..."
    echo "" >> .env
    echo "# DSPy Integration" >> .env
    echo "ENABLE_DSPY_INTEGRATION=true" >> .env
    echo "DSPY_SERVICE_URL=http://localhost:8001" >> .env
    echo "DSPY_FALLBACK_TO_GEMINI=true" >> .env
    echo "DSPY_REQUEST_TIMEOUT=30000" >> .env
    print_status "DSPy integration configuration added"
else
    print_status "DSPy integration already enabled in backend"
fi

cd ..

# Step 5: Create startup scripts
echo -e "\n${BLUE}Step 5: Creating startup scripts...${NC}"

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

# Step 6: Test basic functionality
echo -e "\n${BLUE}Step 6: Testing basic setup...${NC}"

cd dspy-service
source venv/bin/activate

# Test Python imports
print_info "Testing Python imports..."
python3 -c "
try:
    import dspy
    import google.generativeai as genai
    import fastapi
    import uvicorn
    print('✅ All essential imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
" && print_status "Python imports test passed" || print_error "Python imports test failed"

cd ..

# Step 7: Final instructions
echo -e "\n${GREEN}🎉 DSPy Integration Setup Complete (Simplified)!${NC}"
echo "================================================"
echo ""
echo "✅ What's been set up:"
echo "   - Python virtual environment with essential DSPy packages"
echo "   - DSPy service configuration"
echo "   - Node.js backend integration"
echo "   - Startup and test scripts"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Add your Google API key:"
echo "   - Edit dspy-service/.env and set GOOGLE_API_KEY=your_actual_key"
echo "   - Edit backend/.env and set GOOGLE_API_KEY=your_actual_key"
echo ""
echo "2. Start the DSPy service:"
echo "   ./start-dspy.sh"
echo ""
echo "3. In another terminal, start your backend:"
echo "   cd backend && npm start"
echo ""
echo "4. In another terminal, start your frontend:"
echo "   npm start"
echo ""
echo "5. Test the integration:"
echo "   ./test-dspy.sh"
echo ""
echo "🌐 Service URLs:"
echo "   - DSPy Service: http://localhost:8001"
echo "   - Backend API: http://localhost:5000"
echo "   - Frontend: http://localhost:3000"
echo ""
echo "📚 Documentation:"
echo "   - DSPy service docs: dspy-service/README.md"
echo "   - Integration summary: DSPY_INTEGRATION_SUMMARY.md"
echo ""
print_info "The setup is now ready! Add your Google API key and start the services."
echo -e "\n${BLUE}Happy tutoring with DSPy! 🎓${NC}"
