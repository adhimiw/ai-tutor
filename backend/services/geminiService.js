import { GoogleGenerativeAI } from '@google/generative-ai';
import dotenv from 'dotenv';
import vectorMemoryService from './vectorMemoryService.js';
import dspyIntegrationService from './dspyIntegrationService.js';
import Conversation from '../models/Conversation.js';

dotenv.config();

class GeminiService {
  constructor() {
    this.genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
    this.model = this.genAI.getGenerativeModel({
      model: "gemini-2.5-flash",
      generationConfig: {
        temperature: 0.7,
        topP: 0.8,
        topK: 40,
        maxOutputTokens: 8192, // Increased for longer responses
      }
    });

    // Separate model for vision tasks
    this.visionModel = this.genAI.getGenerativeModel({
      model: "gemini-2.5-flash",
      generationConfig: {
        temperature: 0.4, // Lower temperature for more accurate image analysis
        topP: 0.8,
        topK: 40,
        maxOutputTokens: 4096,
      }
    });
    
    // System prompt for AI tutor
    this.systemPrompt = `You are Neto, an advanced AI tutor created to help students learn and understand various subjects. You have access to comprehensive information about Adhithan's portfolio, projects, skills, and educational background.

Your capabilities include:
- Explaining complex concepts in simple terms
- Providing step-by-step solutions to problems
- Offering personalized learning recommendations
- Answering questions about programming, technology, and academic subjects
- Helping with project ideas and implementation guidance
- Providing career advice based on Adhithan's experience
- Analyzing documents and images to provide educational insights
- Processing PDFs and extracting relevant information for learning
- Understanding visual content and explaining concepts through images

Guidelines:
- Be encouraging and supportive
- Adapt your teaching style to the student's level
- Use examples and analogies to clarify concepts
- Ask follow-up questions to ensure understanding
- Provide practical, actionable advice
- Reference Adhithan's projects and experience when relevant
- When analyzing documents or images, provide detailed educational explanations
- Break down complex visual or textual information into digestible parts

Always maintain a friendly, professional, and educational tone.`;
  }

  async generateResponse(userMessage, context = {}) {
    try {
      const conversationId = context.conversationId || `conv_${Date.now()}`;

      // Try DSPy enhanced response first
      try {
        const dspyResponse = await dspyIntegrationService.generateEnhancedResponse(userMessage, {
          ...context,
          conversationId
        });

        if (dspyResponse && dspyResponse.enhanced) {
          console.log('Using DSPy enhanced response');

          // Collect training data for future optimization
          dspyIntegrationService.collectTrainingData(userMessage, dspyResponse.response, {
            conversationId,
            subject: context.subject
          });

          return {
            response: dspyResponse.response,
            conversationId: dspyResponse.conversationId,
            enhanced: true,
            explanation: dspyResponse.explanation,
            nextSteps: dspyResponse.nextSteps,
            confidence: dspyResponse.confidence,
            sources: dspyResponse.sources
          };
        }
      } catch (error) {
        console.warn('DSPy service error, falling back to Gemini:', error.message);
      }

      // Fallback to original Gemini implementation
      console.log('Using fallback Gemini response');

      // Try to retrieve relevant context from vector memory (with fallback)
      let relevantContext = [];
      let conversationHistory = [];

      try {
        // Check if user is asking about previous conversations
        const isMemoryQuery = /remember|recall|previous|earlier|before|conversation about|discussed|talked about/i.test(userMessage);

        if (isMemoryQuery) {
          // Search across all conversations for relevant context
          console.log('Memory query detected, searching across all conversations');
          relevantContext = await vectorMemoryService.retrieveRelevantContext(
            userMessage,
            10, // Get more results for memory queries
            'search_all' // Special flag to search all conversations
          );
        } else {
          // Normal conversation-specific context
          relevantContext = await vectorMemoryService.retrieveRelevantContext(
            userMessage,
            5,
            conversationId
          );
        }

        conversationHistory = await vectorMemoryService.getConversationHistory(
          conversationId,
          5
        );
      } catch (error) {
        console.warn('Vector memory not available, continuing without context:', error.message);
      }

      // Prepare the conversation context
      const contextInfo = this.prepareContext(context, relevantContext, conversationHistory, conversationId);

      const prompt = `${this.systemPrompt}

Context Information:
${contextInfo}

Student Question: ${userMessage}

Please provide a helpful, educational response:`;

      const result = await this.model.generateContent(prompt);
      const response = result.response;
      const responseText = response.text();

      // Try to store the conversation in vector memory (with fallback)
      try {
        await vectorMemoryService.storeConversation(
          conversationId,
          userMessage,
          responseText,
          {
            userId: context.userId,
            timestamp: new Date().toISOString()
          }
        );
      } catch (error) {
        console.warn('Could not store conversation in vector memory:', error.message);
      }

      // Update conversation metadata
      await this.updateConversationMetadata(conversationId, userMessage, context.userId);

      return {
        response: responseText,
        conversationId: conversationId
      };
    } catch (error) {
      console.error('Error generating AI response:', error);
      throw new Error('Failed to generate AI response');
    }
  }

