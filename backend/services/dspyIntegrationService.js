/**
 * DSPy Integration Service
 * Connects the Node.js backend with the Python DSPy service
 * Provides enhanced AI tutoring capabilities with systematic optimization
 */

import axios from 'axios';
import { config } from 'dotenv';
import vectorMemoryService from './vectorMemoryService.js';

config();

class DSPyIntegrationService {
  constructor() {
    this.dspyServiceUrl = process.env.DSPY_SERVICE_URL || 'http://localhost:8001';
    this.isEnabled = process.env.ENABLE_DSPY_INTEGRATION === 'true';
    this.fallbackToGemini = process.env.DSPY_FALLBACK_TO_GEMINI !== 'false';
    this.timeout = parseInt(process.env.DSPY_REQUEST_TIMEOUT) || 60000; // Increased to 60 seconds
    
    // Track service health
    this.isHealthy = false;
    this.lastHealthCheck = null;
    
    console.log(`DSPy Integration Service initialized:`);
    console.log(`- Service URL: ${this.dspyServiceUrl}`);
    console.log(`- Enabled: ${this.isEnabled}`);
    console.log(`- Fallback to Gemini: ${this.fallbackToGemini}`);
  }

  /**
   * Check if DSPy service is available and healthy
   */
  async checkHealth() {
    if (!this.isEnabled) {
      return false;
    }

    try {
      const response = await axios.get(`${this.dspyServiceUrl}/health`, {
        timeout: 5000
      });
      
      this.isHealthy = response.status === 200 && response.data.status === 'healthy';
      this.lastHealthCheck = new Date();
      
      if (this.isHealthy) {
        console.log('DSPy service is healthy');
      }
      
      return this.isHealthy;
    } catch (error) {
      console.warn('DSPy service health check failed:', error.message);
      this.isHealthy = false;
      this.lastHealthCheck = new Date();
      return false;
    }
  }

