# DSPy AI Tutor Service

Enhanced AI tutoring service using DSPy framework for systematic optimization and improved educational effectiveness.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google API Key (for Gemini models)
- Node.js backend (for integration)

### Installation

1. **Set up Python environment:**
```bash
cd dspy-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your Google API key
```

3. **Start the service:**
```bash
python start.py
```

The service will be available at `http://localhost:8001`

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Service Configuration
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8001
LOG_LEVEL=INFO

# Model Configuration
DEFAULT_LM_MODEL=gemini/gemini-2.5-flash
EMBEDDING_MODEL=google/text-embedding-004
EMBEDDING_DIMENSIONS=768

# Optimization Settings
ENABLE_OPTIMIZATION=true
OPTIMIZATION_CACHE_DIR=./cache
MAX_OPTIMIZATION_EXAMPLES=500
```

## 📚 API Endpoints

### Health Check
```http
GET /health
```

### Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
  "message": "Explain quadratic equations",
  "conversation_id": "conv_123",
  "user_id": "user_456",
  "subject": "math",
  "difficulty_level": "intermediate"
}
```

### Module Optimization
```http
POST /optimize
Content-Type: application/json

{
  "module_name": "math",
  "training_examples": [
    {
      "question": "What is 2+2?",
      "response": "2+2 equals 4. This is basic addition..."
    }
  ],
  "metric_name": "educational_effectiveness"
}
```

### Available Modules
```http
GET /modules
```

### Conversation Metrics
```http
GET /metrics/{conversation_id}
```

## 🧠 DSPy Modules

### Available Tutoring Modules

1. **TutorRAG** (`general`)
   - General purpose tutoring with retrieval-augmented generation
   - Optimizable prompts and context handling
   - Confidence scoring and source attribution

2. **MathTutor** (`math`)
   - Specialized mathematical problem solving
   - Step-by-step solutions with verification
   - Practice problem generation

3. **CodeTutor** (`programming`)
   - Code review and programming assistance
   - Debugging help and best practices
   - Multi-language support

4. **AdaptiveTutor** (`adaptive`)
   - Personalized learning based on student performance
   - Learning style adaptation
   - Progress tracking and recommendations

## 🔄 Integration with Node.js Backend

### Enable DSPy Integration

Add to your Node.js backend `.env`:

```env
# DSPy Integration
ENABLE_DSPY_INTEGRATION=true
DSPY_SERVICE_URL=http://localhost:8001
DSPY_FALLBACK_TO_GEMINI=true
DSPY_REQUEST_TIMEOUT=30000
```

### Usage in Node.js

The integration service automatically enhances your existing `geminiService.js`:

```javascript
// Existing code continues to work
const response = await geminiService.generateResponse(userMessage, context);

// Now automatically uses DSPy when available, falls back to Gemini
// Response includes additional fields when enhanced:
// - enhanced: true
// - explanation: detailed explanation
// - nextSteps: suggested learning steps
// - confidence: response confidence score
```

## 📊 Optimization

### Automatic Optimization

The service automatically collects training data from successful interactions and can optimize modules:

```javascript
// Trigger optimization (Node.js backend)
await dspyIntegrationService.optimizeModule('math', trainingExamples);
```

### Optimization Metrics

- **Educational Effectiveness**: Measures how well responses help student learning
- **Content Relevance**: Keyword overlap and topic alignment
- **Response Quality**: Completeness, clarity, and structure
- **Engagement**: Student interaction patterns and satisfaction

## 🔍 Monitoring

### Service Health

Check service status:
```bash
curl http://localhost:8001/health
```

### Logs

Service logs are available in:
- Console output (colored, real-time)
- `logs/dspy_service.log` (file, rotated)

### Metrics

Access conversation and learning metrics through the API endpoints or integrate with your monitoring system.

## 🛠️ Development

### Running in Development Mode

```bash
# Enable auto-reload
export RELOAD_ON_CHANGE=true
python start.py
```

### Testing

```bash
# Run basic functionality tests
python -m pytest tests/

# Test specific module
python -c "
import asyncio
from modules.tutor_rag import TutorRAG
async def test():
    tutor = TutorRAG()
    result = tutor.forward('What is 2+2?')
    print(result)
asyncio.run(test())
"
```

### Adding New Modules

1. Create module in `modules/` directory
2. Inherit from `dspy.Module`
3. Implement `forward()` method
4. Add to `tutor_modules` in `main.py`
5. Test and optimize

## 🚨 Troubleshooting

### Common Issues

1. **Service won't start**
   - Check Google API key is set
   - Verify all dependencies installed
   - Check port 8001 is available

2. **DSPy modules not working**
   - Ensure Google API key has proper permissions
   - Check internet connectivity
   - Review logs for specific errors

3. **Optimization failing**
   - Ensure sufficient training examples (>5)
   - Check training data format
   - Monitor memory usage during optimization

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python start.py
```

## 📈 Performance

### Recommended Settings

- **Production**: Use `gunicorn` or similar WSGI server
- **Memory**: Minimum 2GB RAM for optimization
- **CPU**: Multi-core recommended for concurrent requests
- **Storage**: SSD recommended for cache performance

### Scaling

- Run multiple service instances behind load balancer
- Use Redis for shared optimization cache
- Consider GPU acceleration for large-scale optimization

## 🔐 Security

- Keep Google API key secure
- Use HTTPS in production
- Implement rate limiting
- Monitor API usage and costs

## 📝 License

This DSPy integration is part of the AI Tutor application project.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📞 Support

For issues and questions:
1. Check logs and troubleshooting guide
2. Review DSPy documentation
3. Open GitHub issue with details
