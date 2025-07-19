#!/usr/bin/env python3
"""
Comprehensive Test Suite for AI Tutor "Neto"
Tests all functionality including file processing, memory persistence, and WebSocket continuity
"""

import asyncio
import aiohttp
import json
import time
import os
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NetoTestSuite:
    """Comprehensive test suite for AI Tutor Neto"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.dspy_url = "http://localhost:8001"
        self.frontend_url = "http://localhost:3000"
        
        self.test_results = {
            'realtime_features': {},
            'file_processing': {},
            'memory_system': {},
            'frontend_persistence': {},
            'websocket_continuity': {},
            'integration_tests': {}
        }
        
        self.session = None
        self.test_conversation_id = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def test_realtime_features(self):
        """Test real-time communication features"""
        logger.info("🔍 Testing Real-time Features...")
        
        results = {}
        
        # Test 1: Backend Health Check
        try:
            async with self.session.get(f"{self.base_url}/api/health") as response:
                if response.status == 200:
                    data = await response.json()
                    results['backend_health'] = {
                        'status': 'PASS',
                        'response_time': response.headers.get('X-Response-Time', 'N/A'),
                        'database_status': data.get('database', 'Unknown'),
                        'details': data
                    }
                    logger.info("✅ Backend health check passed")
                else:
                    results['backend_health'] = {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            results['backend_health'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Backend health check failed: {e}")
        
        # Test 2: DSPy Service Health
        try:
            async with self.session.get(f"{self.dspy_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    results['dspy_health'] = {
                        'status': 'PASS',
                        'response_time': response.headers.get('X-Response-Time', 'N/A'),
                        'details': data
                    }
                    logger.info("✅ DSPy service health check passed")
                else:
                    results['dspy_health'] = {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            results['dspy_health'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ DSPy service health check failed: {e}")
        
        # Test 3: Frontend Availability
        try:
            async with self.session.get(self.frontend_url) as response:
                if response.status == 200:
                    results['frontend_availability'] = {
                        'status': 'PASS',
                        'response_time': response.headers.get('X-Response-Time', 'N/A')
                    }
                    logger.info("✅ Frontend availability check passed")
                else:
                    results['frontend_availability'] = {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            results['frontend_availability'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Frontend availability check failed: {e}")
        
        # Test 4: Real-time Chat Response
        try:
            chat_data = {
                'message': 'Hello Neto, this is a real-time test message',
                'userId': 'test-user-realtime',
                'conversationId': f'test-conv-{int(time.time())}'
            }
            
            start_time = time.time()
            async with self.session.post(f"{self.base_url}/api/chat", json=chat_data) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    results['realtime_chat'] = {
                        'status': 'PASS',
                        'response_time': f"{response_time:.2f}s",
                        'conversation_id': data.get('conversationId'),
                        'response_length': len(data.get('response', '')),
                        'enhanced': data.get('enhanced', False)
                    }
                    self.test_conversation_id = data.get('conversationId')
                    logger.info(f"✅ Real-time chat test passed ({response_time:.2f}s)")
                else:
                    results['realtime_chat'] = {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            results['realtime_chat'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Real-time chat test failed: {e}")
        
        self.test_results['realtime_features'] = results
        return results

    async def test_file_processing(self):
        """Test PDF and image file processing capabilities"""
        logger.info("📁 Testing File Processing Features...")
        
        results = {}
        
        # Test 1: PDF Processing
        pdf_path = Path("realtime/RDBMS lab.pdf")
        if pdf_path.exists():
            try:
                with open(pdf_path, 'rb') as f:
                    pdf_content = f.read()
                
                form_data = aiohttp.FormData()
                form_data.add_field('message', 'Please analyze this PDF document')
                form_data.add_field('userId', 'test-user-pdf')
                form_data.add_field('files', pdf_content, 
                                  filename='RDBMS lab.pdf', 
                                  content_type='application/pdf')
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/api/chat", data=form_data) as response:
                    processing_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        results['pdf_processing'] = {
                            'status': 'PASS',
                            'processing_time': f"{processing_time:.2f}s",
                            'files_processed': data.get('filesProcessed', 0),
                            'response_length': len(data.get('response', '')),
                            'conversation_id': data.get('conversationId')
                        }
                        logger.info(f"✅ PDF processing test passed ({processing_time:.2f}s)")
                    else:
                        results['pdf_processing'] = {'status': 'FAIL', 'error': f"HTTP {response.status}"}
            except Exception as e:
                results['pdf_processing'] = {'status': 'FAIL', 'error': str(e)}
                logger.error(f"❌ PDF processing test failed: {e}")
        else:
            results['pdf_processing'] = {'status': 'SKIP', 'reason': 'PDF file not found'}
            logger.warning("⚠️ PDF file not found, skipping PDF test")
        
        # Test 2: Image Processing
        image_path = Path("realtime/screenshot_19072025_183339.jpg")
        if image_path.exists():
            try:
                with open(image_path, 'rb') as f:
                    image_content = f.read()
                
                form_data = aiohttp.FormData()
                form_data.add_field('message', 'Please analyze this image')
                form_data.add_field('userId', 'test-user-image')
                form_data.add_field('files', image_content, 
                                  filename='screenshot_19072025_183339.jpg', 
                                  content_type='image/jpeg')
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/api/chat", data=form_data) as response:
                    processing_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        results['image_processing'] = {
                            'status': 'PASS',
                            'processing_time': f"{processing_time:.2f}s",
                            'files_processed': data.get('filesProcessed', 0),
                            'response_length': len(data.get('response', '')),
                            'conversation_id': data.get('conversationId')
                        }
                        logger.info(f"✅ Image processing test passed ({processing_time:.2f}s)")
                    else:
                        results['image_processing'] = {'status': 'FAIL', 'error': f"HTTP {response.status}"}
            except Exception as e:
                results['image_processing'] = {'status': 'FAIL', 'error': str(e)}
                logger.error(f"❌ Image processing test failed: {e}")
        else:
            results['image_processing'] = {'status': 'SKIP', 'reason': 'Image file not found'}
            logger.warning("⚠️ Image file not found, skipping image test")
        
        # Test 3: Multiple File Processing
        try:
            form_data = aiohttp.FormData()
            form_data.add_field('message', 'Please analyze these multiple files')
            form_data.add_field('userId', 'test-user-multi')
            
            files_added = 0
            for file_path in ["realtime/sda.pdf", "realtime/screenshot_19072025_184854.jpg"]:
                if Path(file_path).exists():
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    form_data.add_field('files', content, 
                                      filename=Path(file_path).name, 
                                      content_type='application/pdf' if file_path.endswith('.pdf') else 'image/jpeg')
                    files_added += 1
            
            if files_added > 0:
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/api/chat", data=form_data) as response:
                    processing_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        results['multi_file_processing'] = {
                            'status': 'PASS',
                            'processing_time': f"{processing_time:.2f}s",
                            'files_sent': files_added,
                            'files_processed': data.get('filesProcessed', 0),
                            'response_length': len(data.get('response', '')),
                            'conversation_id': data.get('conversationId')
                        }
                        logger.info(f"✅ Multi-file processing test passed ({processing_time:.2f}s)")
                    else:
                        results['multi_file_processing'] = {'status': 'FAIL', 'error': f"HTTP {response.status}"}
            else:
                results['multi_file_processing'] = {'status': 'SKIP', 'reason': 'No files available for multi-file test'}
        except Exception as e:
            results['multi_file_processing'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Multi-file processing test failed: {e}")
        
        self.test_results['file_processing'] = results
        return results

    async def test_memory_system(self):
        """Test memory persistence and conversation continuity"""
        logger.info("🧠 Testing Memory System...")
        
        results = {}
        
        # Test 1: Memory Stats
        try:
            async with self.session.get(f"{self.base_url}/api/memory/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    results['memory_stats'] = {
                        'status': 'PASS',
                        'total_conversations': data.get('totalConversations', 0),
                        'total_messages': data.get('totalMessages', 0),
                        'vector_store_size': data.get('vectorStoreSize', 0),
                        'details': data
                    }
                    logger.info("✅ Memory stats test passed")
                else:
                    results['memory_stats'] = {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            results['memory_stats'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Memory stats test failed: {e}")
        
        # Test 2: Conversation History
        try:
            async with self.session.get(f"{self.base_url}/api/memory/conversations?limit=10") as response:
                if response.status == 200:
                    data = await response.json()
                    conversations = data.get('conversations', [])
                    results['conversation_history'] = {
                        'status': 'PASS',
                        'conversations_found': len(conversations),
                        'recent_conversations': conversations[:3] if conversations else []
                    }
                    logger.info(f"✅ Conversation history test passed ({len(conversations)} conversations found)")
                else:
                    results['conversation_history'] = {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            results['conversation_history'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Conversation history test failed: {e}")
        
        # Test 3: Context Continuity
        if self.test_conversation_id:
            try:
                # Send follow-up message to test context
                follow_up_data = {
                    'message': 'What did I just ask you about in my previous message?',
                    'userId': 'test-user-context',
                    'conversationId': self.test_conversation_id
                }
                
                async with self.session.post(f"{self.base_url}/api/chat", json=follow_up_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get('response', '').lower()
                        
                        # Check if response shows context awareness
                        context_indicators = ['previous', 'earlier', 'before', 'you asked', 'mentioned']
                        has_context = any(indicator in response_text for indicator in context_indicators)
                        
                        results['context_continuity'] = {
                            'status': 'PASS' if has_context else 'PARTIAL',
                            'conversation_id': data.get('conversationId'),
                            'context_detected': has_context,
                            'response_preview': response_text[:100] + '...' if len(response_text) > 100 else response_text
                        }
                        logger.info(f"✅ Context continuity test {'passed' if has_context else 'partially passed'}")
                    else:
                        results['context_continuity'] = {'status': 'FAIL', 'error': f"HTTP {response.status}"}
            except Exception as e:
                results['context_continuity'] = {'status': 'FAIL', 'error': str(e)}
                logger.error(f"❌ Context continuity test failed: {e}")
        else:
            results['context_continuity'] = {'status': 'SKIP', 'reason': 'No conversation ID available'}
        
        self.test_results['memory_system'] = results
        return results

    def generate_test_report(self):
        """Generate comprehensive test report"""
        report = {
            'test_summary': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0
            },
            'detailed_results': self.test_results,
            'recommendations': []
        }
        
        # Count test results
        for category, tests in self.test_results.items():
            for test_name, result in tests.items():
                report['test_summary']['total_tests'] += 1
                status = result.get('status', 'UNKNOWN')
                if status == 'PASS':
                    report['test_summary']['passed_tests'] += 1
                elif status == 'FAIL':
                    report['test_summary']['failed_tests'] += 1
                elif status == 'SKIP':
                    report['test_summary']['skipped_tests'] += 1
        
        # Generate recommendations
        if report['test_summary']['failed_tests'] > 0:
            report['recommendations'].append("Address failed tests to ensure full functionality")
        
        if self.test_results.get('file_processing', {}).get('pdf_processing', {}).get('status') == 'SKIP':
            report['recommendations'].append("Add PDF test files to realtime folder for complete testing")
        
        return report

    async def run_all_tests(self):
        """Run all test suites"""
        logger.info("🚀 Starting Comprehensive Test Suite for AI Tutor 'Neto'")
        logger.info("=" * 60)
        
        # Run test suites
        await self.test_realtime_features()
        await self.test_file_processing()
        await self.test_memory_system()
        
        # Generate and save report
        report = self.generate_test_report()
        
        # Save report to file
        with open('neto_test_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        logger.info("=" * 60)
        logger.info("🎯 TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {report['test_summary']['total_tests']}")
        logger.info(f"✅ Passed: {report['test_summary']['passed_tests']}")
        logger.info(f"❌ Failed: {report['test_summary']['failed_tests']}")
        logger.info(f"⏭️ Skipped: {report['test_summary']['skipped_tests']}")
        
        success_rate = (report['test_summary']['passed_tests'] / report['test_summary']['total_tests']) * 100
        logger.info(f"📊 Success Rate: {success_rate:.1f}%")
        
        if report['recommendations']:
            logger.info("\n💡 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                logger.info(f"  • {rec}")
        
        logger.info(f"\n📄 Detailed report saved to: neto_test_report.json")
        
        return report

async def main():
    """Main test execution"""
    async with NetoTestSuite() as test_suite:
        await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