  /**
   * Enhanced chat response using DSPy modules
   * Replaces or enhances the current geminiService.generateResponse
   */
  async generateEnhancedResponse(userMessage, context = {}) {
    // Check if DSPy service is available
    if (!this.isEnabled || !(await this.checkHealth())) {
      if (this.fallbackToGemini) {
        console.log('DSPy service unavailable, falling back to Gemini');
        return null; // Let the caller handle fallback
      } else {
        throw new Error('DSPy service is not available');
      }
    }

    try {
      // Check if user is asking about previous conversations
      const isMemoryQuery = /remember|recall|previous|earlier|before|conversation about|discussed|talked about/i.test(userMessage);

      // If it's a memory query, try to retrieve relevant context from all conversations
      let relevantMemoryContext = [];
      if (isMemoryQuery) {
        console.log('Memory query detected in DSPy service, searching across all conversations');
        try {
          relevantMemoryContext = await vectorMemoryService.retrieveRelevantContext(
            userMessage,
            10, // Get more results for memory queries
            'search_all' // Special flag to search all conversations
          );
          console.log(`Found ${relevantMemoryContext.length} relevant memory contexts`);
        } catch (error) {
          console.warn('Could not retrieve memory context:', error.message);
        }
      }

      const requestData = {
        message: userMessage,
        conversation_id: context.conversationId,
        user_id: context.userId || 'anonymous',
        subject: this._detectSubject(userMessage),
        difficulty_level: context.difficultyLevel || 'intermediate',
        context: {
          ...context,
          timestamp: new Date().toISOString(),
          memory_context: relevantMemoryContext.length > 0 ? relevantMemoryContext : null,
          is_memory_query: isMemoryQuery
        }
      };

      console.log('Sending request to DSPy service:', {
        message: userMessage.substring(0, 100) + '...',
        subject: requestData.subject,
        conversationId: context.conversationId
      });

      const response = await axios.post(`${this.dspyServiceUrl}/chat`, requestData, {
        timeout: this.timeout,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.data && response.data.response) {
        console.log('DSPy service responded successfully');

        // Store conversation in vector memory for future retrieval
        try {
          await vectorMemoryService.storeConversation(
            context.conversationId || response.data.conversation_id,
            userMessage,
            response.data.response,
            {
              userId: context.userId,
              timestamp: new Date().toISOString(),
              enhanced: true,
              subject: requestData.subject,
              confidence: response.data.confidence
            }
          );
          console.log('Stored DSPy conversation in vector memory');
        } catch (error) {
          console.warn('Could not store DSPy conversation in vector memory:', error.message);
        }

        return {
          response: response.data.response,
          explanation: response.data.explanation,
          nextSteps: response.data.next_steps,
          confidence: response.data.confidence,
          sources: response.data.sources,
          conversationId: response.data.conversation_id,
          enhanced: true, // Flag to indicate this came from DSPy
          processingTime: response.headers['x-processing-time'] || null
        };
      } else {
        throw new Error('Invalid response from DSPy service');
      }

    } catch (error) {
      console.error('Error calling DSPy service:', error.message);
      
      if (this.fallbackToGemini) {
        console.log('Falling back to Gemini service');
        return null; // Let the caller handle fallback
      } else {
        throw new Error(`DSPy service error: ${error.message}`);
      }
    }
  }

  /**
   * Generate response with file processing using DSPy multimodal capabilities
   */
  async generateResponseWithFiles(userMessage, files = [], context = {}) {
    if (!this.isEnabled || !(await this.checkHealth())) {
      if (this.fallbackToGemini) {
        return null; // Fallback to existing implementation
      } else {
        throw new Error('DSPy service is not available');
      }
    }

    try {
      // Prepare file content for DSPy service
      const filesContent = files.map(file => ({
        name: file.originalname || file.name,
        type: file.mimetype || file.type,
        content: file.processedContent || file.content || 'File content not available',
        metadata: file.metadata || {}
      }));

      const requestData = {
        message: userMessage,
        conversation_id: context.conversationId,
        user_id: context.userId || 'anonymous',
        subject: this._detectSubject(userMessage),
        difficulty_level: context.difficultyLevel || 'intermediate',
        context: {
          ...context,
          files_content: filesContent,
          has_files: true,
          file_count: files.length
        }
      };

      const response = await axios.post(`${this.dspyServiceUrl}/chat`, requestData, {
        timeout: this.timeout * 2, // Longer timeout for file processing
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.data && response.data.response) {
        // Store conversation with files in vector memory
        try {
          // Create a comprehensive document that includes file information
          const documentContent = `User Message: ${userMessage}\n\nFiles Processed:\n${filesContent.map(f => `- ${f.name} (${f.type}): ${f.content.substring(0, 500)}...`).join('\n')}\n\nAI Response: ${response.data.response}`;

          await vectorMemoryService.storeConversation(
            context.conversationId || response.data.conversation_id,
            userMessage,
            response.data.response,
            {
              userId: context.userId,
              timestamp: new Date().toISOString(),
              enhanced: true,
              subject: requestData.subject,
              confidence: response.data.confidence,
              hasFiles: true,
              fileCount: files.length,
              fileNames: files.map(f => f.originalname || f.name)
            }
          );

          // Also store file content separately for better searchability
          for (const file of filesContent) {
            if (file.content && file.content.length > 50) {
              await vectorMemoryService.storeDocument(
                file.content,
                {
                  type: 'file_content',
                  fileName: file.name,
                  fileType: file.type,
                  conversationId: context.conversationId || response.data.conversation_id,
                  userId: context.userId,
                  timestamp: new Date().toISOString()
                }
              );
            }
          }

          console.log('Stored DSPy file conversation in vector memory');
        } catch (error) {
          console.warn('Could not store DSPy file conversation in vector memory:', error.message);
        }

        return {
          response: response.data.response,
          explanation: response.data.explanation,
          nextSteps: response.data.next_steps,
          confidence: response.data.confidence,
          sources: response.data.sources,
          conversationId: response.data.conversation_id,
          enhanced: true,
          filesProcessed: files.length,
          processingTime: response.headers['x-processing-time'] || null
        };
      } else {
        throw new Error('Invalid response from DSPy service');
      }

    } catch (error) {
      console.error('Error calling DSPy service with files:', error.message);
      
      if (this.fallbackToGemini) {
        return null; // Fallback to existing implementation
      } else {
        throw new Error(`DSPy service error: ${error.message}`);
      }
    }
  }

  /**
   * Optimize a specific module using collected training data
   */
  async optimizeModule(moduleName, trainingExamples) {
    if (!this.isEnabled || !(await this.checkHealth())) {
      throw new Error('DSPy service is not available for optimization');
    }

    try {
      const requestData = {
        module_name: moduleName,
        training_examples: trainingExamples,
        metric_name: 'educational_effectiveness'
      };

      console.log(`Starting optimization for module: ${moduleName} with ${trainingExamples.length} examples`);

      const response = await axios.post(`${this.dspyServiceUrl}/optimize`, requestData, {
        timeout: 300000, // 5 minutes for optimization
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('Module optimization started successfully');
      return response.data;

    } catch (error) {
      console.error('Error optimizing module:', error.message);
      throw new Error(`Module optimization failed: ${error.message}`);
    }
  }

  /**
   * Get available DSPy modules
   */
  async getAvailableModules() {
    if (!this.isEnabled || !(await this.checkHealth())) {
      return [];
    }

    try {
      const response = await axios.get(`${this.dspyServiceUrl}/modules`, {
        timeout: 5000
      });

      return response.data;
    } catch (error) {
      console.error('Error fetching available modules:', error.message);
      return [];
    }
  }

  /**
   * Get conversation metrics from DSPy service
   */
  async getConversationMetrics(conversationId) {
    if (!this.isEnabled || !(await this.checkHealth())) {
      return null;
    }

    try {
      const response = await axios.get(`${this.dspyServiceUrl}/metrics/${conversationId}`, {
        timeout: 10000
      });

      return response.data;
    } catch (error) {
      console.error('Error fetching conversation metrics:', error.message);
      return null;
    }
  }

  /**
   * Detect subject area from user message
   * This helps select the appropriate DSPy module
   */
  _detectSubject(message) {
    const messageLower = message.toLowerCase();
    
    // Math indicators
    if (this._containsAny(messageLower, [
      'math', 'equation', 'solve', 'calculate', 'algebra', 'geometry', 
      'calculus', 'statistics', 'number', 'formula', 'theorem'
    ])) {
      return 'math';
    }
    
    // Programming indicators
    if (this._containsAny(messageLower, [
      'code', 'programming', 'function', 'variable', 'loop', 'algorithm',
      'debug', 'syntax', 'javascript', 'python', 'java', 'c++', 'html', 'css'
    ])) {
      return 'programming';
    }
    
    // Science indicators
    if (this._containsAny(messageLower, [
      'science', 'physics', 'chemistry', 'biology', 'experiment', 
      'hypothesis', 'theory', 'research', 'analysis'
    ])) {
      return 'science';
    }
    
    return 'general';
  }

  /**
   * Helper method to check if message contains any of the given keywords
   */
  _containsAny(text, keywords) {
    return keywords.some(keyword => text.includes(keyword));
  }

  /**
   * Get service statistics and health information
   */
  async getServiceStats() {
    const stats = {
      isEnabled: this.isEnabled,
      isHealthy: this.isHealthy,
      lastHealthCheck: this.lastHealthCheck,
      serviceUrl: this.dspyServiceUrl,
      fallbackEnabled: this.fallbackToGemini
    };

    if (this.isEnabled && this.isHealthy) {
      try {
        // Get additional stats from DSPy service
        const response = await axios.get(`${this.dspyServiceUrl}/health`, {
          timeout: 5000
        });
        
        stats.dspyServiceInfo = response.data;
      } catch (error) {
        console.warn('Could not fetch DSPy service stats:', error.message);
      }
    }

    return stats;
  }

  /**
   * Collect training data from successful interactions
   * This can be called after each successful interaction to build training dataset
   */
  collectTrainingData(userMessage, aiResponse, context = {}) {
    // This would typically store training examples for later optimization
    // For now, we'll just log the collection
    console.log('Collecting training data:', {
      question: userMessage.substring(0, 50) + '...',
      responseLength: aiResponse.length,
      subject: context.subject || 'general',
      conversationId: context.conversationId
    });

    // In a real implementation, you might:
    // 1. Store in database with quality ratings
    // 2. Periodically trigger optimization when enough data is collected
    // 3. A/B test optimized vs non-optimized modules
  }
}

export default new DSPyIntegrationService();
