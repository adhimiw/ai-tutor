#!/bin/bash
echo "🧪 Testing DSPy Integration..."
cd dspy-service
source venv/bin/activate
python test_service.py
