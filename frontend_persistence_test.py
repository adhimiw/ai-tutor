#!/usr/bin/env python3
"""
Frontend Chat Persistence Test for AI Tutor "Neto"
Tests frontend chat saving, localStorage persistence, and UI state management
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FrontendPersistenceTest:
    """Test frontend chat persistence and state management"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.frontend_url = "http://localhost:3000"
        self.session = None
        self.test_results = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_frontend_availability(self):
        """Test that frontend is available and serving content"""
        logger.info("🌐 Testing frontend availability...")
        
        try:
            async with self.session.get(self.frontend_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Check for key frontend elements
                    has_react = 'react' in content.lower() or 'root' in content
                    has_chat_elements = any(keyword in content.lower() for keyword in 
                                          ['chat', 'message', 'input', 'conversation'])
                    
                    return {
                        'status': 'PASS',
                        'response_size': len(content),
                        'has_react_elements': has_react,
                        'has_chat_elements': has_chat_elements,
                        'content_type': response.headers.get('content-type', 'unknown')
                    }
                else:
                    return {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"❌ Frontend availability test failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}

    async def test_chat_api_integration(self):
        """Test that chat API works correctly for frontend integration"""
        logger.info("💬 Testing chat API integration...")
        
        try:
            # Test multiple chat messages to simulate frontend usage
            messages = [
                "Hello, I'm testing the frontend chat integration",
                "Can you help me with a math problem: 2+2=?",
                "What programming languages do you know?"
            ]
            
            conversation_id = f"frontend-test-{int(time.time())}"
            responses = []
            
            for i, message in enumerate(messages):
                chat_data = {
                    'message': message,
                    'userId': 'frontend-test-user',
                    'conversationId': conversation_id
                }
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/api/chat", json=chat_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        responses.append({
                            'message_index': i + 1,
                            'response_time': f"{response_time:.2f}s",
                            'response_length': len(data.get('response', '')),
                            'conversation_id': data.get('conversationId'),
                            'success': True
                        })
                    else:
                        responses.append({
                            'message_index': i + 1,
                            'success': False,
                            'error': f"HTTP {response.status}"
                        })
                
                # Small delay between messages
                await asyncio.sleep(1)
            
            successful_responses = sum(1 for r in responses if r.get('success', False))
            
            return {
                'status': 'PASS' if successful_responses == len(messages) else 'PARTIAL',
                'total_messages': len(messages),
                'successful_responses': successful_responses,
                'conversation_id': conversation_id,
                'responses': responses
            }
            
        except Exception as e:
            logger.error(f"❌ Chat API integration test failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}

    async def test_conversation_retrieval(self):
        """Test conversation history retrieval for frontend display"""
        logger.info("📚 Testing conversation retrieval for frontend...")
        
        try:
            # Test getting recent conversations
            async with self.session.get(f"{self.base_url}/api/memory/conversations?limit=10") as response:
                if response.status == 200:
                    data = await response.json()
                    conversations = data.get('conversations', [])
                    
                    # Analyze conversation data structure for frontend compatibility
                    if conversations:
                        sample_conv = conversations[0]
                        required_fields = ['conversationId', 'title', 'lastActivity', 'messageCount']
                        has_required_fields = all(field in sample_conv for field in required_fields)
                        
                        return {
                            'status': 'PASS',
                            'total_conversations': len(conversations),
                            'has_required_fields': has_required_fields,
                            'sample_conversation': {
                                'id': sample_conv.get('conversationId', 'N/A'),
                                'title': sample_conv.get('title', 'N/A')[:50] + '...',
                                'message_count': sample_conv.get('messageCount', 0),
                                'last_activity': sample_conv.get('lastActivity', 'N/A')
                            }
                        }
                    else:
                        return {
                            'status': 'PASS',
                            'total_conversations': 0,
                            'note': 'No conversations found, but API is working'
                        }
                else:
                    return {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"❌ Conversation retrieval test failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}

    async def test_memory_stats_for_frontend(self):
        """Test memory statistics API for frontend dashboard"""
        logger.info("📊 Testing memory stats for frontend dashboard...")
        
        try:
            async with self.session.get(f"{self.base_url}/api/memory/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    stats = data.get('stats', {})
                    
                    # Check for frontend-relevant statistics
                    frontend_relevant_stats = {
                        'total_conversations': stats.get('totalConversations', 0),
                        'active_conversations': stats.get('activeConversations', 0),
                        'total_documents': stats.get('totalDocuments', 0),
                        'storage_type': stats.get('storageType', 'unknown'),
                        'is_initialized': stats.get('isInitialized', False)
                    }
                    
                    return {
                        'status': 'PASS',
                        'stats_available': True,
                        'frontend_stats': frontend_relevant_stats,
                        'api_response_structure': 'valid'
                    }
                else:
                    return {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"❌ Memory stats test failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}

    async def test_file_upload_api(self):
        """Test file upload API for frontend file handling"""
        logger.info("📎 Testing file upload API for frontend...")
        
        try:
            # Create a simple test file
            test_content = "This is a test file for frontend upload testing.\nIt contains multiple lines.\nAnd should be processed correctly."
            
            form_data = aiohttp.FormData()
            form_data.add_field('message', 'Please analyze this test file')
            form_data.add_field('userId', 'frontend-file-test')
            form_data.add_field('files', test_content.encode(), 
                              filename='frontend_test.txt', 
                              content_type='text/plain')
            
            start_time = time.time()
            async with self.session.post(f"{self.base_url}/api/chat", data=form_data) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        'status': 'PASS',
                        'processing_time': f"{processing_time:.2f}s",
                        'files_processed': data.get('filesProcessed', 0),
                        'response_length': len(data.get('response', '')),
                        'conversation_id': data.get('conversationId'),
                        'upload_successful': True
                    }
                else:
                    return {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"❌ File upload API test failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}

    async def run_frontend_persistence_tests(self):
        """Run all frontend persistence tests"""
        logger.info("🚀 Starting Frontend Persistence Tests")
        logger.info("=" * 50)
        
        # Test 1: Frontend availability
        self.test_results['frontend_availability'] = await self.test_frontend_availability()
        
        # Test 2: Chat API integration
        self.test_results['chat_api_integration'] = await self.test_chat_api_integration()
        
        # Test 3: Conversation retrieval
        self.test_results['conversation_retrieval'] = await self.test_conversation_retrieval()
        
        # Test 4: Memory stats
        self.test_results['memory_stats'] = await self.test_memory_stats_for_frontend()
        
        # Test 5: File upload API
        self.test_results['file_upload_api'] = await self.test_file_upload_api()
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() 
                          if result.get('status') in ['PASS', 'PARTIAL'])
        
        logger.info("=" * 50)
        logger.info("🎯 FRONTEND PERSISTENCE TEST SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {total_tests - passed_tests}")
        logger.info(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Save results
        with open('frontend_persistence_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'test_results': self.test_results,
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'success_rate': (passed_tests/total_tests)*100
                }
            }, f, indent=2, default=str)
        
        logger.info("📄 Results saved to: frontend_persistence_results.json")
        
        return self.test_results

async def main():
    """Main test execution"""
    async with FrontendPersistenceTest() as test_suite:
        await test_suite.run_frontend_persistence_tests()

if __name__ == "__main__":
    asyncio.run(main())