  async generateTutorialContent(topic, difficulty = 'beginner') {
    try {
      const prompt = `${this.systemPrompt}

Create a comprehensive tutorial on: ${topic}
Difficulty level: ${difficulty}

Please structure the tutorial with:
1. Introduction and overview
2. Prerequisites (if any)
3. Step-by-step explanation
4. Practical examples
5. Common mistakes to avoid
6. Practice exercises
7. Next steps for further learning

Make it engaging and educational:`;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Error generating tutorial content:', error);
      throw new Error('Failed to generate tutorial content');
    }
  }

  async analyzeCode(code, language) {
    try {
      const prompt = `${this.systemPrompt}

Please analyze the following ${language} code and provide:
1. Code explanation
2. Potential improvements
3. Best practices suggestions
4. Common issues or bugs (if any)
5. Learning opportunities

Code:
\`\`\`${language}
${code}
\`\`\`

Provide educational feedback:`;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Error analyzing code:', error);
      throw new Error('Failed to analyze code');
    }
  }

  prepareContext(context, relevantContext = [], conversationHistory = [], currentConversationId = null) {
    let contextInfo = '';

    if (context.userProfile) {
      contextInfo += `Student Profile: ${JSON.stringify(context.userProfile, null, 2)}\n\n`;
    }

    if (context.portfolioData) {
      contextInfo += `Portfolio Information:\n`;
      if (context.portfolioData.about) {
        contextInfo += `About: ${context.portfolioData.about.name} - ${context.portfolioData.about.title}\n`;
        contextInfo += `Bio: ${context.portfolioData.about.bio}\n\n`;
      }

      if (context.portfolioData.projects) {
        contextInfo += `Projects:\n`;
        context.portfolioData.projects.forEach(project => {
          contextInfo += `- ${project.title}: ${project.description}\n`;
          contextInfo += `  Technologies: ${project.technologies.join(', ')}\n`;
        });
        contextInfo += '\n';
      }

      if (context.portfolioData.skills) {
        contextInfo += `Skills:\n`;
        context.portfolioData.skills.forEach(skill => {
          contextInfo += `- ${skill.name} (${skill.category}): Level ${skill.level}/5\n`;
        });
        contextInfo += '\n';
      }
    }

    // Add relevant context from vector memory
    if (relevantContext.length > 0) {
      contextInfo += `Relevant Previous Context:\n`;
      relevantContext.forEach((item, index) => {
        const isFromDifferentConversation = item.conversationId && item.conversationId !== currentConversationId;
        const contextLabel = isFromDifferentConversation ?
          `Previous Conversation ${index + 1}` :
          `${index + 1}`;
        contextInfo += `${contextLabel}. ${item.content}\n`;
        if (isFromDifferentConversation) {
          contextInfo += `   (From conversation: ${item.conversationId})\n`;
        }
      });
      contextInfo += '\n';
    }

    // Add recent conversation history
    if (conversationHistory.length > 0) {
      contextInfo += `Recent Conversation History:\n`;
      conversationHistory.forEach((item, index) => {
        const type = item.metadata.type === 'user_message' ? 'Student' : 'Tutor';
        contextInfo += `${type}: ${item.content}\n`;
      });
      contextInfo += '\n';
    }

    if (context.conversationHistory) {
      contextInfo += `Additional Context:\n${context.conversationHistory}\n\n`;
    }

    return contextInfo;
  }

