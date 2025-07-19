#!/usr/bin/env python3
"""
Test script for DSPy AI Tutor Service
Verifies that the service is working correctly
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DSPyServiceTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_health(self):
        """Test health endpoint"""
        print("🔍 Testing health endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data.get('status', 'unknown')}")
                print(f"   Service: {data.get('service', 'unknown')}")
                print(f"   Version: {data.get('version', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_modules_endpoint(self):
        """Test modules listing endpoint"""
        print("\n🔍 Testing modules endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/modules", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                modules = data.get('modules', [])
                descriptions = data.get('descriptions', {})
                
                print(f"✅ Modules endpoint working")
                print(f"   Available modules: {', '.join(modules)}")
                
                for module in modules:
                    desc = descriptions.get(module, 'No description')
                    print(f"   - {module}: {desc}")
                
                return True
            else:
                print(f"❌ Modules endpoint failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Modules endpoint failed: {e}")
            return False
    
    def test_chat_endpoint(self):
        """Test chat endpoint with different subjects"""
        print("\n🔍 Testing chat endpoint...")
        
        test_cases = [
            {
                "name": "General Question",
                "data": {
                    "message": "What is artificial intelligence?",
                    "subject": "general",
                    "difficulty_level": "intermediate"
                }
            },
            {
                "name": "Math Question",
                "data": {
                    "message": "Solve the equation: 2x + 5 = 13",
                    "subject": "math",
                    "difficulty_level": "beginner"
                }
            },
            {
                "name": "Programming Question",
                "data": {
                    "message": "Explain what a function is in programming",
                    "subject": "programming",
                    "difficulty_level": "beginner"
                }
            }
        ]
        
        success_count = 0
        
        for test_case in test_cases:
            print(f"\n   Testing: {test_case['name']}")
            
            try:
                response = self.session.post(
                    f"{self.base_url}/chat",
                    json=test_case['data'],
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('response'):
                        print(f"   ✅ {test_case['name']} - Success")
                        print(f"      Response length: {len(data['response'])} chars")
                        
                        if data.get('explanation'):
                            print(f"      Has explanation: Yes")
                        
                        if data.get('next_steps'):
                            print(f"      Next steps provided: {len(data['next_steps'])}")
                        
                        if data.get('confidence'):
                            print(f"      Confidence: {data['confidence']:.2f}")
                        
                        success_count += 1
                    else:
                        print(f"   ❌ {test_case['name']} - No response content")
                else:
                    print(f"   ❌ {test_case['name']} - HTTP {response.status_code}")
                    if response.text:
                        print(f"      Error: {response.text[:200]}...")
                        
            except requests.exceptions.RequestException as e:
                print(f"   ❌ {test_case['name']} - Request failed: {e}")
        
        print(f"\n✅ Chat endpoint tests: {success_count}/{len(test_cases)} passed")
        return success_count == len(test_cases)
    
    def test_conversation_flow(self):
        """Test conversation flow with context"""
        print("\n🔍 Testing conversation flow...")
        
        conversation_id = "test_conv_123"
        
        messages = [
            "What is a quadratic equation?",
            "Can you give me an example?",
            "How do I solve x² - 5x + 6 = 0?"
        ]
        
        success_count = 0
        
        for i, message in enumerate(messages):
            print(f"   Message {i+1}: {message[:50]}...")
            
            try:
                response = self.session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": message,
                        "conversation_id": conversation_id,
                        "subject": "math",
                        "difficulty_level": "intermediate"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('response'):
                        print(f"   ✅ Message {i+1} - Success")
                        success_count += 1
                    else:
                        print(f"   ❌ Message {i+1} - No response")
                else:
                    print(f"   ❌ Message {i+1} - HTTP {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Message {i+1} - Request failed: {e}")
        
        print(f"\n✅ Conversation flow tests: {success_count}/{len(messages)} passed")
        return success_count == len(messages)
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        print("\n🔍 Testing metrics endpoint...")
        
        conversation_id = "test_conv_123"
        
        try:
            response = self.session.get(
                f"{self.base_url}/metrics/{conversation_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Metrics endpoint working")
                
                if 'conversation_id' in data:
                    print(f"   Conversation ID: {data['conversation_id']}")
                
                if 'engagement_score' in data:
                    print(f"   Engagement score: {data['engagement_score']}")
                
                return True
            else:
                print(f"❌ Metrics endpoint failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Metrics endpoint failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting DSPy Service Tests")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health),
            ("Modules Endpoint", self.test_modules_endpoint),
            ("Chat Endpoint", self.test_chat_endpoint),
            ("Conversation Flow", self.test_conversation_flow),
            ("Metrics Endpoint", self.test_metrics_endpoint)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} - Unexpected error: {e}")
        
        print("\n" + "=" * 50)
        print(f"🏁 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! DSPy service is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Please check the service configuration.")
            return False

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test DSPy AI Tutor Service")
    parser.add_argument(
        "--url",
        default="http://localhost:8001",
        help="Base URL of the DSPy service (default: http://localhost:8001)"
    )
    
    args = parser.parse_args()
    
    tester = DSPyServiceTester(args.url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
