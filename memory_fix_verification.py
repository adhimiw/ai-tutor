#!/usr/bin/env python3
"""
Memory Fix Verification Test for AI Tutor "Neto"
Tests that the AI can now remember previous conversations
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemoryFixVerification:
    """Test memory fix functionality"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_memory_functionality(self):
        """Test that AI can remember previous conversations"""
        logger.info("🧠 Testing Memory Functionality...")
        
        results = {}
        
        # Test 1: Ask about RDBMS conversation
        try:
            memory_query = {
                'message': 'Can you remember our conversation about RDBMS?',
                'userId': 'memory-verification-user'
            }
            
            async with self.session.post(f"{self.base_url}/api/chat", json=memory_query) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get('response', '').lower()
                    
                    # Check if AI shows memory of RDBMS conversation
                    memory_indicators = ['remember', 'rdbms', 'database', 'lab', 'analyzed', 'discussed']
                    memory_score = sum(1 for indicator in memory_indicators if indicator in response_text)
                    
                    results['rdbms_memory_test'] = {
                        'status': 'PASS' if memory_score >= 3 else 'FAIL',
                        'memory_score': memory_score,
                        'memory_indicators_found': [ind for ind in memory_indicators if ind in response_text],
                        'response_preview': response_text[:200] + '...' if len(response_text) > 200 else response_text,
                        'conversation_id': data.get('conversationId')
                    }
                    
                    if memory_score >= 3:
                        logger.info(f"✅ RDBMS memory test PASSED (score: {memory_score}/6)")
                    else:
                        logger.info(f"❌ RDBMS memory test FAILED (score: {memory_score}/6)")
                else:
                    results['rdbms_memory_test'] = {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            results['rdbms_memory_test'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ RDBMS memory test failed: {e}")
        
        # Test 2: Ask about specific document content
        try:
            specific_query = {
                'message': 'What specific topics were covered in the RDBMS lab document we discussed?',
                'userId': 'memory-verification-user'
            }
            
            async with self.session.post(f"{self.base_url}/api/chat", json=specific_query) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get('response', '').lower()
                    
                    # Check for specific RDBMS topics
                    specific_topics = ['sql', 'normalization', 'constraints', 'relational', 'schema', 'queries']
                    topic_score = sum(1 for topic in specific_topics if topic in response_text)
                    
                    results['specific_content_test'] = {
                        'status': 'PASS' if topic_score >= 2 else 'FAIL',
                        'topic_score': topic_score,
                        'topics_found': [topic for topic in specific_topics if topic in response_text],
                        'response_preview': response_text[:200] + '...' if len(response_text) > 200 else response_text,
                        'conversation_id': data.get('conversationId')
                    }
                    
                    if topic_score >= 2:
                        logger.info(f"✅ Specific content test PASSED (score: {topic_score}/6)")
                    else:
                        logger.info(f"❌ Specific content test FAILED (score: {topic_score}/6)")
                else:
                    results['specific_content_test'] = {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            results['specific_content_test'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Specific content test failed: {e}")
        
        # Test 3: Cross-conversation memory
        try:
            cross_conv_query = {
                'message': 'Do you remember any previous conversations we had about databases or files?',
                'userId': 'memory-verification-user'
            }
            
            async with self.session.post(f"{self.base_url}/api/chat", json=cross_conv_query) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get('response', '').lower()
                    
                    # Check for cross-conversation awareness
                    cross_indicators = ['previous', 'conversation', 'remember', 'discussed', 'analyzed', 'files']
                    cross_score = sum(1 for indicator in cross_indicators if indicator in response_text)
                    
                    results['cross_conversation_test'] = {
                        'status': 'PASS' if cross_score >= 2 else 'FAIL',
                        'cross_score': cross_score,
                        'indicators_found': [ind for ind in cross_indicators if ind in response_text],
                        'response_preview': response_text[:200] + '...' if len(response_text) > 200 else response_text,
                        'conversation_id': data.get('conversationId')
                    }
                    
                    if cross_score >= 2:
                        logger.info(f"✅ Cross-conversation test PASSED (score: {cross_score}/6)")
                    else:
                        logger.info(f"❌ Cross-conversation test FAILED (score: {cross_score}/6)")
                else:
                    results['cross_conversation_test'] = {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            results['cross_conversation_test'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Cross-conversation test failed: {e}")
        
        return results

    async def check_vector_memory_stats(self):
        """Check vector memory statistics"""
        logger.info("📊 Checking Vector Memory Stats...")
        
        try:
            async with self.session.get(f"{self.base_url}/api/memory/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    stats = data.get('stats', {})
                    
                    return {
                        'status': 'PASS',
                        'total_documents': stats.get('totalDocuments', 0),
                        'storage_type': stats.get('storageType', 'unknown'),
                        'is_initialized': stats.get('isInitialized', False),
                        'total_conversations': stats.get('totalConversations', 0)
                    }
                else:
                    return {'status': 'FAIL', 'error': f"HTTP {response.status}"}
        except Exception as e:
            return {'status': 'FAIL', 'error': str(e)}

    async def run_verification(self):
        """Run complete memory fix verification"""
        logger.info("🚀 Starting Memory Fix Verification")
        logger.info("=" * 60)
        
        # Check vector memory stats
        memory_stats = await self.check_vector_memory_stats()
        logger.info(f"📊 Vector Memory: {memory_stats.get('total_documents', 0)} documents stored")
        
        # Test memory functionality
        memory_results = await self.test_memory_functionality()
        
        # Generate summary
        total_tests = len(memory_results)
        passed_tests = sum(1 for result in memory_results.values() if result.get('status') == 'PASS')
        
        logger.info("=" * 60)
        logger.info("🎯 MEMORY FIX VERIFICATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {total_tests - passed_tests}")
        logger.info(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        for test_name, result in memory_results.items():
            status_emoji = "✅" if result.get('status') == 'PASS' else "❌"
            logger.info(f"{status_emoji} {test_name}: {result.get('status')}")
        
        # Save results
        final_results = {
            'timestamp': datetime.now().isoformat(),
            'memory_stats': memory_stats,
            'memory_tests': memory_results,
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': (passed_tests/total_tests)*100,
                'memory_fix_status': 'WORKING' if passed_tests >= 2 else 'NEEDS_WORK'
            }
        }
        
        with open('memory_fix_verification_results.json', 'w') as f:
            json.dump(final_results, f, indent=2, default=str)
        
        logger.info("📄 Results saved to: memory_fix_verification_results.json")
        
        # Final verdict
        if passed_tests >= 2:
            logger.info("🎉 MEMORY FIX VERIFICATION: SUCCESS!")
            logger.info("✅ AI Tutor 'Neto' can now remember previous conversations!")
        else:
            logger.info("⚠️ MEMORY FIX VERIFICATION: NEEDS IMPROVEMENT")
            logger.info("❌ Memory functionality needs further work")
        
        return final_results

async def main():
    """Main verification execution"""
    async with MemoryFixVerification() as verifier:
        await verifier.run_verification()

if __name__ == "__main__":
    asyncio.run(main())