  async updateConversationMetadata(conversationId, userMessage, userId = null) {
    try {
      let conversation = await Conversation.findOne({ conversationId });

      if (!conversation) {
        // Create new conversation
        const title = userMessage.length > 50 ?
          userMessage.substring(0, 47) + '...' :
          userMessage;

        conversation = new Conversation({
          conversationId,
          userId,
          title,
          messageCount: 1,
          hasVectorMemory: true
        });
      } else {
        // Update existing conversation
        await conversation.incrementMessageCount();
      }

      await conversation.save();
    } catch (error) {
      console.error('Error updating conversation metadata:', error);
      // Don't throw error as this is not critical for the main flow
    }
  }

  async generateQuiz(topic, questionCount = 5, difficulty = 'medium') {
    try {
      const prompt = `${this.systemPrompt}

Generate a quiz on: ${topic}
Number of questions: ${questionCount}
Difficulty: ${difficulty}

Create a JSON response with the following structure:
{
  "title": "Quiz Title",
  "description": "Brief description",
  "questions": [
    {
      "id": 1,
      "question": "Question text",
      "type": "multiple-choice", // or "true-false", "short-answer"
      "options": ["A", "B", "C", "D"], // for multiple choice
      "correctAnswer": "A",
      "explanation": "Explanation of the correct answer"
    }
  ]
}

Generate educational quiz content:`;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return JSON.parse(response.text());
    } catch (error) {
      console.error('Error generating quiz:', error);
      throw new Error('Failed to generate quiz');
    }
  }
  async analyzeImage(imageBuffer, mimeType, prompt = "Analyze this image and explain what you see in an educational context.") {
    try {
      const imagePart = {
        inlineData: {
          data: imageBuffer.toString('base64'),
          mimeType: mimeType
        }
      };

      const fullPrompt = `${this.systemPrompt}

${prompt}

Please provide a detailed educational analysis of this image, including:
- What you observe in the image
- Key concepts or subjects related to the content
- Educational insights or learning opportunities
- Relevant explanations that would help a student understand the content`;

      const result = await this.visionModel.generateContent([fullPrompt, imagePart]);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Error analyzing image:', error);
      throw new Error('Failed to analyze image');
    }
  }

  async processDocument(documentText, documentType = 'pdf', query = null) {
    try {
      let prompt = `${this.systemPrompt}

Document Type: ${documentType}
Document Content:
${documentText}

`;

      if (query) {
        prompt += `Specific Question: ${query}

Please answer the question based on the document content and provide educational context.`;
      } else {
        prompt += `Please analyze this document and provide:
- A comprehensive summary of the key concepts
- Important educational points and insights
- Potential learning objectives
- Questions that students might ask about this content
- Suggestions for further study or related topics`;
      }

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Error processing document:', error);
      throw new Error('Failed to process document');
    }
  }

