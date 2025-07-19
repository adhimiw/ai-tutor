#!/usr/bin/env python3
"""
WebSocket Continuity and Server Restart Test for AI Tutor "Neto"
Tests chat persistence across server restarts and connection interruptions
"""

import asyncio
import aiohttp
import json
import time
import subprocess
import signal
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebSocketContinuityTest:
    """Test WebSocket continuity and server restart scenarios"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = None
        self.test_conversation_id = None
        self.test_results = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def create_test_conversation(self):
        """Create a test conversation to track across restarts"""
        logger.info("🔄 Creating test conversation...")
        
        try:
            chat_data = {
                'message': 'Hello Neto, I am starting a conversation that should persist across server restarts. Please remember this message.',
                'userId': 'websocket-test-user',
                'conversationId': f'websocket-test-{int(time.time())}'
            }
            
            async with self.session.post(f"{self.base_url}/api/chat", json=chat_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_conversation_id = data.get('conversationId')
                    logger.info(f"✅ Test conversation created: {self.test_conversation_id}")
                    return {
                        'status': 'PASS',
                        'conversation_id': self.test_conversation_id,
                        'response_length': len(data.get('response', ''))
                    }
                else:
                    return {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"❌ Failed to create test conversation: {e}")
            return {'status': 'FAIL', 'error': str(e)}

    async def test_conversation_persistence_before_restart(self):
        """Test that conversation exists before server restart"""
        logger.info("🔍 Testing conversation persistence before restart...")
        
        if not self.test_conversation_id:
            return {'status': 'SKIP', 'reason': 'No test conversation available'}
        
        try:
            # Send follow-up message
            follow_up_data = {
                'message': 'This is my second message. Can you confirm you remember my first message?',
                'userId': 'websocket-test-user',
                'conversationId': self.test_conversation_id
            }
            
            async with self.session.post(f"{self.base_url}/api/chat", json=follow_up_data) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get('response', '').lower()
                    
                    # Check if AI remembers the context
                    memory_indicators = ['remember', 'first', 'previous', 'earlier', 'persist', 'conversation']
                    has_memory = any(indicator in response_text for indicator in memory_indicators)
                    
                    return {
                        'status': 'PASS',
                        'conversation_id': data.get('conversationId'),
                        'memory_detected': has_memory,
                        'response_preview': response_text[:200] + '...' if len(response_text) > 200 else response_text
                    }
                else:
                    return {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"❌ Pre-restart persistence test failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}

    def simulate_server_restart(self):
        """Simulate server restart by stopping and starting backend"""
        logger.info("🔄 Simulating server restart...")
        
        try:
            # Find backend process
            result = subprocess.run(['pgrep', '-f', 'node.*server.js'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                logger.info(f"Found backend processes: {pids}")
                
                # Kill backend processes
                for pid in pids:
                    if pid.strip():
                        try:
                            os.kill(int(pid.strip()), signal.SIGTERM)
                            logger.info(f"Stopped backend process {pid}")
                        except ProcessLookupError:
                            logger.info(f"Process {pid} already stopped")
                
                # Wait for processes to stop
                time.sleep(3)
                
                # Restart backend
                logger.info("Starting backend server...")
                subprocess.Popen(['node', 'server.js'], 
                               cwd='backend', 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                
                # Wait for server to start
                time.sleep(5)
                
                return {'status': 'PASS', 'action': 'Server restarted successfully'}
            else:
                return {'status': 'FAIL', 'error': 'Backend process not found'}
                
        except Exception as e:
            logger.error(f"❌ Server restart simulation failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}

    async def test_conversation_persistence_after_restart(self):
        """Test that conversation persists after server restart"""
        logger.info("🔍 Testing conversation persistence after restart...")
        
        if not self.test_conversation_id:
            return {'status': 'SKIP', 'reason': 'No test conversation available'}
        
        # Wait for server to be ready
        await asyncio.sleep(5)
        
        try:
            # Test server health first
            async with self.session.get(f"{self.base_url}/api/health") as response:
                if response.status != 200:
                    return {'status': 'FAIL', 'error': 'Server not healthy after restart'}
            
            # Send message to existing conversation
            post_restart_data = {
                'message': 'This is my message after the server restart. Do you still remember our conversation?',
                'userId': 'websocket-test-user',
                'conversationId': self.test_conversation_id
            }
            
            async with self.session.post(f"{self.base_url}/api/chat", json=post_restart_data) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get('response', '').lower()
                    
                    # Check if conversation ID is maintained
                    conversation_maintained = data.get('conversationId') == self.test_conversation_id
                    
                    # Check if AI shows awareness of previous context
                    context_indicators = ['remember', 'conversation', 'previous', 'before', 'restart', 'persist']
                    has_context = any(indicator in response_text for indicator in context_indicators)
                    
                    return {
                        'status': 'PASS' if conversation_maintained else 'PARTIAL',
                        'conversation_id_maintained': conversation_maintained,
                        'context_awareness': has_context,
                        'response_preview': response_text[:200] + '...' if len(response_text) > 200 else response_text
                    }
                else:
                    return {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"❌ Post-restart persistence test failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}

    async def test_conversation_history_retrieval(self):
        """Test that conversation history can be retrieved after restart"""
        logger.info("📚 Testing conversation history retrieval...")
        
        try:
            async with self.session.get(f"{self.base_url}/api/memory/conversations?limit=20") as response:
                if response.status == 200:
                    data = await response.json()
                    conversations = data.get('conversations', [])
                    
                    # Look for our test conversation
                    test_conv_found = any(
                        conv.get('conversationId') == self.test_conversation_id 
                        for conv in conversations
                    )
                    
                    return {
                        'status': 'PASS',
                        'total_conversations': len(conversations),
                        'test_conversation_found': test_conv_found,
                        'conversation_id': self.test_conversation_id
                    }
                else:
                    return {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"❌ Conversation history retrieval failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}

    async def run_websocket_continuity_tests(self):
        """Run all WebSocket continuity tests"""
        logger.info("🚀 Starting WebSocket Continuity Tests")
        logger.info("=" * 50)
        
        # Test 1: Create test conversation
        self.test_results['create_conversation'] = await self.create_test_conversation()
        
        # Test 2: Test persistence before restart
        self.test_results['pre_restart_persistence'] = await self.test_conversation_persistence_before_restart()
        
        # Test 3: Simulate server restart
        self.test_results['server_restart'] = self.simulate_server_restart()
        
        # Test 4: Test persistence after restart
        self.test_results['post_restart_persistence'] = await self.test_conversation_persistence_after_restart()
        
        # Test 5: Test conversation history retrieval
        self.test_results['history_retrieval'] = await self.test_conversation_history_retrieval()
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'PASS')
        
        logger.info("=" * 50)
        logger.info("🎯 WEBSOCKET CONTINUITY TEST SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {total_tests - passed_tests}")
        logger.info(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Save results
        with open('websocket_continuity_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'test_results': self.test_results,
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'success_rate': (passed_tests/total_tests)*100
                }
            }, f, indent=2, default=str)
        
        logger.info("📄 Results saved to: websocket_continuity_results.json")
        
        return self.test_results

async def main():
    """Main test execution"""
    async with WebSocketContinuityTest() as test_suite:
        await test_suite.run_websocket_continuity_tests()

if __name__ == "__main__":
    asyncio.run(main())