  async generateResponseWithFiles(userMessage, files = [], context = {}) {
    try {
      const conversationId = context.conversationId || `conv_${Date.now()}`;

      // Try DSPy enhanced response with files first
      try {
        const dspyResponse = await dspyIntegrationService.generateResponseWithFiles(userMessage, files, {
          ...context,
          conversationId
        });

        if (dspyResponse && dspyResponse.enhanced) {
          console.log('Using DSPy enhanced response with files');

          // Collect training data for future optimization
          dspyIntegrationService.collectTrainingData(userMessage, dspyResponse.response, {
            conversationId,
            hasFiles: true,
            fileCount: files.length
          });

          return {
            response: dspyResponse.response,
            conversationId: dspyResponse.conversationId,
            enhanced: true,
            filesProcessed: dspyResponse.filesProcessed,
            explanation: dspyResponse.explanation,
            nextSteps: dspyResponse.nextSteps
          };
        }
      } catch (error) {
        console.warn('DSPy service error with files, falling back to Gemini:', error.message);
      }

      // Fallback to original Gemini implementation
      console.log('Using fallback Gemini response with files');

      // Retrieve relevant context from vector memory
      const relevantContext = await vectorMemoryService.retrieveRelevantContext(
        userMessage,
        5,
        conversationId
      );

      // Get conversation history
      const conversationHistory = await vectorMemoryService.getConversationHistory(
        conversationId,
        5
      );

      let prompt = `${this.systemPrompt}

Context Information:
${this.prepareContext(context, relevantContext, conversationHistory, conversationId)}

Student Question: ${userMessage}

`;

      const parts = [prompt];

      // Process attached files
      if (files && files.length > 0) {
        prompt += `\nAttached Files:\n`;

        for (const file of files) {
          if (file.type === 'image') {
            const imagePart = {
              inlineData: {
                data: file.buffer.toString('base64'),
                mimeType: file.mimeType
              }
            };
            parts.push(imagePart);
            prompt += `- Image: ${file.name}\n`;
          } else if (file.type === 'document') {
            prompt += `- Document: ${file.name}\nContent: ${file.content}\n\n`;
          } else if (file.type === 'text') {
            prompt += `- Text Document: ${file.name}\nContent: ${file.content}\n\n`;
          }
        }

        prompt += `\nPlease analyze the attached files in the context of the student's question and provide a comprehensive educational response.`;
        parts[0] = prompt; // Update the text part
      }

      const result = await this.model.generateContent(parts);
      const response = await result.response;
      const responseText = response.text();

      // Store the conversation in vector memory
      await vectorMemoryService.storeConversation(
        conversationId,
        userMessage,
        responseText,
        {
          userId: context.userId,
          timestamp: new Date().toISOString(),
          hasFiles: files.length > 0,
          fileTypes: files.map(f => f.type)
        }
      );

      // Update conversation metadata
      await this.updateConversationMetadata(conversationId, userMessage, context.userId);

      return {
        response: responseText,
        conversationId: conversationId
      };
    } catch (error) {
      console.error('Error generating response with files:', error);
      throw new Error('Failed to generate response with files');
    }
  }

  async searchDocumentContent(query, documentId) {
    try {
      // Search for relevant document chunks
      const results = await vectorMemoryService.searchDocuments(query, documentId, 5);

      if (results.length === 0) {
        return "No relevant content found in the document for your query.";
      }

      // Combine relevant chunks
      const relevantContent = results.map(r => r.content).join('\n\n');

      const prompt = `${this.systemPrompt}

Document Content (relevant sections):
${relevantContent}

Student Query: ${query}

Based on the relevant sections from the document, please provide a comprehensive answer to the student's query. Include:
- Direct answer to the question
- Educational context and explanations
- References to specific parts of the document
- Additional insights that would help the student understand the topic better`;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Error searching document content:', error);
      throw new Error('Failed to search document content');
    }
  }
  async analyzeImage(imageBuffer, mimeType, prompt = "Analyze this image and explain what you see in an educational context.") {
    try {
      const imagePart = {
        inlineData: {
          data: imageBuffer.toString('base64'),
          mimeType: mimeType
        }
      };

      const fullPrompt = `${this.systemPrompt}

${prompt}

Please provide a detailed educational analysis of this image, including:
- What you observe in the image
- Key concepts or subjects related to the content
- Educational insights or learning opportunities
- Relevant explanations that would help a student understand the content`;

      const result = await this.visionModel.generateContent([fullPrompt, imagePart]);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Error analyzing image:', error);
      throw new Error('Failed to analyze image');
    }
  }

  async processDocument(documentBuffer, mimeType = 'application/pdf', query = null) {
    try {
      const documentPart = {
        inlineData: {
          data: documentBuffer.toString('base64'),
          mimeType: mimeType
        }
      };

      let prompt = `${this.systemPrompt}

Document Analysis Request:
`;

      if (query) {
        prompt += `Specific Question: ${query}

Please answer the question based on the document content and provide educational context.`;
      } else {
        prompt += `Please analyze this document and provide:
- A comprehensive summary of the key concepts
- Important educational points and insights
- Potential learning objectives
- Questions that students might ask about this content
- Suggestions for further study or related topics`;
      }

      const result = await this.model.generateContent([prompt, documentPart]);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Error processing document:', error);
      throw new Error('Failed to process document');
    }
  }

  async generateResponseWithFiles(userMessage, files = [], context = {}) {
    try {
      const conversationId = context.conversationId || `conv_${Date.now()}`;

      // Retrieve relevant context from vector memory
      const relevantContext = await vectorMemoryService.retrieveRelevantContext(
        userMessage,
        5,
        conversationId
      );

      // Get conversation history
      const conversationHistory = await vectorMemoryService.getConversationHistory(
        conversationId,
        5
      );

      let prompt = `${this.systemPrompt}

Context Information:
${this.prepareContext(context, relevantContext, conversationHistory, conversationId)}

Student Question: ${userMessage}

`;

      const parts = [prompt];

      // Process attached files
      if (files && files.length > 0) {
        prompt += `\nAttached Files:\n`;

        for (const file of files) {
          if (file.type === 'image') {
            const imagePart = {
              inlineData: {
                data: file.buffer.toString('base64'),
                mimeType: file.mimeType
              }
            };
            parts.push(imagePart);
            prompt += `- Image: ${file.name}\n`;
          } else if (file.type === 'document') {
            const documentPart = {
              inlineData: {
                data: file.buffer.toString('base64'),
                mimeType: file.mimeType
              }
            };
            parts.push(documentPart);
            prompt += `- Document: ${file.name}\n`;
          } else if (file.type === 'text') {
            prompt += `- Text Document: ${file.name}\nContent: ${file.content}\n\n`;
          }
        }

        prompt += `\nPlease analyze the attached files in the context of the student's question and provide a comprehensive educational response.`;
        parts[0] = prompt; // Update the text part
      }

      const result = await this.model.generateContent(parts);
      const response = await result.response;
      const responseText = response.text();

      // Store the conversation in vector memory
      await vectorMemoryService.storeConversation(
        conversationId,
        userMessage,
        responseText,
        {
          userId: context.userId,
          timestamp: new Date().toISOString(),
          hasFiles: files.length > 0,
          fileTypes: files.map(f => f.type)
        }
      );

      // Update conversation metadata
      await this.updateConversationMetadata(conversationId, userMessage, context.userId);

      return {
        response: responseText,
        conversationId: conversationId
      };
    } catch (error) {
      console.error('Error generating response with files:', error);
      throw new Error('Failed to generate response with files');
    }
  }

  async searchDocumentContent(query, documentId) {
    try {
      // Search for relevant document chunks
      const results = await vectorMemoryService.searchDocuments(query, documentId, 5);

      if (results.length === 0) {
        return "No relevant content found in the document for your query.";
      }

      // Combine relevant chunks
      const relevantContent = results.map(r => r.content).join('\n\n');

      const prompt = `${this.systemPrompt}

Document Content (relevant sections):
${relevantContent}

Student Query: ${query}

Based on the relevant sections from the document, please provide a comprehensive answer to the student's query. Include:
- Direct answer to the question
- Educational context and explanations
- References to specific parts of the document
- Additional insights that would help the student understand the topic better`;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Error searching document content:', error);
      throw new Error('Failed to search document content');
    }
  }
}

export default new GeminiService();
